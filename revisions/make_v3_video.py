from pathlib import Path
import sys,json,subprocess,asyncio,wave,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
ROOT=BASE/'交付_V3_含模板_无字幕'
OUT=ROOT/'04_视频成片'
WORK=OUT/'制作文件'
VOICE=WORK/'voice'
for p in [OUT,WORK,VOICE]:p.mkdir(parents=True,exist_ok=True)
M=ROOT/'03_图片素材/01_主分镜_1080p'
E=ROOT/'03_图片素材/02_补充分镜_1080p'
entries=[
 (0,5,'材料计算，从一句话开始。'),
 (5,15,'从基础计算，到电子结构、输运和光学，丰富的模板，覆盖多类材料计算场景。'),
 (15,23,'告诉 AI 你的计算目标。比如，我想计算一下金属熔点。'),
 (23,31,'从理解需求，到分析参数，AI 帮你梳理材料计算思路。'),
 (31,40,'让复杂数据直观呈现，对比不同温度下的原子运动，观察材料的变化。'),
 (40,49,'结合结果，给出分析结论，说明局限，为下一步验证提供参考。'),
 (49,54,'模板、AI、计算、可视化，让流程更连贯。'),
 (54,60,'ABACUSLab，让材料计算更简单。')]
(WORK/'旁白时间线.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
def run(args,**kw):return subprocess.run([FF,'-hide_banner','-loglevel','error',*args],check=True,**kw)

async def voices():
 import edge_tts
 for i,(a,b,t) in enumerate(entries):
  dest=VOICE/f'{i:02d}.mp3'
  if dest.exists() and dest.stat().st_size>2000:continue
  await asyncio.wait_for(edge_tts.Communicate(t.replace('ABACUSLab','ABACUS LAB'),'zh-CN-XiaoxiaoNeural',rate='+0%').save(str(dest)),timeout=50)
  print('Voice',i,flush=True)

def mix():
 SR=48000;N=SR*60
 narration=np.zeros(N,np.float32);report=[]
 for i,(a,b,t) in enumerate(entries):
  raw=subprocess.check_output([FF,'-v','error','-i',str(VOICE/f'{i:02d}.mp3'),'-f','f32le','-ar',str(SR),'-ac','1','pipe:1'])
  data=np.frombuffer(raw,np.float32).copy();ix=np.flatnonzero(abs(data)>.004)
  if len(ix):data=data[max(0,ix[0]-int(.05*SR)):min(len(data),ix[-1]+int(.12*SR))]
  start=a+.30;available=b-start-.35
  factor=max(1.0,len(data)/SR/available)
  if factor>1.001:
   data=np.frombuffer(subprocess.check_output([FF,'-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0','-af',f'atempo={factor:.6f}','-f','f32le','pipe:1'],input=data.tobytes()),np.float32).copy()
  data*=min(.12/max(float(np.sqrt(np.mean(data**2))),.001),.78/max(float(abs(data).max()),.001))
  st=round(start*SR);narration[st:st+len(data)]+=data
  report.append({'start':start,'end':start+len(data)/SR,'speed':factor,'text':t})
 music=np.zeros((N,2),np.float32)
 chords=[[50,57,62,64,69],[46,53,58,60,65],[53,60,65,67,72],[48,55,60,62,67]]
 for bar in range(15):
  st=bar*4*SR;n=min(int(5.1*SR),N-st);tt=np.arange(n)/SR
  env=np.minimum(1,tt/1.1)*np.minimum(1,np.maximum(0,(5.1-tt)/1.4))
  chord=sum(np.sin(2*np.pi*440*2**((note-69)/12)*tt+j*.5) for j,note in enumerate(chords[bar%4]))/5*.035*env
  music[st:st+n]+=chord[:,None]
  for k in range(6):
   pst=int((bar*4+k*2/3)*SR);pn=min(int(1.4*SR),N-pst);pt=np.arange(pn)/SR
   f=440*2**((chords[bar%4][[2,3,4,3,1,3][k]]+12-69)/12)
   tone=np.sin(2*np.pi*f*pt)*(1-np.exp(-pt*50))*np.exp(-pt*3)*.012
   music[pst:pst+pn,k%2]+=tone
 fade=np.minimum(1,np.arange(N)/SR)*np.minimum(1,(N-1-np.arange(N))/SR/1.5)
 audio=(music+narration[:,None])*fade[:,None]
 with wave.open(str(WORK/'配音与音乐.wav'),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(audio,-.97,.97)*32767).astype('<i2').tobytes())
 (WORK/'配音检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Audio mixed',flush=True)

def corrected_images():
 # Update only the prompt wording for the user's later melting-point correction.
 for name,rect,xy,size,color,bold in [
 ('01_开场',(1045,438,1668,510),(1052,444),40,'white',True),
 ('03_自然语言提问',(734,645,1350,710),(740,654),43,'#15203b',False),
 ('07_流程回顾',(562,533,906,636),(578,543),28,'#15203b',False)]:
  im=Image.open(M/f'{name}.png').convert('RGB');d=ImageDraw.Draw(im)
  d.rectangle(rect,fill='#16223e' if name.startswith('01') else 'white')
  ft=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc',size)
  if name.startswith('07'):
   d.text(xy,'我想计算一下',font=ft,fill=color);d.text((xy[0],590),'金属熔点',font=ft,fill=color)
  else:d.text(xy,'我想计算一下金属熔点',font=ft,fill=color)
  im.save(WORK/f'{name}.png')

def picture():
 corrected_images()
 scenes=[(WORK/'01_开场.png',5),(E/'02a_模板库总览.png',2),(E/'02b_基础计算模板特写.png',4),(M/'02_计算模板.png',4),
 (WORK/'03_自然语言提问.png',8),(M/'04_平台操作.png',8),(M/'05_数据可视化.png',9),(M/'06_分析与验证.png',3),
 (E/'06b_局限说明.png',3),(E/'06c_验证建议.png',3),(WORK/'07_流程回顾.png',5),(M/'08_品牌片尾.png',6)]
 for i,(path,dur) in enumerate(scenes):
  dest=WORK/f'scene_{i:02d}.mp4'
  if dest.exists() and dest.stat().st_size>10000:continue
  args=['-y','-loop','1','-framerate','30','-i',str(path)]
  # Reuse the original real interaction panel only; exclude all old captions and headings.
  if i==5:
   args+=['-stream_loop','-1','-ss','30','-t','5','-i',str(BASE/'picture.mp4')]
   filt='[1:v]crop=1120:674:670:208,setpts=PTS-STARTPTS[panel];[0:v][panel]overlay=670:208:eof_action=repeat,fade=t=in:st=0:d=0.20,fade=t=out:st=7.8:d=0.20,format=yuv420p[v]'
   args+=['-filter_complex',filt,'-map','[v]']
  else:
   args+=['-vf',f'fade=t=in:st=0:d=0.20,fade=t=out:st={dur-.20}:d=0.20,format=yuv420p']
  args+=['-t',str(dur),'-r','30','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','4',str(dest)]
  run(args);print('Scene',i+1,'of',len(scenes),flush=True)
 (WORK/'concat.txt').write_text('\n'.join(f"file 'scene_{i:02d}.mp4'" for i in range(len(scenes))),encoding='utf-8')
 run(['-y','-f','concat','-safe','0','-i',str(WORK/'concat.txt'),'-c','copy',str(WORK/'picture.mp4')])

def final():
 dest=OUT/'ABACUSLab_V3_60秒_1080p_无字幕.mp4'
 run(['-y','-i',str(WORK/'picture.mp4'),'-i',str(WORK/'配音与音乐.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','volume=0.8','-c:a','aac','-b:a','192k','-t','60','-movflags','+faststart',str(dest)])
 print('DONE',dest,flush=True)

if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in ['voice','all']:asyncio.run(voices())
 if mode in ['mix','all']:mix()
 if mode in ['picture','all']:picture()
 if mode in ['final','all']:final()
