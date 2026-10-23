from pathlib import Path
import sys,subprocess,json,re,io
from PIL import Image,ImageDraw,ImageFont
import numpy as np
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
out=BASE/'交付_V3_含模板_无字幕/04_视频成片'
src=out/'ABACUSLab_V3_60秒_1080p_无字幕.mp4'
probe=subprocess.run([ff,'-hide_banner','-i',str(src)],capture_output=True).stderr.decode('utf-8','replace')
assert '1920x1080' in probe and '30 fps' in probe and 'Audio: aac' in probe
assert 'Subtitle:' not in probe
decode=subprocess.run([ff,'-v','error','-i',str(src),'-f','null','-'],capture_output=True)
assert decode.returncode==0 and not decode.stderr
times=[2,6,9,13,19,26,35,41,44,47,51,57]
contact=Image.new('RGB',(1440,1200),'#e8ecf5')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
for i,t in enumerate(times):
 raw=subprocess.check_output([ff,'-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
 im=Image.open(io.BytesIO(raw)).convert('RGB')
 if t in [2,19,26,51]:im.save(out/'制作文件'/f'核对帧_{t:02d}.png')
 im.thumbnail((480,270));x=(i%3)*480;y=(i//3)*300
 ImageDraw.Draw(contact).text((x+10,y+5),f'{t:02d} s',font=font,fill='#15203b');contact.paste(im,(x,y+30))
contact.save(out/'成片画面核对.jpg',quality=94)
audio=np.frombuffer(subprocess.check_output([ff,'-v','error','-i',str(src),'-f','f32le','-ac','1','-ar','16000','pipe:1']),np.float32)
assert float(abs(audio).max())<.98
report=json.loads((out/'制作文件/配音检查.json').read_text(encoding='utf-8'))
for r,end in zip(report,[5,15,23,31,40,49,54,60]):assert r['end']<end
check={'duration':len(audio)/16000,'resolution':[1920,1080],'fps':30,'decode_errors':False,'subtitle_track':False,'audio_peak':float(abs(audio).max()),'audio_rms':float(np.sqrt(np.mean(audio**2))),'max_voice_speed':max(r['speed'] for r in report),'bytes':src.stat().st_size}
(out/'成片检查.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'制作说明.md').write_text('# V3 视频成片\n\n60 秒，1920×1080，30 fps，H.264 / AAC。保留中文女声和合成背景音乐，无配音字幕及字幕轨。\n\n沿用 V3 含模板方案：模板总览与两组卡片特写、AI 提问、原平台操作片段、MSD 图表、结论与局限、流程回顾及品牌片尾。依据后续用户更正，视频输入示例及旁白将“金属熔断”统一为“金属熔点”。V3 原始审查图保持存档，视频使用修订后的对应画面。\n\n镜间使用短淡入淡出；平台操作采用原片内真实录屏区域，其余为清晰静态图文镜头。配音与画面按八段时间线对齐。\n',encoding='utf-8')
print(json.dumps(check,ensure_ascii=False))
