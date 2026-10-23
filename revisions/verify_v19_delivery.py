"""Check actual encoded opening stability, subtitles, and selected delivered frames."""
from pathlib import Path
import importlib.util,subprocess,json,re
import numpy as np
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent.parent
R=B/'交付_V19_五分钟_去重与稳定重剪'
s=importlib.util.spec_from_file_location('v19',R/'制作文件/build_v19.py')
v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
results=[]
for a,b,mode,key,*_ in v.SHOTS:
    if a>=43 or mode not in ('concept','candidate_intro'):continue
    raw=subprocess.check_output([v.FF,'-v','error','-ss',str(a+.8),'-i',str(v.DEST),'-t','1','-vf','crop=1680:650:120:275,fps=5','-pix_fmt','gray','-f','rawvideo','pipe:1'])
    frames=np.frombuffer(raw,np.uint8).reshape(-1,650,1680).astype(np.float32)
    base=frames[0,4:-4:2,4:-4:2]
    shifts=[];diffs=[]
    for f in frames[1:]:
        scores=[]
        for dy in range(-2,3):
            for dx in range(-2,3):
                sample=f[4+dy:646+dy:2,4+dx:1676+dx:2]
                scores.append((float(np.mean((sample-base)**2)),dx,dy))
        best=min(scores);shifts.append([best[1],best[2]])
        diffs.append(float(np.abs(f[4:-4:2,4:-4:2]-base).mean()))
    assert all(x==[0,0] for x in shifts),(key,shifts)
    results.append({'start':a,'asset':key,'frames_checked':len(frames),'best_translation_pixels':shifts,'max_mean_luma_change':max(diffs)})
def secs(t):
    h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
caps=[]
for block in (R/'中文字幕.srt').read_text(encoding='utf-8').strip().split('\n\n'):
    lines=block.splitlines();a,b=map(secs,lines[1].split(' --> '));text=''.join(lines[2:]);assert 0<=a<b<=300
    caps.append((a,b,text))
assert all(caps[i][1]<=caps[i+1][0] for i in range(len(caps)-1))
assert all(v.l.font(40).getlength(t)<1750 for _,_,t in caps)
folder=R/'成片重点复核';folder.mkdir(exist_ok=True)
for t in [1,53,130,150,177.6,197,255,297]:
    dest=folder/f'{t:06.1f}秒.jpg'
    subprocess.run([v.FF,'-v','error','-y','-ss',str(t),'-i',str(v.DEST),'-frames:v','1','-q:v','2',str(dest)],check=True)
report={'encoded_opening_stability':results,'subtitle_count':len(caps),'subtitle_overlap':False,'subtitles_within_frame':True,'note':'Compression can change pixel values slightly; all tested consecutive opening frames have zero best-fit integer translation.'}
(R/'制作文件/编码后稳定性与字幕检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('ENCODED_QA_PASS',len(results),'shots;',len(caps),'captions',flush=True)
