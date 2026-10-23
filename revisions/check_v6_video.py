from pathlib import Path
import sys,subprocess,json,io,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
ROOT=BASE/'交付_V6_80秒审看版';OUT=ROOT/'04_视频成片'
src=OUT/'ABACUSLab_V6_80秒_浅色动态审看版_无字幕.mp4'
probe=subprocess.run([ff,'-hide_banner','-i',str(src)],capture_output=True).stderr.decode('utf-8','replace')
assert '1920x1080' in probe and '30 fps' in probe and 'Audio: aac' in probe
assert 'Subtitle:' not in probe
decode=subprocess.run([ff,'-hide_banner','-i',str(src),'-vf','blackdetect=d=0.033:pix_th=0.10:pic_th=0.98','-an','-f','null','-'],capture_output=True)
log=decode.stderr.decode('utf-8','replace');assert decode.returncode==0
black=re.findall(r'black_start:([^\s]+) black_end:([^\s]+) black_duration:([^\s]+)',log)
assert not black
def getframe(t):
    data=subprocess.check_output([ff,'-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
    return Image.open(io.BytesIO(data)).convert('RGB')
times=[2,10,18,22,28,36,42,45,47,50,54,58,61,65,69,76]
sheet=Image.new('RGB',(1440,1200),'#e9edf5');font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
for i,t in enumerate(times):
    im=getframe(t)
    if t in [10,28,47,58]:im.save(OUT/'制作文件'/f'核对帧_{t}.png')
    im.thumbnail((360,203));x=i%4*360;y=i//4*300
    ImageDraw.Draw(sheet).text((x+10,y+12),f'{t}s',font=font,fill='#15203b');sheet.paste(im,(x,y+50))
sheet.save(OUT/'成片画面核对.jpg',quality=95)
metrics=[]
for name,a,b,roi in [('开场结构运动',2,4,(1040,250,1830,820)),('输入逐字出现',27,29.5,(730,640,1700,720)),('工作流状态强调',45,47,(1120,560,1800,930)),('曲线逐步绘制',51,56,(720,275,1740,817))]:
    aa=np.asarray(getframe(a).crop(roi),dtype=np.float32);bb=np.asarray(getframe(b).crop(roi),dtype=np.float32)
    diff=float(np.mean(np.abs(aa-bb)));assert diff>.3,(name,diff)
    metrics.append({'item':name,'pixel_difference':diff})
taildiff=float(np.mean(np.abs(np.asarray(getframe(78.1),dtype=np.float32)-np.asarray(getframe(79.7),dtype=np.float32))))
assert taildiff<.15,taildiff
audio=np.frombuffer(subprocess.check_output([ff,'-v','error','-i',str(src),'-f','f32le','-ac','1','-ar','16000','pipe:1']),np.float32)
assert abs(len(audio)/16000-80)<.08
assert float(abs(audio).max())<.98
voices=json.loads((OUT/'制作文件/配音检查.json').read_text(encoding='utf-8'))
for r,end in zip(voices,[7,15,24,34,40,44,49,62,72,80]):assert r['end']<end
assert voices[-1]['end']<78
report={'duration':len(audio)/16000,'resolution':[1920,1080],'fps':30,'subtitle_track':False,'decode_completed':True,'black_intervals':black,'audio_peak':float(abs(audio).max()),'audio_rms':float(np.sqrt(np.mean(audio**2))),'max_voice_speed':max(r['speed'] for r in voices),'last_two_seconds_mean_difference':taildiff,'motion_checks':metrics,'bytes':src.stat().st_size}
(OUT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
