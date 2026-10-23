"""Seven PDF storyboard sections, retimed to 80 s with user light/no-caption overrides."""
from pathlib import Path
import sys,math,json,subprocess,asyncio,shutil,time
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import make_v6_video as v
m=v.m;BASE=v.BASE;FF=v.FF
ROOT=BASE/'交付_V7_按PDF分镜_80秒'
OUT=ROOT/'04_视频成片';WORK=OUT/'制作文件';VOICE=WORK/'voice'
ASSETS=ROOT/'03_素材';RAW=ASSETS/'原始素材';STILLS=ASSETS/'关键帧'
for p in [OUT,WORK,VOICE,RAW,STILLS,ROOT/'01_演讲稿',ROOT/'02_分镜脚本',ROOT/'05_音频']:p.mkdir(parents=True,exist_ok=True)
NEW=Path('C:/Users/13118/AppData/Local/Temp/codex-clipboard-b51843db-4fa9-4c9d-bc1d-7d83ca59496a.png')
HOMEFILE=RAW/'平台首页_用户最新截图.png'
if not HOMEFILE.exists():shutil.copy2(NEW,HOMEFILE)
HOME=Image.open(HOMEFILE).convert('RGB')
shutil.copy2(v.TASKFILE,RAW/v.TASKFILE.name)
BLUE,INK,MUTED=m.BLUE,m.INK,m.MUTED
txt,rr,enter,fit,ease,smooth=m.txt,m.rr,m.enter,m.fit,m.ease,m.smooth
CHAPTER=0

def base(chapter,t):
    im=m.LIGHT.copy();im.paste(m.LOGO,(70,30),m.LOGO)
    txt(im,(1810,62),'AI 驱动的材料计算与设计平台',22,MUTED,anchor='ra')
    ImageDraw.Draw(im).line((80,128,1840,128),fill='#dce2f0')
    for i in range(7):
        x=1520+i*44;rr(im,(x,1032,x+28,1036),BLUE if i==CHAPTER else '#d5dcec',2)
    return im
m.base=base;v.base=base

def centered(im,text,y,size,color,t,delay=0):
    w=m.ft(size,True).getlength(text);enter(im,((1920-w)/2,y),text,t,delay,size,color,True)

def intro(t):
    im=base(0,t)
    # The user clarified that brand presentation should use the actual homepage.
    close=im.copy();wide=im.copy()
    rr(close,(85,268,1835,788),'white',26,'#dce2f0')
    rr(wide,(85,268,1835,788),'white',26,'#dce2f0')
    scale=1+.022*smooth(t/3)
    obj=fit(HOME_BRAND,round(1450*scale),350)
    close.paste(obj,((1920-obj.width)//2,400+(300-obj.height)//2))
    hero=fit(HOME_HERO,1710,400)
    wide.paste(hero,((1920-hero.width)//2,320+(400-hero.height)//2))
    im=Image.blend(close,wide,smooth((t-2.8)/1.2))
    centered(im,'让材料计算更简单',850,46,BLUE,t,.6)
    return im

def homecrop(rect):
    return HOME.crop(tuple(round(n*(HOME.width/2048 if i%2==0 else HOME.height/1017)) for i,n in enumerate(rect)))
HOME_CONTENT=homecrop((242,64,2026,1003))
HOME_ENGINES=homecrop((915,107,1546,253))
HOME_BRAND=homecrop((265,91,899,202))
HOME_HERO=homecrop((243,65,2023,298))
def homepage(t):
    im=base(1,t);enter(im,(90,165),'专业计算能力',t,0,44,INK,True)
    rr(im,(84,248,1836,987),'white',24,'#dce2f0')
    obj=fit(HOME_CONTENT,1700,700);im.paste(obj,((1920-obj.width)//2,268+(700-obj.height)//2))
    return im

def engines(t):
    im=base(1,t);enter(im,(90,165),'ABACUS 第一性原理计算基础',t,0,44,INK,True)
    obj=fit(HOME_ENGINES,1600,480)
    rr(im,(125,330,1795,845),'white',24,'#dce2f0')
    im.paste(obj,((1920-obj.width)//2,365+(400-obj.height)//2))
    p=ease(t/.8);ImageDraw.Draw(im).line((180,876,180+470*p,876),fill=BLUE,width=3)
    txt(im,(180,909),'平台引擎 · 首页实截',23,MUTED)
    return im

def templates(t):
    im=v.templates(t)
    for i,s in enumerate(['结构优化','电子结构','分子动力学','材料物性']):
        x=106+i*442;rr(im,(x,302,x+389,352),'#e7ebff',15)
        txt(im,(x+194,309),s,24,BLUE,True,anchor='ma')
    return im

def ai_workflow(t):
    im=base(2,t);enter(im,(90,165),'AI 智能规划计算流程',t,0,43,INK,True)
    frames=m.recording();idx=min(len(frames)-1,int(t/14*(len(frames)-1)))
    rr(im,(378,235,1542,925),'#dce2ee',23)
    im.paste(frames[idx],(400,243))
    active=min(3,int(t/3.5));d=ImageDraw.Draw(im)
    for i,s in enumerate(['理解需求','规划流程','配置参数','组织计算']):
        x=90+i*450;fill=BLUE if i==active else 'white'
        rr(im,(x,941,x+390,1004),fill,17,None if i==active else '#dce2f0')
        txt(im,(x+195,954),s,28,'white' if i==active else INK,True,anchor='ma')
        if i<3:txt(im,(x+418,952),'→',29,BLUE,anchor='ma')
    txt(im,(1580,367),'输入核对',26,BLUE,True)
    for i,s in enumerate(['材料结构','势函数','温度范围','体系规模']):
        enter(im,(1580,437+i*85),s,t,6+i*.6,25,MUTED)
    return im

PROMPT='我想研究金属的熔化行为'
def case_input(t):
    im=base(3,t);enter(im,(90,165),'从一句话，开始材料计算',t,0,43,INK,True)
    panel=m.QPANEL;im.paste(panel,(418,238))
    # Clear the empty editorial field then render the user's example phrase.
    rr(im,(405,665,1515,850),'white',23,'#b9212b',3)
    n=min(len(PROMPT),max(0,int((t-1)*4.8)))
    txt(im,(445,704),PROMPT[:n],43,INK)
    if t<5.3 and int(t*3)%2==0:
        cx=445+m.ft(43).getlength(PROMPT[:n]);ImageDraw.Draw(im).line((cx+3,711,cx+3,756),fill='#b9212b',width=2)
    txt(im,(445,795),'附件    知识库',20,MUTED)
    rr(im,(1427,773,1483,829),'#bb252e',28);txt(im,(1455,772),'↑',36,'white',anchor='ma')
    if t>4.5:
        enter(im,(445,895),'正在理解需求',t,4.5,24,BLUE)
        for i in range(3):
            x=632+i*23;y=910+round(4*math.sin(t*5-i));ImageDraw.Draw(im).ellipse((x,y,x+8,y+8),fill=BLUE)
    return im

def execution(t):return v.execution(t)

# Reveal the two original traces separately, as requested in the PDF.
arr=np.array(m.CHART);a=arr.astype(int)
curve_masks=[]
for colored in [(a[:,:,0]-a[:,:,1]>2)&(a[:,:,2]-a[:,:,1]>2),(a[:,:,1]-a[:,:,0]>2)&(a[:,:,1]-a[:,:,2]>2)]:
    mm=colored.copy()
    mm[:73,:]=False;mm[616:,:]=False;mm[:,1147:]=False;mm[70:150,130:320]=False
    curve_masks.append(Image.fromarray((mm*255).astype('uint8')))
blank=arr.copy()
blank[(np.asarray(curve_masks[0])>0)|(np.asarray(curve_masks[1])>0)]=255
CHART_BLANK=Image.fromarray(blank)
del arr,a

def charts(t):
    im=base(4,t);enter(im,(90,165),'计算结果，直观呈现',t,0,43,INK,True)
    panel=CHART_BLANK.copy()
    for i,mask in enumerate(curve_masks):
        p=smooth((t-(.6 if i==0 else 4.8))/3.7);cut=0 if p==0 else round(132+1015*p)
        current=mask.copy();ImageDraw.Draw(current).rectangle((cut,0,1200,714),fill=0)
        panel.paste(m.CHART,(0,0),current)
    if t>=8.6:panel=m.CHART.copy()
    rr(im,(600,245,1850,996),'white',25,'#dce2f0');im.paste(panel,(625,259))
    enter(im,(92,305),'不同温度下的',t,.2,36,INK,True)
    enter(im,(92,367),'原子运动',t,.35,42,BLUE,True)
    for i,(title,sub,y,col) in enumerate([('300 K','MSD 呈平台',526,'#54206b'),('1600 K','MSD 随时间上升',710,'#70ac37')]):
        rr(im,(93,y,105,y+94),col,5)
        txt(im,(130,y-3),title,37,col,True);txt(im,(130,y+56),sub,26,MUTED)
        if (i==0 and .6<t<4.8) or (i==1 and 4.8<=t<9):rr(im,(80,y-16,535,y+116),None,18,col,2)
    txt(im,(92,928),'示例结果 · 300 K / 1600 K',20,MUTED)
    return im

ANALYSIS_PANELS=[fit(m.ANALYSIS.crop(rect),1004,500) for rect in [(190,75,1470,290),(190,320,1470,785),(190,815,1470,1085)]]
def analysis(t):
    im=base(5,t);enter(im,(90,165),'智能分析，辅助科学决策',t,0,43,INK,True)
    active=min(2,int(t/3))
    for i,(a,b) in enumerate([('主要发现','不同温度下的原子运动差异'),('结论局限','两点对比，不足以确定精确熔点'),('验证建议','进一步温度扫描，扩大体系验证')]):
        y=330+i*190;rr(im,(90,y,714,y+151),'white',22,BLUE if i==active else '#dce2f0',2)
        txt(im,(122,y+24),a,34,BLUE if i==active else INK,True)
        txt(im,(122,y+91),b,24,MUTED)
    rr(im,(766,312,1840,937),'white',24,'#dce2f0')
    def layer(i):
        canvas=Image.new('RGB',(1004,500),'white');p=ANALYSIS_PANELS[i]
        canvas.paste(p,((1004-p.width)//2,(500-p.height)//2));return canvas
    obj=layer(active)
    if active and t%3<.45:obj=Image.blend(layer(active-1),obj,smooth(t%3/.45))
    im.paste(obj,(802,356));txt(im,(802,889),'AI 分析原文 · 局部放大',19,MUTED)
    return im

SCENES=[(0,8,intro,0),(8,11,homepage,1),(11,13,engines,1),(13,22,templates,1),(22,36,ai_workflow,2),(36,44,case_input,3),(44,50,execution,3),(50,63,charts,4),(63,72,analysis,5),(72,80,v.outro,6)]
def frame(t):
    global CHAPTER
    for i,(a,b,fn,c) in enumerate(SCENES):
        if a<=t<b:
            CHAPTER=c;im=fn(t-a)
            if i and t-a<.45:
                pa,pb,pfn,pc=SCENES[i-1];CHAPTER=pc;old=pfn(pb-pa+t-a)
                im=Image.blend(old,im,smooth((t-a)/.45));CHAPTER=c
            return im
    return v.outro(8)

ENTRIES=[
 (0,8,'ABACUSLab，AI 驱动的材料计算与设计平台。'),
 (8,22,'以第一性原理计算软件 ABACUS 为基础，平台内置丰富的计算模板，覆盖结构优化、电子结构、分子动力学和材料物性计算。'),
 (22,36,'AI 理解研究目标，规划计算流程，帮助核对关键输入、配置参数，并组织计算任务，让自然语言需求连接真实计算。'),
 (36,44,'例如，只需一句话：我想研究金属的熔化行为，就能开始提出模拟需求。'),
 (44,50,'在平台中，可以查看执行状态和任务步骤。'),
 (50,63,'不同温度下的均方位移曲线，直观展示原子运动的差异。对比三百开尔文与一千六百开尔文，观察材料的变化。'),
 (63,72,'AI 解读结果、提示局限。两个温度点，还不足以确定精确熔点，仍需进一步温度扫描。'),
 (72,80,'ABACUSLab，让材料计算更简单。')]

# Reuse matching voice takes; regenerate only changed sentences.
for target,source in [(0,0),(4,6),(6,8),(7,9)]:
    dest=VOICE/f'{target:02d}.mp3'
    if not dest.exists():shutil.copy2(v.VOICE/f'{source:02d}.mp3',dest)

v.ROOT=ROOT;v.OUT=OUT;v.WORK=WORK;v.VOICE=VOICE;v.ENTRIES=ENTRIES;v.frame=frame
v.STILLS=STILLS;v.ASSETS=ASSETS;v.TIMES=[2,9,12,16,20,24,29,34,39,43,47,52,56,61,64,67,70,76]
DEST=OUT/'ABACUSLab_V7_按PDF分镜_80秒_无字幕.mp4'

def docs():
    rows=['# V7 演讲稿｜PDF 分镜顺序','','沿用现有中文女声；不加配音字幕。','', '| 时间（秒） | 配音内容 |','|---|---|']
    rows += [f'| {a}—{b} | {s} |' for a,b,s in ENTRIES]
    (ROOT/'01_演讲稿/演讲稿_含时间.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    (ROOT/'01_演讲稿/演讲稿_纯配音.txt').write_text('\n\n'.join(s for _,_,s in ENTRIES)+'\n',encoding='utf-8')

def previews():
    sheet=Image.new('RGB',(1440,1800),'#e9edf5')
    for i,t in enumerate(v.TIMES):
        im=frame(t);im.save(STILLS/f'{t:02d}s.png');im=im.resize((480,270),Image.Resampling.LANCZOS)
        x=i%3*480;y=i//3*300;txt(sheet,(x+10,y+4),f'{t}s',20,INK);sheet.paste(im,(x,y+30))
    sheet.save(ASSETS/'分镜总览.jpg',quality=95);docs();print('Previews complete',flush=True)

def final():
    m.run(['-y','-i',str(WORK/'picture.mp4'),'-i',str(WORK/'配音与音乐.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','volume=0.8','-c:a','aac','-b:a','192k','-t','80','-movflags','+faststart',str(DEST)])
    print('DONE',DEST,flush=True)

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if mode=='previews':previews()
    elif mode=='voice':asyncio.run(v.voices())
    elif mode=='mix':v.mix_audio()
    elif mode=='picture':v.picture()
    elif mode=='final':final()
