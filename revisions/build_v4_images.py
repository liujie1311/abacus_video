"""Render V4 review stills using supplied screenshots and explicit workflow diagrams."""
from pathlib import Path
from PIL import Image, ImageDraw
import shutil, json, zipfile

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'交付_V4_115秒方案'
ASSETS=ROOT/'03_图片素材'
MAIN=ASSETS/'01_主分镜_1080p'
EXTRA=ASSETS/'02_补充分镜_1080p'
RAW=ASSETS/'03_原始素材'
CROPS=ASSETS/'04_裁切素材'
for p in [MAIN,EXTRA,RAW,CROPS]: p.mkdir(parents=True,exist_ok=True)
new_sources=[
 ('C:/Users/13118/AppData/Local/Temp/codex-clipboard-e6bfc694-0502-4492-8d18-375a22fbbf0a.png','工具箱原图.png'),
 ('C:/Users/13118/AppData/Local/Temp/codex-clipboard-c0414a9f-950c-45de-b841-6fd91619c7e1.png','平台首页原图.png'),
]
for p,name in new_sources: shutil.copy2(p,RAW/name)
for name in ['0252131c-9fe3-48d6-9f17-739ffb635336.png','17ca551a-694e-46b7-8861-0ff29629ef79.png','b4e1e888-5ae5-4e77-b3fc-6431ac4fab0b.png']:
    shutil.copy2(BASE.parent/name,RAW/name)
v3=BASE/'交付_V3_含模板_无字幕/03_图片素材'
for p in (v3/'03_原始截图').glob('*.png'): shutil.copy2(p,RAW/p.name)

style_path=BASE/'revisions/render_review_images.py'
style=style_path.read_text(encoding='utf-8').split('\nscenes = [',1)[0]
style=style.replace("OUT = BASE / 'revisions' / 'review_images_v2_no_subtitles'", "OUT = BASE / '交付_V4_115秒方案' / '03_图片素材'")
style=style.replace("f'{index:02d} / 07'","f'{index:02d} / 10'").replace('range(7)','range(10)').replace('1540+n*42','1430+n*40')
style=style.replace('我想计算一下金属熔断','我想计算这种金属的熔点')
style=style.replace('def question():\n    im = base(2)','def question():\n    im = base(3)')
style=style.replace('def charts():\n    im = base(4)','def charts():\n    im = base(7)')
style=style.replace('def results(active=0):\n    im = base(5)','def results(active=0):\n    im = base(7)')
style=style.replace('01  /  自然语言交互','03  /  自然语言交互').replace('03  /  数据可视化','07  /  金属熔点分析').replace('04  /  分析与验证','07  /  分析与验证')
ns={'__file__':str(style_path),'__name__':'v4_style'}
exec(compile(style,str(style_path),'exec'),ns)
base,label,text,box,fit=[ns[k] for k in ['base','label','text','box','fit']]
BLUE,INK,MUTED=[ns[k] for k in ['BLUE','INK','MUTED']]

home=Image.open(RAW/'平台首页原图.png').convert('RGB')
tool=Image.open(RAW/'工具箱原图.png').convert('RGB')
work=Image.open(RAW/'b4e1e888-5ae5-4e77-b3fc-6431ac4fab0b.png').convert('RGB')
templates=Image.open(RAW/'模板库全景_3450x1701.png').convert('RGB')
detail=Image.open(RAW/'模板卡片_3009x1245.png').convert('RGB')
def crop_ref(src,rect,ref):
    sx,sy=src.width/ref[0],src.height/ref[1]
    return src.crop(tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(rect)))
# Coordinates referenced to the supplied display previews; crops omit desktop and user controls.
hero=crop_ref(home,(244,66,2022,297),(2048,1017))
home_main=crop_ref(home,(244,66,2022,1004),(2048,1017))
quick=crop_ref(home,(246,312,2018,463),(2048,1017))
tool_panel=crop_ref(tool,(35,190,784,442),(2048,1051))
tool_tabs=crop_ref(tool,(22,79,506,125),(2048,1051))
for name,im in [('首页品牌区',hero),('首页主体',home_main),('首页快捷入口',quick),('工具箱转换面板',tool_panel),('工具箱功能标签',tool_tabs)]:
    im.save(CROPS/f'{name}.png')

def heading(im,k,title,sub=None):
    label(im,k)
    text(im,(88,218),title,53,INK,True)
    if sub: text(im,(92,298),sub,27,MUTED)

def opening():
    im=base(1,True)
    text(im,(88,219),'ABACUSLab',68,'white',True)
    text(im,(90,330),'面向材料设计与第一性原理计算',47,'#b8c1ff',True)
    text(im,(90,402),'的 AI 平台',47,'white',True)
    box(im,(80,548,1840,861),'#e3e6f6',22)
    fit(im,hero,(95,563,1730,283))
    text(im,(92,913),'从一句话开始，让材料计算更简单',30,'#b9c7e2')
    return im

def homepage():
    im=base(1)
    heading(im,'01  /  平台总览','材料设计与计算，在一个平台中展开')
    box(im,(80,323,1840,977),'white',22,'#dce2f0')
    fit(im,home_main,(100,338,1720,622))
    return im

def workflow(pain=False):
    im=base(2)
    heading(im,'02  /  完整工作流','一个平台，连接材料计算全流程','可复用 · 可追踪')
    names=['结构建模','计算任务','超算调度','物性分析','结果可视化']
    desc=['准备结构与输入','组织计算步骤','配置与提交资源','提取材料性质','展示图表与结论']
    pains=['输入文件多','软件衔接难','调度配置复杂','状态日志分散','结果解析繁琐']
    for i in range(5):
        x=90+i*355
        if pain:
            box(im,(x,418,x+320,493),'#eef0fa',18)
            text(im,(x+160,437),pains[i],25,MUTED,True,'ma')
        box(im,(x,552,x+320,768),'white',22,'#d9dff0',2)
        text(im,(x+30,578),f'0{i+1}',25,BLUE,True)
        text(im,(x+160,625),names[i],32,INK,True,'ma')
        text(im,(x+160,694),desc[i],23,MUTED,anchor='ma')
        if i<4: text(im,(x+337,639),'→',26,BLUE,anchor='ma')
    text(im,(960,877),'从分散操作，到可复用的工作流',36,BLUE,True,'ma')
    text(im,(92,965),'流程示意',18,MUTED)
    return im

def parameters():
    im=base(4)
    heading(im,'04  /  模板与输入','找到合适模板，确认关键输入','金属熔点分析 · 关键输入检查示意')
    box(im,(90,391,650,902),'white',24,'#dce2f0')
    for i,(a,b) in enumerate([('检索相关模板','匹配模拟与分析流程'),('推荐执行平台','结合任务与计算资源'),('补充并确认输入','不凭空编造关键参数')]):
        y=433+i*145
        text(im,(124,y),f'0{i+1}',25,BLUE,True)
        text(im,(188,y-2),a,30,INK,True)
        text(im,(188,y+49),b,24,MUTED)
    specs=[('金属结构','材料组成与初始构型'),('势函数','适用体系与参数文件'),('温度范围','对比温度与扫描计划'),('体系规模','原子数量与边界条件')]
    for i,(a,b) in enumerate(specs):
        x,y=710+(i%2)*570,391+(i//2)*266
        box(im,(x,y,x+540,y+235),'white',22,'#dce2f0')
        text(im,(x+30,y+31),a,37,BLUE,True)
        text(im,(x+30,y+103),b,26,INK)
        text(im,(x+30,y+171),'需询问、核对并确认',23,MUTED)
    return im

def computation():
    im=base(5)
    heading(im,'05  /  多步骤计算','确认方案，连接多步计算','金属熔点案例 · LAMMPS 分子动力学')
    items=[('01','多温度模拟','300 K / 1600 K','LAMMPS'),('02','轨迹与 MSD 分析','比较原子运动','轨迹 → 均方位移'),('03','结果汇总','结论与验证建议','图表 + 分析')]
    for i,(n,title,sub,tag) in enumerate(items):
        x=100+i*590
        box(im,(x,407,x+530,745),'white',24,'#dce2f0',2)
        text(im,(x+32,439),n,30,BLUE,True)
        text(im,(x+32,505),title,37,INK,True)
        text(im,(x+32,579),sub,28,MUTED)
        text(im,(x+32,660),tag,26,BLUE)
        if i<2:text(im,(x+560,552),'→',35,BLUE,anchor='ma')
    for i,s in enumerate(['参数校验','文件衔接','资源配置','任务提交']):
        x=100+i*445
        box(im,(x,817,x+410,893),'#e9ecff',16)
        text(im,(x+205,837),s,29,BLUE,True,'ma')
    text(im,(100,958),'基于已有案例的流程示意',18,MUTED)
    return im

def tracking():
    im=base(6)
    heading(im,'06  /  过程追踪','计算过程，清晰可追踪')
    for i,s in enumerate(['工作流','任务状态','实时事件','运行日志']):
        y=386+i*122
        box(im,(90,y,469,y+86),'white',18,'#dce2f0')
        text(im,(124,y+24),f'0{i+1}',25,BLUE,True)
        text(im,(196,y+20),s,31,INK,True)
    box(im,(520,326,1840,964),'white',23,'#dce2f0')
    # Existing metal melting workflow screen. Keep its task names and counters intact.
    view=work.crop((400,110,3800,1890))
    fit(im,view,(538,343,1284,590))
    text(im,(548,935),'已有金属熔点任务 · 工作台画面',19,MUTED)
    return im

def library():
    im=base(8)
    heading(im,'08  /  平台能力总览','多种物性分析，汇聚一处','从金属熔点案例，拓展到更多材料性质')
    groups=[('电子结构',['能带','投影能带','态密度']),('费米面与自旋',['费米面','自旋纹理']),('光学与拓扑响应',['贝里曲率','光学','拓扑响应'])]
    for i,(title,items) in enumerate(groups):
        x=100+i*590
        box(im,(x,400,x+530,876),'white',23,'#dce2f0')
        text(im,(x+34,437),title,32,BLUE,True)
        for j,s in enumerate(items):
            y=527+j*99
            box(im,(x+31,y,x+499,y+73),'#f4f5fd',14)
            text(im,(x+57,y+17),s,30,INK,True)
    return im

def template_cards():
    im=base(8)
    heading(im,'08  /  模板卡片特写','清晰模板，直观选择','电子结构 / 输运 / 光学')
    for i,name in enumerate(['04_态密度_DOS.png','05_反常霍尔电导_AHC.png','06_联合态密度_JDOS.png']):
        card=Image.open(v3/'04_模板卡片原像素'/name).convert('RGB')
        im.paste(card,(143+i*580,413))
    return im

def toolbox():
    im=base(9)
    heading(im,'09  /  工具箱','结构转换与输入生成，让准备更便捷')
    for i,s in enumerate(['VASP → ABACUS','CIF → STRU','PYATB Input','ABACUS INPUT']):
        x=90+i*445
        box(im,(x,331,x+410,407),BLUE if i==0 else 'white',18,None if i==0 else '#dce2f0')
        text(im,(x+205,352),s,27,'white' if i==0 else BLUE,True,'ma')
    box(im,(90,443,1395,979),'white',23,'#dce2f0')
    fit(im,tool_panel,(108,457,1269,503))
    for i,(a,b) in enumerate([('结构文件转换','常用结构与输入格式衔接'),('输入文件生成','ABACUS / PYATB'),('集中准备','减少分散操作')]):
        y=473+i*164
        text(im,(1450,y),a,31,BLUE,True)
        text(im,(1450,y+65),b,23,MUTED)
    return im

def engine():
    im=base(9)
    heading(im,'09  /  计算引擎','工具协同，连接多种计算引擎','平台能力总览')
    box(im,(650,390,1270,521),'white',25,'#dce2f0',2)
    text(im,(960,423),'ABACUSLab',51,BLUE,True,'ma')
    d=ImageDraw.Draw(im)
    d.line((960,522,960,607),fill='#b9c2ec',width=3)
    d.line((305,607,1610,607),fill='#b9c2ec',width=3)
    for i,s in enumerate(['ABACUS','PYATB','TB2J','LAMMPS']):
        x=100+i*435
        d.line((x+205,607,x+205,658),fill='#b9c2ec',width=3)
        box(im,(x,658,x+410,811),'white',23,'#dce2f0',2)
        text(im,(x+205,708),s,43,BLUE,True,'ma')
    text(im,(960,886),'结构准备 · 计算执行 · 后处理分析',30,MUTED,anchor='ma')
    return im

def value():
    im=base(10)
    heading(im,'10  /  智能工作流','从会算，到会协同、会验证、会解释')
    for i,(a,b) in enumerate([('会协同','连接工具与计算流程'),('会验证','核对输入与结果边界'),('会解释','解读数据与下一步')]):
        x=100+i*590
        box(im,(x,413,x+530,771),'white',25,'#dce2f0')
        text(im,(x+265,496),a,57,BLUE,True,'ma')
        text(im,(x+265,632),b,28,MUTED,anchor='ma')
    text(im,(960,884),'让材料计算更简单',43,INK,True,'ma')
    return im

def live_page(kind):
    im=base(4 if kind=='template' else 9)
    live=ASSETS/'05_平台实截'
    if kind=='template':
        heading(im,'04  /  真实模板检索','金属熔点计算，已有模板可用','LAMMPS · 金属熔点计算模板')
        shot=Image.open(live/'05_金属熔点模板检索.jpg').convert('RGB').crop((350,90,800,440))
        box(im,(90,390,770,920),'white',24,'#dce2f0')
        fit(im,shot,(110,410,640,490))
        text(im,(865,432),'金属熔点计算',48,BLUE,True)
        text(im,(868,525),'模板描述：Al-Mg LAMMPS 金属熔点计算',28,INK)
        for j,s in enumerate(['热学性质类','LAMMPS 计算引擎','选择模板后，结合实际材料核对输入']):
            text(im,(868,620+j*75),s,28,MUTED)
    else:
        ispy=kind=='pyatb'
        title='PYATB Input：选择物性，配置输入' if ispy else 'ABACUS INPUT：参数配置与预览'
        heading(im,'09  /  工具箱实截',title)
        shot=Image.open(live/('03_工具箱_PYATB_Input.jpg' if ispy else '04_工具箱_ABACUS_INPUT.jpg')).convert('RGB')
        shot=shot.crop((206,108,1288,565 if ispy else 727))
        box(im,(90,335,1240,983),'white',24,'#dce2f0')
        fit(im,shot,(110,349,1110,619))
        items=['输入来源','计算属性','高级参数','生成与导出'] if ispy else ['快速模板','参数分类','配置预览','复制与下载']
        for j,s in enumerate(items):
            y=395+j*129
            text(im,(1330,y),f'0{j+1}',26,BLUE,True)
            text(im,(1400,y-2),s,34,INK,True)
    return im

rows=[
 ('01_平台定位',0,10,opening(),'新首页品牌区裁切 + 编辑标题'),
 ('02_完整工作流',10,19,workflow(),'功能流程示意'),
 ('03_自然语言提问',19,30,ns['question'](),'旧对话版式 + 熔点提问文案排版'),
 ('04_模板与关键输入',30,43,parameters(),'输入检查流程示意，非实际确认结果'),
 ('05_多步骤计算',43,57,computation(),'基于已有 LAMMPS 案例的流程示意'),
 ('06_过程追踪',57,68,tracking(),'已有金属熔点工作台截图 + 功能标签'),
 ('07_MSD结果分析',68,80,ns['charts'](),'已有原始 MSD 曲线'),
 ('08_物性分析能力',80,94,library(),'平台物性能力分类展示'),
 ('09_工具箱',94,105,toolbox(),'新工具箱截图裁切 + 功能标签'),
 ('10_品牌片尾',105,115,ns['outro'](),'沿用品牌片尾版式'),
]
extras=[
 ('01b_平台首页总览',3,10,homepage(),'新首页截图'),
 ('02a_痛点与工作流',10,13,workflow(True),'流程示意'),
 ('07b_分析结论',74,77,ns['results'](0),'已有分析原文'),
 ('07c_局限与验证',77,80,ns['results'](1),'已有局限原文'),
 ('07d_下一步建议',77,80,ns['results'](2),'已有建议原文，作为局限画面的可选替换'),
 ('08b_真实模板特写',80,94,template_cards(),'原像素模板卡片，穿插于能力介绍'),
 ('09b_计算引擎',102,105,engine(),'平台引擎连接示意'),
 ('10a_三个能力',105,109,value(),'品牌价值示意'),
 ('04a_金属熔点模板实截',30,34,live_page('template'),'平台实际检索结果；模板描述不等同于旧示例实际材料组成'),
 ('09c_PYATB输入配置实截',98,100,live_page('pyatb'),'真实配置界面，未执行生成'),
 ('09d_ABACUS输入配置实截',100,102,live_page('abacus'),'真实配置界面，未选择参数或下载文件'),
]
for name,a,b,im,source in rows: im.save(MAIN/f'{name}.png')
for name,a,b,im,source in extras: im.save(EXTRA/f'{name}.png')
def tc(s):return f'{s//60:02d}:{s%60:02d}'
contact=Image.new('RGB',(1980,3180),'#e8ecf5')
text(contact,(40,24),'ABACUSLab｜115 秒 · 金属熔点案例 · 无字幕版',36,INK,True)
text(contact,(40,85),'10 个主分镜 / 新增首页与工具箱素材 / 完整图片见对应镜号',25,MUTED)
for i,(name,a,b,im,source) in enumerate(rows):
    x,y=30+(i%2)*975,150+(i//2)*605
    text(contact,(x+8,y),f'{name.replace("_","  ")}   {tc(a)}–{tc(b)}',26,INK,True)
    contact.paste(im.resize((945,532),Image.Resampling.LANCZOS),(x,y+39))
contact.save(ASSETS/'00_分镜总览.jpg',quality=95)
index=['# V4 图片素材索引','',
       '10 张主分镜、11 张补充分镜，全部为 1920×1080 PNG，无配音字幕。另附 5 张平台实截，数字编号与演讲稿、分镜脚本对应。','',
       '## 新补两张图的使用','',
       '- 平台首页：用于 01_平台定位及 01b_平台首页总览；裁掉顶部用户控件。品牌区的晶格图为首页原有装饰，不作为本次模拟材料结构。首页的任务统计与能带记录属于平台总体信息，不当作熔点案例数据。',
       '- 工具箱：用于 09_工具箱，裁去右侧桌面、悬浮入口和下方留白，放大真实转换面板。图中尚未选择目录，保持原有未执行状态；四个标签展示已有功能入口，不伪造转换成功或其他标签打开后的内容。','',
       '## 分镜文件','', '| 时间 | 文件 | 来源与性质 |','|---|---|---|']
for name,a,b,im,source in rows:index.append(f'| {tc(a)}—{tc(b)} | [01_主分镜_1080p/{name}.png](01_主分镜_1080p/{name}.png) | {source} |')
index+=['','## 补充镜头','', '| 适用时间 | 文件 | 说明 |','|---|---|---|']
for name,a,b,im,source in extras:index.append(f'| {tc(a)}—{tc(b)} | [02_补充分镜_1080p/{name}.png](02_补充分镜_1080p/{name}.png) | {source} |')
index+=['','## 使用说明','',
        '- 01—10 为主画面；补充镜头用于同一时段内切换，不叠加到 115 秒之外。',
        '- 03 的输入框是静态排版示意；04、05 为流程说明图，不是已发生的产品操作录像。06 的实时事件、运行日志仅为功能标签，右侧截图实际展示工作台。',
        '- 正式视频若需要展现真实模板推荐、参数追问、资源配置、事件和日志的操作细节，仍需补录相应界面；现有静态示意可用于审核版面与叙事。',
        '- 07c、07d 是 01:17—01:20 的两种备选画面；建议使用 07c，下一步建议由左侧摘要卡片呈现。',
        '- 图片以 PNG 原文件为准，不从 JPG 总览或聊天缩略图截图制作。原始截图与局部裁切已分别存入 03_原始素材、04_裁切素材。']
index += ['', '## 平台实截已补充', '',
          '- 05_平台实截：保存首页、VASP 转换、PYATB Input、ABACUS INPUT、金属熔点模板检索共 5 张真实截图。',
          '- 第 04 镜前 4 秒使用 04a_金属熔点模板实截，再切关键输入说明图；无需模板详情。',
          '- 第 09 镜依次使用工具箱转换面板（01:34—01:38）、PYATB 配置（01:38—01:40）、ABACUS 配置（01:40—01:42）、引擎示意（01:42—01:45）。',
          '- 当前素材足够制作图文演示版本，不再要求补拍。原脚本中的真实交互补拍仅为可选增强。']
(ASSETS/'素材索引与使用说明.md').write_text('\n'.join(index),encoding='utf-8')
manifest={'size':[1920,1080],'subtitles':False,'duration':115,'main':[{'file':f'01_主分镜_1080p/{n}.png','start':a,'end':b,'source':s} for n,a,b,im,s in rows], 'extras':[{'file':f'02_补充分镜_1080p/{n}.png','start':a,'end':b,'source':s} for n,a,b,im,s in extras]}
(ASSETS/'素材索引.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
gallery=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ABACUSLab V4 分镜素材</title><style>body{margin:0;background:#edf0f7;color:#15203b;font:18px "Microsoft YaHei",sans-serif}main{max-width:1440px;margin:auto;padding:36px}section{margin:40px 0}img{width:100%;border-radius:12px}p,small{color:#69758d}a{color:#5865ed}</style><main><h1>ABACUSLab · 115 秒金属熔点案例</h1><p>无字幕素材审查。点击图片查看原图；补充镜头在同一段内切换。</p>']
for name,a,b,im,source in rows:
    rel=f'01_主分镜_1080p/{name}.png'
    gallery.append(f'<section><h2>{name} <small>{tc(a)}—{tc(b)}</small></h2><p>{source}</p><a href="{rel}"><img src="{rel}" loading="lazy"></a>')
    for en,ea,eb,ei,es in extras:
        if en[:2]==name[:2]:
            er=f'02_补充分镜_1080p/{en}.png'
            gallery.append(f'<details><summary>{en} · {es}</summary><a href="{er}"><img src="{er}" loading="lazy"></a></details>')
    gallery.append('</section>')
gallery.append('</main></html>')
(ASSETS/'逐张审查.html').write_text('\n'.join(gallery),encoding='utf-8')
with zipfile.ZipFile(ROOT/'03_图片素材_V4_无字幕.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in ASSETS.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
assert rows[0][1]==0 and rows[-1][2]==115
assert all(x[2]==y[1] for x,y in zip(rows,rows[1:]))
for name,a,b,im,source in rows+extras:assert im.size==(1920,1080)
print(json.dumps({'main':len(rows),'extras':len(extras),'output':str(ASSETS)},ensure_ascii=False))
