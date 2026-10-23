"""Five-minute cut: local 3D scenes, existing platform footage and factual charts."""
from pathlib import Path
from functools import lru_cache
import sys,json,math,time,subprocess,importlib.util,io,re
import numpy as np
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent;WORK=ROOT/'制作文件'
spec=importlib.util.spec_from_file_location('v17tools',BASE/'交付_V17_五分钟_浅色完整审看版/制作文件/build_film.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
l=v.l;FF=l.FF;W,H,FPS=1920,1080,30;PAPER='#f5f7fe';INK=l.INK;BLUE=l.BLUE;MUTED=l.MUTED
DEST=ROOT/'ABACUSLab_V18_五分钟_浅色三维场景版.mp4'
ART=ROOT/'素材/本地三维概念图';CLIPS=ROOT/'素材/视频帧'
# start, end, mode, asset, title, subtitle
SHOTS=[
 (0,3.4,'concept','G01','新材料的发现与设计','能源材料 · 层状结构与储能研究'),
 (3.4,6.7,'concept','G02','新材料的发现与设计','半导体 · 从晶圆走向微观结构'),
 (6.7,9,'concept','G03','新材料的发现与设计','先进结构材料 · 组成与结构协同'),
 (9,10,'concept','G09','新材料的发现与设计','深入微观结构'),
 (10,16,'concept','G04','材料空间广阔','不同组成、不同排列，打开新的研究方向'),
 (16,22,'structures','','材料空间广阔','从元素组合到晶体结构'),
 (22,25,'concept','G05','研发周期长，试错成本高','材料制备'),
 (25,27.5,'concept','G06','研发周期长，试错成本高','实验表征'),
 (27.5,30,'concept','G07','研发周期长，试错成本高','性能测试'),
 (30,32,'concept','G08','研发周期长，试错成本高','比较、调整，再次验证'),
 (32,35,'concept','G09','理解机制 · 预测性能 · 探索设计','从宏观材料，深入原子结构'),
 (35,37.5,'concept','G10','理解机制 · 预测性能 · 探索设计','电子云 · 微观行为'),
 (37.5,40,'concept','G11','理解机制 · 预测性能 · 探索设计','电荷密度 · 性质与结构的关联'),
 (40,44,'concept','G10','从原子与电子，研究材料性质','第一性原理计算，提供物理依据'),
 (44,47,'concept','G11','从原子与电子，研究材料性质','AI 辅助规划与分析'),
 (47,50,'screen','pyatb','衔接专业计算与结果分析','平台已有电子结构计算界面'),
 (50,54,'brand','','ABACUSLab','AI 驱动的材料计算与设计平台'),
 (54,60,'clip','old_home','ABACUSLab｜AI 驱动的材料计算与设计平台','以国产开源第一性原理软件 ABACUS 为计算核心'),
 (60,70,'flow','platform','连接 AI、专业计算与标准流程','第一性原理计算 · AI 智能体 · 标准化工作流程'),
 (70,78,'clip','old_templates','专业计算模板','结构优化 · 电子结构 · 分子动力学 · 材料物性'),
 (78,85,'clip','old_cards','从研究需求，选择计算方法','专业模板，减少重复准备'),
 (85,90,'clip','old_reuse','将计算组织为可复用的流程','基础计算与多步骤分析'),
 (90,95,'clip','old_workflow','工作流与任务管理','查看计算环节与步骤'),
 (95,101,'clip','old_project','围绕研究目标，组织计算任务','项目管理 · 任务状态'),
 (101,105,'screen','task','运行状态，集中查看','从整体进展到关键任务'),
 (105,108,'clip','old_config','准备输入，配置参数','输入文件与计算设置'),
 (108,111,'screen','pdos','数据可视化','电子态密度'),
 (111,115,'screen','optical','数据可视化','光学响应'),
 (115,125,'clip','ref_prompt','从研究问题到计算方案','用自然语言描述具体研究目标'),
 (125,135,'clip','ref_plan','梳理目标、条件与待确认问题','研究人员检查方案，AI 提供辅助'),
 (135,145,'clip','old_workflow','规划流程，组织计算任务','连接研究思路与专业工具'),
 (145,150,'clip','ref_task','从方案到执行','真实任务界面展示'),
 (150,155,'screen','completebody','检查、调整，再进入下一步','让 AI 辅助与专业判断相结合'),
 (155,165,'clip','ref_prompt','案例一｜铝合金熔化行为研究','向智能体描述研究目标'),
 (165,175,'clip','ref_plan','明确条件，组织计算思路','检查温度条件与所需参数'),
 (175,178,'clip','ref_task','分子动力学任务','查看运行状态与执行记录'),
 (178,190,'motion','','不同温度下的原子运动','固态振动与液态迁移的概念说明'),
 (190,205,'msd','msd','不同温度下的均方位移（MSD）','观察运动差异，保留结论边界'),
 (205,210,'screen','conclusion','结果分析与后续验证','AI 辅助归纳主要特征'),
 (210,215,'screen','suggest','进一步验证，让结论更有依据','扩大温度扫描，复核体系与计算条件'),
 (215,220,'screen','structbody','案例二｜电子结构与物性分析','从结构模型到专业计算'),
 (220,225,'screen','pyatb','电子结构计算与结果展示','衔接计算与分析流程'),
 (225,230,'screen','band','能带结构','从真实图表观察电子性质'),
 (230,235,'screen','pdos','电子态密度','观察电子态的分布特征'),
 (235,241,'screen','pdosfull','从计算数据，提取研究信息','图表分析与物理理解'),
 (241,245,'concept','G10','连接微观结构与材料性质','电子行为概念示意'),
 (245,250,'screen','pdos','理解性质，探索物理机制','已有图表功能展示'),
 (250,260,'concept','G14','从材料计算，走向材料设计','候选结构比较 · 设计思路示意'),
 (260,266,'screen','pdos','关键物性分析','结合计算条件，理解结果的适用范围'),
 (266,270,'screen','optical','让比较有依据，让设计有方向','已有结果示例 · 不同候选需在可比条件下验证'),
 (270,280,'flow','design','结构优化与设计探索','候选结构 → 计算验证 → 结果比较 → 进一步优化'),
 (280,282.3,'clip','ref_prompt','AI 智能辅助 + 第一性原理计算 + 科学判断','研究问题与智能辅助'),
 (282.3,284.6,'clip','old_templates','AI 智能辅助 + 第一性原理计算 + 科学判断','专业计算与标准流程'),
 (284.6,287,'screen','msd','AI 智能辅助 + 第一性原理计算 + 科学判断','结果分析与研究判断'),
 (287,292,'brand','','ABACUSLab','AI 驱动的材料计算与设计平台'),
 (292,300,'outro','','让材料计算更简单','把更多精力，留给研究与发现。')]
CLIP_INFO={e['key']:e for e in json.loads((ROOT/'素材/复用视频时间索引.json').read_text(encoding='utf-8'))}

def bg():return Image.new('RGB',(W,H),PAPER)
def txt(im,xy,s,n=30,col=INK,b=False,anchor=None):l.txt(im,xy,s,n,col,b,anchor)
def header(im,title,sub='',tag='ABACUSLab'):
    txt(im,(88,52),'ABACUSLab',30,BLUE,True)
    txt(im,(1832,65),tag,22,MUTED,anchor='ra')
    ImageDraw.Draw(im).line((88,110,1832,110),fill='#dce4f4',width=2)
    size=min(54,int(1740/max(1,l.font(54,True).getlength(title))*54))
    txt(im,(88,145),title,size,INK,True)
    if sub:txt(im,(91,220),sub,27,MUTED)

@lru_cache(16)
def concept_rgba(key):
    im=Image.open(ART/'render_raw'/f'{key}.png').convert('RGBA')
    arr=np.array(im)
    # Shadow catcher pixels remain translucent. Soften only dark shadow pixels.
    shadow=(arr[:,:,:3].max(axis=2)<80)&(arr[:,:,3]<250)
    arr[:,:,3][shadow]=(arr[:,:,3][shadow]*.30).astype('uint8')
    return Image.fromarray(arr)

@lru_cache(16)
def cutout(key):
    im=concept_rgba(key)
    rect=im.getchannel('A').point(lambda x:255 if x>250 else 0).getbbox()
    if key=='G10':rect=(390,100,1530,850)
    if not rect:rect=(300,80,1620,980)
    a,b,c,d=rect;pad=75
    a=max(0,a-pad);b=max(0,b-pad);c=min(W,c+pad);d=min(H,d+pad)
    im=im.crop((a,b,c,d));arr=np.array(im);yy,xx=np.mgrid[:im.height,:im.width]
    feather=np.minimum(np.minimum(xx,im.width-1-xx),np.minimum(yy,im.height-1-yy))/40
    arr[:,:,3]=(arr[:,:,3]*np.clip(feather,0,1)).astype('uint8')
    return Image.fromarray(arr)

def add_concept(im,key,t,dur,box=(120,280,1680,680),zoom=.035):
    x,y,w,h=box;src=cutout(key);p=min(1,max(0,t/max(dur,.01)))
    scale=min(w/src.width,h/src.height)*(1+zoom*p)
    obj=src.resize((round(src.width*scale),round(src.height*scale)),Image.Resampling.BICUBIC)
    im.paste(obj,(round(x+(w-obj.width)/2),round(y+(h-obj.height)/2)),obj)

@lru_cache(8)
def clip_frame(key,index):
    path=CLIPS/key/f'{index:04d}.jpg';im=Image.open(path).convert('RGB')
    if key=='ref_prompt':return im.crop((405,240,1516,996))
    if key=='ref_plan':return im.crop((389,240,1524,922))
    if key=='ref_task':return im.crop((85,345,1835,974))
    return im.crop((105,275,1817,980))

def fit(im,source,box=(96,284,1728,690)):
    x,y,w,h=box;p=ImageOps.contain(source,(w,h),Image.Resampling.LANCZOS)
    im.paste(p,(round(x+(w-p.width)/2),round(y+(h-p.height)/2)))

@lru_cache(40)
def screen_prepared(key,w,h):return ImageOps.contain(v.IMG[key],(w,h),Image.Resampling.LANCZOS)
def screen(im,key,box=(96,284,1728,685)):
    x,y,w,h=box;p=screen_prepared(key,w,h);im.paste(p,(round(x+(w-p.width)/2),round(y+(h-p.height)/2)))

def note(im,s):txt(im,(1825,975),s,19,MUTED,anchor='ra')

def atom_motion(im,t):
    for side in [0,1]:
        cx=510+900*side;cy=600
        pts=np.array([(i-1.5,j-1.5,k-1.5) for i in range(4) for j in range(4) for k in range(4) if (i+j+k)%2==0],float)
        ids=np.arange(len(pts))
        if side==0:
            pts+=np.column_stack([np.sin(t*6+ids)*.045,np.cos(t*6.7+ids)*.045,np.sin(t*5.6+ids)*.045])
        else:
            # Continuous, illustrative rearrangement; no temperature or trajectory data.
            pts+=np.column_stack([np.sin(ids*2.3+t*.65)*.43,np.cos(ids*1.7+t*.6)*.43,np.sin(ids*1.3+t*.7)*.4])
        a=.5+t*.018;b=.40
        mat=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
        tilt=np.array([[1,0,0],[0,math.cos(b),-math.sin(b)],[0,math.sin(b),math.cos(b)]])
        pts=pts@mat.T@tilt.T
        for i in np.argsort(pts[:,2]):
            x,y,z=pts[i];pers=1/(1-z*.055);r=round(25*pers)
            s=l.sphere(r,0);im.paste(s,(round(cx+x*112*pers-r),round(cy+y*112*pers-r)),s)
        txt(im,(cx,869),'固态：平衡位置附近振动' if side==0 else '液态：位置随时间迁移',31,BLUE,True,'mm')

def flow(im,t,dur,mode):
    keys=['question','templates','workflow'] if mode=='platform' else ['structbody','config','pdos','suggest']
    labels=['AI 智能体','专业计算','标准流程'] if mode=='platform' else ['候选结构','计算验证','结果比较','进一步优化']
    n=len(keys);width=1700/n;d=ImageDraw.Draw(im)
    for i,(key,label) in enumerate(zip(keys,labels)):
        x=110+i*width
        screen(im,key,(round(x+18),380,round(width-58),350))
        txt(im,(x+width/2,807),label,35,BLUE,True,'mm')
        if i<n-1:
            progress=l.ease((t-i*.75)/1.5)
            xa=x+width-20;xb=x+width+12;yy=800
            d.line((xa,yy,xa+(xb-xa)*progress,yy),fill=BLUE,width=3)
            if progress>.9:d.polygon([(xb,yy),(xb-9,yy-7),(xb-9,yy+7)],fill=BLUE)
    txt(im,(960,925),'研究人员检查与调整，AI 提供辅助' if mode=='platform' else '计算 · 分析 · 验证',28,MUTED,anchor='mm')

def brand(im,t,outro=False):
    add_concept(im,'G09',2,10,(1040,270,780,630),0)
    txt(im,(108,360),'ABACUSLab',100,BLUE,True)
    txt(im,(114,518),'让材料计算更简单' if outro else 'AI 驱动的材料计算与设计平台',44,INK,True)
    if outro:txt(im,(117,614),'把更多精力，留给研究与发现。',30,MUTED)
    else:
        txt(im,(118,640),'开发单位',24,MUTED)
        txt(im,(118,685),'合肥综合性国家科学中心人工智能研究院',29,INK)
    txt(im,(117,840),'第一性原理计算 · AI 智能体 · 科学判断',26,MUTED)

def scene(i,t):
    a,b,mode,key,title,sub=SHOTS[i];dur=b-a;im=bg()
    if mode=='concept':
        add_concept(im,key,t,dur);note(im,'概念示意')
    elif mode=='structures':
        # Changing structured representations, not a scientific screening result.
        for j,kind in enumerate(['fcc','layer','cube']):
            l.atoms(im,t+j,370+j*590,600,67,kind,8)
            txt(im,(370+j*590,872),['三维排列','层状结构','组成与局域环境'][j],30,BLUE,True,'mm')
        note(im,'结构与组成概念示意')
    elif mode=='clip':
        info=CLIP_INFO[key];count=len(list((CLIPS/key).glob('*.jpg')))
        tick=min(count,max(1,int((t/max(dur,.01))*(count-1))+1))
        fit(im,clip_frame(key,tick))
        note(im,'已有平台画面' if key.startswith('old') else '用户参考片画面')
    elif mode in ['screen','msd']:
        screen(im,key)
        if mode=='msd':
            msg='比较不同温度下的运动特征' if t<6 else '少数温度点不足以精确确定熔点'
            txt(im,(960,965),msg,26,BLUE,True,'mm')
        else:note(im,'已有平台图表' if key in ['pdos','band','optical','pdosfull'] else '已有平台画面')
    elif mode=='motion':atom_motion(im,t);note(im,'原子运动概念示意 · 非实际轨迹')
    elif mode=='flow':flow(im,t,dur,key)
    elif mode in ['brand','outro']:brand(im,t,mode=='outro')
    if mode not in ['brand','outro']:
        tag='概念示意' if mode in ['concept','motion','structures'] else '平台与研究'
        header(im,title,sub,tag)
    else:
        txt(im,(88,52),'ABACUSLab',30,BLUE,True)
        ImageDraw.Draw(im).line((88,110,1832,110),fill='#dce4f4',width=2)
    return im

@lru_cache(6)
def end_frame(i):return scene(i,SHOTS[i][1]-SHOTS[i][0]-.04)
def frame(t):
    i=next((i for i,s in enumerate(SHOTS) if s[0]<=t<s[1]),len(SHOTS)-1)
    local=t-SHOTS[i][0];im=scene(i,local)
    transition=min(.42,(SHOTS[i][1]-SHOTS[i][0])*.2)
    if i and local<transition:im=Image.blend(end_frame(i-1),im,l.ease(local/transition))
    return im

def preflight():
    assert SHOTS[0][0]==0 and SHOTS[-1][1]==300
    assert all(SHOTS[i][1]==SHOTS[i+1][0] for i in range(len(SHOTS)-1))
    for key in [f'G{i:02d}' for i in range(1,15)]:assert (ART/'render_raw'/f'{key}.png').exists(),key
    assert (WORK/'mixed.wav').exists() and (WORK/'captions.ass').exists()
    for mode,key in {(s[2],s[3]) for s in SHOTS}:
        if mode=='clip':assert len(list((CLIPS/key).glob('*.jpg')))>0,key
    for boundary in [0,40,70,115,155,215,250,280,300]:assert boundary in {p for s in SHOTS for p in s[:2]},boundary

def previews():
    preflight();folder=ROOT/'分镜预览';folder.mkdir(exist_ok=True)
    rows=math.ceil(len(SHOTS)/4);sheet=Image.new('RGB',(1600,rows*254),PAPER)
    for i,s in enumerate(SHOTS):
        im=scene(i,min(3,(s[1]-s[0])*.55));im.save(folder/f'{i+1:02d}_{s[0]:06.1f}.jpg',quality=92)
        sheet.paste(im.resize((392,220),Image.Resampling.LANCZOS),((i%4)*400+4,(i//4)*254))
        txt(sheet,((i%4)*400+7,(i//4)*254+223),f'{s[0]:05.1f}–{s[1]:05.1f}  {s[3] or s[2]}',17)
    sheet.save(ROOT/'V18_分镜总览.jpg',quality=92)
    (WORK/'镜头时间线.json').write_text(json.dumps(SHOTS,ensure_ascii=False,indent=2),encoding='utf-8')
    assets=Image.new('RGB',(1600,4*254),PAPER)
    for j in range(14):
        key=f'G{j+1:02d}';im=bg();add_concept(im,key,0,1,(60,20,1800,1000),0)
        im.save(ART/f'{key}.png')
        assets.paste(im.resize((392,220),Image.Resampling.LANCZOS),((j%4)*400+4,(j//4)*254))
        txt(assets,((j%4)*400+10,(j//4)*254+222),key,20)
    assets.save(ROOT/'V18_新增三维素材总览.jpg',quality=94)
    print('PREVIEWS_READY',len(SHOTS),flush=True)

def render(start=0,end=300,dest=None):
    preflight();dest=dest or DEST
    # Trim original audio with the same absolute time as the video window.
    args=[FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-ss',str(start),'-i','mixed.wav',
          '-vf',f'setpts=PTS+{start}/TB,ass=captions.ass,setpts=PTS-STARTPTS','-map','0:v:0','-map','1:a:0',
          '-c:v','libx264','-preset','fast','-crf','18','-threads','6','-pix_fmt','yuv420p','-af','loudnorm=I=-17:TP=-2:LRA=9,aresample=48000','-c:a','aac','-b:a','192k','-t',str(end-start),'-movflags','+faststart',str(dest)]
    proc=subprocess.Popen(args,cwd=WORK,stdin=subprocess.PIPE);beg=time.time()
    try:
        for n in range(round((end-start)*FPS)):
            proc.stdin.write(frame(start+n/FPS).tobytes())
            if n%450==0:print(f'RENDER {start+n/FPS:.0f}/{end}s | {time.time()-beg:.1f}s',flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('FFmpeg encode failed')
    print('VIDEO_READY',dest,flush=True)

def verify():
    meta=subprocess.run([FF,'-hide_banner','-i',str(DEST)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
    for s in ['1920x1080','30 fps','h264','aac','00:05:00.00']:assert s in meta,(s,meta)
    dec=subprocess.run([FF,'-v','error','-i',str(DEST),'-f','null','-'],capture_output=True,text=True)
    assert dec.returncode==0 and not dec.stderr,dec.stderr
    sound=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(DEST),'-vn','-ar','48000','-ac','2','-f','f32le','pipe:1']),np.float32)
    duration=len(sound)/(48000*2);peak=float(np.abs(sound).max());assert abs(duration-300)<.05 and peak<.98
    report={'duration_seconds':duration,'resolution':'1920x1080','fps':30,'shots':len(SHOTS),'chapters':[0,40,70,115,155,215,250,280,300],
            'audio_peak':peak,'decode_errors':0,'size_mb':round(DEST.stat().st_size/1048576,1),'new_3d_assets':14,'image_generation_api_used':False,
            'limitations':['原子运动为概念动画，非实际轨迹','电子云与电荷密度为概念示意','未获得同条件候选物性数据，设计段展示分析思路与已有图表功能']}
    (ROOT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    times=[1,5,8,13,24,26,29,31,34,36,39,43,48,52,57,65,75,91,99,107,112,119,129,139,148,153,159,169,176,182,188,195,203,208,213,218,228,233,239,243,255,263,268,275,282,289,297]
    sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*254),PAPER)
    for i,t in enumerate(times):
        raw=subprocess.check_output([FF,'-v','error','-ss',str(t),'-i',str(DEST),'-frames:v','1','-vf','scale=392:220','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        im=Image.frombytes('RGB',(392,220),raw);sheet.paste(im,((i%4)*400+4,(i//4)*254))
        txt(sheet,((i%4)*400+8,(i//4)*254+224),f'{t//60:02d}:{t%60:02d}',18)
    sheet.save(ROOT/'V18_成片实帧核验.jpg',quality=92)
    preview=ROOT/'ABACUSLab_V18_前70秒预览.mp4'
    subprocess.run([FF,'-v','error','-y','-i',str(DEST),'-t','70','-c','copy','-movflags','+faststart',str(preview)],check=True)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':
    cmd=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if cmd=='render':render()
    elif cmd=='sample':render(70,85,ROOT/'V18_平台复用片段校验.mp4')
    else:{'previews':previews,'verify':verify,'preflight':preflight}[cmd]()
