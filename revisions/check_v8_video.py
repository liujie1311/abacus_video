from pathlib import Path
import sys,subprocess,json,io,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
ROOT=BASE/'交付_V8_60秒_原动态开场_按PDF分镜';OUT=ROOT/'04_视频成片'
src=OUT/'ABACUSLab_V8_60秒_原动态开场_男声_无字幕.mp4'
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
times=[2,5,7.5,11,15,18,22,26,30,32,35,39,42,47,51,57]
sheet=Image.new('RGB',(1440,1200),'#e9edf5');font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
for i,t in enumerate(times):
    im=getframe(t)
    if t in [2,5,30,35,39,42,57]:im.save(OUT/'制作文件'/f'核对帧_{t}.png')
    im.thumbnail((360,203));x=i%4*360;y=i//4*300
    ImageDraw.Draw(sheet).text((x+10,y+12),f'{t}s',font=font,fill='#15203b');sheet.paste(im,(x,y+50))
sheet.save(OUT/'成片画面核对.jpg',quality=95)
metrics=[]
for name,a,b,roi in [('原开场结构旋转',2,4,(1040,250,1830,820)),('输入逐字出现',28,30.5,(430,700,1400,770)),('工作流状态强调',33.7,35,(1120,560,1800,930)),('曲线依次绘制',38.5,43,(750,332,1770,875))]:
    aa=np.asarray(getframe(a).crop(roi),dtype=np.float32);bb=np.asarray(getframe(b).crop(roi),dtype=np.float32)
    diff=float(np.mean(np.abs(aa-bb)));assert diff>.3,(name,diff)
    metrics.append({'item':name,'pixel_difference':diff})
taildiff=float(np.mean(np.abs(np.asarray(getframe(58.1),dtype=np.float32)-np.asarray(getframe(59.7),dtype=np.float32))))
assert taildiff<.15,taildiff
audio=np.frombuffer(subprocess.check_output([ff,'-v','error','-i',str(src),'-f','f32le','-ac','1','-ar','16000','pipe:1']),np.float32)
assert abs(len(audio)/16000-60)<.08
assert float(abs(audio).max())<.98
voices=json.loads((OUT/'制作文件/配音检查.json').read_text(encoding='utf-8'))
for r,end in zip(voices,[6,16,27,37,46,53,60]):assert r['end']<end
assert voices[-1]['end']<58
report={'duration':len(audio)/16000,'resolution':[1920,1080],'fps':30,'subtitle_track':False,'decode_completed':True,'black_intervals':black,'audio_peak':float(abs(audio).max()),'audio_rms':float(np.sqrt(np.mean(audio**2))),'max_voice_speed':max(r['speed'] for r in voices),'last_two_seconds_mean_difference':taildiff,'motion_checks':metrics,'bytes':src.stat().st_size}
(OUT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
