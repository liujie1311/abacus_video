"""Check the encoded deliverable, motion, replacement frame and preserved audio."""
import io
import json
import re
import subprocess
import numpy as np
from PIL import Image, ImageDraw
import make_v10_clean_platform as r

ff = r.s.FF
def command(args):
    return subprocess.check_output([ff,'-v','error',*args])
def frame(t):
    data = command(['-ss',str(t),'-i',str(r.DEST),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
    return Image.open(io.BytesIO(data)).convert('RGB')
def audio(path):
    return command(['-i',str(path),'-map','0:a:0','-f','f32le','-ac','1','-ar','16000','pipe:1'])

probe = subprocess.run([ff,'-hide_banner','-i',str(r.DEST)],capture_output=True).stderr.decode('utf-8','replace')
assert '1920x1080' in probe and '30 fps' in probe and 'Audio: aac' in probe
assert 'Subtitle:' not in probe
decode = subprocess.run([ff,'-hide_banner','-i',str(r.DEST),'-vf','blackdetect=d=0.033:pix_th=0.10:pic_th=0.98','-an','-f','null','-'],capture_output=True)
assert decode.returncode == 0
black = re.findall(r'black_start:([^\s]+) black_end:([^\s]+) black_duration:([^\s]+)',decode.stderr.decode('utf-8','replace'))
assert not black
new_audio, old_audio = audio(r.DEST), audio(r.SOURCE)
assert new_audio == old_audio, 'Audio must remain identical to V9'
pcm = np.frombuffer(new_audio,np.float32)
assert abs(len(pcm)/16000-60)<.08
assert float(abs(pcm).max())<.98

checks = []
for name,a,b,roi in [
    ('开场晶格运动',2,4,(1040,250,1830,820)),
    ('平台截图轻微推进',6.5,8.2,(100,160,1820,1000)),
    ('输入逐字出现',17,19.5,(430,700,1400,770)),
    ('曲线动态绘制',38.5,43,(750,332,1770,875)),
]:
    diff = float(np.mean(np.abs(np.asarray(frame(a).crop(roi),dtype=float)-np.asarray(frame(b).crop(roi),dtype=float))))
    assert diff>.3,(name,diff)
    checks.append({'item':name,'pixel_difference':diff})

times = [2,5,7.5,11,18,26,35,42,50,57]
sheet = Image.new('RGB',(800,1280),'#e9edf5')
errors = []
for i,t in enumerate(times):
    im = frame(t)
    expected = r.frame(t)
    mae = float(np.mean(np.abs(np.asarray(im,dtype=float)-np.asarray(expected,dtype=float))))
    assert mae<5,(t,mae)
    errors.append({'time':t,'encoded_frame_mae':mae})
    im.save(r.STILLS/f'{t:04.1f}s.png')
    x,y = i%2*400,i//2*256
    r.original_txt(sheet,(x+10,y+4),f'{t:g}s',20,r.s.INK)
    sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),(x,y+30))
sheet.save(r.OUT/'成片画面核对.jpg',quality=95)
report = {'duration':len(pcm)/16000,'resolution':[1920,1080],'fps':30,'subtitle_track':False,'black_intervals':black,'audio_identical_to_v9':True,'motion_checks':checks,'encoded_frame_checks':errors,'bytes':r.DEST.stat().st_size}
(r.OUT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
