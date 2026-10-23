"""V19: stable opening, source-level recut, distinct chapter roles and requested brand art."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import importlib.util,json,sys,math,subprocess,time,io,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageOps,ImageFilter
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent;WORK=ROOT/'制作文件';PREV=BASE/'交付_V18_五分钟_按方案实景重制'
s=importlib.util.spec_from_file_location('v18',PREV/'制作文件/build_v18.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
l=v.l;FF=v.FF;W,H,FPS=1920,1080,30;PAPER=v.PAPER;BLUE=v.BLUE;INK=v.INK;MUTED=v.MUTED
DEST=ROOT/'ABACUSLab_V19_五分钟_去重稳定重剪版.mp4'
IMG=dict(v.v.IMG)
MAN=BASE/'宣传片方案_210秒_20261019/04_平台截图素材/用户手册历史截图'
RAW=BASE/'宣传片方案_210秒_20261019/05_用户新截图筛选/原图留档_不代表选用'
for key,file in [('projectlist','01_项目管理.png'),('template_detail','04_模板详情.png'),('workflow_detail','06_工作流详情.png'),('task_output','07_任务输出.png'),('convert','08_结构转换.png'),('dos_manual','11_态密度绘制.png')]:IMG[key]=Image.open(MAN/file).convert('RGB')
for key,file in [('bandflow','05_能带流程.png'),('inputadvanced','08_INPUT高级参数.png')]:IMG[key]=Image.open(RAW/file).convert('RGB')
IMG['dashboard']=Image.open(BASE.parent/'4a7dc3e3-6164-4d4f-962f-5af30c7c468d.png').convert('RGB')
def crop(key,rect):
    im=IMG[key];return im.crop(tuple(round(a*(im.width if i%2==0 else im.height)) for i,a in enumerate(rect)))
IMG['ai_input']=crop('question',(.032,.018,.922,.992))
IMG['ai_feedback']=crop('complete',(.05,.035,.86,.79))
IMG['workflow_body']=crop('workflow',(.105,.06,.99,.94))
IMG['config_body']=crop('config',(.18,.06,.97,.95))
IMG['task_body']=crop('task',(.07,.07,.97,.94))
IMG['project_body']=crop('projectlist',(.105,.06,.99,.9))
IMG['template_body']=crop('template_detail',(.105,.06,.99,.93))
IMG['convert_body']=crop('convert',(.105,.06,.99,.95))
IMG['dashboard_body']=crop('dashboard',(.10,.055,.99,.92))
IMG['bandflow_body']=crop('bandflow',(.10,.06,.99,.94))
IMG['advanced_body']=crop('inputadvanced',(.19,.12,.98,.94))
IMG['pyatb_body']=crop('pyatb',(.105,.065,.99,.76))
IMG['dos_body']=crop('dos_manual',(.105,.065,.99,.95))
SOURCE={x['key']:x for x in json.loads((WORK/'原始镜头索引.json').read_text(encoding='utf-8'))}
# Each visual source has one continuous treatment. Final recap is a labelled composite, not replay.
SHOTS=[
 (0,4,'concept','G01','新材料的发现与设计','能源材料'),
 (4,7,'concept','G02','新材料的发现与设计','半导体'),
 (7,10,'concept','G03','新材料的发现与设计','先进结构材料'),
 (10,22,'candidate_intro','G04','材料空间广阔','组成与排列，打开不同的研究方向'),
 (22,25,'concept','G05','研发周期长，试错成本高','材料制备'),
 (25,27.5,'concept','G06','研发周期长，试错成本高','实验表征'),
 (27.5,30,'concept','G07','研发周期长，试错成本高','性能测试'),
 (30,32,'concept','G08','研发周期长，试错成本高','调整方案，再次验证'),
 (32,35,'concept','G09','理解机制 · 预测性能 · 探索设计','微观原子结构'),
 (35,38,'concept','G10','理解机制 · 预测性能 · 探索设计','电子行为'),
 (38,43,'concept','G11','从原子与电子层面研究材料','第一性原理计算，提供物理依据'),
 (43,50,'screen','pyatb_body','连接微观结构与专业计算','ABACUS · 国产开源第一性原理计算软件'),
 (50,56,'brand','login_brand','ABACUSLab','AI 驱动的材料计算与设计平台'),
 (56,60,'screen','homebody','一个平台，连接材料研究','专业计算 · AI 智能体 · 标准化工作流程'),
 (60,70,'capabilities','capabilities','让智能辅助，与专业计算结合','研究人员检查与调整，平台组织计算与分析'),
 (70,78,'screen','templates','专业计算模板','结构优化 · 电子结构 · 分子动力学 · 材料物性'),
 (78,85,'screen','template_body','从研究目标，选择计算方法','模板说明与计算步骤'),
 (85,95,'screen','bandflow_body','将基础计算组织成可复用流程','多步骤计算 · 条件配置 · 方法复用'),
 (95,100,'screen','project_body','按项目组织研究任务','围绕研究目标，积累计算记录'),
 (100,105,'screen','task_body','任务进展，集中管理','查看状态，检查关键环节'),
 (105,108,'screen','convert_body','结构转换与输入准备','连接不同计算环节'),
 (108,111,'screen','config_body','计算参数，可视化配置','核对输入设置'),
 (111,115,'result_overview','results_overview','计算结果，转化为直观图表','态密度 · 光学响应 · 结果分析'),
 (115,125,'ai_input','ai_input','用自然语言，描述研究需求','AI 智能体 · 真实交互界面'),
 (125,135,'raw','ai_conditions','从研究目标，梳理条件与步骤','材料体系 · 计算条件 · 待确认问题'),
 (135,145,'feedback','ai_feedback','让计算任务与结果入口衔接','查看反馈，回到具体任务核对'),
 (145,155,'raw','ai_review','检查与调整，让研究判断始终参与','AI 提供辅助，研究人员决定下一步'),
 (155,165,'raw','case_question','案例一｜铝合金熔化行为研究','描述研究目标，明确关注问题'),
 (165,175,'raw','case_plan','梳理计算思路，核对所需条件','温度条件 · 计算参数 · 任务组织'),
 (175,178,'raw','case_task','分子动力学任务','查看执行状态'),
 (178,190,'motion','motion','观察不同状态下的原子运动','概念动画 · 非实际轨迹'),
 (190,205,'msd','msd','不同温度下的均方位移（MSD）','比较曲线差异，保留结论边界'),
 (205,215,'analysis','analysis','归纳主要特征，提出验证方向','AI 分析与后续建议'),
 (215,225,'electronic','electronic_setup','案例二｜电子结构与物性分析','从结构模型，到电子结构计算'),
 (225,235,'band','band','能带结构','观察电子能量随波矢的变化'),
 (235,250,'pdos','pdos','电子态密度与物性分析','观察态分布，结合材料体系理解物理意义'),
 (250,260,'design_candidates','design_new','从材料计算，走向材料设计','组成 · 结构 · 研究目标'),
 (260,270,'design_criteria','design_criteria','比较有依据，设计才有方向','在可比条件下，研究影响性质的关键因素'),
 (270,280,'design_path','design_path','计算 · 分析 · 验证','让结果成为下一轮研究的依据'),
 (280,287,'recap','recap','AI 智能辅助 + 第一性原理计算 + 科学判断','把不同环节，连接成完整的研究过程'),
 (287,300,'closing','closing','ABACUSLab','让材料计算更简单')]

def txt(im,xy,s,n=30,col=INK,b=False,anchor=None):l.txt(im,xy,s,n,col,b,anchor)
def bg():return Image.new('RGB',(W,H),PAPER)
def header(im,title,sub='',tag='ABACUSLab'):
    txt(im,(86,45),'ABACUSLab',29,BLUE,True);txt(im,(1834,57),tag,20,MUTED,anchor='ra')
    ImageDraw.Draw(im).line((86,103,1834,103),fill='#dce4f4',width=2)
    n=min(53,int(1740/max(1,l.font(53,True).getlength(title))*53))
    txt(im,(86,132),title,n,INK,True)
    if sub:txt(im,(89,208),sub,27,MUTED)
def note(im,s):txt(im,(1833,972),s,19,MUTED,anchor='ra')

@lru_cache(64)
def prepared(key,w,h):return ImageOps.contain(IMG[key],(w,h),Image.Resampling.LANCZOS)
def screenshot(im,key,box=(94,278,1732,674)):
    x,y,w,h=box;p=prepared(key,w,h);im.paste(p,(x+(w-p.width)//2,y+(h-p.height)//2))

@lru_cache(16)
def concept_layer(key,box):
    im=bg()
    if key=='design_new':
        src=Image.open(ROOT/'素材/设计候选_新构图.png').convert('RGBA');arr=np.array(src)
        shadow=(arr[:,:,:3].max(axis=2)<80)&(arr[:,:,3]<250);arr[:,:,3][shadow]=(arr[:,:,3][shadow]*.3).astype('uint8')
        src=Image.fromarray(arr).crop((180,130,1735,990));src=ImageOps.contain(src,(box[2],box[3]),Image.Resampling.LANCZOS)
        im.paste(src,(box[0]+(box[2]-src.width)//2,box[1]+(box[3]-src.height)//2),src)
    else:v.add_concept(im,key,0,1,box,0)
    return im
def concept(im,key,box=(120,275,1680,680)):
    # Fixed source raster and fixed paste coordinates: no rounded per-frame scaling.
    im.paste(concept_layer(key,box),(0,0))

@lru_cache(2)
def brand_base(closing=False):
    source=ImageOps.fit(Image.open(ROOT/'素材/登录页原始背景.png').convert('RGB'),(W,H),method=Image.Resampling.LANCZOS)
    if closing:
        white=Image.new('RGB',(W,H),PAPER);return Image.blend(source,white,.76)
    x=np.arange(W,dtype=np.float32);alpha=.06+.90/(1+np.exp((x-760)/190))
    veil=Image.new('RGBA',(W,H),'#123353');veil.putalpha(Image.fromarray(np.broadcast_to((alpha*255).astype('uint8'),(H,W)).copy()))
    source.paste(veil,(0,0),veil)
    card=Image.open(ROOT/'素材/登录卡片.png').convert('RGBA');card=ImageOps.contain(card,(415,600),Image.Resampling.LANCZOS)
    shadow=Image.new('RGBA',(card.width+70,card.height+70));ImageDraw.Draw(shadow).rounded_rectangle((25,25,25+card.width,25+card.height),12,fill=(20,40,60,60));shadow=shadow.filter(ImageFilter.GaussianBlur(18))
    source.paste(shadow,(998,192),shadow);source.paste(card,(1023,217),card)
    txt(source,(87,178),'MATERIALS × AI',25,'#bcdcf6',True)
    txt(source,(81,262),'ABACUSLab',106,'white',True)
    txt(source,(87,430),'AI 驱动的材料计算',48,'white',True)
    txt(source,(87,505),'与设计平台',48,'white',True)
    ImageDraw.Draw(source).line((88,635,690,635),fill='#b5cfe4',width=2)
    txt(source,(88,691),'让材料计算更简单',33,'#d5e6f4',True)
    txt(source,(88,843),'开发单位',21,'#cbdceb')
    txt(source,(88,887),'合肥综合性国家科学中心人工智能研究院',26,'#e8f1f9')
    return source

@lru_cache(16)
def rawframe(key,index):
    meta=SOURCE[key];im=Image.open(ROOT/'素材'/key/f'{index:04d}.jpg').convert('RGB')
    rect=tuple(round(a*(W if i%2==0 else H)) for i,a in enumerate(meta['crop']))
    return ImageOps.contain(im.crop(rect),(1450,675),Image.Resampling.LANCZOS)
def raw(im,key,t,dur):
    m=SOURCE[key]
    # Native 30 fps; play each source once, then hold the last frame for reading.
    tick=min(m['frames'],max(1,int(t*30)+1));p=rawframe(key,tick)
    im.paste(p,((W-p.width)//2,278+(675-p.height)//2))

def bullet(im,x,y,title,body,index=None):
    if index is not None:txt(im,(x,y),f'{index:02d}',26,BLUE,True)
    txt(im,(x+(58 if index else 0),y),title,32,INK,True)
    txt(im,(x+(58 if index else 0),y+57),body,25,MUTED)

def steps(im,labels,t,subtitles=None):
    n=len(labels);width=1700/n;d=ImageDraw.Draw(im)
    for j,label in enumerate(labels):
        x=110+j*width;active=min(n-1,int(t/2))
        col=BLUE if j<=active else '#9ba9bf'
        d.ellipse((x+width/2-30,463,x+width/2+30,523),fill=col)
        txt(im,(x+width/2,493),str(j+1),26,'white',True,'mm')
        txt(im,(x+width/2,590),label,34,INK,True,'mm')
        if subtitles:txt(im,(x+width/2,659),subtitles[j],24,MUTED,anchor='mm')
        if j<n-1:d.line((x+width/2+47,493,x+1.5*width-47,493),fill='#b8c7e4',width=3)

def scene(i,t):
    a,b,mode,key,title,sub=SHOTS[i];dur=b-a;im=bg();tag='平台实际画面'
    if mode in ['concept','candidate_intro','design_candidates']:
        concept(im,key);tag='概念示意'
        if mode=='candidate_intro':
            for j,label in enumerate(['不同组成','不同排列','不同局域环境']):txt(im,(390+j*570,921),label,28,BLUE,True,'mm')
        if mode=='design_candidates':
            for j,label in enumerate(['基准结构','组成变化','局域缺陷']):txt(im,(400+j*565,926),label,27,BLUE,True,'mm')
            tag='候选比较思路示意'
    elif mode=='screen':screenshot(im,key)
    elif mode=='brand':return brand_base().copy()
    elif mode=='capabilities':
        steps(im,['研究目标','AI 辅助','专业计算','结果分析'],t,['描述需求','梳理方案','标准流程','科学判断']);tag='平台能力'
        txt(im,(960,817),'ABACUS：由中国科学技术大学团队牵头研发的国产开源软件',26,MUTED,anchor='mm')
    elif mode=='result_overview':
        screenshot(im,'pdosfull',(96,300,850,600));screenshot(im,'optical',(1010,300,810,600))
        txt(im,(960,931),'结果可视化入口概览',25,MUTED,anchor='mm')
    elif mode=='ai_input':
        screenshot(im,key,(650,280,1160,665))
        bullet(im,105,400,'描述研究目标','用自然语言提出问题',1)
        bullet(im,105,575,'补充必要条件','材料体系、关注性质',2)
        note(im,'已有真实对话截图')
    elif mode=='raw':raw(im,key,t,dur)
    elif mode=='feedback':
        screenshot(im,key,(570,282,1210,664))
        bullet(im,98,390,'查看任务反馈','检查执行结果',1)
        bullet(im,98,565,'衔接绘图入口','核对所需文件',2)
    elif mode=='motion':v.atom_motion(im,t);tag='原子运动概念动画'
    elif mode=='msd':
        screenshot(im,'msd',(450,289,1375,665))
        bullet(im,95,397,'比较曲线','观察时间变化')
        bullet(im,95,593,'继续验证','扫描更多温度点')
        if t>7:txt(im,(960,955),'少数温度点不足以精确确定熔点',26,BLUE,True,'mm')
    elif mode=='analysis':
        screenshot(im,'analysis',(530,282,1250,664))
        bullet(im,95,373,'归纳变化','提取主要特征',1)
        bullet(im,95,554,'明确边界','结合体系与设置',2)
        bullet(im,95,735,'后续验证','检查原始数据',3)
    elif mode=='electronic':
        screenshot(im,'structbody',(86,302,970,600));screenshot(im,'task_output',(1115,299,700,610))
        txt(im,(570,936),'结构展示',28,BLUE,True,'mm');txt(im,(1458,936),'计算输出',28,BLUE,True,'mm')
    elif mode=='band':
        screenshot(im,'band',(600,277,1150,682))
        bullet(im,94,405,'能量与波矢','观察能带的分布')
        bullet(im,94,608,'连接物理理解','结合体系解释特征')
        note(im,'已有能带图表 · 功能示例')
    elif mode=='pdos':
        screenshot(im,'pdos',(585,278,1230,676))
        bullet(im,94,400,'电子态分布','观察能量范围与峰形')
        bullet(im,94,595,'结果与条件','结合材料体系与设置')
        if t>7:txt(im,(105,824),'从图表走向科学信息',30,BLUE,True)
        note(im,'已有态密度图表 · 功能示例')
    elif mode=='design_criteria':
        # Research criteria, deliberately no invented candidate performance data.
        titles=['结构与组成','计算条件','性质与目标'];bodies=['比较候选的差异','保持参数与方法可比','明确筛选依据']
        for j in range(3):
            x=145+j*580
            txt(im,(x,380),f'0{j+1}',72,'#c6d4ed',True)
            txt(im,(x,495),titles[j],40,INK,True)
            txt(im,(x,589),bodies[j],28,MUTED)
            ImageDraw.Draw(im).line((x,680,x+430,680),fill='#cdd8ea',width=2)
        txt(im,(960,827),'同条件比较 → 识别关键因素 → 选择验证方向',30,BLUE,True,'mm');tag='设计方法示意'
    elif mode=='design_path':
        steps(im,['候选结构','计算验证','结果比较','进一步优化'],t,['设定研究问题','检查物理与参数','寻找差异与原因','规划下一轮研究'])
        txt(im,(960,828),'研究人员结合物理规律，作出下一步判断',30,BLUE,True,'mm');tag='设计流程示意'
    elif mode=='recap':
        for j,(k,label) in enumerate([('ai_input','描述目标'),('templates','专业计算'),('workflow','任务管理'),('msd','结果分析')]):
            x=90+(j%2)*900;y=282+(j//2)*330;screenshot(im,k,(x,y,835,265));txt(im,(x+417,y+290),label,27,BLUE,True,'mm')
        tag='平台能力回顾'
    elif mode=='closing':
        im=brand_base(True).copy()
        txt(im,(960,311),'ABACUSLab',108,BLUE,True,'mm')
        txt(im,(960,465),'AI 驱动的材料计算与设计平台',43,INK,True,'mm')
        if t>4:
            txt(im,(960,625),'让材料计算更简单',55,INK,True,'mm')
            txt(im,(960,733),'把更多精力，留给研究与发现。',34,MUTED,anchor='mm')
        return im
    header(im,title,sub,tag);return im

@lru_cache(8)
def end_frame(i):return scene(i,SHOTS[i][1]-SHOTS[i][0]-.01)
def frame(t):
    i=next((j for j,s in enumerate(SHOTS) if s[0]<=t<s[1]),len(SHOTS)-1)
    local=t-SHOTS[i][0];im=scene(i,local)
    fade=.55 if SHOTS[i][0]<50 else .35
    if i and local<fade:im=Image.blend(end_frame(i-1),im,l.ease(local/fade))
    return im

def audit():
    assert SHOTS[0][0]==0 and SHOTS[-1][1]==300
    assert all(SHOTS[i][1]==SHOTS[i+1][0] for i in range(len(SHOTS)-1))
    keys=[s[3] for s in SHOTS];duplicates={k:n for k,n in Counter(keys).items() if n>1};assert not duplicates,duplicates
    # Verify the complaint at source-frame level: no unwanted transform motion within opening holds.
    stability=[]
    for i,s in enumerate(SHOTS):
        if s[0]>=50:break
        if s[2] not in ['concept','candidate_intro']:continue
        frames=[np.asarray(scene(i,t),dtype=np.int16) for t in [.7,1.0,1.5]]
        delta=[float(np.abs(frames[j]-frames[j-1]).mean()) for j in range(1,len(frames))]
        assert max(delta)==0,(i,delta);stability.append({'start':s[0],'source':s[3],'mean_pixel_change':0})
    (WORK/'重复与稳定性检查.json').write_text(json.dumps({'shots':len(SHOTS),'duplicate_primary_sources':duplicates,'opening_stability':stability,'intentional_secondary_reuse':'111–115 秒为结果入口概览，280–287 秒为明确标识的功能回顾；不重播完整案例段','source_playback':'30 fps 原录屏各播放一次；短片尾帧停留便于阅读，不慢放复制帧'},ensure_ascii=False,indent=2),encoding='utf-8')
    print('AUDIT_PASS',len(SHOTS),len(stability),flush=True)

def previews():
    audit();folder=ROOT/'分镜预览';folder.mkdir(exist_ok=True)
    sheet=Image.new('RGB',(1600,math.ceil(len(SHOTS)/4)*252),PAPER)
    for i,s in enumerate(SHOTS):
        im=scene(i,min((s[1]-s[0])*.6,5));im.save(folder/f'{i+1:02d}_{s[0]:03.0f}.jpg',quality=94)
        sheet.paste(im.resize((392,220),Image.Resampling.LANCZOS),(i%4*400+4,i//4*252))
        txt(sheet,(i%4*400+8,i//4*252+222),f'{s[0]:05.1f}–{s[1]:05.1f} {s[3]}',16)
    sheet.save(ROOT/'V19_完整分镜总览.jpg',quality=94)
    (WORK/'镜头时间线.json').write_text(json.dumps(SHOTS,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PREVIEWS_READY',flush=True)

def render(start=0,end=300,dest=None):
    audit();dest=dest or DEST
    args=[FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-ss',str(start),'-i','mixed.wav','-vf',f'setpts=PTS+{start}/TB,ass=captions.ass,setpts=PTS-STARTPTS','-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','17','-threads','6','-pix_fmt','yuv420p','-af','loudnorm=I=-17:TP=-2:LRA=9,aresample=48000','-c:a','aac','-b:a','192k','-t',str(end-start),'-movflags','+faststart',str(dest)]
    proc=subprocess.Popen(args,cwd=WORK,stdin=subprocess.PIPE);beg=time.time()
    try:
        for n in range(round((end-start)*FPS)):
            proc.stdin.write(frame(start+n/FPS).tobytes())
            if n%450==0:print(f'RENDER {start+n/FPS:.0f}/{end}s | {time.time()-beg:.1f}s',flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('encode failed')
    print('VIDEO_READY',dest,flush=True)

def verify():
    meta=subprocess.run([FF,'-hide_banner','-i',str(DEST)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
    for s in ['1920x1080','30 fps','h264','aac','00:05:00.00']:assert s in meta,(s,meta)
    dec=subprocess.run([FF,'-v','error','-i',str(DEST),'-f','null','-'],capture_output=True,text=True);assert not dec.stderr and dec.returncode==0,dec.stderr
    audio=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(DEST),'-vn','-ar','48000','-ac','2','-f','f32le','pipe:1']),np.float32)
    dur=len(audio)/96000;peak=float(abs(audio).max());assert abs(dur-300)<.05 and peak<.98
    times=[1,5,8,15,23,26,29,31,33,36,40,46,53,58,65,74,82,90,97,102,106,109,113,119,130,140,150,159,169,176,184,197,210,219,230,243,255,265,275,284,289,297]
    sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*252),PAPER)
    for i,t in enumerate(times):
        out=subprocess.check_output([FF,'-v','error','-ss',str(t),'-i',str(DEST),'-frames:v','1','-vf','scale=392:220','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
        im=Image.frombytes('RGB',(392,220),out);sheet.paste(im,(i%4*400+4,i//4*252));txt(sheet,(i%4*400+8,i//4*252+222),f'{t//60:02d}:{t%60:02d}',18)
    sheet.save(ROOT/'V19_成片实帧核验.jpg',quality=94)
    report={'duration_seconds':dur,'resolution':'1920x1080','fps':30,'decode_errors':0,'peak_audio':peak,'shots':len(SHOTS),'duplicate_primary_shots':0,'size_mb':round(DEST.stat().st_size/1048576,1),'opening':'fixed composition, no per-frame resize','source_motion':'native 30 fps, no replay loops','brand':'user requested molecular login artwork','concept_animation':'MD motion is illustrative, not measured trajectory'}
    (ROOT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    for name,start,duration in [('开头与品牌预览_70秒',0,70),('中段去重预览_100秒',115,100)]:
        subprocess.run([FF,'-v','error','-y','-ss',str(start),'-i',str(DEST),'-t',str(duration),'-c:v','libx264','-preset','fast','-crf','18','-threads','4','-c:a','aac','-b:a','192k','-movflags','+faststart',str(ROOT/f'V19_{name}.mp4')],check=True)
    print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':
    cmd=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if cmd=='render':render()
    elif cmd=='sample':render(50,60,ROOT/'V19_品牌替换校验.mp4')
    else:{'previews':previews,'audit':audit,'verify':verify}[cmd]()
