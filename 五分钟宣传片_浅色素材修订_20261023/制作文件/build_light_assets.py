"""Light editorial motion assets; scientific screenshots retain their source pixels.
Run previews, render, assemble, verify. No simulated result or trajectory is generated.
"""
from pathlib import Path
from functools import lru_cache
import math, sys, json, subprocess, hashlib, re, time, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent
OLD=BASE/'五分钟宣传片_补充素材_20261023'
SRC=OLD/'01_已有平台素材'
VIDEO=ROOT/'01_浅色动画'; PREV=ROOT/'预览与核验'
for p in [VIDEO,PREV,ROOT/'02_案例与成片']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
REFERENCE=Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/msg/video/2026-10/0da312f692b46fe2d0afac91646097cf.mp4')
W,H,FPS=1920,1080,30
INK='#182744'; MUTED='#71809b'; BLUE='#596bde'; LINE='#dce4f4'; PAPER='#f5f7fe'
@lru_cache(None)
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc',size)
def txt(im,xy,s,size=30,col=INK,bold=False,anchor=None):
    ImageDraw.Draw(im).text(xy,s,font=font(size,bold),fill=col,anchor=anchor)
def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
yy,xx=np.mgrid[0:H,0:W]
g=np.exp(-((xx-1430)/850)**2-((yy-430)/700)**2)
BG=Image.fromarray(np.stack([248-13*g,250-13*g,255-3*g],-1).astype('uint8'))
del yy,xx,g
def background():return BG.copy()
@lru_cache(None)
def shadow(w,h,r=30):
    a=Image.new('RGBA',(w+70,h+70));ImageDraw.Draw(a).rounded_rectangle((28,20,w+42,h+34),r,fill=(86,111,160,21));return a.filter(ImageFilter.GaussianBlur(15))
def panel(im,box,fill='white',edge=LINE,r=28):
    x,y,x2,y2=map(round,box);s=shadow(x2-x,y2-y,r);im.paste(s,(x-35,y-22),s)
    ImageDraw.Draw(im).rounded_rectangle((x,y,x2,y2),r,fill,edge,2)
def chrome(im,title,subtitle='',tag='概念示意'):
    txt(im,(96,55),'ABACUSLab',28,BLUE,True)
    txt(im,(1824,66),tag,23,MUTED,anchor='ra')
    ImageDraw.Draw(im).line((96,112,1824,112),fill=LINE,width=2)
    txt(im,(96,165),title,60,INK,True)
    if subtitle:txt(im,(100,257),subtitle,29,MUTED)
def footer(im,s):txt(im,(1824,1014),s,21,MUTED,anchor='ra')
@lru_cache(256)
def sphere(radius,tone=0):
    r=int(radius);n=4*r+4;y,x=np.mgrid[-1:1:complex(n),-1:1:complex(n)];rho=x*x+y*y
    z=np.sqrt(np.maximum(0,1-rho));a=np.clip((1-rho)*n/2,0,1)
    light=np.maximum(0,-.42*x-.54*y+.73*z);spec=np.exp(-((x+.33)**2+(y+.42)**2)/.035)*.58
    color=np.array([(95,134,222),(182,199,221),(110,158,197)][tone])
    c=np.clip(color[None,None,:]*(.50+.52*light[:,:,None])+255*spec[:,:,None],0,255)
    # Soft studio reflection keeps the atoms luminous on a white background.
    c=c*(1-.10*z[:,:,None])+np.array([233,243,255])*.10*z[:,:,None]
    arr=np.dstack([c,a*255]).astype('uint8')
    return Image.fromarray(arr).resize((r*2+2,r*2+2),Image.Resampling.LANCZOS)
@lru_cache(None)
def model(kind):
    if kind=='fcc':
        points=[(i-2,j-2,k-2) for i in range(5) for j in range(5) for k in range(5) if (i+j+k)%2==0]
        near=2.01
    elif kind=='layer':
        points=[(1.35*i+.675*(j%2)-2,1.17*j-1.76,z) for z in [-.8,.8] for i in range(4) for j in range(4)];near=1.85
    else:
        points=[(i-1,j-1,k-1) for i in range(3) for j in range(3) for k in range(3)];near=1.01
    a=np.array(points,dtype=float);edges=[]
    for i in range(len(a)):
        for j in range(i+1,len(a)):
            d=np.sum((a[i]-a[j])**2)
            if d<near and d>.01:edges.append((i,j))
    return a,edges
@lru_cache(24)
def floor_shadow(w,h):
    im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im);d.ellipse((w*.06,h*.22,w*.94,h*.78),fill=(94,126,188,30));return im.filter(ImageFilter.GaussianBlur(22))
def atoms(im,t,cx,cy,scale=98,kind='fcc',loop=12):
    pts,edges=model(kind);ang=.52+.17*math.sin(2*math.pi*t/loop);tilt=.34+.045*math.cos(2*math.pi*t/loop)
    a=np.array([[math.cos(ang),0,math.sin(ang)],[0,1,0],[-math.sin(ang),0,math.cos(ang)]])
    b=np.array([[1,0,0],[0,math.cos(tilt),-math.sin(tilt)],[0,math.sin(tilt),math.cos(tilt)]])
    p=pts@a.T@b.T;pers=1/(1-p[:,2]*.045)
    x=cx+p[:,0]*scale*pers;y=cy+p[:,1]*scale*pers
    sh=floor_shadow(round(scale*7),100);im.paste(sh,(round(cx-sh.width/2),round(cy+scale*2.65)),sh)
    d=ImageDraw.Draw(im)
    for i,j in sorted(edges,key=lambda e:(p[e[0],2]+p[e[1],2])):
        depth=(p[i,2]+p[j,2])/2;v=int(np.clip(193-depth*9,167,214));color=(v,min(230,v+13),min(245,v+30))
        xy=(round(x[i]),round(y[i]),round(x[j]),round(y[j]));d.line(xy,fill=color,width=max(2,round(scale*.043)))
        d.line((xy[0]-1,xy[1]-1,xy[2]-1,xy[3]-1),fill='#eef3fc',width=max(1,round(scale*.012)))
    for i in np.argsort(p[:,2]):
        r=max(6,round(scale*.155*pers[i]));sp=sphere(r,0 if kind=='fcc' or i%4==0 else 1)
        im.paste(sp,(round(x[i]-r),round(y[i]-r)),sp)
def pill(im,x,y,s):
    w=round(font(25).getlength(s))+38
    ImageDraw.Draw(im).rounded_rectangle((x,y,x+w,y+47),23,fill='#eaf0fd');txt(im,(x+19,y+7),s,25,BLUE)
def crystal(t,dur):
    im=background();chrome(im,'从原子结构，走向材料发现','在微观尺度，连接结构与材料计算','STRUCTURE')
    txt(im,(105,458),'看见微观',62,INK,True);txt(im,(108,553),'理解材料',62,BLUE,True)
    txt(im,(111,679),'让结构成为探索的起点',30,MUTED)
    pill(im,110,772,'原子结构');pill(im,274,772,'计算建模')
    atoms(im,t,1375,625,105,'fcc',dur)
    footer(im,'晶体结构概念示意');return im
def space(t,dur):
    im=background();chrome(im,'探索不同结构的可能','从组成与排列出发，打开材料研究空间','MATERIALS')
    for i,(kind,title,sub) in enumerate([('fcc','三维晶体','规则排列 · 周期结构'),('layer','层状结构','层间连接 · 空间构型'),('cube','结构组合','组成变化 · 结构探索')]):
        x=96+i*588;panel(im,(x,358,x+552,939))
        atoms(im,t+i*.3,x+276,590,65 if i!=1 else 59,kind,dur)
        txt(im,(x+276,810),title,39,INK,True,'mm');txt(im,(x+276,875),sub,25,MUTED,anchor='mm')
    footer(im,'结构概念示意');return im
def icon(im,kind,cx,cy,col=BLUE):
    d=ImageDraw.Draw(im);w=4
    d.rounded_rectangle((cx-42,cy-42,cx+42,cy+42),22,fill='#edf1ff')
    if kind==0:
        for x,y in [(cx-18,cy+12),(cx+18,cy+12),(cx,cy-19)]:
            for xx,yy in [(cx-18,cy+12),(cx+18,cy+12),(cx,cy-19)]:d.line((x,y,xx,yy),fill='#a5b4eb',width=3)
        for x,y in [(cx-18,cy+12),(cx+18,cy+12),(cx,cy-19)]:d.ellipse((x-7,y-7,x+7,y+7),fill=col)
    elif kind==1:
        for j in range(3):
            yy=cy-20+j*20;d.line((cx-24,yy,cx+24,yy),fill=col,width=w);xx=cx+[-8,13,-2][j];d.ellipse((xx-5,yy-5,xx+5,yy+5),fill='white',outline=col,width=2)
    elif kind==2:
        for j,h in enumerate([18,32,45]):d.rounded_rectangle((cx-25+j*19,cy+23-h,cx-14+j*19,cy+23),3,fill=col)
    else:
        d.arc((cx-24,cy-24,cx+24,cy+24),25,300,fill=col,width=w);d.polygon([(cx+12,cy-25),(cx+25,cy-23),(cx+22,cy-10)],fill=col)
def flow(t,dur,title,sub,labels,conclusion):
    im=background();chrome(im,title,sub,'WORKFLOW')
    d=ImageDraw.Draw(im);active=min(3,int(t/(dur/4)))
    for i,(a,b) in enumerate(labels):
        x=96+443*i;panel(im,(x,401,x+398,777),edge='#9caee9' if i==active else LINE)
        icon(im,i,x+69,474);txt(im,(x+342,462),f'0{i+1}',28,'#a5b2cc',True,anchor='ra')
        txt(im,(x+37,566),a,41,INK,True);txt(im,(x+39,641),b,27,MUTED)
        if i<3:
            xx=x+409;d.line((xx,590,xx+23,590),fill='#a7b7e8',width=3);d.line((xx+16,583,xx+23,590,xx+16,597),fill='#a7b7e8',width=3)
    txt(im,(960,884),conclusion,35,BLUE,True,'mm');footer(im,'研究流程概念示意');return im
def research(t,dur):return flow(t,dur,'研究在探索中不断前进','从材料制备到性能测试，让每一步观察支持下一步研究',[('材料制备','组成与工艺'),('实验表征','结构与特征'),('性能测试','目标与指标'),('方案迭代','继续研究')],'观察差异  ·  复核条件  ·  迭代研究')
def ai(t,dur):return flow(t,dur,'从一句话，到研究下一步','让 AI 辅助连接计算与分析环节',[('理解需求','研究目标与条件'),('规划流程','方法与计算模板'),('组织任务','确认后进入计算'),('分析结果','归纳与验证建议')],'AI 智能辅助  ·  专业计算  ·  科学判断')
def design(t,dur):return flow(t,dur,'让计算，为设计提供依据','从候选结构到结果比较，支持进一步优化',[('候选结构','明确组成与结构'),('计算验证','采用可比较条件'),('结果比较','分析差异与依据'),('进一步优化','提出下一轮方案')],'把计算结果，转化为研究依据')
def brand(t,dur):
    im=background();atoms(im,t,1450,570,106,'fcc',dur)
    txt(im,(110,150),'MATERIALS  ×  AI',24,BLUE,True)
    txt(im,(105,340),'ABACUSLab',104,BLUE,True)
    txt(im,(114,504),'AI 驱动的材料计算',43,INK,True);txt(im,(114,573),'与设计平台',43,INK,True)
    txt(im,(116,730),'让材料计算更简单',40,INK,True)
    txt(im,(118,815),'把更多精力，留给研究与发现',28,MUTED)
    return im
@lru_cache(None)
def msd():
    return ImageOps.contain(Image.open(SRC/'P02_MSD原图裁切.png').convert('RGB'),(1194,566),Image.Resampling.LANCZOS)
def aluminum(t,dur):
    im=background();chrome(im,'铝合金的熔化行为研究','比较不同温度下的原子运动，连接计算、图表与分析','研究场景')
    panel(im,(578,352,1824,958));chart=msd();im.paste(chart,(round(1201-chart.width/2),round(655-chart.height/2)))
    txt(im,(104,375),'不同温度下的',34,INK,True);txt(im,(104,428),'原子运动',42,BLUE,True)
    for y,title,desc,col in [(558,'300 K','MSD 曲线对照','#8760a0'),(729,'1600 K','MSD 曲线对照','#6c9d56')]:
        panel(im,(99,y,532,y+129),edge='#d9e4f1',r=20)
        ImageDraw.Draw(im).rounded_rectangle((101,y+20,106,y+108),2,fill=col)
        txt(im,(125,y+20),title,35,col,True);txt(im,(128,y+78),desc,25,MUTED)
    footer(im,'平台图表功能示例');return im
SPECS=[('M00_浅色立体原子片头_6秒',6,brand),('M01_微观晶体结构_浅色_12秒',12,crystal),('M02_材料探索空间_浅色_10秒',10,space),('M03_研发迭代流程_浅色_10秒',10,research),('M04_AI与计算流程_浅色_12秒',12,ai),('M05_计算支撑设计_浅色_12秒',12,design),('M06_品牌循环背景_浅色_10秒',10,brand),('M07_铝合金研究场景_MSD原图_10秒',10,aluminum)]
def previews():
    contact=Image.new('RGB',(1600,1040),PAPER)
    for i,(name,dur,fn) in enumerate(SPECS):
        im=fn(dur*.45,dur);im.save(PREV/f'{name}.jpg',quality=95)
        thumb=im.resize((768,432),Image.Resampling.LANCZOS);thumb=thumb.resize((384,216),Image.Resampling.LANCZOS)
        # Two rows of four preserve the full 16:9 composition.
        x=16+(i%4)*396;y=16+(i//4)*260
        contact.paste(thumb,(x,y));txt(contact,(x+4,y+220),name[:3]+'  '+name.split('_')[1],19,INK)
    contact=contact.crop((0,0,1600,540));contact.save(PREV/'浅色新版_全部画面.jpg',quality=95)
    print('PREVIEWS_READY',flush=True)
def render():
    manifest=[]
    for name,dur,fn in SPECS:
        dest=VIDEO/f'{name}.mp4';start=time.time()
        cmd=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for i in range(dur*FPS):p.stdin.write(fn(i/FPS,dur).tobytes())
        p.stdin.close()
        if p.wait():raise RuntimeError(name)
        manifest.append({'name':name,'duration':dur,'file':str(dest.relative_to(ROOT)),'format':'1920x1080, 30 fps, H.264, silent','source':'现有 MSD 原图＋编辑排版' if fn==aluminum else '原创程序概念动画','sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
        (PREV/'动画清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'RENDERED {name} {time.time()-start:.1f}s',flush=True)
def run(args):subprocess.run([FF,'-hide_banner','-loglevel','error',*args],check=True)
def assemble():
    dest=ROOT/'02_案例与成片'
    intro=VIDEO/(SPECS[0][0]+'.mp4')
    # The reference still has dark intro remnants at 6.0—6.8 s. Replace the whole transition.
    raw=subprocess.run([FF,'-v','error','-ss','8','-i',str(REFERENCE),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],check=True,stdout=subprocess.PIPE).stdout
    target=Image.open(io.BytesIO(raw)).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    bridge=ROOT/'制作文件/浅色转场_2秒.mp4'
    proc=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(bridge)],stdin=subprocess.PIPE)
    for n in range(60):
        t=n/30;im=Image.blend(brand(t,6),target,ease((t-.2)/1.5));proc.stdin.write(im.tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError('bridge encoding failed')
    graph='[0:v]trim=0:6,setpts=PTS-STARTPTS,fps=30,format=yuv420p,setsar=1[a];[2:v]setpts=PTS-STARTPTS,fps=30,setsar=1[c];[1:v]trim=start=8:end=60,setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,fps=30,setsar=1[b];[a][c][b]concat=n=3:v=1:a=0[out]'
    run(['-y','-i',str(intro),'-i',str(REFERENCE),'-i',str(bridge),'-filter_complex',graph,'-map','[out]','-map','1:a:0','-t','60','-r','30','-fps_mode','cfr','-c:v','libx264','-preset','fast','-crf','18','-c:a','copy','-movflags','+faststart',str(dest/'ABACUSLab_60秒_浅色原子片头_参考片修订.mp4')])
    print('ASSEMBLED_REFERENCE',flush=True)
    run(['-y','-ss','16','-i',str(REFERENCE),'-t','36','-vf','scale=1920:1080:flags=lanczos','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest/'C01_铝合金案例_沿用参考片_36秒_无声.mp4')])
    # A short visual review reel includes all new cards and the actual platform handoff.
    seq=[(name,3) for name,_,_ in SPECS[1:]]
    inputs=[];parts=[]
    for i,(name,d) in enumerate(seq):
        inputs+=['-i',str(VIDEO/(name+'.mp4'))];parts.append(f'[{i}:v]trim=0:{d},setpts=PTS-STARTPTS,setsar=1[v{i}]')
    inputs+=['-ss','8','-i',str(REFERENCE)]
    parts.append('[7:v]trim=0:5,setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,setsar=1[v7]')
    parts.append(''.join(f'[v{i}]' for i in range(8))+'concat=n=8:v=1:a=0[out]')
    run(['-y',*inputs,'-filter_complex',';'.join(parts),'-map','[out]','-an','-r','30','-fps_mode','cfr','-t','26','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'浅色素材_26秒连贯预览.mp4')])
    # Correct the older spatial crop's navy letterboxing to the same light canvas.
    run(['-y','-i',str(SRC/'R01_原始平台录屏.mp4'),'-vf','crop=3800:1860:0:130,scale=1920:940,pad=1920:1080:0:70:color=0xf5f7fe,setsar=1','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest/'R01_真实对话到MSD_浅色边框_1080p.mp4')])
    print('ASSEMBLY_DONE',flush=True)
def verify():
    results=[]
    for path in sorted(ROOT.rglob('*.mp4')):
        r=subprocess.run([FF,'-v','error','-i',str(path),'-f','null','-'],capture_output=True,text=True)
        meta=subprocess.run([FF,'-hide_banner','-i',str(path)],capture_output=True,text=True).stderr
        dur=re.search(r'Duration: ([0-9:.]+)',meta)
        results.append({'file':str(path.relative_to(ROOT)),'decode_ok':r.returncode==0 and not r.stderr.strip(),'duration':dur.group(1) if dur else None,'video':next((l.strip() for l in meta.splitlines() if 'Video:' in l),''),'audio':next((l.strip() for l in meta.splitlines() if 'Audio:' in l),''),'errors':r.stderr})
    (PREV/'视频核验.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False,indent=2))
    assert all(r['decode_ok'] for r in results)
if __name__=='__main__':
    {'previews':previews,'render':render,'assemble':assemble,'verify':verify}[sys.argv[1] if len(sys.argv)>1 else 'previews']()
