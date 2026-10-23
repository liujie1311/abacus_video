"""210 s promotional cut. Real screenshot pixels + editorial motion graphics.
Independent examples are not presented as one continuous recorded calculation.
"""
from pathlib import Path
from functools import lru_cache
import sys, math, json, asyncio, subprocess, wave, time, shutil, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
PLAN=BASE/'宣传片方案_210秒_20261019'
ROOT=BASE/'交付_V12_210秒_平台全景_AI重点_男声'
WORK=ROOT/'制作文件'; VOICE=WORK/'voice'; STILL=ROOT/'分镜预览'; AUDIO=ROOT/'音频'
for p in [ROOT,WORK,VOICE,STILL,AUDIO]: p.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'ABACUSLab_3分30秒_男声_动画宣传片.mp4'
W,H,FPS,DUR=1920,1080,30,210
BLUE='#5368eb'; CYAN='#77e4ef'; INK='#14223f'; MUTED='#687996'

def run(args,**kw):return subprocess.run([FF,'-hide_banner','-loglevel','error',*args],check=True,**kw)
def clamp(x):return max(0,min(1,x))
def ease(x):x=clamp(x);return x*x*x*(x*(x*6-15)+10)
@lru_cache(None)
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if b else 'C:/Windows/Fonts/msyh.ttc',n)
def text(im,xy,s,n=32,c=INK,b=False,anchor=None):ImageDraw.Draw(im).text(xy,s,font=font(n,b),fill=c,anchor=anchor)
def rect(im,box,fill,outline=None,r=24,width=1):ImageDraw.Draw(im).rounded_rectangle(tuple(round(v) for v in box),r,fill,outline,width)
@lru_cache(256)
def sprite(s,n,c,b):
    box=font(n,b).getbbox(s);im=Image.new('RGBA',(box[2]+8,box[3]+8));text(im,(0,0),s,n,c,b);return im
def enter(im,xy,s,t,delay=0,n=44,c=INK,b=True):
    a=ease((t-delay)/1.2)
    if a<=0:return
    sp=sprite(s,n,c,b)
    if a<1:sp=sp.copy();sp.putalpha(sp.getchannel('A').point(lambda z:int(z*a)))
    im.paste(sp,(round(xy[0]),round(xy[1]+26*(1-a))),sp)

N=PLAN/'06_补充素材与AI复核/原图'
C=PLAN/'05_用户新截图筛选/主选裁切'
O=PLAN/'05_用户新截图筛选/原图留档_不代表选用'
FILES={
 'home':N/'N01_平台首页.png','pyatb':N/'N02_PYATB生成结果.png','pdosfull':N/'N03_PDOS绘图结果.png',
 'questionfull':N/'A01_AI提问.png','completefull':N/'A02_AI完成与绘图链接.png',
 'msdfull':N/'A03_MSD原始曲线.png','analysisfull':N/'A04_AI分析与建议.png',
 'templates':C/'01_模板库主画面.png','task':C/'04_项目任务卡片.png',
 'config':C/'07_INPUT配置弹窗.png','workflow':C/'10_工作流总览.png','optical':C/'12_光学结果图.png',
 'logsfull':O/'11_任务日志.png'}
IMG={k:Image.open(p).convert('RGB') for k,p in FILES.items()}
def crop(k,box):
    im=IMG[k];return im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box)))
IMG['homecontent']=crop('home',(.105,.045,.99,.94))
IMG['pyatbcontent']=crop('pyatb',(.105,.065,.99,.76))
IMG['pdos']=crop('pdosfull',(.414,.505,.677,.887))
IMG['question']=crop('questionfull',(.207,.82,.745,.975))
IMG['complete']=crop('completefull',(.045,.055,.96,.79))
IMG['msd']=crop('msdfull',(.06,.19,.98,.98))
IMG['analysis']=crop('analysisfull',(.105,.06,.80,.86))
IMG['suggest']=crop('analysisfull',(.105,.64,.80,.86))
IMG['steps']=crop('workflow',(.79,.085,.994,.68))
IMG['logs']=crop('logsfull',(.32,.27,.98,.90))
for i in range(3):IMG[f'card{i}']=crop('templates',(.092+i*.129,.15,.215+i*.129,.455))
# Source logo, untouched. White background retained as a pill in both themes.
IMG['logo']=crop('home',(.009,.006,.094,.047))

yy,xx=np.mgrid[0:H,0:W];glow=np.exp(-((xx-1450)**2/780**2+(yy-300)**2/630**2))
LIGHT=Image.fromarray(np.stack([244-11*glow,247-10*glow,254-2*glow],-1).astype('uint8'))
DARK=Image.fromarray(np.stack([8+13*glow,15+23*glow,35+41*glow],-1).astype('uint8'))
del xx,yy,glow
rng=np.random.default_rng(29);STARS=rng.uniform(0,1,(80,4))
def background(t,dark=False):
    im=(DARK if dark else LIGHT).copy();d=ImageDraw.Draw(im)
    for j,(x,y,z,v) in enumerate(STARS):
        px=(x*W+t*(3+z*9))%W;py=(y*H-t*(1+z*2))%H;r=1+z*1.6
        col=tuple(int(c*(.5+.4*math.sin(t*.6+j)**2)) for c in (119,166,213)) if dark else '#cbd5ee'
        d.ellipse((px-r,py-r,px+r,py+r),fill=col)
    if dark:
        for j in range(3):
            pts=[(x,650+j*85+50*math.sin(x/420+t*.14+j)) for x in range(-20,1940,20)]
            d.line(pts,fill=['#1c4663','#263b65','#294f6c'][j],width=2)
    return im
@lru_cache(120)
def prepared(key,w,h):
    src=IMG[key];s=min(w/src.width,h/src.height)
    return src.resize((round(src.width*s),round(src.height*s)),Image.Resampling.LANCZOS)
def panel(im,key,box,t=4,delay=0,zoom=0):
    x,y,w,h=box;a=ease((t-delay)/1.0);y+=round(34*(1-a))
    rect(im,(x+6,y+15,x+w+6,y+h+15),'#dce3f0',r=26)
    rect(im,(x,y,x+w,y+h),'white','#dae3f3',26)
    obj=prepared(key,w-32,h-32)
    if zoom:
        scale=1+zoom;obj=obj.resize((round(obj.width*scale),round(obj.height*scale)),Image.Resampling.BICUBIC)
    # Respect the panel bounds even during a camera move.
    if obj.width>w-28 or obj.height>h-28:
        obj=obj.crop((max(0,(obj.width-w+28)//2),max(0,(obj.height-h+28)//2),min(obj.width,(obj.width+w-28)//2),min(obj.height,(obj.height+h-28)//2)))
    im.paste(obj,(round(x+(w-obj.width)/2),round(y+(h-obj.height)/2)))
def chrome(im,title,k,t,dark=False):
    text(im,(86,43),'ABACUSLab',27,'#d9e7ff' if dark else BLUE,True)
    text(im,(1830,56),k,22,'#97b6d8' if dark else MUTED,anchor='ra')
    ImageDraw.Draw(im).line((88,106,1830,106),fill='#294261' if dark else '#d6dff0',width=1)
    enter(im,(85,151),title,t,.05,55,'#f4f8ff' if dark else INK)
def label(im,s,x,y,t,delay=0,dark=False):
    enter(im,(x,y),s,t,delay,29,CYAN if dark else BLUE)

LATTICE=[(x,y,z) for x in [-1,0,1] for y in [-1,0,1] for z in [-1,0,1]]
EDGES=[(i,j) for i,a in enumerate(LATTICE) for j,b in enumerate(LATTICE) if j>i and sum(abs(a[k]-b[k]) for k in range(3))==1]
def lattice(im,t,cx=1435,cy=510,scale=140):
    d=ImageDraw.Draw(im);pts=[];a=t*.16+.5
    for x,y,z in LATTICE:
        rx=x*math.cos(a)+z*math.sin(a);rz=-x*math.sin(a)+z*math.cos(a)
        pts.append((cx+rx*scale,cy+(y*.86-rz*.38)*scale,rz))
    for i,j in EDGES:
        x,y,_=pts[i];u,v,_=pts[j];d.line((x,y,u,v),fill='#3e6989',width=2)
    for i,(x,y,z) in sorted(enumerate(pts),key=lambda q:q[1][2]):
        r=7+(z+1.5)*2;d.ellipse((x-r-6,y-r-6,x+r+6,y+r+6),fill='#1d3f62')
        d.ellipse((x-r,y-r,x+r,y+r),fill=CYAN if i%4==0 else '#8097ff')
        d.ellipse((x-r*.4,y-r*.55,x,y-r*.2),fill='#f2ffff')
    for j in range(3):
        ang=t*.3+j*2.09;px=cx+340*math.cos(ang);py=cy+200*math.sin(ang)
        d.ellipse((px-5,py-5,px+5,py+5),fill=CYAN)

def intro(t,ending=False):
    im=background(t,True);d=ImageDraw.Draw(im)
    if ending:
        for j in range(3):
            r=210+j*95+math.sin(t*.2)*12
            d.ellipse((960-r*1.8,520-r,960+r*1.8,520+r),outline='#274469',width=1)
        for s,y,n,col,delay in [('ABACUSLab',300,108,'#eff6ff',.1),('让材料计算更简单',477,70,CYAN,.4),('把更多精力，留给研究与发现',620,33,'#abc1de',.8)]:
            enter(im,((W-font(n,True).getlength(s))/2,y),s,t,delay,n,col)
        logo=prepared('logo',280,70);im.paste(logo,((W-logo.width)//2,185))
    else:
        lattice(im,t);enter(im,(112,265),'MATERIALS  /  COMPUTATION  /  AI',t,.2,23,CYAN)
        enter(im,(103,345),'ABACUSLab',t,.7,102,'#f1f7ff')
        enter(im,(110,500),'连接材料计算与分析',t,1.2,54,'#d7e7ff')
        a=ease((t-1.8)/2);d.line((114,613,114+580*a,613),fill=CYAN,width=3)
        enter(im,(114,661),'从微观结构，走向材料发现',t,2.2,30,'#8daed1',False)
    return im

def flow(t,title,labels,dark=False):
    im=background(t,dark);chrome(im,title,'AI AGENT' if dark else 'CONNECTED WORKSPACE',t,dark)
    n=len(labels);width=510 if n==3 else 390;gap=65;total=n*width+(n-1)*gap;x0=(W-total)//2;y=427
    d=ImageDraw.Draw(im)
    for i,s in enumerate(labels):
        x=x0+i*(width+gap);a=ease((t-.2-i*.28)/1.1);dy=round(40*(1-a))
        rect(im,(x,y+dy,x+width,y+dy+280),'#122440' if dark else 'white','#355780' if dark else '#dce4f3',26,2)
        enter(im,(x+35,y+dy+27),f'0{i+1}',t,.2+i*.28,29,CYAN if dark else BLUE)
        enter(im,(x+35,y+dy+115),s,t,.35+i*.28,43,'#f0f7ff' if dark else INK)
        if i<n-1:
            p=ease((t-1-i*.55)/1.0);xx=x+width+8;end=xx+(gap-16)*p
            d.line((xx,y+140,end,y+140),fill=CYAN if dark else BLUE,width=3)
            if p>.9:d.polygon([(end,y+140),(end-8,y+134),(end-8,y+146)],fill=CYAN if dark else BLUE)
    for i in range(n-1):
        a=(t*.22-i*.27)%1;x=x0+width+i*(width+gap)+gap*a
        d.ellipse((x-4,y+136,x+4,y+144),fill=CYAN if dark else BLUE)
    return im

def scene(kind,t,span):
    if kind=='intro':return intro(t)
    if kind=='outro':return intro(min(t,7),True)
    if kind=='reuse':return flow(t,'把计算方法，变成可复用的流程',['选择模板','调整方案','复用流程'])
    if kind=='taskflow':return flow(t,'让每一次计算，有序积累',['研究项目','计算任务','执行记录'])
    if kind=='plan':return flow(t,'从研究目标，走向计算方案',['理解需求','梳理步骤','确认条件'],True)
    if kind=='aiflow':return flow(t,'连接计算与结果展示',['组织任务','查看进展','衔接绘图'],True)
    if kind=='summary':return flow(t,'让智能协助，贯穿研究过程',['提出目标','组织计算','绘图展示','分析结果'],True)
    if kind=='aihero':
        im=background(t,True);chrome(im,'研究，也可以从一句话开始','AI AGENT',t,True)
        d=ImageDraw.Draw(im)
        for j in range(4):
            r=165+j*35+8*math.sin(t*.6+j)
            d.ellipse((1390-r,570-r*.75,1390+r,570+r*.75),outline=['#2c5677','#35528b','#497d9b','#244361'][j],width=2)
            a=t*.45+j*1.57;x=1390+r*math.cos(a);y=570+r*.75*math.sin(a);d.ellipse((x-5,y-5,x+5,y+5),fill=CYAN)
        enter(im,(1230,443),'AI',t,.1,190,'#b9f1ff')
        enter(im,(105,398),'说出目标',t,.25,84,'#eff7ff')
        enter(im,(110,536),'让智能体协助下一步',t,.65,46,CYAN)
        return im
    im=background(t);title,tag={
      'home':('一个平台，连接研究全程','PLATFORM'),
      'templates':('丰富模板，让计算有据可循','TEMPLATES'),
      'cards':('常用方法，随需调用','TEMPLATES'),
      'project':('围绕研究目标，组织计算任务','PROJECTS'),
      'task':('方案可调整，任务可复用','TASKS'),
      'workflow':('运行进展，清晰可追踪','WORKFLOWS'),
      'steps':('从整体进度，到关键环节','WORKFLOWS'),
      'logs':('计算过程，有迹可循','WORKFLOWS'),
      'config':('参数配置，更直观','TOOLS'),
      'pyatb':('工具协同，衔接计算环节','TOOLS'),
      'pdos':('从态密度，看见材料特征','VISUALIZATION'),
      'optical':('从光学响应，理解数据变化','VISUALIZATION'),
      'question':('用自然语言，描述研究需求','AI AGENT'),
      'complete':('从组织计算，到结果就绪','AI AGENT'),
      'msd':('让计算结果，以图表呈现','AI AGENT'),
      'analysis':('分析图表，归纳主要发现','AI AGENT'),
      'suggest':('提示适用范围，提出下一步建议','AI AGENT'),
      'portfolio':('从计算准备，到研究发现','ABACUSLab')
    }[kind];chrome(im,title,tag,t)
    if kind in ['home','templates','workflow','pyatb','logs']:
        key={'home':'homecontent','pyatb':'pyatbcontent'}.get(kind,kind)
        panel(im,key,(105,276,1710,705),t,zoom=.012*ease(t/span))
    elif kind=='cards':
        for i,s in enumerate(['自洽计算','非自洽计算','原子位置优化']):
            panel(im,f'card{i}',(128+i*578,315,510,560),t,i*.25)
            label(im,s,184+i*578,922,t,.4+i*.25)
    elif kind in ['project','task']:
        panel(im,'task',(660,305,1110,650),t)
        enter(im,(108,400),'项目有序',t,.25,64)
        enter(im,(110,515),'任务可管理' if kind=='project' else '计算可复用',t,.6,47,BLUE)
        label(im,'组织 · 调整 · 积累',112,675,t,1)
    elif kind=='steps':
        panel(im,'workflow',(100,338,1080,550),t)
        panel(im,'steps',(1260,285,550,680),t,.25)
    elif kind=='config':
        panel(im,'config',(858,267,870,720),t)
        enter(im,(110,402),'准备更顺畅',t,.3,63)
        label(im,'可视化配置 · 输入文件准备',114,552,t,.7)
    elif kind in ['pdos','optical','msd']:
        panel(im,kind,(655,270,1150,720),t)
        lines={'pdos':['物性可视','观察轨道贡献'],'optical':['数据可读','理解响应变化'],'msd':['图表呈现','比较不同条件']}[kind]
        enter(im,(106,412),lines[0],t,.2,68)
        label(im,lines[1],111,564,t,.6)
    elif kind=='question':
        enter(im,(113,351),'描述目标',t,.15,76)
        label(im,'自然语言交互',117,472,t,.5)
        panel(im,'question',(570,551,1220,310),t,.25)
        enter(im,(580,380),'ABACUSLab 智能体',t,.65,43,BLUE)
    elif kind=='complete':
        panel(im,'complete',(758,278,1020,700),t)
        enter(im,(110,415),'计算与绘图',t,.25,61)
        label(im,'任务反馈 · 绘图入口',114,555,t,.6)
    elif kind=='analysis':
        panel(im,'analysis',(864,263,880,725),t)
        for i,s in enumerate(['归纳主要发现','解释数据变化','保留结论边界']):label(im,s,116,390+i*140,t,.3+i*.35)
    elif kind=='suggest':
        panel(im,'suggest',(151,480,1620,400),t)
        for i,s in enumerate(['理解结果','明确局限','继续验证']):label(im,s,200+i*570,334,t,.2+i*.3)
    elif kind=='portfolio':
        for i,(key,s) in enumerate([('templates','模板'),('task','任务'),('pdos','分析'),('analysis','AI')]):
            x=105+(i%2)*865;y=272+(i//2)*355
            panel(im,key,(x,y,810,310),t,i*.18)
            rect(im,(x+15,y+15,x+104,y+60),'#eef2ff',r=10);text(im,(x+30,y+20),s,23,BLUE,True)
    return im

SHOTS=[(0,8,'intro'),(8,15,'home'),(15,23,'templates'),(23,32,'cards'),(32,40,'reuse'),
 (40,49,'project'),(49,55,'task'),(55,60,'taskflow'),(60,68,'workflow'),(68,76,'steps'),(76,80,'logs'),
 (80,90,'config'),(90,100,'pyatb'),(100,110,'pdos'),(110,120,'optical'),
 (120,127,'aihero'),(127,135,'question'),(135,145,'plan'),(145,153,'complete'),(153,160,'aiflow'),
 (160,170,'msd'),(170,179,'analysis'),(179,187,'suggest'),(187,195,'summary'),(195,201,'portfolio'),(201,210,'outro')]
@lru_cache(32)
def lastframe(i):
    a,b,k=SHOTS[i];return scene(k,b-a,b-a)
def frame(t):
    idx=next((i for i,(a,b,k) in enumerate(SHOTS) if a<=t<b),len(SHOTS)-1)
    a,b,k=SHOTS[idx];local=t-a;im=scene(k,local,b-a)
    if idx and local<.85:
        # Eased horizontal drift and dissolve, with a continuous cyan guide line.
        p=ease(local/.85);old=lastframe(idx-1)
        old=old.transform((W,H),Image.Transform.AFFINE,(1,0,24*p,0,1,0),Image.Resampling.BILINEAR)
        im=Image.blend(old,im,p)
    d=ImageDraw.Draw(im)
    if 8<t<201:
        d.line((90,1027,1830,1027),fill='#9aaed0',width=1)
        d.line((90,1027,90+1740*t/DUR,1027),fill='#72a7e9',width=3)
        x=90+1740*t/DUR;d.ellipse((x-4,1023,x+4,1031),fill=CYAN)
    if t<1:im=Image.blend(Image.new('RGB',(W,H),'#080f23'),im,ease(t))
    if t>209:im=Image.blend(im,Image.new('RGB',(W,H),'#080f23'),ease(t-209))
    return im

def entries():
    rows=[]
    for line in (PLAN/'01_台词时间轴.md').read_text(encoding='utf-8').splitlines():
        if re.match(r'\| \d\d:',line):
            cols=[s.strip() for s in line.split('|')[1:-1]];a,b=cols[0].split('—')
            sec=lambda x:int(x[:2])*60+int(x[3:])
            rows.append((sec(a),sec(b),cols[-1]))
    assert len(rows)==10 and rows[-1][1]==DUR
    return rows
ENTRIES=entries()
async def voices():
    import edge_tts
    for i,(a,b,s) in enumerate(ENTRIES):
        dest=VOICE/f'{i:02d}.mp3'
        if dest.exists() and dest.stat().st_size>3000:continue
        for attempt in range(3):
            try:
                await asyncio.wait_for(edge_tts.Communicate(s.replace('ABACUSLab','ABACUS LAB'),'zh-CN-YunjianNeural',rate='-8%',pitch='-2Hz').save(str(dest)),timeout=55)
                break
            except Exception:
                if attempt==2:raise
        print(f'Male narration {i+1}/10',flush=True)

def wav(path,data,sr=48000):
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1 if data.ndim==1 else data.shape[1]);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((np.clip(data,-.98,.98)*32767).astype('<i2').tobytes())
def mix():
    sr=48000;n=DUR*sr;voice=np.zeros(n,np.float32);duck=np.ones(n,np.float32);report=[];subs=[]
    for i,(a,b,s) in enumerate(ENTRIES):
        pcm=subprocess.check_output([FF,'-v','error','-i',str(VOICE/f'{i:02d}.mp3'),'-ac','1','-ar',str(sr),'-f','f32le','pipe:1'])
        data=np.frombuffer(pcm,np.float32).copy();active=np.flatnonzero(abs(data)>.004)
        data=data[max(0,active[0]-2400):min(len(data),active[-1]+7200)]
        start=a+(1.6 if i==0 else .65);available=b-start-.7
        # Relax the delivery while preserving pitch; leave room for transitions.
        speed=max(.86,len(data)/sr/available)
        if speed>1.18:raise ValueError(f'Voice section {i} too long: {speed}')
        if abs(speed-1)>.001:
            data=np.frombuffer(subprocess.check_output([FF,'-v','error','-f','f32le','-ar',str(sr),'-ac','1','-i','pipe:0','-af',f'atempo={speed:.6f}','-f','f32le','pipe:1'],input=data.tobytes()),np.float32).copy()
        data*=min(.15/max(float(np.sqrt(np.mean(data**2))),.001),.82/max(float(abs(data).max()),.001))
        pos=round(start*sr);voice[pos:pos+len(data)]+=data;end=start+len(data)/sr
        ds=max(0,pos-12000);de=min(n,pos+len(data)+18000);duck[ds:de]=.43
        duck[ds:pos]=np.linspace(1,.43,pos-ds);duck[pos+len(data):de]=np.linspace(.43,1,de-pos-len(data))
        report.append({'section':i,'male_voice':'zh-CN-YunjianNeural','start':start,'end':end,'speed_adjust':speed,'text':s})
        # Approximate phrase captions are optional external files, never burned into pictures.
        phrases=[x+'。' for x in s.split('。') if x.strip()];count=sum(map(len,phrases));cursor=start
        for phrase in phrases:
            length=len(data)/sr*len(phrase)/count;subs.append((cursor,cursor+length,phrase));cursor+=length
    music=np.zeros((n,2),np.float32);chords=[[50,57,62,65,69],[46,53,58,62,65],[53,60,65,69,72],[48,55,60,64,67]]
    musicrng=np.random.default_rng(81)
    for bar in range(math.ceil(DUR/6)):
        start=bar*6;st=start*sr;ln=min(int(7.5*sr),n-st);tt=np.arange(ln)/sr
        env=np.minimum(1,tt/1.5)*np.minimum(1,(7.5-tt)/1.8);chord=chords[bar%4]
        lift=1.15 if 120<=start<170 else .85 if start<15 or start>=195 else 1
        for j,note in enumerate(chord):
            f=440*2**((note-69)/12)
            for channel in range(2):
                pad=(np.sin(2*np.pi*f*(1+(channel*2-1)*.0009)*tt+j*.7)+.22*np.sin(2*np.pi*f*2*tt))
                music[st:st+ln,channel]+=pad*env*.012*lift
        # Low foundation, restrained plucked arpeggio, gentle heartbeat rhythm.
        bass=np.sin(2*np.pi*440*2**((chord[0]-12-69)/12)*tt)*env*.018*lift
        music[st:st+ln]+=bass[:,None]
        for k in range(8):
            pst=int((start+k*.75)*sr);pn=min(int(1.7*sr),n-pst)
            if pn<=0:continue
            pt=np.arange(pn)/sr;f=440*2**((chord[[0,2,3,4,2,3,1,4][k]]+12-69)/12)
            arp=(np.sin(2*np.pi*f*pt)+.18*np.sin(2*np.pi*f*2*pt))*(1-np.exp(-pt*90))*np.exp(-pt*3.5)*.026*lift
            music[pst:pst+pn,k%2]+=arp
            if 15<=start<195 and k%2==0:
                kick=np.sin(2*np.pi*(46*pt+18*(1-np.exp(-pt*18))/18))*np.exp(-pt*13)*.045*lift
                music[pst:pst+pn]+=kick[:,None]
    # Soft airy transitions at chapter boundaries, independent of any UI action.
    for mark in [8,15,40,60,80,100,120,145,170,195,201]:
        ln=round(1.6*sr);st=round((mark-.75)*sr);tt=np.arange(ln)/sr
        noise=musicrng.normal(0,1,ln);noise=np.convolve(noise,np.ones(45)/45,mode='same')
        whoosh=noise*np.sin(np.pi*tt/1.6)**2*.08
        music[st:st+ln,0]+=whoosh;music[st:st+ln,1]+=np.roll(whoosh,180)
    timeline=np.arange(n)/sr;fade=np.minimum(1,timeline/2.2)*np.minimum(1,(DUR-timeline)/3.2)
    music*=duck[:,None]*fade[:,None]
    wav(AUDIO/'男声旁白.wav',voice);wav(AUDIO/'原创配乐与转场.wav',music)
    wav(WORK/'mixed.wav',(voice[:,None]+music)*fade[:,None])
    (WORK/'配音时间核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
    (ROOT/'可选旁白字幕_句级估时.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(subs)),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

def previews():
    sheet=Image.new('RGB',(1440,math.ceil(len(SHOTS)/3)*298),'#e5ebf4')
    for i,(a,b,k) in enumerate(SHOTS):
        t=min(b-.5,a+3);im=frame(t);im.save(STILL/f'{i+1:02d}_{k}.jpg',quality=94)
        x=i%3*480;y=i//3*298;text(sheet,(x+10,y+5),f'{a:03d}–{b:03d}s   {k}',20)
        sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y+28))
    sheet.save(ROOT/'分镜总览.jpg',quality=95)
    (WORK/'镜头时间线.json').write_text(json.dumps(SHOTS,ensure_ascii=False,indent=2),encoding='utf-8')
    shutil.copy2(PLAN/'01_台词时间轴.md',ROOT/'台词时间轴.md')
    print('Preview ready',flush=True)

def picture():
    p=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','6','-movflags','+faststart',str(WORK/'picture.mp4')],stdin=subprocess.PIPE)
    start=time.time()
    try:
        for i in range(DUR*FPS):
            p.stdin.write(frame(i/FPS).tobytes())
            if i%300==0:print(f'Render {i/FPS:.0f}/{DUR} s; elapsed {time.time()-start:.1f} s',flush=True)
    finally:p.stdin.close()
    if p.wait():raise RuntimeError('Video encoding failed')
    print('Picture ready',flush=True)
def final():
    run(['-y','-i',str(WORK/'picture.mp4'),'-i',str(WORK/'mixed.wav'),'-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-17:TP=-3:LRA=9,aresample=48000,alimiter=limit=0.78:level=false:latency=true','-ar','48000','-c:a','aac','-b:a','192k','-t',str(DUR),'-movflags','+faststart',str(DEST)])
    print('FINAL',DEST,flush=True)
if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if mode=='voice':asyncio.run(voices())
    elif mode=='mix':mix()
    elif mode=='previews':previews()
    elif mode=='picture':picture()
    elif mode=='final':final()
