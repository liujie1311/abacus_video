"""Decode and visually sample the final revision and standalone assets."""
import io
import json
import re
import subprocess
import numpy as np
from PIL import Image, ImageDraw
import make_v5_clean as m

v = m.v

def probe(path, seconds):
    result = subprocess.run([v.FF, '-hide_banner', '-i', str(path),
        '-vf', 'blackdetect=d=0.033:pix_th=0.10:pic_th=0.98',
        '-f', 'null', '-'], capture_output=True)
    log = result.stderr.decode('utf-8', 'replace')
    assert result.returncode == 0, log[-2000:]
    duration = re.search(r'Duration: (\d+):(\d+):([\d.]+)', log)
    duration = int(duration[1]) * 3600 + int(duration[2]) * 60 + float(duration[3])
    assert abs(duration - seconds) < .08, (path, duration)
    assert '1920x1080' in log and '30 fps' in log
    assert 'Subtitle:' not in log and 'black_start:' not in log
    frames = re.findall(r'frame=\s*(\d+)', log)
    assert int(frames[-1]) == seconds * 30, (path, frames[-1])
    return {'file': path.name, 'duration': duration, 'frames': int(frames[-1]),
            'resolution': [1920, 1080], 'fps': 30, 'audio': 'Audio:' in log,
            'decode_completed': True, 'black_intervals': []}

def frame(path, t):
    raw = subprocess.check_output([v.FF, '-v', 'error', '-ss', str(t), '-i',
        str(path), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', 'pipe:1'])
    return Image.open(io.BytesIO(raw)).convert('RGB')

report = {'main': probe(m.DEST, 60), 'assets': []}
assert report['main']['audio']
for name, duration, _ in m.CLIPS:
    check = probe(m.ASSETS / f'{name}.mp4', duration)
    assert not check['audio']
    report['assets'].append(check)

times = [4, 17, 23, 28, 33, 35.5, 39, 44, 45.5, 48, 50.5, 51.3, 53, 58]
sheet = Image.new('RGB', (1440, 1500), '#edf0f9')
errors = []
for i, t in enumerate(times):
    im = frame(m.DEST, t)
    expected = v.frame(t)
    error = float(np.abs(np.asarray(im, dtype=float) - np.asarray(expected, dtype=float)).mean())
    assert error < 4, (t, error)
    errors.append({'time': t, 'mean_pixel_error_vs_clean_render': error})
    x, y = i % 3 * 480, i // 3 * 300
    ImageDraw.Draw(sheet).text((x + 10, y + 3), f'{t:g} s', font=v.ft(20), fill=v.INK)
    sheet.paste(im.resize((480, 270), Image.Resampling.LANCZOS), (x, y + 30))
sheet.save(m.OUT / '成片画面核对.jpg', quality=95)

label_checks = []
for t, box, name in [
    (4, (1310, 842, 1550, 885), '材料结构示意'),
    (17, (660, 921, 930, 966), '平台操作实录'),
    (23, (95, 955, 285, 1000), '流程示意'),
    (28, (590, 900, 1000, 932), '示例结果 · 原始曲线逐步展示'),
    (33, (795, 871, 1240, 910), 'AI 分析原文 · 局部放大'),
    (58, (780, 650, 1140, 720), '片尾：从一句话开始'),
]:
    crop = np.asarray(frame(m.DEST, t).crop(box))
    dark = int((crop.min(axis=2) < 180).sum())
    assert dark == 0, (name, dark)
    label_checks.append({'removed_label': name, 'dark_pixels_in_former_label_area': dark})

clip = m.ASSETS / '01_通用开场_6秒_无辅助小字.mp4'
a = np.asarray(frame(clip, 2).crop((1040, 250, 1830, 820)), dtype=float)
b = np.asarray(frame(clip, 4).crop((1040, 250, 1830, 820)), dtype=float)
motion = float(abs(a - b).mean())
assert motion > .3
def pcm(path):
    return subprocess.check_output([v.FF, '-v', 'error', '-i', str(path),
        '-t', '59.9', '-f', 'f32le', '-ac', '1', '-ar', '16000', 'pipe:1'])
audio = pcm(m.DEST)
assert audio == pcm(m.ORIGINAL_OUT / 'ABACUSLab_V5_60秒_浅色动态版_无字幕.mp4')
report.update({'sample_checks': errors, 'label_checks': label_checks,
    'intro_motion_mean_pixel_change': motion,
    'original_audio_preserved': True, 'removed_scene': '原45–51秒四类物性示意卡片',
    'replacement': '37–51秒真实模板总览和原始卡片展示'})
(m.OUT / '成片检查.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
