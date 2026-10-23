"""V16: explain the real 300 K / 1600 K MSD comparison with state cards."""
from pathlib import Path
import sys, shutil, json, subprocess
from PIL import Image, ImageDraw
import make_v15 as v15

v = v15.v
BASE = v15.BASE
ROOT = BASE / '交付_V16_210秒_MSD固液态对照标注'
WORK=ROOT/'制作文件'; AUDIO=ROOT/'音频'; STILL=ROOT/'分镜预览'; ASSETS=ROOT/'素材'; VOICE=WORK/'voice'
for p in (ROOT,WORK,AUDIO,STILL,ASSETS,VOICE): p.mkdir(parents=True,exist_ok=True)
v.ROOT,v.WORK,v.AUDIO,v.STILL,v.DEST=ROOT,WORK,AUDIO,STILL,ROOT/'ABACUSLab_V16_3分30秒_MSD状态说明.mp4'
v.VOICE=VOICE

light_renderer = v15.prev.prev
original_scene = light_renderer.scene
def scene(kind,t,span):
    im=original_scene(kind,t,span)
    if kind!='msd': return im
    d=ImageDraw.Draw(im)
    # Two editorial cards align with the original purple/green plot series.
    cards=[
      ((105,605,610,755),'#68447a','300 K · 固态','原子局域振动','MSD 近似平台'),
      ((105,790,610,940),'#83c85b','1600 K · 熔融态','原子持续扩散','MSD 随时间上升')]
    for box,color,title,line1,line2 in cards:
        d.rounded_rectangle(box,radius=22,fill='#ffffff',outline=color,width=3)
        x1,y1,x2,y2=box
        d.rounded_rectangle((x1+14,y1+16,x1+26,y2-16),radius=6,fill=color)
        d.text((x1+48,y1+18),title,font=v.font(31,True),fill=color)
        d.text((x1+48,y1+65),line1,font=v.font(24,False),fill='#26344d')
        d.text((x1+48,y1+103),line2,font=v.font(22,False),fill='#687996')
    # Preserve original screenshot data and axes; the existing section title
    # already introduces this comparison, so avoid adding a competing heading.
    return im

# Patch the V13 light-theme renderer's own scene lookup so its palette,
# transitions and editorial chapter cards remain intact throughout V16.
light_renderer.scene=scene
def frame(t):
    if t<7: return v15.prev.first_frames(t)
    return light_renderer.frame(t)
v.frame=frame

def docs():
    shutil.copy2(v15.ROOT/'台词时间轴.md',ROOT/'台词时间轴.md')
    shutil.copy2(v15.ROOT/'V15修改说明.md',ROOT/'V15修改说明.md')
    shutil.copy2(v15.ASSETS/'AI研究目标_编辑示意.png',ASSETS/'AI研究目标_编辑示意.png')
    for src,dst in [(v15.WORK/'mixed.wav',WORK/'mixed.wav'),(v15.WORK/'配音时间核验.json',WORK/'配音时间核验.json')]: shutil.copy2(src,dst)
    for src in v.VOICE.glob('*.mp3'): shutil.copy2(src,VOICE/src.name)
    (ROOT/'V16修改说明.md').write_text('''# V16 修改说明

- 在 1600 K / 300 K 的原始 MSD 对比图左侧加入两张颜色匹配的状态说明卡：300 K 固态（局域振动、MSD近似平台）与 1600 K 熔融态（持续扩散、MSD随时间上升）。
- 保留原图曲线、图例和坐标，不重绘、不改数据；状态文案是对现有温度对比示例的解释。
- 沿用 V15 自然语速旁白、铝合金融化研究目标示意和去除气流扫音的配乐。

''',encoding='utf-8')

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'picture'
    docs()
    if mode=='picture': v.picture()
    elif mode=='final':
        v.run(['-y','-i',str(WORK/'picture.mp4'),'-i',str(WORK/'mixed.wav'),'-map','0:v','-map','1:a',
               '-c:v','copy','-af','loudnorm=I=-17:TP=-3:LRA=9,aresample=48000,alimiter=limit=0.78:level=false:latency=true',
               '-ar','48000','-c:a','aac','-b:a','192k','-t','210','-movflags','+faststart',str(v.DEST)])
    elif mode=='check':
        v.DEST=v.ROOT/'ABACUSLab_V16_3分30秒_MSD状态说明.mp4'
        # Reuse V15's media/voice checks and its contact-sheet logic.
        v15.ROOT=ROOT;v15.WORK=WORK;v15.DEST=v.DEST;v15.v.ENTRIES=v15.ENTRIES
        v15.check()
