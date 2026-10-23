import sys,json,subprocess,wave,math
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000;DUR=60;N=SR*DUR
timeline=json.loads((BASE/'timeline.json').read_text(encoding='utf-8'))
voice=np.zeros(N,np.float32);report=[]
for i,item in enumerate(timeline):
 src=BASE/'voice'/f'{i:02d}.mp3'
 raw=subprocess.check_output([FF,'-v','error','-i',str(src),'-f','f32le','-ar',str(SR),'-ac','1','pipe:1'])
 data=np.frombuffer(raw,np.float32).copy()
 # Remove TTS leading and trailing silence before fitting each editorial slot.
 indices=np.flatnonzero(np.abs(data)>.004)
 if len(indices):data=data[max(0,indices[0]-int(.045*SR)):min(len(data),indices[-1]+int(.08*SR))]
 available=item['end']-item['start']-.10
 factor=max(.80,len(data)/SR/available)
 if abs(factor-1)>.001:
  raw=subprocess.check_output([FF,'-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0','-af',f'atempo={factor:.6f}','-f','f32le','pipe:1'],input=data.tobytes())
  data=np.frombuffer(raw,np.float32).copy()
 rms=np.sqrt(np.mean(data**2));data*=min(.115/max(rms,.001),.79/max(np.max(np.abs(data)),.001))
 st=round(item['start']*SR);en=min(N,st+len(data));voice[st:en]+=data[:en-st]
 report.append({'segment':i,'start':item['start'],'duration':round(len(data)/SR,3),'speed':round(factor,3),'text':item['text']})

# Original synthesized underscore: warm suspended chords and a sparse soft arpeggio.
music=np.zeros((N,2),np.float32)
chords=[[50,57,62,64,69],[46,53,58,60,65],[53,60,65,67,72],[48,55,60,62,67]]
def freq(n):return 440*2**((n-69)/12)
def add(start,duration,notes,amp,pan=.5,pluck=False):
 st=int(start*SR);length=min(int(duration*SR),N-st)
 if length<=0:return
 t=np.arange(length,dtype=np.float32)/SR
 if pluck:env=(1-np.exp(-t*55))*np.exp(-t*2.5)*np.minimum(1,(duration-t)*4)
 else:env=np.minimum(1,t/1.2)*np.minimum(1,np.maximum(0,(duration-t)/1.6))
 sig=np.zeros(length,np.float32)
 for j,note in enumerate(notes):
  f=freq(note);sig+=(np.sin(2*np.pi*f*t+j*.6)+.15*np.sin(2*np.pi*f*2*t+j*.4))/len(notes)
 sig*=amp*env
 music[st:st+length,0]+=sig*math.sqrt(1-pan);music[st:st+length,1]+=sig*math.sqrt(pan)
for bar in range(15):
 chord=chords[bar%4];add(bar*4,5.1,chord,.065,.5)
 for b in range(6):
  note=chord[[2,3,4,3,1,3][b]]+12
  add(bar*4+b*2/3,1.5,[note],.026,.25 if b%2 else .75,True)
 # Rounded bass pulse with no hard percussion, leaving room for narration.
 for b in range(2):add(bar*4+b*2,1.7,[chord[0]-12],.028,.5,True)

# Gentle UI taps aligned with send, section changes and closing card.
for st in [5,12,26.15,30,35,38,41,44,53,53.7,54.4,55.1,56]:
 add(st,.24,[81,88],.033,.5,True)

duck=np.ones(N,np.float32)
for item in timeline:
 st=int(max(0,item['start']-.15)*SR);en=int(min(DUR,item['end']+.15)*SR)
 duck[st:en]=.48
window=np.ones(4800,np.float32)/4800
# Smooth ducking in a compact control signal then interpolate to audio rate.
control=duck[::480];control=np.convolve(control,np.ones(15)/15,mode='same')
duck=np.interp(np.arange(N),np.arange(len(control))*480,control).astype(np.float32)
music*=duck[:,None]
fade=np.minimum(1,np.arange(N)/SR/1.0)*np.minimum(1,(N-1-np.arange(N))/SR/1.2)
mix=(music+voice[:,None])*fade[:,None]
peak=float(np.max(np.abs(mix)))
if peak>.95:mix*=.95/peak
with wave.open(str(BASE/'soundtrack.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
(BASE/'audio_report.json').write_text(json.dumps({'segments':report,'peak':peak},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True,indent=2),flush=True)
if '--mix-only' not in sys.argv:
 subprocess.run([FF,'-y','-hide_banner','-loglevel','warning','-i',str(BASE/'picture.mp4'),'-i',str(BASE/'soundtrack.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t','60','-movflags','+faststart',str(BASE/'ABACUSLAB_60s_1080p.mp4')],check=True)
 print('FINAL VIDEO READY',flush=True)
