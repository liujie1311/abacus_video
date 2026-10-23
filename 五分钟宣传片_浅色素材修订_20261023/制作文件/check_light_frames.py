from pathlib import Path
import sys,subprocess,json,hashlib,io
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from build_light_assets import ROOT,PREV,VIDEO,SPECS,FF,REFERENCE,font,txt
def frame(path,t):
    r=subprocess.run([FF,'-v','error','-ss',str(t),'-i',str(path),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],check=True,stdout=subprocess.PIPE)
    return Image.open(io.BytesIO(r.stdout)).convert('RGB')
rows=[];out=Image.new('RGB',(1440,8*294),'#f5f7fe')
for i,(name,dur,_) in enumerate(SPECS):
    av=[]
    for j,t in enumerate([0,dur/2,dur-1/30]):
        im=frame(VIDEO/(name+'.mp4'),t)
        if j==1:im.save(PREV/(name+'_视频实帧.jpg'),quality=94)
        thumb=im.resize((464,261),Image.Resampling.LANCZOS);out.paste(thumb,(8+j*480,i*294))
        txt(out,(12+j*480,i*294+263),name[:3]+f' · {t:.2f}s',19)
        a=np.asarray(im);av.append(float(a[20:50,20:50].mean()))
    rows.append({'clip':name,'start_mid_end_corner_brightness':av})
out.save(PREV/'视频实帧_首中尾核验.jpg',quality=91)
film=ROOT/'02_案例与成片/ABACUSLab_60秒_浅色原子片头_参考片修订.mp4'
out=Image.new('RGB',(1440,3*294),'#f5f7fe')
for i,t in enumerate([0,3,5.96,6,6.2,7,22,42,59]):
    im=frame(film,t);out.paste(im.resize((464,261),Image.Resampling.LANCZOS),(8+(i%3)*480,(i//3)*294));txt(out,(12+(i%3)*480,(i//3)*294+263),f'{t:.2f}s',19)
out.save(PREV/'60秒改版_衔接核验.jpg',quality=94)
def audio_hash(p):
    r=subprocess.run([FF,'-v','error','-i',str(p),'-map','0:a:0','-t','59','-f','s16le','-acodec','pcm_s16le','-'],check=True,stdout=subprocess.PIPE)
    return hashlib.sha256(r.stdout).hexdigest()
result={'frame_checks':rows,'audio_first_59s_unchanged':audio_hash(film)==audio_hash(REFERENCE),'source_video_sha256':hashlib.sha256(REFERENCE.read_bytes()).hexdigest()}
(PREV/'画面与原配音核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
