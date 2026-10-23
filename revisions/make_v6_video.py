"""80-second review cut using supplied task-status evidence and existing originals."""
from pathlib import Path
import sys,math,json,subprocess,asyncio,wave,time,shutil
import numpy as np
from PIL import Image,ImageDraw
import make_v5_motion as m

BASE=m.BASE;FF=m.FF;FPS=30
ROOT=BASE/'交付_V6_80秒审看版'
OUT=ROOT/'04_视频成片';WORK=OUT/'制作文件';VOICE=WORK/'voice'
ASSETS=ROOT/'03_素材';STILLS=ASSETS/'关键帧';RAW=ASSETS/'原始素材'
for p in [OUT,WORK,VOICE,ASSETS,STILLS,RAW,ROOT/'01_演讲稿',ROOT/'02_分镜脚本',ROOT/'05_音频']:p.mkdir(parents=True,exist_ok=True)
SOURCE=Path('C:/Users/13118/AppData/Local/Temp/codex-clipboard-f87111eb-785a-4e07-8f37-5dc353d2afc6.png')
TASKFILE=RAW/'金属熔点_工作流执行状态_原图.png'
if not TASKFILE.exists():shutil.copy2(SOURCE,TASKFILE)
TASK=Image.open(TASKFILE).convert('RGB')
BLUE=m.BLUE;INK=m.INK;MUTED=m.MUTED
txt,rr,enter,fit,ease,smooth=m.txt,m.rr,m.enter,m.fit,m.ease,m.smooth
CHAPTER=0

def base(chapter,t):
    im=m.LIGHT.copy();d=ImageDraw.Draw(im);im.paste(m.LOGO,(70,30),m.LOGO)
    txt(im,(1810,62),'AI 驱动的材料计算与设计平台',22,MUTED,anchor='ra')
    d.line((80,128,1840,128),fill='#dce2f0')
    for i in range(8):
        x=1480+i*44;rr(im,(x,1032,x+28,1036),BLUE if i==CHAPTER else '#d5dcec',2)
    return im
m.base=base
m.PROMPT='我想研究这种金属的熔化行为'

def intro(t):
    im=base(0,t);d=ImageDraw.Draw(im);m.lattice(im,t)
    enter(im,(91,234),'MATERIALS × AI',t,0,24,BLUE,True)
    enter(im,(84,316),'ABACUSLab',t,.05,94,BLUE,True)
    enter(im,(90,459),'AI 驱动的',t,.35,46,INK,True)
    enter(im,(90,529),'材料计算与设计平台',t,.55,50,INK,True)
    p=ease((t-.9)/1.1);d.line((94,628,94+640*p,628),fill='#c4ccf4',width=3)
    enter(im,(94,684),'让材料计算更简单',t,1.2,37,BLUE,True)
    txt(im,(1430,847),'材料结构示意',20,MUTED,anchor='ma')
    return im

HERO=Image.open(m.V4/'04_裁切素材/首页品牌区.png').convert('RGB')
ENGINES=HERO.crop((1270,85,2450,360))
ENGINE_PANEL=fit(ENGINES,1200,360)

def foundation(t):
    im=base(1,t);m.heading(im,'专业计算基础','从结构建模，到物性分析',t)
    enter(im,(94,353),'ABACUS',t,.25,66,BLUE,True)
    enter(im,(98,449),'第一性原理计算',t,.45,37,INK,True)
    enter(im,(98,517),'连接多种计算与分析工具',t,.65,26,MUTED)
    rr(im,(650,342,1830,711),'white',24,'#dce2f0')
    obj=fit(ENGINE_PANEL,1120,300);im.paste(obj,(680+(1120-obj.width)//2,376+(300-obj.height)//2))
    txt(im,(686,676),'平台计算引擎 · 首页实截',18,MUTED)
    d=ImageDraw.Draw(im)
    for i,s in enumerate(['结构建模','材料计算','物性分析']):
        x=100+i*592;y=810+round(30*(1-ease((t-.8-i*.3)/.8)))
        rr(im,(x,y,x+525,y+107),'white',18,'#dce2f0')
        enter(im,(x+166,y+29),s,t,1+i*.3,32,BLUE,True)
        if i<2:
            p=ease((t-1.6-i*.4)/.8);d.line((x+535,y+53,x+535+45*p,y+53),fill=BLUE,width=3)
    return im

CARDS=[Image.open(m.V3/'04_模板卡片原像素'/f).convert('RGB') for f in ['02_原子位置弛豫_Relax.png','04_态密度_DOS.png','03_分子动力学_MD.png']]
def templates(t):
    im=base(2,t);m.heading(im,'丰富计算模板','覆盖多类材料计算场景',t)
    overview=im.copy();obj=m.TEMPLATE_OVERVIEW
    rr(overview,(83,340,1837,969),'white',24,'#dce2f0')
    sc=1+.018*smooth(t/2.5);obj=obj.resize((round(obj.width*sc),round(obj.height*sc)),Image.Resampling.LANCZOS)
    overview.paste(obj,((1920-obj.width)//2,round(653-obj.height/2)))
    close=im.copy()
    for i,(card,cat) in enumerate(zip(CARDS,['结构优化','电子结构','分子动力学'])):
        x=143+i*580;y=380+round(65*(1-ease((t-2-i*.22)/.8)))
        rr(close,(x-10,y-10,x+card.width+10,y+card.height+10),'#e1e6f8',22)
        close.paste(card,(x,y));enter(close,(x+145,950),cat,t,2.3+i*.22,28,BLUE,True)
        if t>3.4 and min(2,int((t-3.4)/1.5))==i:rr(close,(x-10,y-10,x+card.width+10,y+card.height+10),None,22,BLUE,3)
    return Image.blend(overview,close,smooth((t-2)/.65))

def question(t):return m.question(t)
def operation(t):return m.operation(min(t,4.9))
def workflow(t):return m.workflow(t*1.2)

# Native-pixel crops from the user screenshot, omitting personal controls and file paths.
sx=TASK.width/2048;sy=TASK.height/1107
def crop_ref(rect):return TASK.crop(tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(rect)))
TASK_SUMMARY=crop_ref((78,198,800,259))
TASK_STEPS=crop_ref((53,365,435,551))
TASK_OVERVIEW=crop_ref((31,157,2000,554))
for n,im in [('任务名称与完成状态',TASK_SUMMARY),('两个温度任务步骤',TASK_STEPS)]:im.save(RAW/f'{n}.png')
summary=fit(TASK_SUMMARY,1260,142);steps=fit(TASK_STEPS,900,440)

def execution(t):
    im=base(4,t);m.heading(im,'工作流执行状态','任务进度，清晰可见',t)
    rr(im,(91,352,1830,507),'white',23,'#dce2f0')
    im.paste(summary,(125,366+(128-summary.height)//2))
    enter(im,(1480,397),'2 个任务',t,.3,36,BLUE,True)
    rr(im,(91,542,1053,973),'white',23,'#dce2f0')
    obj=fit(TASK_STEPS,880,375);im.paste(obj,(120,564))
    for i,(title,sub) in enumerate([('300 K','lammps_calc_300'),('1600 K','lammps_calc_1600')]):
        y=587+i*172
        enter(im,(1130,y),title,t,.4+i*.8,42,BLUE,True)
        enter(im,(1133,y+66),sub,t,.6+i*.8,28,INK,True)
    # Editorial emphasis surrounds original, already-completed rows; no fake state change.
    d=ImageDraw.Draw(im)
    if t>1:
        p=ease((t-1)/.7);d.line((1128,904,1128+580*p,904),fill='#b9c5ef',width=3)
    txt(im,(1133,930),'金属熔点计算 · 执行记录',20,MUTED)
    return im

def charts(t):
    im=m.charts(t*.55)
    if t>8:
        # Highlight temperature keys while the complete original figure stays visible.
        i=0 if t<10.3 else 1;y=625 if i==0 else 761
        rr(im,(82,y-17,487,y+100),None,18,'#70ac37' if i==0 else '#54206b',2)
    return im

def results(t):return m.results(t*.60)

def outro(t):
    t=min(t,6);im=m.LIGHT.copy();d=ImageDraw.Draw(im)
    for j in range(16):
        a=j*math.pi/8+t*.07;x=960+650*math.cos(a);y=540+370*math.sin(a)
        d.ellipse((x-3,y-3,x+3,y+3),fill='#c8d0f4')
    im.paste(m.ICON,(908,180+round(25*(1-ease(t/.9)))),m.ICON)
    for s,size,y,col,delay in [('ABACUSLab',86,325,BLUE,.1),('AI 驱动的材料计算与设计平台',35,477,MUTED,.3),('让材料计算更简单',64,610,INK,.5)]:
        width=m.ft(size,True).getlength(s);enter(im,((1920-width)/2,y),s,t,delay,size,col,True)
    p=ease((t-.5)/1);d.line((960-155*p,569,960+155*p,569),fill='#c5cff2',width=2)
    return im

SCENES=[(0,7,intro,0),(7,15,foundation,1),(15,24,templates,2),(24,34,question,3),(34,40,operation,4),(40,44,workflow,4),(44,49,execution,4),(49,62,charts,5),(62,72,results,6),(72,80,outro,7)]
def frame(t):
    global CHAPTER
    for i,(a,b,fn,c) in enumerate(SCENES):
        if a<=t<b:
            CHAPTER=c;im=fn(t-a)
            if i and t-a<.55:
                pa,pb,pfn,pc=SCENES[i-1];CHAPTER=pc;old=pfn(pb-pa+t-a)
                im=Image.blend(old,im,smooth((t-a)/.55));CHAPTER=c
            return im
    return outro(8)

ENTRIES=[
 (0,7,'ABACUSLab，AI 驱动的材料计算与设计平台。'),
 (7,15,'依托 ABACUS 第一性原理计算，连接结构建模、材料计算与物性分析。'),
 (15,24,'平台内置丰富模板，覆盖结构优化、电子结构、分子动力学等多类计算场景。'),
 (24,34,'从一句话开始。例如，告诉 AI：我想研究这种金属的熔化行为。'),
 (34,40,'AI 梳理计算思路，帮助确认结构、势函数和温度等关键输入。'),
 (40,44,'再将模拟与分析，组织成工作流。'),
 (44,49,'在平台中，可以查看执行状态和任务步骤。'),
 (49,62,'对比三百开尔文和一千六百开尔文的均方位移，观察原子运动的差异，让计算结果直观呈现。'),
 (62,72,'AI 解读结果、提示局限。两个温度点，还不足以确定精确熔点，仍需进一步温度扫描。'),
 (72,80,'ABACUSLab，让材料计算更简单。')]

async def voices():
    import edge_tts
    for i,(_,_,s) in enumerate(ENTRIES):
        dest=VOICE/f'{i:02d}.mp3'
        if dest.exists() and dest.stat().st_size>2000:continue
        await asyncio.wait_for(edge_tts.Communicate(s.replace('ABACUSLab','ABACUS LAB'),'zh-CN-XiaoxiaoNeural',rate='-5%').save(str(dest)),timeout=50)
        print('Voice',i+1,'/ 10',flush=True)

def writewav(path,data,sr=48000):
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1 if data.ndim==1 else data.shape[1]);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((np.clip(data,-.97,.97)*32767).astype('<i2').tobytes())

def mix_audio(duration=80):
    sr=48000;n=int(duration*sr);narration=np.zeros(n,np.float32);report=[]
    for i,(a,b,text) in enumerate(ENTRIES):
        raw=subprocess.check_output([FF,'-v','error','-i',str(VOICE/f'{i:02d}.mp3'),'-f','f32le','-ar',str(sr),'-ac','1','pipe:1'])
        data=np.frombuffer(raw,np.float32).copy();ix=np.flatnonzero(abs(data)>.004)
        if len(ix):data=data[max(0,ix[0]-int(.05*sr)):min(len(data),ix[-1]+int(.12*sr))]
        start=a+.35;available=b-start-.35;factor=max(1.,len(data)/sr/available)
        if factor>1.001:
            data=np.frombuffer(subprocess.check_output([FF,'-v','error','-f','f32le','-ar',str(sr),'-ac','1','-i','pipe:0','-af',f'atempo={factor:.6f}','-f','f32le','pipe:1'],input=data.tobytes()),np.float32).copy()
        data*=min(.12/max(float(np.sqrt(np.mean(data**2))),.001),.78/max(float(abs(data).max()),.001))
        st=round(start*sr);narration[st:st+len(data)]+=data
        report.append({'start':start,'end':start+len(data)/sr,'speed':factor,'text':text})
    music=np.zeros((n,2),np.float32);chords=[[50,57,62,64,69],[46,53,58,60,65],[53,60,65,67,72],[48,55,60,62,67]]
    for bar in range(math.ceil(duration/4)):
        st=bar*4*sr;ln=min(int(5.1*sr),n-st);tt=np.arange(ln)/sr
        env=np.minimum(1,tt/1.1)*np.minimum(1,np.maximum(0,(5.1-tt)/1.4))
        chord=sum(np.sin(2*np.pi*440*2**((note-69)/12)*tt+j*.5) for j,note in enumerate(chords[bar%4]))/5*.035*env
        music[st:st+ln]+=chord[:,None]
        for k in range(6):
            pst=int((bar*4+k*2/3)*sr);pn=min(int(1.4*sr),n-pst);pt=np.arange(pn)/sr
            f=440*2**((chords[bar%4][[2,3,4,3,1,3][k]]+12-69)/12)
            tone=np.sin(2*np.pi*f*pt)*(1-np.exp(-pt*50))*np.exp(-pt*3)*.012
            music[pst:pst+pn,k%2]+=tone
    fade=np.minimum(1,np.arange(n)/sr)*np.minimum(1,(n-1-np.arange(n))/sr/1.5)
    writewav(WORK/'配音与音乐.wav',(music+narration[:,None])*fade[:,None])
    writewav(ROOT/'05_音频/纯旁白_无音乐.wav',narration)
    (WORK/'配音检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Audio mixed',flush=True)

TIMES=[2,10,18,22,28,36,42,45,47,50,54,58,61,65,69,76]
def previews():
    sheet=Image.new('RGB',(1440,1200),'#e9edf5')
    for i,t in enumerate(TIMES):
        im=frame(t);im.save(STILLS/f'{t:02d}s.png');im=im.resize((360,203),Image.Resampling.LANCZOS)
        x=i%4*360;y=i//4*300;txt(sheet,(x+10,y+12),f'{t}s',20,INK);sheet.paste(im,(x,y+50))
    sheet.save(ASSETS/'画面总览.jpg',quality=95)
    print('Previews complete',flush=True)

def picture(duration=80):
    p=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(WORK/'picture.mp4')],stdin=subprocess.PIPE)
    start=time.time()
    try:
        for n in range(int(duration*FPS)):
            p.stdin.write(frame(n/FPS).tobytes())
            if n%300==0:print(f'Render {n//FPS}/{duration} s; elapsed {time.time()-start:.1f}s',flush=True)
    finally:p.stdin.close()
    if p.wait():raise RuntimeError('Encoding failed')
    print('Picture complete',flush=True)

DEST=OUT/'ABACUSLab_V6_80秒_浅色动态审看版_无字幕.mp4'
def final():
    m.run(['-y','-i',str(WORK/'picture.mp4'),'-i',str(WORK/'配音与音乐.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','volume=0.8','-c:a','aac','-b:a','192k','-t','80','-movflags','+faststart',str(DEST)])
    m.run(['-y','-ss','44','-i',str(DEST),'-t','5','-an','-c:v','libx264','-preset','fast','-crf','18','-movflags','+faststart',str(ASSETS/'执行状态_5秒片段.mp4')])
    print('DONE',DEST,flush=True)

def docs():
    rows=['# V6｜80 秒审看版演讲稿','','沿用中文女声；保留配音、音乐，不加字幕。','', '| 时间（秒） | 配音内容 |','|---|---|']
    for a,b,s in ENTRIES:rows.append(f'| {a}—{b} | {s} |')
    (ROOT/'01_演讲稿/演讲稿_含时间.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    (ROOT/'01_演讲稿/演讲稿_纯配音.txt').write_text('\n\n'.join(s for a,b,s in ENTRIES)+'\n',encoding='utf-8')
    (WORK/'旁白时间线.json').write_text(json.dumps(ENTRIES,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if mode=='voice':asyncio.run(voices())
    elif mode=='mix':mix_audio()
    elif mode=='previews':previews();docs()
    elif mode=='picture':picture()
    elif mode=='final':final()
