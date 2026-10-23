from pathlib import Path
import sys,subprocess,json,io,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
ROOT=BASE/'交付_V5_60秒_AI演示优先'
OUT=ROOT/'04_视频成片'
SRC=OUT/'ABACUSLab_V5_60秒_浅色动态版_无字幕.mp4'
probe=subprocess.run([FF,'-hide_banner','-i',str(SRC)],capture_output=True).stderr.decode('utf-8','replace')
assert '1920x1080' in probe and '30 fps' in probe and 'Audio: aac' in probe
assert 'Subtitle:' not in probe
decode=subprocess.run([FF,'-hide_banner','-i',str(SRC),'-vf','blackdetect=d=0.033:pix_th=0.10:pic_th=0.98','-an','-f','null','-'],capture_output=True)
log=decode.stderr.decode('utf-8','replace')
assert decode.returncode==0
black=re.findall(r'black_start:([^\s]+) black_end:([^\s]+) black_duration:([^\s]+)',log)
assert not black,black
def getframe(t):
    raw=subprocess.check_output([FF,'-v','error','-ss',str(t),'-i',str(SRC),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
    return Image.open(io.BytesIO(raw)).convert('RGB')
times=[1,4,10,17,23,26,28,30.5,33,35.5,38.5,41,44,48,53,58]
contact=Image.new('RGB',(1440,1200),'#e9edf5')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
for i,t in enumerate(times):
    im=getframe(t);im.thumbnail((360,202));x=i%4*360;y=i//4*300
    ImageDraw.Draw(contact).text((x+10,y+12),f'{t:g} s',font=font,fill='#15203b')
    contact.paste(im,(x,y+50))
contact.save(OUT/'成片画面核对.jpg',quality=95)
metrics=[]
for name,a,b,roi in [('开场结构持续运动',2,4,(1040,250,1830,820)),('输入逐字出现',8.5,11,(730,640,1670,720)),('原始曲线逐步绘制',26,28.5,(720,275,1740,817)),('模板总览到卡片',38.5,41,(90,370,1840,970))]:
    aa=np.asarray(getframe(a).crop(roi),dtype=np.float32);bb=np.asarray(getframe(b).crop(roi),dtype=np.float32)
    diff=float(np.mean(np.abs(aa-bb)));assert diff>.3,(name,diff)
    metrics.append({'检查项':name,'平均像素变化':diff})
audio=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(SRC),'-f','f32le','-ac','1','-ar','16000','pipe:1']),np.float32)
peak=float(abs(audio).max());assert peak<.98
duration=len(audio)/16000;assert abs(duration-60)<.08
voices=json.loads((OUT/'制作文件/配音检查.json').read_text(encoding='utf-8'))
for r,end in zip(voices,[6,15,25,37,51,60]):assert r['end']<end
report={'duration':duration,'resolution':[1920,1080],'fps':30,'subtitle_track':False,'decode_completed':True,'black_intervals':black,'audio_peak':peak,'audio_rms':float(np.sqrt(np.mean(audio**2))),'max_voice_speed':max(r['speed'] for r in voices),'motion_checks':metrics,'bytes':SRC.stat().st_size}
(OUT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
