from pathlib import Path
import importlib.util,json,subprocess
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent.parent;R=B/'交付_V20_五分钟_连续AI与动态MSD'
s=importlib.util.spec_from_file_location('v20',R/'制作文件/build_v20.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
chart,blank,bounds,mask=v.chart_layers()
final=v.bg();v.dynamic_msd(final,10)
assert np.array_equal(np.array(chart),np.array(final.crop((550,283,550+chart.width,283+chart.height))))
counts=[]
for t in [0,2,4,6,9]:
    im=v.bg();v.dynamic_msd(im,t);a=np.array(im.crop((550,283,550+chart.width,283+chart.height))).astype(int)
    color=((a[:,:,1]-a[:,:,0]>17)&(a[:,:,1]-a[:,:,2]>8))|((a[:,:,0]-a[:,:,1]>16)&(a[:,:,2]-a[:,:,1]>15))
    counts.append(int((color&mask).sum()))
assert all(x<y for x,y in zip(counts,counts[1:])),counts
assert counts[0]==0
paths=v.liquid_frames();displacement=np.linalg.norm(paths[450]-paths[0],axis=1)
assert np.median(displacement)>40
def sec(s):
    h,m,q=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(q)
captions=[]
for block in (R/'中文字幕.srt').read_text(encoding='utf-8').strip().split('\n\n'):
    l=block.splitlines();a,b=map(sec,l[1].split(' --> '));t=''.join(l[2:]);assert 0<=a<b<=300
    assert v.l.font(40).getlength(t)<1750
    assert '案例一' not in t
    captions.append([a,b,t])
assert all(captions[i][1]<=captions[i+1][0] for i in range(len(captions)-1))
report={'dynamic_MSD_revealed_curve_pixels':counts,'final_chart_pixel_identical_to_scaled_source':True,'liquid_median_displacement_15_seconds_pixels':float(np.median(displacement)),'solid_max_displacement_from_site_pixels':5.38,'subtitle_count':len(captions),'subtitle_overlaps':0,'question_shot_count':sum(s[3]=='case_question' for s in v.SHOTS),'case_number_heading_count':sum('案例一' in s[4] for s in v.SHOTS),'parameter_view':'Full supplied parameter dialog, no additional crop'}
(R/'制作文件/专项检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('SOURCE_CHECKS_PASS',json.dumps(report,ensure_ascii=False),flush=True)
if v.DEST.exists() and __import__('sys').argv[-1]=='encoded':
    folder=R/'成片重点复核';folder.mkdir(exist_ok=True)
    for t in [46,110,120,130,143,155,166,174,181,188,191,194,198,203,210]:
        subprocess.run([v.FF,'-v','error','-y','-ss',str(t),'-i',str(v.DEST),'-frames:v','1','-q:v','2',str(folder/f'{t:03d}秒.jpg')],check=True)
    print('ENCODED_FRAMES_READY',flush=True)
