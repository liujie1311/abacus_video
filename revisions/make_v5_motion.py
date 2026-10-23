"""V5: unified light palette, layered motion, continuous transitions, no subtitles.

Scientific plots reveal original screenshot pixels; no invented curve data.
"""
from pathlib import Path
from functools import lru_cache
import sys, math, subprocess, time, json, asyncio, wave, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
ROOT=BASE/'交付_V5_60秒_AI演示优先'
OUT=ROOT/'04_视频成片'
WORK=OUT/'制作文件'
ASSETS=ROOT/'03_动态素材'
STILLS=ASSETS/'关键帧'
VOICE=WORK/'voice'
for p in [OUT,WORK,ASSETS,STILLS,VOICE]: p.mkdir(parents=True,exist_ok=True)
V3=BASE/'交付_V3_含模板_无字幕/03_图片素材'
V4=BASE/'交付_V4_115秒方案/03_图片素材'
W,H,FPS=1920,1080,30
BLUE='#5865ed'; INK='#15203b'; MUTED='#69758d'; TEAL='#46b9ae'

def run(args,**kw):
    return subprocess.run([FF,'-hide_banner','-loglevel','error',*args],check=True,**kw)

@lru_cache(None)
def ft(size,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc',size)

def txt(im,xy,s,size=32,color=INK,bold=False,anchor=None):
    ImageDraw.Draw(im).text(xy,s,font=ft(size,bold),fill=color,anchor=anchor)

def rr(im,rect,fill='white',radius=20,outline=None,width=1):
    ImageDraw.Draw(im).rounded_rectangle(tuple(round(v) for v in rect),radius,fill,outline,width)

def ease(t):
    t=max(0,min(1,t));return 1-(1-t)**3

def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

@lru_cache(150)
def text_sprite(s,size,color,bold):
    b=ft(size,bold).getbbox(s)
    im=Image.new('RGBA',(b[2]+8,b[3]+8))
    txt(im,(0,0),s,size,color,bold)
    return im

def enter(im,xy,s,t,delay=0,size=32,color=INK,bold=False):
    a=ease((t-delay)/.8)
    if a<=0:return
    sp=text_sprite(s,size,color,bold)
    if a<1:
        sp=sp.copy();sp.putalpha(sp.getchannel('A').point(lambda v:round(v*a)))
    im.paste(sp,(round(xy[0]),round(xy[1]+30*(1-a))),sp)

def fit(src,w,h):
    r=min(w/src.width,h/src.height)
    return src.resize((round(src.width*r),round(src.height*r)),Image.Resampling.LANCZOS)

def transparent(src):
    a=np.array(src.convert('RGBA'));a[np.min(a[:,:,:3],axis=2)>245,3]=0
    return Image.fromarray(a)

raw=Image.open(BASE.parent/'86a62f81-69e0-4354-a45c-8c812c4133d6.png').convert('RGB')
LOGO=transparent(raw.crop((35,12,348,106))).resize((235,71),Image.Resampling.LANCZOS)
ICON=transparent(raw.crop((35,12,126,106))).resize((104,108),Image.Resampling.LANCZOS)
yy,xx=np.mgrid[0:H,0:W]
g=np.exp(-((xx-W*.78)**2/(W*.55)**2+(yy-H*.26)**2/(H*.8)**2))
LIGHT=Image.fromarray(np.stack([247-8*g,249-10*g,254-g],axis=-1).astype('uint8'))
del xx,yy,g

def base(chapter,t):
    im=LIGHT.copy();d=ImageDraw.Draw(im)
    im.paste(LOGO,(70,30),LOGO)
    txt(im,(1810,62),'材料计算智能体',22,MUTED,anchor='ra')
    d.line((80,128,1840,128),fill='#dce2f0',width=1)
    for i in range(6):
        x=1560+i*44
        rr(im,(x,1032,x+28,1036),BLUE if i==chapter else '#d5dcec',2)
    return im

def heading(im,k,title,t,sub=None):
    enter(im,(90,165),k,t,0,20,BLUE,True)
    enter(im,(86,225),title,t,.12,54,INK,True)
    if sub: enter(im,(91,306),sub,t,.24,26,MUTED)

# Abstract structure is illustrative, not atom coordinates from the calculation.
LATTICE=[(x,y,z) for x in [-1,0,1] for y in [-1,0,1] for z in [-1,0,1]]
EDGES=[(i,j) for i,a in enumerate(LATTICE) for j,b in enumerate(LATTICE) if j>i and sum(abs(a[k]-b[k]) for k in range(3))==1]

def lattice(im,t,cx=1430,cy=520,scale=135):
    d=ImageDraw.Draw(im);angle=t*.17+.45;points=[]
    for x,y,z in LATTICE:
        rx=x*math.cos(angle)+z*math.sin(angle)
        rz=-x*math.sin(angle)+z*math.cos(angle)
        ry=y*.88-rz*.40
        points.append((cx+rx*scale,cy+ry*scale,rz))
    reveal=ease((t+.25)/2.2)
    for i,j in EDGES[:int(len(EDGES)*reveal)]:
        a,b=points[i],points[j];d.line((a[0],a[1],b[0],b[1]),fill='#b9c3f4',width=2)
    for i,(x,y,z) in sorted(enumerate(points),key=lambda q:q[1][2]):
        if i/len(points)>reveal:continue
        r=7+(z+1.5)*2
        d.ellipse((x-r-5,y-r-5,x+r+5,y+r+5),fill='#e7eafe')
        d.ellipse((x-r,y-r,x+r,y+r),fill=TEAL if i%5==0 else BLUE)
        d.ellipse((x-r*.3,y-r*.55,x+r*.15,y-r*.1),fill='white')
    for i in range(3):
        a=t*.35+i*2.094
        x=cx+305*math.cos(a);y=cy+220*math.sin(a)
        d.ellipse((x-4,y-4,x+4,y+4),fill='#9ba6f8')

def intro(t):
    im=base(0,t);d=ImageDraw.Draw(im)
    for x in range(1050,1830,60):
        for y in range(260,840,60):d.ellipse((x,y,x+2,y+2),fill='#d5dcf5')
    lattice(im,t)
    enter(im,(91,246),'MATERIALS × AI',t,0,24,BLUE,True)
    enter(im,(84,328),'ABACUSLab',t,.1,94,BLUE,True)
    enter(im,(87,467),'让材料计算更简单',t,.45,64,INK,True)
    p=ease((t-1)/1.1)
    d.line((94,591,94+570*p,591),fill='#c4ccf4',width=3)
    enter(im,(94,647),'从一句话开始',t,1.5,37,BLUE,True)
    enter(im,(94,717),'提出目标  ·  组织计算  ·  理解结果',t,2.1,25,MUTED)
    txt(im,(1430,847),'材料结构示意',20,MUTED,anchor='ma')
    return im

qfull=Image.open(V4/'01_主分镜_1080p/03_自然语言提问.png').convert('RGB')
QPANEL=qfull.crop((746,178,1829,935))
# Blank the enlarged editorial callout; animate it below rather than leaving a still.
ImageDraw.Draw(QPANEL).rectangle((0,438,1082,626),fill='white')
ImageDraw.Draw(QPANEL).rectangle((25,664,560,717),fill='white')
PROMPT='我想计算这种金属的熔点'

def question(t):
    im=base(1,t)
    enter(im,(90,165),'01  /  自然语言交互',t,0,20,BLUE,True)
    enter(im,(88,304),'从一句话',t,.1,68,INK,True)
    enter(im,(88,402),'开始',t,.22,78,BLUE,True)
    enter(im,(94,581),'用自然语言描述计算目标',t,.7,28,MUTED)
    enter(im,(94,637),'金属熔点 · AI 演示',t,1,26,BLUE)
    dx=round(50*(1-ease(t/.8)));im.paste(QPANEL,(746+dx,178))
    y=618+round(35*(1-ease((t-.25)/.8)))
    rr(im,(703,y,1813,y+185),'white',22,'#b9212b',3)
    n=min(len(PROMPT),max(0,int((t-2.2)*4.8)))
    txt(im,(740,y+36),PROMPT[:n],43,INK)
    if t<6 and int(t*3)%2==0:
        cx=740+ImageDraw.Draw(im).textlength(PROMPT[:n],font=ft(43))
        ImageDraw.Draw(im).line((cx+3,y+46,cx+3,y+91),fill='#bb252e',width=2)
    txt(im,(741,y+130),'附件    知识库',20,MUTED)
    rr(im,(1725,y+102,1781,y+158),'#bb252e',28)
    txt(im,(1753,y+100),'↑',36,'white',anchor='ma')
    if 5.5<t<6.5:
        a=smooth((t-5.5)/.6);cx=1835-85*a;cy=850-105*a
        d=ImageDraw.Draw(im)
        d.polygon([(cx,cy),(cx+4,cy+31),(cx+13,cy+23),(cx+22,cy+23)],fill='white',outline=INK,width=2)
        if t>6:
            r=18+(t-6)*55;d.ellipse((1753-r,748-r,1753+r,748+r),outline='#da9299',width=2)
    if t>6.25:
        enter(im,(790,850),'正在理解需求',t,6.25,24,BLUE)
        for i in range(3):
            y=866+round(4*math.sin(t*5-i));x=974+i*23
            ImageDraw.Draw(im).ellipse((x,y,x+8,y+8),fill=BLUE)
    return im

RECORD=None
def recording():
    global RECORD
    if RECORD is None:
        raw=subprocess.check_output([FF,'-v','error','-ss','30','-i',str(BASE/'picture.mp4'),'-t','5','-vf','crop=1120:674:670:208,fps=15','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        n=1120*674*3
        RECORD=[Image.frombytes('RGB',(1120,674),raw[k:k+n]) for k in range(0,len(raw),n)]
    return RECORD

def operation(t):
    im=base(2,t)
    enter(im,(90,165),'02  /  AI AGENT',t,0,20,BLUE,True)
    enter(im,(88,263),'理解目标',t,.1,62,INK,True)
    enter(im,(88,353),'确认关键参数',t,.25,51,BLUE,True)
    for i,s in enumerate(['金属结构','势函数','温度范围','体系规模']):
        y=498+i*94;dx=round(25*(1-ease((t-.35-i*.25)/.6)))
        rr(im,(92+dx,y,524+dx,y+73),'white',16,'#dce2f0')
        txt(im,(116+dx,y+20),f'0{i+1}',24,BLUE,True)
        txt(im,(181+dx,y+17),s,29,INK,True)
        if i==min(3,int(max(0,t-.7))):
            rr(im,(92+dx,y,524+dx,y+73),None,16,BLUE,2)
    rr(im,(648,189,1812,901),'#dce2ee',24)
    frames=recording();im.paste(frames[min(len(frames)-1,int(t*15))],(670,208))
    txt(im,(670,925),'平台操作实录',20,MUTED)
    return im

def workflow(t):
    im=base(2,t);heading(im,'02  /  工作流','把计算步骤连接起来',t,'金属熔点案例 · LAMMPS 分子动力学')
    labels=[('多温度模拟','配置模拟任务'),('轨迹与 MSD 分析','比较原子运动'),('结果汇总','图表与验证建议')]
    d=ImageDraw.Draw(im)
    for i,(title,sub) in enumerate(labels):
        a=ease((t-.3-i*.5)/.7);x=100+i*590;y=436+int(45*(1-a))
        rr(im,(x,y,x+530,y+300),'white',24,'#dce2f0',2)
        enter(im,(x+34,y+29),f'0{i+1}',t,.3+i*.5,28,BLUE,True)
        enter(im,(x+34,y+103),title,t,.4+i*.5,38,INK,True)
        enter(im,(x+34,y+195),sub,t,.5+i*.5,28,MUTED)
        if i<2:
            p=ease((t-1-i*.7)/.8);start=x+533;end=start+54*p
            d.line((start,586,end,586),fill=BLUE,width=3)
            if p>.9:d.polygon([(end,586),(end-9,580),(end-9,592)],fill=BLUE)
    if t>1.2:
        px=130+((t-1.2)/3.8%1)*1630
        d.line((130,813,1760,813),fill='#d7ddf6',width=2)
        d.ellipse((px-6,807,px+6,819),fill=TEAL)
    for i,s in enumerate(['参数校验','文件衔接','资源配置','任务提交']):
        enter(im,(138+i*444,860),s,t,1.3+i*.2,28,BLUE,True)
    txt(im,(100,961),'流程示意',19,MUTED)
    return im

CHART=Image.open(V4/'03_原始素材/0252131c-9fe3-48d6-9f17-739ffb635336.png').convert('RGB').crop((270,325,2060,1390)).resize((1200,714),Image.Resampling.LANCZOS)
arr=np.array(CHART);a=arr.astype(int)
mask=((a[:,:,1]-a[:,:,0]>18)|((a[:,:,0]-a[:,:,1]>20)&(a[:,:,2]-a[:,:,1]>15)))
# Include antialiased edge pixels, so an unrevealed trace is genuinely blank.
mask=np.array(Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)))>0
# Preserve the legend, axes and labels; only the plot-area curve pixels are revealed.
mask[:73,:]=False;mask[616:,:]=False;mask[:,:132]=False;mask[:,1147:]=False
mask[70:150,130:320]=False
blank=arr.copy();blank[mask]=255
CHART_BLANK=Image.fromarray(blank)
del a,arr,mask,blank

def charts(t):
    im=base(3,t);d=ImageDraw.Draw(im)
    enter(im,(90,165),'03  /  数据可视化',t,0,20,BLUE,True)
    enter(im,(88,236),'复杂数据',t,.1,58,INK,True)
    enter(im,(88,322),'直观呈现',t,.25,58,BLUE,True)
    enter(im,(92,463),'不同温度下的',t,.5,27,MUTED)
    enter(im,(92,512),'均方位移（MSD）',t,.55,27,MUTED)
    for i,(y,col,title,detail) in enumerate([(625,'#70ac37','1600 K','MSD 随时间上升'),(761,'#54206b','300 K','MSD 呈平台')]):
        rr(im,(93,y,105,y+79),col,5)
        enter(im,(126,y-3),title,t,.6+i*.25,35,col,True)
        enter(im,(127,y+48),detail,t,.7+i*.25,25,MUTED)
    rr(im,(554,190,1836,937),'white',26,'#dfe4ee')
    panel=CHART_BLANK.copy();p=smooth((t-.5)/4.4);cut=round(132+1015*p)
    panel.paste(CHART.crop((0,0,cut,714)),(0,0))
    if p>=1:panel=CHART.copy()
    im.paste(panel,(590,201))
    if .02<p<.995:
        x=590+cut;d.line((x,275,x,817),fill='#c4cce9',width=1)
        d.ellipse((x-4,813,x+4,821),fill=BLUE)
    txt(im,(593,907),'示例结果 · 原始曲线逐步展示',18,MUTED)
    return im

ANALYSIS=Image.open(V4/'03_原始素材/17ca551a-694e-46b7-8861-0ff29629ef79.png').convert('RGB')
RESULT_PANELS=[fit(ANALYSIS.crop(rect),1004,475) for rect in [(190,320,1470,785),(190,815,1470,1085)]]

def results(t):
    im=base(3,t);heading(im,'03  /  分析与验证','理解结果，明确下一步',t)
    active=0 if t<2.8 else 1
    for i,(title,sub) in enumerate([('已有对比','300 K 呈平台，1600 K 呈扩散'),('验证边界','两点对比，不等于精确熔点'),('下一步','加密温度扫描，扩大体系验证')]):
        y=360+i*172
        rr(im,(90,y,716,y+142),'white',22,BLUE if i==active+1 else '#dce2f0',2)
        enter(im,(120,y+20),title,t,.15+i*.15,34,BLUE if i==active+1 else INK,True)
        enter(im,(120,y+83),sub,t,.3+i*.15,24,MUTED)
    rr(im,(769,340,1839,921),'white',24,'#dfe4f1')
    canvas=[]
    for panel in RESULT_PANELS:
        p=Image.new('RGB',(1004,475),'white');p.paste(panel,((1004-panel.width)//2,(475-panel.height)//2));canvas.append(p)
    obj=Image.blend(canvas[0],canvas[1],smooth((t-2.65)/.55))
    im.paste(obj,(802,370))
    txt(im,(802,877),'AI 分析原文 · 局部放大',19,MUTED)
    return im

TEMPLATE_OVERVIEW=fit(Image.open(V3/'03_原始截图/模板库全景_3450x1701.png').convert('RGB'),1710,580)
CARDS=[Image.open(V3/'04_模板卡片原像素'/name).convert('RGB') for name in ['04_态密度_DOS.png','05_反常霍尔电导_AHC.png','06_联合态密度_JDOS.png']]

def templates(t):
    im=base(4,t);heading(im,'04  /  模板库','内置丰富计算模板',t,'不止于一个案例，拓展更多材料计算场景')
    overview=im.copy()
    rr(overview,(83,361,1837,971),'white',24,'#dce2f0')
    # Slow camera movement on the source image, retaining the original sharp PNG.
    sc=1+.015*smooth(t/3);obj=TEMPLATE_OVERVIEW.resize((round(TEMPLATE_OVERVIEW.width*sc),round(TEMPLATE_OVERVIEW.height*sc)),Image.Resampling.LANCZOS)
    overview.paste(obj,(round(960-obj.width/2),round(662-obj.height/2)))
    close=im.copy()
    for i,(card,cat) in enumerate(zip(CARDS,['电子结构','输运','光学'])):
        x=143+i*580;y=403+round(70*(1-ease((t-2.3-i*.23)/.8)))
        rr(close,(x-11,y-11,x+card.width+11,y+card.height+11),'#e1e6f8',24)
        close.paste(card,(x,y))
        enter(close,(x+160,961),cat,t,2.6+i*.23,28,BLUE,True)
        if t>4.2 and min(2,int((t-4.2)/1.1))==i:
            rr(close,(x-11,y-11,x+card.width+11,y+card.height+11),None,24,BLUE,3)
    return Image.blend(overview,close,smooth((t-2.5)/.65))

def properties(t):
    im=base(4,t);heading(im,'04  /  材料计算能力','覆盖多类材料计算场景',t)
    names=[('电子结构','能带 · 态密度'),('输运','电导 · 霍尔响应'),('光学','联合态密度 · 光学响应'),('磁性','磁矩 · 磁性分析')]
    d=ImageDraw.Draw(im)
    for i,(title,sub) in enumerate(names):
        x=90+i*445;y=399+round(50*(1-ease((t-.25-i*.22)/.8)))
        rr(im,(x,y,x+410,y+450),'white',24,'#dce2f0',2)
        # Graphic traces indicate subject areas; these are explicitly illustrative.
        cx=x+205;cy=y+143
        if i in (0,1,2):
            for j in range(3):
                pts=[]
                for k in range(120):
                    xx=x+65+k*2.35
                    yy=cy+36*math.sin(k/24+j*1.4+t*.35)+(j-1)*30
                    pts.append((xx,yy))
                d.line(pts,fill=[BLUE,TEAL,'#a1aaf2'][j],width=3)
        else:
            for k in range(9):
                xx=x+98+(k%3)*105;yy=y+82+(k//3)*65
                off=6*math.sin(t*1.2+k*.3)
                d.line((xx,yy+25,xx+off,yy-12),fill=BLUE,width=3)
                d.polygon([(xx+off,yy-18),(xx+off-7,yy-7),(xx+off+7,yy-7)],fill=BLUE)
        enter(im,(x+35,y+280),title,t,.35+i*.22,40,INK,True)
        enter(im,(x+35,y+354),sub,t,.55+i*.22,22,MUTED)
    txt(im,(94,933),'物性类别示意',18,MUTED)
    return im

RECAP=[fit(qfull.crop((746,178,1829,935)),480,340),fit(Image.open(V4/'01_主分镜_1080p/05_多步骤计算.png').crop((88,375,1820,907)),480,340),fit(CHART,480,340)]
def recap(t):
    im=base(5,t);heading(im,'05  /  从问题到结果','从提出问题，到理解结果',t)
    d=ImageDraw.Draw(im)
    for i,(panel,title) in enumerate(zip(RECAP,['提出问题','组织计算','理解结果'])):
        x=100+i*590;y=405+round(50*(1-ease((t-.2-i*.25)/.7)))
        rr(im,(x,y,x+530,y+447),'white',24,'#dce2f0',2)
        im.paste(panel,(x+(530-panel.width)//2,y+30+(300-panel.height)//2))
        enter(im,(x+168,y+357),title,t,.4+i*.25,34,BLUE,True)
        if i<2:
            p=ease((t-.7-i*.45)/.8);d.line((x+533,y+223,x+533+53*p,y+223),fill=BLUE,width=3)
    return im

def outro(t):
    im=LIGHT.copy();d=ImageDraw.Draw(im)
    # Shared light palette, matching the opening and all intermediate scenes.
    for j in range(16):
        a=j*math.pi/8+t*.07
        x=960+600*math.cos(a);y=550+340*math.sin(a)
        d.ellipse((x-3,y-3,x+3,y+3),fill='#c8d0f4')
    dy=round(25*(1-ease(t/.9)));im.paste(ICON,(908,202+dy),ICON)
    for s,size,y,col,delay in [('ABACUSLab',86,350,BLUE,.1),('让材料计算更简单',64,510,INK,.3),('从一句话开始',36,653,BLUE,.6)]:
        width=ft(size,True).getlength(s);enter(im,((W-width)/2,y),s,t,delay,size,col,True)
    p=ease((t-.5)/1);d.line((960-155*p,622,960+155*p,622),fill='#c5cff2',width=2)
    return im

SCENES=[(0,6,intro),(6,15,question),(15,20,operation),(20,25,workflow),(25,31,charts),(31,37,results),(37,45,templates),(45,51,properties),(51,55,recap),(55,60,outro)]
def frame(t):
    for i,(a,b,fn) in enumerate(SCENES):
        if a<=t<b:
            im=fn(t-a)
            if i and t-a<.55:
                pa,pb,pfn=SCENES[i-1]
                old=pfn(pb-pa+t-a)
                im=Image.blend(old,im,smooth((t-a)/.55))
            return im
    return outro(5)

ENTRIES=[
    (0,6,'ABACUSLab，让材料计算更简单。'),
    (6,15,'从一句话开始。告诉 AI：“我想计算这种金属的熔点。”'),
    (15,25,'AI 帮你梳理计算思路，确认关键参数，再将模拟、分析和结果汇总，串成工作流。'),
    (25,37,'对比不同温度下的原子运动，看懂计算结果。定位熔点，还需进一步温度扫描，AI 为你梳理下一步验证方向。'),
    (37,51,'不止于这个案例。平台内置丰富的计算模板，覆盖电子结构、输运、光学、磁性等多类材料计算场景。'),
    (51,60,'从提出问题，到理解结果。ABACUSLab，让材料计算更简单。'),
]
async def voices():
    import edge_tts
    for i,(_,_,s) in enumerate(ENTRIES):
        path=VOICE/f'{i:02d}.mp3'
        if path.exists() and path.stat().st_size>2000:continue
        await asyncio.wait_for(edge_tts.Communicate(s.replace('ABACUSLab','ABACUS LAB'),'zh-CN-XiaoxiaoNeural',rate='+0%').save(str(path)),timeout=50)
        print('Voice',i+1,'/ 6',flush=True)

def mix_audio():
    # Reuse the established V3 accompaniment algorithm, with the new V5 narration.
    import make_v3_video as audio
    audio.WORK=WORK;audio.VOICE=VOICE;audio.entries=ENTRIES
    audio.mix()

def previews():
    times=[.4,2,4.5,7.5,11,17,23,26,28,30.5,33,35.5,38.5,41,44,48,53,58]
    sheet=Image.new('RGB',(1440,1800),'#edf0f9')
    for i,t in enumerate(times):
        im=frame(t);im.save(STILLS/f'{t:04.1f}s.png')
        im=im.resize((480,270),Image.Resampling.LANCZOS);x=i%3*480;y=i//3*300
        txt(sheet,(x+10,y+4),f'{t:g} s',19,INK);sheet.paste(im,(x,y+30))
    sheet.save(ASSETS/'00_动态版画面总览.jpg',quality=95)
    print('Previews complete',flush=True)

def picture():
    p=subprocess.Popen([FF,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(WORK/'picture_motion.mp4')],stdin=subprocess.PIPE)
    start=time.time()
    try:
        for n in range(60*FPS):
            p.stdin.write(frame(n/FPS).tobytes())
            if n%150==0:print(f'Render {n//FPS}/60 s; elapsed {time.time()-start:.1f}s',flush=True)
    finally:p.stdin.close()
    if p.wait()!=0:raise RuntimeError('Video encode failed')
    print('Picture complete',flush=True)

DEST=OUT/'ABACUSLab_V5_60秒_浅色动态版_无字幕.mp4'
def final():
    run(['-y','-i',str(WORK/'picture_motion.mp4'),'-i',str(WORK/'配音与音乐.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','volume=0.8','-c:a','aac','-b:a','192k','-t','60','-movflags','+faststart',str(DEST)])
    for name,a,b in [('01_开场_浅色材料结构动画',0,6),('02_AI提问_逐字输入',6,15),('03_工作流_连线推进',20,25),('04_MSD_原始曲线逐步绘制',25,31),('05_模板_总览转卡片特写',37,45),('06_品牌片尾',55,60)]:
        # Standalone clips omit transition carry-over from the preceding scene.
        p=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(ASSETS/f'{name}.mp4')],stdin=subprocess.PIPE)
        fn=next(fn for sa,sb,fn in SCENES if sa==a)
        try:
            for n in range((b-a)*FPS):p.stdin.write(fn(n/FPS).tobytes())
        finally:p.stdin.close()
        if p.wait():raise RuntimeError('Clip encoding failed')
        print('Clip',name,flush=True)
    print('DONE',DEST,flush=True)

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if mode=='voice':asyncio.run(voices())
    elif mode=='mix':mix_audio()
    elif mode=='previews':previews()
    elif mode=='picture':picture()
    elif mode=='final':final()
