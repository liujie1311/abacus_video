"""Reorder the middle section: request, planning, execution, chart, analysis."""
from pathlib import Path
import sys,asyncio,shutil,json,subprocess
from PIL import Image,ImageDraw
import make_v7_pdf_cut as s
v=s.v;m=s.m;BASE=s.BASE;FF=s.FF
ROOT=BASE/'交付_V9_60秒_先提问再规划'
OUT=ROOT/'04_视频成片';WORK=OUT/'制作文件';VOICE=WORK/'voice'
ASSETS=ROOT/'03_素材';STILLS=ASSETS/'关键帧'
for p in [ROOT/'01_演讲稿',ROOT/'02_分镜脚本',OUT,WORK,VOICE,ASSETS,STILLS,ROOT/'05_音频']:p.mkdir(parents=True,exist_ok=True)
txt,enter,ease=s.txt,s.enter,s.ease
BLUE,INK,MUTED=s.BLUE,s.INK,s.MUTED

def intro(t):
    # Same composition, palette, lattice and movement as the delivered V5 6 s clip.
    im=s.base(0,t);d=ImageDraw.Draw(im)
    for x in range(1050,1830,60):
        for y in range(260,840,60):d.ellipse((x,y,x+2,y+2),fill='#d5dcf5')
    m.lattice(im,t)
    enter(im,(91,246),'MATERIALS × AI',t,0,24,BLUE,True)
    enter(im,(84,328),'ABACUSLab',t,.1,94,BLUE,True)
    enter(im,(87,467),'AI 驱动的材料计算',t,.45,52,INK,True)
    enter(im,(87,545),'与设计平台',t,.65,52,INK,True)
    p=ease((t-1)/1.1);d.line((94,650,94+640*p,650),fill='#c4ccf4',width=3)
    txt(im,(1430,847),'材料结构示意',20,MUTED,anchor='ma')
    return im

def engines(t):return s.engines(t)
def templates(t):return s.templates(t*1.15)
def ai_workflow(t):return s.ai_workflow(t*14/10)
def case_input(t):return s.case_input(t*8/7)
def execution(t):return s.execution(t*1.3)
def charts(t):return s.charts(t*13/9)
def analysis(t):return s.analysis(t*9/7)
def outro(t):return v.outro(min(6,t*1.2))

SCENES=[(0,6,intro,0),(6,8.5,engines,1),(8.5,16,templates,1),(16,23,case_input,2),(23,33,ai_workflow,3),(33,37,execution,3),(37,46,charts,4),(46,53,analysis,5),(53,60,outro,6)]
def frame(t):
    for i,(a,b,fn,c) in enumerate(SCENES):
        if a<=t<b:
            s.CHAPTER=c;im=fn(t-a)
            if i and t-a<.4:
                pa,pb,pfn,pc=SCENES[i-1];s.CHAPTER=pc;old=pfn(pb-pa+t-a)
                im=Image.blend(old,im,s.smooth((t-a)/.4));s.CHAPTER=c
            return im
    return outro(7)

ENTRIES=[
 (0,6,'ABACUSLab，AI 驱动的材料计算与设计平台。'),
 (6,16,'以自主研发的第一性原理计算软件 ABACUS 为核心，内置丰富的常用计算模板。'),
 (16,23,'例如，只需一句话，就能启动金属熔化行为的模拟研究。'),
 (23,37,'AI 理解研究目标，自主规划计算流程、配置参数，组织计算任务。'),
 (37,46,'不同温度下的均方位移曲线，直观展示原子运动的差异。'),
 (46,53,'AI 解读结果、提示局限，并提出下一步验证建议。'),
 (53,60,'ABACUSLab，让材料计算更简单。')]


# The exact approved male takes remain valid; reorder them without a new TTS request.
previous=BASE/'交付_V8_60秒_原动态开场_按PDF分镜/04_视频成片/制作文件/voice'
for target,source in enumerate([0,1,3,2,4,5,6]):
    dest=VOICE/f'{target:02d}.mp3'
    if not dest.exists():shutil.copy2(previous/f'{source:02d}.mp3',dest)

async def voices():
    import edge_tts
    for i,(_,_,text) in enumerate(ENTRIES):
        path=VOICE/f'{i:02d}.mp3'
        if path.exists() and path.stat().st_size>2000:continue
        await asyncio.wait_for(edge_tts.Communicate(text.replace('ABACUSLab','ABACUS LAB'),'zh-CN-YunjianNeural',rate='-5%').save(str(path)),timeout=50)
        print('Male voice',i+1,'/ 7',flush=True)

v.ROOT=ROOT;v.OUT=OUT;v.WORK=WORK;v.VOICE=VOICE;v.ENTRIES=ENTRIES;v.frame=frame
DEST=OUT/'ABACUSLab_V9_60秒_先提问再规划_无字幕.mp4'

def docs():
    rows=['# V9 演讲稿｜一分钟 · 先提问再规划','','普通话男声；无配音字幕。','', '| 时间（秒） | 配音内容 |','|---|---|']
    rows += [f'| {a}—{b} | {text} |' for a,b,text in ENTRIES]
    (ROOT/'01_演讲稿/演讲稿_含时间.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    (ROOT/'01_演讲稿/演讲稿_纯配音.txt').write_text('\n\n'.join(text for _,_,text in ENTRIES)+'\n',encoding='utf-8')
    (WORK/'旁白时间线.json').write_text(json.dumps(ENTRIES,ensure_ascii=False,indent=2),encoding='utf-8')

def previews():
    times=[2,5,7.5,11,15,18,22,26,30,32,35,39,42,45,47,50,52,57]
    sheet=Image.new('RGB',(1440,1800),'#e9edf5')
    for i,t in enumerate(times):
        im=frame(t);im.save(STILLS/f'{t:04.1f}s.png');im=im.resize((480,270),Image.Resampling.LANCZOS)
        x=i%3*480;y=i//3*300;txt(sheet,(x+10,y+4),f'{t:g}s',20,INK);sheet.paste(im,(x,y+30))
    sheet.save(ASSETS/'分镜总览.jpg',quality=95);docs();print('Previews complete',flush=True)

def final():
    m.run(['-y','-i',str(WORK/'picture.mp4'),'-i',str(WORK/'配音与音乐.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','volume=0.8','-c:a','aac','-b:a','192k','-t','60','-movflags','+faststart',str(DEST)])
    m.run(['-y','-i',str(DEST),'-t','6','-c:v','libx264','-crf','18','-preset','fast','-c:a','aac','-b:a','192k','-movflags','+faststart',str(ASSETS/'开场6秒_新定位文案.mp4')])
    print('DONE',DEST,flush=True)

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if mode=='previews':previews()
    elif mode=='voice':asyncio.run(voices())
    elif mode=='mix':v.mix_audio(60)
    elif mode=='picture':v.picture(60)
    elif mode=='final':final()
