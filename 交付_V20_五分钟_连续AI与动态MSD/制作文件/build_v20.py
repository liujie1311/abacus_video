"""V20: stable opening, source-level recut, distinct chapter roles and requested brand art."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import importlib.util,json,sys,math,subprocess,time,io,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageOps,ImageFilter
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent;WORK=ROOT/'制作文件';PREV=BASE/'交付_V18_五分钟_按方案实景重制'
s=importlib.util.spec_from_file_location('v18',PREV/'制作文件/build_v18.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
l=v.l;FF=v.FF;W,H,FPS=1920,1080,30;PAPER=v.PAPER;BLUE=v.BLUE;INK=v.INK;MUTED=v.MUTED
DEST=ROOT/'ABACUSLab_V20_五分钟_连续演示与动态MSD版.mp4'
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
 (43,50,'principles','principles','从微观结构，理解材料性质','ABACUS · 国产开源第一性原理计算软件'),
 (50,56,'brand','login_brand','ABACUSLab','AI 驱动的材料计算与设计平台'),
 (56,60,'screen','homebody','一个平台，连接材料研究','专业计算 · AI 智能体 · 标准化工作流程'),
 (60,70,'capabilities','capabilities','让智能辅助，与专业计算结合','研究人员检查与调整，平台组织计算与分析'),
 (70,78,'screen','templates','专业计算模板','结构优化 · 电子结构 · 分子动力学 · 材料物性'),
 (78,85,'screen','template_body','从研究目标，选择计算方法','模板说明与计算步骤'),
 (85,95,'screen','bandflow_body','将基础计算组织成可复用流程','多步骤计算 · 条件配置 · 方法复用'),
 (95,100,'screen','project_body','按项目组织研究任务','围绕研究目标，积累计算记录'),
 (100,105,'screen','task_body','任务进展，集中管理','查看状态，检查关键环节'),
 (105,108,'screen','convert_body','结构转换与输入准备','连接不同计算环节'),
 (108,115,'config_full','config_full','计算参数，可视化配置','选择计算类型 · 配置参数 · 预览输入文件'),
 (115,125,'raw','case_question','从一个研究问题开始','铝合金熔化行为研究'),
 (125,138,'raw','ai_conditions','把研究目标，转化为计算方案','梳理体系、温度和计算步骤'),
 (138,150,'raw','ai_review','确认计算条件','检查结构、势函数与模拟设置'),
 (150,162,'tasks','case_task','查看计算任务与执行状态','300 K 与 1600 K · 两组温度条件'),
 (162,172,'feedback','ai_feedback','从计算任务，到结果图表','查看完成反馈与绘图入口'),
 (172,190,'atoms_new','atoms_new','固态振动与熔融态扩散','从原子运动，理解两种状态的差异'),
 (190,205,'msd_dynamic','msd_dynamic','不同温度下的均方位移（MSD）','300 K 固态与 1600 K 熔融态对照'),
 (205,215,'analysis','analysis','从结果分析，走向进一步验证','归纳主要变化，明确下一步研究方向'),
 (215,225,'electronic','electronic_setup','电子结构与物性分析','从结构模型，到电子结构计算'),
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

def base_scene(i,t):
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

# V20 scene overrides. Included in the standalone build script at preparation.
PURPLE='#734388';GREEN='#5b9f46'

@lru_cache(1)
def principles_canvas():
    im=bg();d=ImageDraw.Draw(im)
    # Illustrative density field; no computed quantity or numerical scale is implied.
    yy,xx=np.mgrid[-1:1:430j,-1:1:430j]
    field=sum(np.exp(-((xx-x)**2+(yy-y)**2)/.12) for x,y in [(-.36,-.3),(.38,-.26),(-.02,.35)])
    z=np.clip(field/field.max(),0,1);rgba=np.zeros((430,430,4),np.uint8)
    rgba[:,:,:3]=[102,169,194];rgba[:,:,3]=(z*165).astype(np.uint8)
    rings=(np.mod(z,.13)<.008)&(z>.08);rgba[rings,:3]=[87,133,183];rgba[rings,3]=130
    fieldim=Image.fromarray(rgba);im.paste(fieldim,(745,360),fieldim)
    for row in range(4):
        for col in range(4):
            x=235+col*83+row*21;y=403+row*83
            if col<3:d.line((x,y,x+83,y),fill='#cbd5e7',width=3)
            if row<3:d.line((x,y,x+21,y+83),fill='#cbd5e7',width=3)
            sp=l.sphere(22,0);im.paste(sp,(x-22,y-22),sp)
    for x in [659,1235]:
        d.line((x,575,x+55,575),fill='#a8b9d8',width=3);d.polygon([(x+55,575),(x+44,568),(x+44,582)],fill='#a8b9d8')
    for j,label in enumerate(['总能量与受力','电子态与成键','材料性质']):
        txt(im,(1480,445+j*105),label,33,INK,True,'mm')
    for x,label in [(390,'原子结构'),(960,'电子分布'),(1480,'性质分析')]:txt(im,(x,838),label,35,BLUE,True,'mm')
    return im

@lru_cache(1)
def chart_layers():
    chart=ImageOps.contain(IMG['msd'],(1280,675),Image.Resampling.LANCZOS).convert('RGB')
    a=np.asarray(chart);dark=a.max(axis=2)<105
    rows=np.where(dark.sum(axis=1)>chart.width*.5)[0]
    top,bottom=int(rows[0]),int(rows[-1])
    cols=np.where(dark[top:bottom+1].sum(axis=0)>(bottom-top)*.70)[0]
    left,right=int(cols[0]),int(cols[-1])
    z=a.astype(int)
    colored=((z[:,:,1]-z[:,:,0]>17)&(z[:,:,1]-z[:,:,2]>8))|((z[:,:,0]-z[:,:,1]>16)&(z[:,:,2]-z[:,:,1]>15))
    mask=np.asarray(Image.fromarray((colored*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)))>0
    mask[:top+2]=False;mask[bottom-1:]=False;mask[:,:left+2]=False;mask[:,right-1:]=False
    mask[top:top+int((bottom-top)*.20),left:left+int((right-left)*.26)]=False
    clean=a.copy();clean[mask]=255
    return chart,Image.fromarray(clean),(left,top,right,bottom),mask

def dynamic_msd(im,t):
    chart,blank,(left,top,right,bottom),_=chart_layers()
    progress=max(0,min(1,(t-.7)/7.5));cut=round(left+(right-left)*progress)
    panel=blank.copy();panel.paste(chart.crop((0,0,cut,chart.height)),(0,0))
    if progress>=1:panel=chart.copy()
    x,y=550,283;im.paste(panel,(x,y));d=ImageDraw.Draw(im)
    if .01<progress<1:d.line((x+cut,y+top+2,x+cut,y+bottom-2),fill='#b6c8db',width=1)
    for yy,col,title,line1,line2 in [(375,PURPLE,'300 K · 固态','原子局域振动','MSD 接近平台'),(650,GREEN,'1600 K · 熔融态','原子扩散迁移','MSD 随时间上升')]:
        d.rounded_rectangle((90,yy,495,yy+205),radius=18,fill='white',outline=col,width=2)
        txt(im,(115,yy+24),title,32,col,True);txt(im,(115,yy+87),line1,28,INK);txt(im,(115,yy+141),line2,25,MUTED)
    note(im,'原始曲线 · 沿时间轴逐步展示')

BASE_ATOMS=np.array([(col*74+(row%2)*37-203.5,row*66-132) for row in range(5) for col in range(6)],float)

@lru_cache(1)
def liquid_frames():
    rng=np.random.default_rng(420);p=BASE_ATOMS.copy()+rng.normal(0,5,BASE_ATOMS.shape);vel=rng.normal(0,30,p.shape)
    frames=[]
    # Confined, repulsive particles illustrate rearrangement only, not an MD trajectory.
    for n in range(1200):
        vel=.985*vel+rng.normal(0,6,p.shape)
        delta=p[:,None,:]-p[None,:,:];dist=np.linalg.norm(delta,axis=2);np.fill_diagonal(dist,1e9)
        force=np.maximum(0,55-dist)[:,:,None]*delta/np.maximum(dist[:,:,None],1)
        vel+=force.sum(axis=1)*.40;vel=np.clip(vel,-85,85);p+=vel/30
        for ax,lim in [(0,240),(1,172)]:
            bad=np.abs(p[:,ax])>lim;vel[bad,ax]*=-.8;p[:,ax]=np.clip(p[:,ax],-lim,lim)
        if n>=600:frames.append(p.copy())
    return np.asarray(frames)

@lru_cache(8)
def atom_sprite(col,marked=False):
    r=24;size=2*r+4;yy,xx=np.mgrid[:size,:size];dx=(xx-r-2)/r;dy=(yy-r-2)/r;rr=dx*dx+dy*dy
    base=np.array(tuple(int(col[i:i+2],16) for i in (1,3,5)),float)
    z=np.sqrt(np.maximum(0,1-rr));shade=np.clip(.48+.36*z-.25*dx-.3*dy,.25,1.2)
    rgb=np.clip(base[None,None,:]*shade[:,:,None]+np.exp(-((dx+.35)**2+(dy+.38)**2)/.08)[:,:,None]*100,0,255)
    alpha=np.clip((1-rr)*r*1.5,0,1)*255
    return Image.fromarray(np.dstack([rgb,alpha]).astype(np.uint8))

def atoms_scene(im,t):
    d=ImageDraw.Draw(im);ids=np.arange(len(BASE_ATOMS));tick=min(599,max(0,round(t*30)))
    solid=BASE_ATOMS+np.column_stack([np.sin(t*7+ids)*3.8,np.cos(t*6.2+ids*1.3)*3.8]);liq=liquid_frames()[tick]
    for side,(points,col,title,caption) in enumerate([(solid,PURPLE,'固态','有序排列 · 平衡位置附近振动'),(liq,GREEN,'熔融态（液态）','近邻持续变化 · 原子扩散迁移')]):
        cx=510+900*side;cy=595
        d.rounded_rectangle((cx-345,340,cx+345,842),radius=30,fill='#ffffff',outline='#e0e6ef',width=2)
        txt(im,(cx,302),title,38,col,True,'mm')
        if side==0:
            for x,y in BASE_ATOMS:d.ellipse((cx+x-6,cy+y-6,cx+x+6,cy+y+6),outline='#bac4d5',width=1)
        tagged=[8,19]
        for k in tagged:
            if side==0:
                ts=np.linspace(max(0,t-3),t,45);track=BASE_ATOMS[k]+np.column_stack([np.sin(ts*7+k)*3.8,np.cos(ts*6.2+k*1.3)*3.8])
            else:track=liquid_frames()[max(0,tick-105):tick+1:3,k]
            if len(track)>1:d.line([(round(cx+x),round(cy+y)) for x,y in track],fill=col,width=3)
        for k,(x,y) in enumerate(points):
            sp=atom_sprite(col if k in tagged else '#7798c8');im.paste(sp,(round(cx+x-26),round(cy+y-26)),sp)
            if k in tagged:d.ellipse((cx+x-28,cy+y-28,cx+x+28,cy+y+28),outline=col,width=2)
        txt(im,(cx,890),caption,29,col,True,'mm')
    txt(im,(960,955),'彩色标记与轨迹，帮助比较同一原子的运动',24,MUTED,anchor='mm')

def scene(i,t):
    a,b,mode,key,title,sub=SHOTS[i]
    if mode not in ['principles','config_full','tasks','atoms_new','msd_dynamic']:return base_scene(i,t)
    im=bg();tag='平台实际画面'
    if mode=='principles':im=principles_canvas().copy();tag='计算原理示意'
    elif mode=='config_full':
        screenshot(im,'config',(595,267,1130,708))
        for y,head,body in [(380,'计算类型','按研究目标选择'),(565,'参数配置','核对方法与精度'),(750,'输入预览','检查生成的文件')]:bullet(im,100,y,head,body)
    elif mode=='tasks':
        raw(im,'case_task',min(t,1.55),b-a)
    elif mode=='atoms_new':atoms_scene(im,t);tag='运动机制示意 · 非实际轨迹'
    elif mode=='msd_dynamic':dynamic_msd(im,t);tag='平台原始图表'
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
    (WORK/'重复与稳定性检查.json').write_text(json.dumps({'shots':len(SHOTS),'duplicate_primary_sources':duplicates,'opening_stability':stability,'intentional_secondary_reuse':'仅280–287秒为功能回顾；研究提问、条件确认、任务、结果各出现一次','source_playback':'30 fps 原录屏各播放一次；短片尾帧停留便于阅读，不慢放复制帧'},ensure_ascii=False,indent=2),encoding='utf-8')
    print('AUDIT_PASS',len(SHOTS),len(stability),flush=True)

def previews():
    audit();folder=ROOT/'分镜预览';folder.mkdir(exist_ok=True)
    sheet=Image.new('RGB',(1600,math.ceil(len(SHOTS)/4)*252),PAPER)
    for i,s in enumerate(SHOTS):
        im=scene(i,min((s[1]-s[0])*.6,5));im.save(folder/f'{i+1:02d}_{s[0]:03.0f}.jpg',quality=94)
        sheet.paste(im.resize((392,220),Image.Resampling.LANCZOS),(i%4*400+4,i//4*252))
        txt(sheet,(i%4*400+8,i//4*252+222),f'{s[0]:05.1f}–{s[1]:05.1f} {s[3]}',16)
    sheet.save(ROOT/'V20_完整分镜总览.jpg',quality=94)
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
    sheet.save(ROOT/'V20_成片实帧核验.jpg',quality=94)
    report={'duration_seconds':dur,'resolution':'1920x1080','fps':30,'decode_errors':0,'peak_audio':peak,'shots':len(SHOTS),'duplicate_primary_shots':0,'size_mb':round(DEST.stat().st_size/1048576,1),'opening':'fixed composition, no per-frame resize','source_motion':'native 30 fps, no replay loops','brand':'user requested molecular login artwork','concept_animation':'MD motion is illustrative, not measured trajectory'}
    (ROOT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    for name,start,duration in [('开头与品牌预览_70秒',0,70),('AI与动态MSD预览_100秒',115,100)]:
        subprocess.run([FF,'-v','error','-y','-ss',str(start),'-i',str(DEST),'-t',str(duration),'-c:v','libx264','-preset','fast','-crf','18','-threads','4','-c:a','aac','-b:a','192k','-movflags','+faststart',str(ROOT/f'V20_{name}.mp4')],check=True)
    print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':
    cmd=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if cmd=='render':render()
    elif cmd=='sample':render(50,60,ROOT/'V20_品牌替换校验.mp4')
    else:{'previews':previews,'audit':audit,'verify':verify}[cmd]()
