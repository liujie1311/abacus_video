"""V5 review revision: remove editorial labels and the illustrative properties scene.

Reuse the original drawing functions and audio; keep the delivered V5 intact.
"""
import json
import math
import shutil
import subprocess
import sys
from PIL import ImageDraw
import make_v5_motion as v

ROOT = v.BASE / '交付_V5_60秒_AI演示优先_修改版'
OUT = ROOT / '04_视频成片'
WORK = OUT / '制作文件'
ASSETS = ROOT / '03_动态素材'
ORIGINAL_OUT = v.OUT
DEST = OUT / 'ABACUSLab_V5修改版_60秒_去辅助小字_无物性示意段.mp4'
for path in [ROOT / '01_演讲稿', ROOT / '02_分镜脚本', WORK, ASSETS / '关键帧']:
    path.mkdir(parents=True, exist_ok=True)

# These labels are editorial overlays, not text within the platform screenshots.
REMOVED_LABELS = {
    '材料结构示意', '平台操作实录', 'AI 分析原文 · 局部放大',
    '流程示意', '示例结果 · 原始曲线逐步展示', '物性类别示意',
}
original_txt = v.txt

def clean_txt(im, xy, s, *args, **kwargs):
    if s not in REMOVED_LABELS:
        original_txt(im, xy, s, *args, **kwargs)

v.txt = clean_txt
original_templates = v.templates

def templates(t):
    # Expand the actual template overview and original cards from 8 to 14 seconds.
    # All entrance animations and highlighting retain their relative timing.
    return original_templates(t * 8 / 14)

def outro(t):
    im = v.LIGHT.copy()
    d = ImageDraw.Draw(im)
    for j in range(16):
        angle = j * math.pi / 8 + t * .07
        x = 960 + 600 * math.cos(angle)
        y = 550 + 340 * math.sin(angle)
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill='#c8d0f4')
    dy = round(25 * (1 - v.ease(t / .9)))
    im.paste(v.ICON, (908, 202 + dy), v.ICON)
    for text, size, y, color, delay in [
        ('ABACUSLab', 86, 350, v.BLUE, .1),
        ('让材料计算更简单', 64, 510, v.INK, .3),
    ]:
        width = v.ft(size, True).getlength(text)
        v.enter(im, ((v.W - width) / 2, y), text, t, delay, size, color, True)
    p = v.ease((t - .5) / 1)
    d.line((960 - 155 * p, 622, 960 + 155 * p, 622), fill='#c5cff2', width=2)
    return im

v.outro = outro

v.SCENES = [
    (0, 6, v.intro), (6, 15, v.question), (15, 20, v.operation),
    (20, 25, v.workflow), (25, 31, v.charts), (31, 37, v.results),
    (37, 51, templates), (51, 55, v.recap), (55, 60, v.outro),
]
v.ROOT, v.OUT, v.WORK, v.ASSETS = ROOT, OUT, WORK, ASSETS
v.STILLS = ASSETS / '关键帧'

CLIPS = [
    ('01_通用开场_6秒_无辅助小字', 6, v.intro),
    ('02_AI提问_逐字输入', 9, v.question),
    ('03_工作流_连线推进_无辅助小字', 5, v.workflow),
    ('04_MSD_原始曲线逐步绘制_无辅助小字', 6, v.charts),
    ('05_模板_总览转卡片特写_14秒', 14, templates),
    ('06_品牌片尾', 5, v.outro),
    ('07_平台操作_无辅助小字', 5, v.operation),
    ('08_AI分析_无辅助小字', 6, v.results),
]

def docs():
    for src in (v.BASE / '交付_V5_60秒_AI演示优先/01_演讲稿').iterdir():
        if src.is_file():
            shutil.copy2(src, ROOT / '01_演讲稿' / src.name)
    shutil.copy2(ORIGINAL_OUT / '制作文件/配音检查.json', WORK / '配音检查.json')
    (ROOT / '00_从这里开始.md').write_text('''# V5 修改版｜60 秒

本次基于 V5「AI 演示优先」版本修改，原 V5 和其他版本保留。

- 成片：04_视频成片/ABACUSLab_V5修改版_60秒_去辅助小字_无物性示意段.mp4
- 新的 6 秒通用开场：03_动态素材/01_通用开场_6秒_无辅助小字.mp4
- 独立动态素材全部为无音轨 MP4，可直接用于剪辑；成片保留 V5 女声配音与音乐。
- 删除「材料结构示意」「平台操作实录」「AI 分析原文 · 局部放大」，并统一删除「流程示意」「示例结果 · 原始曲线逐步展示」同类辅助标注。
- 删除原 45–51 秒「覆盖多类材料计算场景」四卡片示意画面；37–51 秒改为真实模板总览和原始模板卡片展示，保持全片 60 秒。
- 片尾删除「从一句话开始」，保留品牌名称与「让材料计算更简单」。独立片尾素材同步更新。
- 品牌标题、功能文字、平台界面原文、图表坐标和图例保留。开场结构仍为视觉示意，非计算结构或轨迹；科学曲线使用原始图像数据。

规格：1920×1080，30 fps，H.264；成片音频 AAC，无配音字幕及字幕轨。
制作脚本：revisions/make_v5_clean.py，复用 revisions/make_v5_motion.py 绘制函数。
''', encoding='utf-8')
    rows = ['# 修改版时间线', '', '| 时间 | 画面 |', '|---|---|']
    names = ['6 秒通用品牌开场', 'AI 提问与逐字输入', '平台操作与关键参数',
             '工作流连线', 'MSD 原始曲线展示', 'AI 分析与下一步验证',
             '真实模板总览与卡片特写（延长展示）', '从问题到结果回顾', '品牌片尾']
    rows += [f'| {a}–{b} 秒 | {name} |' for (a, b, _), name in zip(v.SCENES, names)]
    (ROOT / '02_分镜脚本/时间线与修改说明.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    rows = ['# 独立动态素材', '', '1920×1080、30 fps、无音轨；无上一镜头的交叉转场残影。', '', '| 文件 | 时长 |', '|---|---|']
    rows += [f'| {name}.mp4 | {duration} 秒 |' for name, duration, _ in CLIPS]
    (ASSETS / '素材说明.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')

def final():
    v.run(['-y', '-i', str(WORK / 'picture_motion.mp4'), '-i',
           str(ORIGINAL_OUT / 'ABACUSLab_V5_60秒_浅色动态版_无字幕.mp4'),
           '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-t', '60',
           '-movflags', '+faststart', str(DEST)])
    for name, duration, fn in CLIPS:
        p = subprocess.Popen([v.FF, '-y', '-v', 'error', '-f', 'rawvideo',
            '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '30', '-i', 'pipe:0',
            '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            '-pix_fmt', 'yuv420p', '-threads', '4', '-movflags', '+faststart',
            str(ASSETS / f'{name}.mp4')], stdin=subprocess.PIPE)
        try:
            for n in range(duration * v.FPS):
                p.stdin.write(fn(n / v.FPS).tobytes())
        finally:
            p.stdin.close()
        if p.wait():
            raise RuntimeError(f'Clip encoding failed: {name}')
        print('Clip complete:', name, flush=True)
    print('DONE', DEST, flush=True)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'previews'
    if mode == 'previews':
        docs()
        v.previews()
    elif mode == 'picture':
        v.picture()
    elif mode == 'final':
        final()
