"""Check the delivered stream, actual duration, audio peaks, and sample frames."""
import json,re,subprocess
import numpy as np
from PIL import Image
import make_v12_210 as v

info=subprocess.run([v.FF,'-hide_banner','-i',str(v.DEST)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
assert '1920x1080' in info and '30 fps' in info,info
assert 'h264' in info and 'aac' in info,info
decode=subprocess.run([v.FF,'-v','error','-i',str(v.DEST),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0 and not decode.stderr,decode.stderr
pcm=subprocess.check_output([v.FF,'-v','error','-i',str(v.DEST),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1'])
a=np.frombuffer(pcm,np.float32).reshape(-1,2);duration=len(a)/48000;peak=float(abs(a).max())
assert abs(duration-210)<.1 and peak<.98,(duration,peak)
voices=json.loads((v.WORK/'配音时间核验.json').read_text(encoding='utf-8'))
for entry,(_,end,_) in zip(voices,v.ENTRIES):assert entry['end']<end
black=subprocess.run([v.FF,'-hide_banner','-i',str(v.DEST),'-vf','blackdetect=d=0.25:pix_th=0.10','-an','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
black_ranges=re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',black.stderr)
assert all(float(b)<1.2 or float(a)>208.5 for a,b,c in black_ranges),black_ranges
times=[4,11,26,44,71,85,104,116,124,132,139,149,164,174,182,191,198,206]
sheet=Image.new('RGB',(1440,6*300),'#e7edf6')
for i,t in enumerate(times):
    raw=subprocess.check_output([v.FF,'-v','error','-ss',str(t),'-i',str(v.DEST),'-frames:v','1','-vf','scale=480:270','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
    im=Image.frombytes('RGB',(480,270),raw);x=i%3*480;y=i//3*300
    v.text(sheet,(x+10,y+3),f'{t//60:02d}:{t%60:02d}',20);sheet.paste(im,(x,y+30))
sheet.save(v.ROOT/'成片抽帧检查.jpg',quality=95)
result={'duration_seconds':duration,'resolution':'1920x1080','fps':30,'video_codec':'H.264','audio_codec':'AAC','decode_errors':0,'audio_peak_linear':peak,'internal_black_frames':False,'male_voice':'zh-CN-YunjianNeural','narration_sections':len(voices),'narration_overruns':0,'shots':len(v.SHOTS),'size_mb':round(v.DEST.stat().st_size/1048576,1),'checks':'Full decode, audio duration and peak, narration boundaries, black detection, encoded-frame contact sheet. No listening claim.'}
(v.ROOT/'成片检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
