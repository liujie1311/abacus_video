from pathlib import Path
import sys,subprocess,json,cv2
import numpy as np
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();video=BASE/'ABACUSLAB_60s_1080p.mp4'
cap=cv2.VideoCapture(str(video));fps=cap.get(cv2.CAP_PROP_FPS);count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
report={'width':int(cap.get(3)),'height':int(cap.get(4)),'fps':fps,'frames':count,'duration':count/fps,'bytes':video.stat().st_size}
assert report['width']==1920 and report['height']==1080
assert count==1800 and abs(fps-30)<.01
times=[0,4.9,5.2,11.9,21.9,23,26.5,29.9,32,36.5,39.5,42,44.5,48,52.9,54.5,56.4,59.9]
sheet=Image.new('RGB',(1440,1620),'white')
for i,t in enumerate(times):
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,fr=cap.read();assert ok, t
 img=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB));assert np.array(img).std()>10
 img.thumbnail((480,270));sheet.paste(img,((i%3)*480,(i//3)*270))
cap.release();sheet.save(BASE/'final_contact.jpg',quality=95)
result=subprocess.run([ff,'-v','error','-i',str(video),'-f','null','-'],capture_output=True)
report['decode_returncode']=result.returncode;report['decode_errors']=result.stderr.decode('utf-8',errors='replace')
assert result.returncode==0 and not report['decode_errors']
audio=subprocess.check_output([ff,'-v','error','-i',str(video),'-vn','-f','f32le','-ar','48000','-ac','2','pipe:1'])
a=np.frombuffer(audio,np.float32);report['audio_seconds']=len(a)/96000;report['audio_peak']=float(np.max(np.abs(a)));report['audio_rms']=float(np.sqrt(np.mean(a*a)))
assert 59.9<report['audio_seconds']<60.1 and report['audio_peak']<1 and report['audio_rms']>.015
(BASE/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
