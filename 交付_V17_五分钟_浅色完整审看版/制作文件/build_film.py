"""Five-minute light review cut, source screenshots plus editorial conceptual graphics.
All time coordinates are seconds. External raw research data is not generated.
"""
from pathlib import Path
from functools import lru_cache
import sys,json,subprocess,importlib.util,math,time,io,hashlib,re,wave
import numpy as np
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent
LIGHT=BASE/'五分钟宣传片_浅色素材修订_20261023'
spec=importlib.util.spec_from_file_location('light',LIGHT/'制作文件/build_light_assets.py');l=importlib.util.module_from_spec(spec);spec.loader.exec_module(l)
FF=l.FF;W,H,FPS,DUR=1920,1080,30,300;WORK=ROOT/'制作文件';STILL=ROOT/'分镜预览';SRC=BASE/'五分钟宣传片_补充素材_20261023/01_已有平台素材'
DEST=ROOT/'ABACUSLab_V17_五分钟_浅色审看版_含字幕.mp4'
INK,BLUE,MUTED=l.INK,l.BLUE,l.MUTED
NAMES={'home':'N01_平台首页.png','templates':'01_模板库主画面.png','task':'04_项目任务卡片.png','workflow':'10_工作流总览.png','config':'07_INPUT配置弹窗.png','pyatb':'N02_PYATB生成结果.png','pdosfull':'N03_PDOS绘图结果.png','pdos':'P01_PDOS原图裁切.png','optical':'12_光学结果图.png','question':'A01_AI提问.png','complete':'A02_AI完成与绘图链接.png','msd':'P02_MSD原图裁切.png','analysis':'A04_AI分析与建议.png','bandfull':'历史手册_10_能带绘制.png','structure':'历史手册_12_结构展示.png'}
IMG={k:Image.open(SRC/f).convert('RGB') for k,f in NAMES.items()}
def crop(key,box):
    im=IMG[key];return im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box)))
IMG['homebody']=crop('home',(.103,.047,.993,.945));IMG['band']=crop('bandfull',(.313,.49,.62,.958));IMG['suggest']=crop('analysis',(.105,.64,.80,.86))
IMG['conclusion']=crop('analysis',(.105,.06,.80,.64));IMG['completebody']=crop('complete',(.045,.055,.96,.79))
IMG['structbody']=crop('structure',(.25,.12,.985,.96))
for i in range(3):IMG[f'template{i}']=crop('templates',(.092+i*.129,.15,.215+i*.129,.455))
SHOTS=[
 (0,6,'opening'),(6,13,'fields'),(13,21,'space'),(21,28,'research'),(28,36,'crystal'),(36,44,'questions'),
 (44,52,'firstprinciples'),(52,59,'ai'),(59,68,'brand_credit'),(68,76,'abacus_credit'),(76,86,'home'),
 (86,96,'templates'),(96,104,'reuse'),(104,112,'project'),(112,119,'config'),(119,124,'pdos'),(124,130,'optical'),
 (130,136,'aihero'),(136,144,'prompt_general'),(144,154,'ai'),(154,163,'review'),
 (163,169,'case_title'),(169,177,'ref_question'),(177,181,'ref_plan'),(181,184,'ref_tasks'),(184,196,'msd'),(196,203,'analysis'),(203,213,'limits'),(213,225,'case_recap'),
 (225,231,'structure'),(231,239,'bands'),(239,245,'pdosdetail'),(245,252,'properties'),
 (252,260,'design_open'),(260,270,'design_compare'),(270,281,'design'),
 (281,289,'value'),(289,294,'brand'),(294,300,'outro')]
def txt(im,xy,s,n=30,col=INK,b=False,anchor=None):l.txt(im,xy,s,n,col,b,anchor)
def chrome(im,title,sub='',tag='ABACUSLab'):
    l.chrome(im,title,sub,tag)
def rounded(im,box,fill='white',edge='#dce4f4'):l.panel(im,box,fill,edge)
@lru_cache(96)
def prepared(key,w,h):return ImageOps.contain(IMG[key],(w,h),Image.Resampling.LANCZOS)
def panel(im,key,box,t=3,delay=0):
    x,y,w,h=box;dy=round(18*(1-l.ease((t-delay)/.85)));y+=dy
    rounded(im,(x,y,x+w,y+h));p=prepared(key,w-32,h-32);im.paste(p,(round(x+(w-p.width)/2),round(y+(h-p.height)/2)))
def lines(im,x,y,rows,n=32,gap=65,col=MUTED):
    for i,s in enumerate(rows):txt(im,(x,y+i*gap),s,n,col)
def notes(im,rows,y=500):
    for i,s in enumerate(rows):
        l.pill(im,106,y+i*90,s)
def source_note(im,s):txt(im,(1810,970),s,20,MUTED,anchor='ra')
def frame_reference(t):
    raw=subprocess.check_output([FF,'-v','error','-ss',str(t),'-i',str(l.REFERENCE),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
    return Image.open(io.BytesIO(raw)).convert('RGB')
def prepare_reference():
    p=ROOT/'素材/参考片帧';p.mkdir(exist_ok=True)
    if len(list(p.glob('frame_*.jpg')))<(39-19)*15:
        subprocess.run([FF,'-v','error','-y','-ss','19','-i',str(l.REFERENCE),'-t','20','-vf','fps=15','-q:v','2',str(p/'frame_%04d.jpg')],check=True)
    for key,t,box in [('refq',22,(.20,.215,.80,.92)),('refplan',30,(.205,.22,.80,.925)),('reftask',37,(.045,.32,.955,.91))]:
        im=frame_reference(t);im=im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box)));im.save(ROOT/f'素材/{key}.png')
    print('REFERENCE_READY',flush=True)
for key in ['refq','refplan','reftask']:
    path=ROOT/f'素材/{key}.png'
    if path.exists():IMG[key]=Image.open(path).convert('RGB')
@lru_cache(12)
def ref_frame(tick,kind):
    idx=max(1,min(300,tick+1));path=ROOT/f'素材/参考片帧/frame_{idx:04d}.jpg';im=Image.open(path).convert('RGB')
    box={'ref_question':(.20,.215,.80,.92),'ref_plan':(.205,.22,.80,.925),'ref_tasks':(.045,.32,.955,.91)}[kind]
    im=im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box)))
    return ImageOps.contain(im,(1232,580),Image.Resampling.LANCZOS)
def scene(kind,t,dur):
    if kind in ['space','research','crystal','ai','design']:
        im={'space':l.space,'research':l.research,'crystal':l.crystal,'ai':l.ai,'design':l.design}[kind](t,dur)
        im.paste(l.BG.crop((0,989,W,H)),(0,989));return im
    im=l.background()
    if kind=='opening':
        txt(im,(100,65),'ABACUSLab',28,BLUE,True);txt(im,(105,290),'新材料的发现与设计',67,INK,True)
        lines(im,110,413,['从微观结构','走向更广阔的研究空间'],39,76);l.atoms(im,t,1430,585,105,'fcc',12)
        l.pill(im,110,665,'MATERIALS × AI');return im
    if kind=='fields':
        chrome(im,'材料创新，连接不同领域','探索组成与结构，寻找性能更优的材料','材料研究')
        for i,(title,sub,model) in enumerate([('能源材料','能量转换与存储','layer'),('半导体','电子性质与器件','fcc'),('结构材料','结构与性能','cube')]):
            x=96+i*588;rounded(im,(x,355,x+552,924));l.atoms(im,t,x+276,574,62,model,dur)
            txt(im,(x+276,785),title,42,INK,True,'mm');txt(im,(x+276,854),sub,28,MUTED,anchor='mm')
        source_note(im,'材料领域与结构概念示意');return im
    if kind=='questions':
        chrome(im,'材料研究，始于关键问题','在原子与电子尺度寻找解释','研究挑战')
        for i,(a,b) in enumerate([('理解机制','结构如何影响行为？'),('预测性能','性质如何随条件变化？'),('探索设计','下一步值得研究什么？')]):
            x=96+i*588;rounded(im,(x,402,x+552,786));l.icon(im,i,x+75,480);txt(im,(x+40,568),a,48,INK,True);txt(im,(x+42,659),b,29,MUTED)
        return im
    if kind=='firstprinciples':
        chrome(im,'以物理规律，连接结构与性质','第一性原理计算，为材料研究提供依据','科学计算')
        l.atoms(im,t,450,619,80,'fcc',dur);panel(im,'band',(949,341,808,597),t)
        txt(im,(760,612),'→',64,BLUE,True);source_note(im,'结构概念示意 / 历史电子结构图表');return im
    if kind in ['brand','outro','brand_credit']:
        im=l.brand(t,10)
        if kind=='brand_credit':
            im.paste(l.BG.crop((90,715,1050,980)),(90,715));txt(im,(116,742),'开发单位',25,MUTED)
            txt(im,(116,795),'合肥综合性国家科学中心',34,INK,True);txt(im,(116,850),'人工智能研究院',34,INK,True)
        elif kind=='outro':
            im.paste(l.BG.crop((90,320,1050,930)),(90,320));txt(im,(106,342),'ABACUSLab',104,BLUE,True)
            txt(im,(115,510),'让材料计算更简单',57,INK,True);txt(im,(117,634),'把更多精力，留给研究与发现',32,MUTED)
        return im
    if kind=='abacus_credit':
        chrome(im,'ABACUS · 专业计算核心','将计算能力、标准流程与人工智能连接起来','平台能力')
        txt(im,(105,412),'ABACUS',92,BLUE,True);lines(im,112,558,['国产开源第一性原理计算软件','中国科学技术大学团队牵头研发'],30,65)
        panel(im,'template0',(1165,344,575,578),t);return im
    if kind in ['home','templates','workflow']:
        titles={'home':'一个平台，连接材料计算与分析','templates':'专业计算模板，覆盖常见研究需求','workflow':'工作流与任务进展，集中查看'}
        chrome(im,titles[kind],{'home':'专业计算 · 标准流程 · 智能辅助','templates':'结构优化 · 电子结构 · 分子动力学 · 材料物性','workflow':'从整体进展到关键步骤'}[kind],'平台实际界面')
        panel(im,'homebody' if kind=='home' else kind,(100,337,1720,610),t);return im
    if kind=='reuse':
        chrome(im,'将计算方法，组织为可复用的流程','选择模板，调整方案，再次用于研究任务','工作流')
        for i in range(3):
            panel(im,f'template{i}',(110+i*590,353,520,551),t,i*.16)
        return im
    if kind=='project':
        chrome(im,'围绕研究目标，组织计算任务','让运行状态与执行记录清晰可见','任务管理')
        panel(im,'workflow',(710,350,1110,590),t);txt(im,(105,430),'项目有序',61,INK,True);txt(im,(109,533),'任务可追踪',49,BLUE,True)
        notes(im,['集中查看状态','检查关键步骤'],666);return im
    if kind=='config':
        chrome(im,'参数配置，衔接计算准备','结构转换 · 输入文件 · 计算设置','工具协同')
        panel(im,'config',(855,321,883,631),t);txt(im,(105,448),'准备更顺畅',60,INK,True);notes(im,['输入文件准备','可视化参数配置'],588);return im
    if kind in ['pdos','optical','pdosdetail']:
        key='optical' if kind=='optical' else 'pdos';title='从光学响应，理解数据变化' if key=='optical' else '电子态密度，呈现计算特征'
        chrome(im,title,'保留真实图表，让结果清楚可读','物性分析')
        panel(im,key,(626,330,1184,619),t);txt(im,(105,435),'观察变化',59,INK,True);txt(im,(109,532),'理解差异',49,BLUE,True)
        notes(im,['可视化结果','支持进一步分析'],676);source_note(im,'平台已有图表');return im
    if kind=='aihero':
        chrome(im,'研究，也可以从一句话开始','ABACUSLab AI 智能体','AI 辅助')
        txt(im,(115,430),'描述目标',76,INK,True);txt(im,(120,555),'连接研究下一步',47,BLUE,True)
        rounded(im,(1150,367,1725,881));txt(im,(1437,590),'AI',170,BLUE,True,'mm');txt(im,(1437,775),'研究目标 · 计算思路',29,MUTED,anchor='mm');return im
    if kind=='prompt_general':
        chrome(im,'用自然语言，描述研究需求','从目标、条件与问题开始','AI 交互')
        panel(im,'question',(1125,325,660,624),t);rounded(im,(105,390,1055,805))
        txt(im,(145,433),'研究目标示例',24,BLUE,True);lines(im,145,517,['我想比较材料在不同条件下的性质，','应该如何设计计算与分析流程？'],35,76,INK)
        txt(im,(146,725),'梳理条件 → 规划方案 → 研究人员确认',26,MUTED);return im
    if kind=='review':
        chrome(im,'让 AI 辅助，与专业判断结合','检查条件，调整方案，再进入下一步','研究人员确认')
        panel(im,'completebody',(1045,326,725,614),t);txt(im,(109,401),'研究人员始终参与',49,INK,True)
        notes(im,['检查研究条件','调整计算方案','结合原始结果判断'],541);return im
    if kind=='case_title':
        chrome(im,'案例一｜铝合金熔化行为研究','从研究目标到计算、图表与分析','研究场景')
        txt(im,(108,434),'不同温度',66,INK,True);txt(im,(110,544),'不同原子运动特征',49,BLUE,True)
        lines(im,114,687,['用计算组织问题','用图表观察差异'],29,65);l.atoms(im,t,1410,623,91,'fcc',dur)
        source_note(im,'结构概念动画 / 参考片案例展示');return im
    if kind in ['ref_question','ref_plan','ref_tasks']:
        title={'ref_question':'从一句话，开始材料计算','ref_plan':'AI 辅助梳理计算思路','ref_tasks':'计算任务与温度条件，清晰可见'}[kind]
        chrome(im,title,'铝合金熔化行为研究','参考片案例')
        if kind=='ref_question':ref_t=19+min(t,7.9);label=['描述研究目标','明确关注问题']
        elif kind=='ref_plan':ref_t=28+min(t,3.9);label=['梳理计算步骤','确认所需条件']
        else:ref_t=37;label=['300 K / 1600 K','分子动力学任务']
        pic=ref_frame(round((ref_t-19)*15),kind);rounded(im,(556,332,1820,944));im.paste(pic,(round(1188-pic.width/2),round(638-pic.height/2)))
        txt(im,(105,444),label[0],38,INK,True);txt(im,(110,536),label[1],30,BLUE,True)
        source_note(im,'沿用用户参考片画面');return im
    if kind=='msd':
        im=l.aluminum(t,dur);im.paste(l.BG.crop((0,989,W,H)),(0,989))
        source_note(im,'平台图表功能示例');return im
    if kind=='analysis':
        chrome(im,'分析图表，归纳主要特征','理解变化，同时明确结论的适用范围','结果分析')
        panel(im,'conclusion',(844,326,925,623),t);notes(im,['归纳主要变化','解释可能含义','提出验证方向'],421)
        source_note(im,'平台已有分析截图');return im
    if kind=='limits':
        chrome(im,'少数温度点，不等于精确熔点','进一步扫描温度，并结合体系与计算设置验证','后续验证')
        panel(im,'msd',(812,333,1012,612),t);notes(im,['扩大温度扫描','复核原始数据','确认体系与设置'],441)
        source_note(im,'平台图表功能示例');return im
    if kind=='case_recap':
        chrome(im,'把计算结果，转化为探索依据','方案组织 → 数据可视化 → 结果分析','铝合金研究场景')
        for i,(key,s) in enumerate([('refq','提出目标'),('reftask','组织计算'),('msd','图表与分析')]):
            x=96+i*588;panel(im,key,(x,365,552,482),t,i*.1);txt(im,(x+276,905),s,33,BLUE,True,'mm')
        return im
    if kind=='structure':
        chrome(im,'案例二｜电子结构与物性分析','从材料结构到计算结果','电子结构')
        panel(im,'structbody',(704,326,1114,620),t);txt(im,(108,426),'连接微观结构',53,INK,True);notes(im,['电子性质','计算与分析流程'],591)
        source_note(im,'历史结构展示界面');return im
    if kind=='bands':
        chrome(im,'能带结构与态密度，呈现电子性质','从已有结果观察差异，探索微观结构与性能的联系','图表功能示例')
        panel(im,'band',(100,339,900,610),t);panel(im,'pdos',(1050,339,770,610),t,.12)
        source_note(im,'不同图表功能示例');return im
    if kind=='properties':
        chrome(im,'从计算数据，提取研究信息','理解性质 · 探索机制 · 支持后续研究','物性分析')
        panel(im,'pdosfull',(100,337,1115,610),t);panel(im,'optical',(1260,389,560,507),t,.1);return im
    if kind=='design_open':
        chrome(im,'从材料计算，走向材料设计','计算的价值，在于支持更有依据的探索','设计探索')
        txt(im,(105,427),'发现 · 筛选 · 设计',56,INK,True);lines(im,111,550,['结合物理规律','比较结果，明确下一步方向'],34,78)
        l.atoms(im,t,1430,637,91,'fcc',dur);source_note(im,'结构概念示意');return im
    if kind=='design_compare':
        chrome(im,'让比较有依据，让设计有方向','候选结构与计算结果，需要在可比条件下研究','设计流程示意')
        for i,(title,sub,kind2) in enumerate([('候选结构','组成与排列','fcc'),('关键性质','计算与分析','layer'),('下一轮方案','复核与优化','cube')]):
            x=96+i*588;rounded(im,(x,355,x+552,932));l.atoms(im,t,x+276,575,61,kind2,dur);txt(im,(x+276,790),title,39,INK,True,'mm');txt(im,(x+276,862),sub,27,MUTED,anchor='mm')
        source_note(im,'设计概念示意');return im
    if kind=='value':
        chrome(im,'让智能辅助，贯穿材料研究','AI 智能辅助 + 第一性原理计算 + 科学判断','ABACUSLab')
        for i,(key,s) in enumerate([('templates','专业计算'),('workflow','流程与任务'),('msd','图表分析')]):
            x=96+i*588;panel(im,key,(x,365,552,480),t,i*.12);txt(im,(x+276,909),s,34,BLUE,True,'mm')
        return im
    raise ValueError(kind)
@lru_cache(48)
def end_frame(i):
    a,b,k=SHOTS[i];return scene(k,b-a-.04,b-a)
def frame(t):
    i=next((i for i,(a,b,k) in enumerate(SHOTS) if a<=t<b),len(SHOTS)-1);a,b,k=SHOTS[i];local=t-a
    im=scene(k,local,b-a)
    if i and local<.55:im=Image.blend(end_frame(i-1),im,l.ease(local/.55))
    return im
def previews():
    sheet=Image.new('RGB',(1600,math.ceil(len(SHOTS)/4)*252),'#f5f7fe')
    for i,(a,b,k) in enumerate(SHOTS):
        im=frame(min(a+3,b-.5));im.save(STILL/f'{i+1:02d}_{a:03d}_{k}.jpg',quality=94);thumb=im.resize((392,220),Image.Resampling.LANCZOS)
        x=(i%4)*400;y=(i//4)*252;sheet.paste(thumb,(x+4,y));txt(sheet,(x+8,y+222),f'{a//60:02d}:{a%60:02d}–{b//60:02d}:{b%60:02d} {k}',17)
    sheet.save(ROOT/'五分钟分镜总览.jpg',quality=94)
    (WORK/'镜头时间线.json').write_text(json.dumps(SHOTS,ensure_ascii=False,indent=2),encoding='utf-8')
    print('STORYBOARD_READY',len(SHOTS),flush=True)
def picture():
    cmd=[FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','6','-movflags','+faststart',str(WORK/'picture.mp4')]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.time()
    try:
        for n in range(DUR*FPS):
            proc.stdin.write(frame(n/FPS).tobytes())
            if n%450==0:print(f'PICTURE {n/FPS:.0f}/{DUR}s | {time.time()-start:.1f}s elapsed',flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('picture encode failed')
    print('PICTURE_READY',flush=True)
def final():
    # Run with WORK as cwd so FFmpeg subtitle escaping is independent of Windows drive letters.
    args=[FF,'-v','error','-y','-i','picture.mp4','-i','mixed.wav','-vf','ass=captions.ass','-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','30','-af','loudnorm=I=-17:TP=-2:LRA=9,aresample=48000','-ar','48000','-c:a','aac','-b:a','192k','-t','300','-movflags','+faststart',str(DEST)]
    subprocess.run(args,cwd=str(WORK),check=True);print('FINAL_READY',str(DEST),flush=True)
def verify():
    meta=subprocess.run([FF,'-hide_banner','-i',str(DEST)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
    assert all(s in meta for s in ['1920x1080','30 fps','h264','aac']),meta
    dec=subprocess.run([FF,'-v','error','-i',str(DEST),'-f','null','-'],capture_output=True,text=True);assert dec.returncode==0 and not dec.stderr,dec.stderr
    pcm=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(DEST),'-vn','-ar','48000','-ac','2','-f','f32le','pipe:1']),np.float32).reshape(-1,2)
    duration=len(pcm)/48000;assert abs(duration-300)<.05;peak=float(abs(pcm).max());assert peak<.98
    report={'duration_seconds':duration,'width':1920,'height':1080,'fps':30,'decode_errors':0,'audio_peak':peak,'size_mb':round(DEST.stat().st_size/1048576,1),'shots':len(SHOTS),'chapters':8,'subtitles':'burned-in Chinese plus external SRT','voice':'zh-CN-YunjianNeural','voice_speed':1.0,'source_note':'用户原稿、截图、参考片及原创概念动画；不含伪造研究数据'}
    (ROOT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
    times=[2,8,17,25,32,40,48,56,64,72,81,91,100,108,116,122,127,133,140,149,158,166,173,179,182,190,200,208,219,228,235,242,248,256,266,276,285,291,297]
    sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*252),'#f5f7fe')
    for i,t in enumerate(times):
        raw=subprocess.check_output([FF,'-v','error','-ss',str(t),'-i',str(DEST),'-frames:v','1','-vf','scale=392:220','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);im=Image.frombytes('RGB',(392,220),raw)
        x=i%4*400;y=i//4*252;sheet.paste(im,(x+4,y));txt(sheet,(x+10,y+223),f'{t//60:02d}:{t%60:02d}',18)
    sheet.save(ROOT/'成片实际画面核验.jpg',quality=94);print('VISUAL_CHECK_READY',flush=True)
if __name__=='__main__':
    {'prepare':prepare_reference,'previews':previews,'picture':picture,'final':final,'verify':verify}[sys.argv[1] if len(sys.argv)>1 else 'previews']()
