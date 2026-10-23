"""Build the separated V3 scripts and subtitle-free review assets."""
from pathlib import Path
import json
import shutil
import zipfile
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE / '交付_V3_含模板_无字幕'
SPEECH = ROOT / '01_演讲稿'
STORY = ROOT / '02_分镜脚本'
ASSETS = ROOT / '03_图片素材'
MAIN = ASSETS / '01_主分镜_1080p'
EXTRA = ASSETS / '02_补充分镜_1080p'
RAW = ASSETS / '03_原始截图'
CARDS = ASSETS / '04_模板卡片原像素'
for folder in [SPEECH, STORY, MAIN, EXTRA, RAW, CARDS]:
    folder.mkdir(parents=True, exist_ok=True)

sources = [
    (Path('C:/Users/13118/AppData/Local/Temp/codex-clipboard-50901e85-d9f7-40e0-8b07-a226d5e88d51.png'), '模板库全景_3450x1701.png'),
    (Path('C:/Users/13118/AppData/Local/Temp/codex-clipboard-8fd2ce7e-672e-4a60-9fbb-a7527d67462d.png'), '模板卡片_3009x1245.png'),
]
for source, name in sources:
    shutil.copy2(source, RAW / name)
full = Image.open(RAW / sources[0][1]).convert('RGB')
detail = Image.open(RAW / sources[1][1]).convert('RGB')
assert full.size == (3450, 1701)
assert detail.size == (3009, 1245)

# Reuse the reviewed style and real data, without executing the V2 export block.
style_path = BASE / 'revisions' / 'render_review_images.py'
style = style_path.read_text(encoding='utf-8').split('\nscenes = [', 1)[0]
style = style.replace("OUT = BASE / 'revisions' / 'review_images_v2_no_subtitles'", "OUT = BASE / '交付_V3_含模板_无字幕' / '03_图片素材'")
style = style.replace("f'{index:02d} / 07'", "f'{index:02d} / 08'")
style = style.replace('range(7)', 'range(8)').replace('1540+n*42', '1500+n*42')
for name, old, new in [('question',2,3),('operation',3,4),('charts',4,5),('results',5,6)]:
    args = 'active=0' if name == 'results' else ''
    style = style.replace(f'def {name}({args}):\n    im = base({old})', f'def {name}({args}):\n    im = base({new})')
for before, after in [('01  /  自然语言交互','02  /  自然语言交互'),('02  /  平台操作实录','03  /  平台操作实录'),('03  /  数据可视化','04  /  数据可视化'),('04  /  分析与验证','05  /  分析与验证')]:
    style = style.replace(before, after)
ns = {'__file__': str(style_path), '__name__': 'review_style'}
exec(compile(style, str(style_path), 'exec'), ns)
base, label, text, box, fit = [ns[x] for x in ['base','label','text','box','fit']]
BLUE, INK, MUTED = [ns[x] for x in ['BLUE','INK','MUTED']]

crop_specs = [
    ('01_自洽场计算_SCF', full, (334,197,752,674)),
    ('02_原子位置弛豫_Relax', full, (1220,197,1638,674)),
    ('03_分子动力学_MD', full, (2104,197,2522,674)),
    ('04_态密度_DOS', detail, (21,25,495,557)),
    ('05_反常霍尔电导_AHC', detail, (21,587,495,1119)),
    ('06_联合态密度_JDOS', detail, (1531,25,2005,557)),
]
cards = []
for name, src, rect in crop_specs:
    card = src.crop(rect)
    card.save(CARDS / f'{name}.png')
    cards.append(card)

def templates_overview():
    im = base(2)
    label(im, '01  /  计算模板')
    text(im, (90, 212), '丰富模板，覆盖多类材料计算场景', 49, INK, True)
    text(im, (92, 292), '基础计算  /  电子结构  /  输运  /  光学', 27, BLUE)
    box(im, (80, 356, 1840, 967), '#e0e5f0', 24)
    # Overview conveys breadth; the following frames carry readable card detail.
    fit(im, full.crop((325, 112, 3420, 1135)), (96, 370, 1728, 580))
    return im

def templates_cards(basic=False):
    im = base(2)
    label(im, '01  /  计算模板')
    text(im, (90, 212), '从基础计算，到材料性质分析', 52, INK, True)
    text(im, (92, 291), '丰富模板，覆盖多类材料计算场景', 29, MUTED)
    selected = cards[:3] if basic else cards[3:]
    categories = ['自洽场计算', '结构弛豫', '分子动力学'] if basic else ['电子结构', '输运', '光学']
    for i, (card, category) in enumerate(zip(selected, categories)):
        x = 123+i*580
        box(im, (x, 373, x+514, 447), BLUE if i == 0 else 'white', 18, None if i == 0 else '#dce2f0')
        text(im, (x+257, 390), category, 32, 'white' if i == 0 else BLUE, True, 'ma')
        # Paste at 1:1 native resolution: do not upscale or reconstruct UI text.
        im.paste(card, (x+(514-card.width)//2, 469))
    return im

def montage():
    im = base(7)
    label(im, '06  /  一个平台，连接计算流程')
    text(im, (960, 222), '模板、AI、计算、可视化', 54, INK, True, 'ma')
    headings = ['计算模板', 'AI 对话', '计算分析', '数据可视化']
    for i in range(4):
        x = 90+i*445
        box(im, (x, 363, x+405, 852), 'white', 23, '#dce2f0', 2)
        if i == 0:
            fit(im, cards[0], (x+25, 388, 355, 345))
        elif i == 1:
            text(im, (x+202, 423), 'ABACUSLab', 29, BLUE, True, 'ma')
            box(im, (x+23, 521, x+382, 653), 'white', 14, '#b9212b', 2)
            text(im, (x+43, 543), '我想计算一下', 28, INK)
            text(im, (x+43, 590), '金属熔断', 28, INK)
        elif i == 2:
            for j, value in enumerate(['分析结论', '说明局限', '验证建议']):
                y=425+j*88
                box(im, (x+28, y, x+377, y+64), '#f6f7fe', 12)
                text(im, (x+202, y+12), value, 28, INK, True, 'ma')
        else:
            fit(im, ns['CHART'], (x+18, 407, 369, 298))
        text(im, (x+202, 767), headings[i], 32, BLUE, True, 'ma')
        if i<3:
            text(im, (x+425, 561), '→', 31, BLUE, anchor='ma')
    return im

rows = [
    ('01',0,5,'开场','材料计算，从一句话开始。','深蓝背景，先出现“材料计算”，再出现“从一句话开始”；右侧一句需求文字输入。','材料计算，从一句话开始；ABACUSLab ——让材料计算更简单',ns['intro']()),
    ('02',5,15,'计算模板','从基础计算，到电子结构、输运和光学，丰富的模板，覆盖多类材料计算场景。','先用两秒展示模板库总览，再依次切换三张基础计算卡片与三张性质分析卡片。','从基础计算，到材料性质分析；丰富模板，覆盖多类材料计算场景',templates_cards()),
    ('03',15,23,'自然语言提问','告诉 AI 你的计算目标。比如：“我想计算一下金属熔断。”','切到现有对话界面，放大输入框，逐字输入需求并点击发送。','说出你的材料计算需求',ns['question']()),
    ('04',23,31,'平台操作','从理解需求，到分析参数，AI 帮你梳理材料计算思路。','复用原片平台操作实录，聚焦 AI 响应，理解目标、分析参数、梳理流程依次高亮。','从需求，到计算思路；理解目标／分析参数／梳理流程',ns['operation']()),
    ('05',31,40,'数据可视化','让复杂数据直观呈现，对比不同温度下的原子运动，观察材料的变化。','显示原始 MSD 曲线，依次突出 300 K 的平台与 1600 K 的上升趋势。','复杂数据，直观呈现；不同温度下的均方位移（MSD）',ns['charts']()),
    ('06',40,49,'分析与验证','结合结果，给出分析结论，说明局限，为下一步验证提供参考。','依次显示结论、局限和下一步建议，右侧放大对应分析原文。','看懂结果，明确下一步；两点对比，不等于精确熔点',ns['results']()),
    ('07',49,54,'流程回顾','模板、AI、计算、可视化，让流程更连贯。','四张卡片依次出现，展示计算模板、AI 对话、计算分析与数据可视化。','模板、AI、计算、可视化',montage()),
    ('08',54,60,'品牌片尾','ABACUSLab，让材料计算更简单。','浅色品牌收尾，图标、品牌名、定位与口号依次出现，最后两秒稳定停留。','ABACUSLab；材料计算智能体；让材料计算更简单；从一句话开始',ns['outro']()),
]
def tc(s): return f'{s//60:02d}:{s%60:02d}'
for num,a,b,title,voice,shot,screen,im in rows:
    im.save(MAIN / f'{num}_{title}.png')
extras = [
    ('02a_模板库总览',5,7,templates_overview()),
    ('02b_基础计算模板特写',7,11,templates_cards(True)),
    ('06b_局限说明',43,46,ns['results'](1)),
    ('06c_验证建议',46,49,ns['results'](2)),
]
for name,a,b,im in extras: im.save(EXTRA / f'{name}.png')

speech = ['# ABACUSLab 宣传片演讲稿｜V3 含模板·无字幕版','',
          '总时长：60 秒。保留配音，不添加配音字幕。以下时间为拟定剪辑区间，录音后可在段内微调。','',
          '| 段落 | 时间 | 时长 | 演讲／配音内容 |','|---|---|---|---|']
for num,a,b,title,voice,shot,screen,im in rows:
    speech.append(f'| {num} {title} | {tc(a)}—{tc(b)} | {b-a} 秒 | {voice} |')
speech += ['', '配音建议：自然、清晰。开场“从一句话开始”与片尾口号稍作停顿；模板段按“基础计算／电子结构／输运／光学”分组表达。', '', '本文件只包含配音内容。镜头和画面文字见同级“02_分镜脚本”；图片见“03_图片素材”。']
(SPEECH/'演讲稿_含时间.md').write_text('\n'.join(speech),encoding='utf-8')
(SPEECH/'演讲稿_纯配音.txt').write_text('\n\n'.join(row[4] for row in rows)+'\n',encoding='utf-8')

story = ['# ABACUSLab 分镜脚本｜V3 含模板·无字幕版','',
         '规格：60 秒，1920×1080，16:9，建议 30 fps，共 8 个主分镜。无底部配音字幕、无字幕轨。画面标题、品牌口号、界面文字及图表标注保留。','',
         '| 镜号 | 时间 | 镜头及动作 | 屏幕文案 | 对应素材 |','|---|---|---|---|---|']
for num,a,b,title,voice,shot,screen,im in rows:
    story.append(f'| {num} | {tc(a)}—{tc(b)} | {shot} | {screen} | ../03_图片素材/01_主分镜_1080p/{num}_{title}.png |')
story += ['', '## 模板段：分三个镜头展示，保证可读性','',
          '| 时间 | 镜头 | 图片 |','|---|---|---|',
          '| 00:05—00:07 | 总览交代模板种类，轻微横移，不要求观众阅读全部小字。 | 02_补充分镜_1080p/02a_模板库总览.png |',
          '| 00:07—00:11 | 三张基础模板特写：自洽场计算、原子位置弛豫、分子动力学；每张依次强调。 | 02_补充分镜_1080p/02b_基础计算模板特写.png |',
          '| 00:11—00:15 | 三张性质模板特写：态密度、反常霍尔电导、联合态密度；对应电子结构、输运、光学。 | 01_主分镜_1080p/02_计算模板.png |',
          '', '## 分析段：三个状态','',
          '- 00:40—00:43：06_分析与验证.png，显示结论。',
          '- 00:43—00:46：06b_局限说明.png，说明两点对比不是精确熔点。',
          '- 00:46—00:49：06c_验证建议.png，显示温度扫描、扩大体系等建议。',
          '', '## 清晰度与素材使用','',
          '- 模板原图分别为 3450×1701 和 3009×1245，已单独保存；特写从原图裁切，以原像素 1:1 放入 1080p 画面。',
          '- 特写只展示三张卡片，不把整页缩小后再放大；原图中被界面省略号截断的内容不补写、不猜测。',
          '- 卡片名、分类标题为重点阅读信息；类别标题单独排版，截图保持原有比例。',
          '- 使用 PNG 素材直接剪辑，不要从总览 JPG 或聊天缩略图截取。总览只用于审查。',
          '- 图表和分析使用已有真实素材；300 K／1600 K 仅为示例对比，不宣称测得精确熔点或熔断条件。',
          '- 第 04 镜审查图来自原视频操作画面；正式剪辑应使用原录屏，静态图仅供构图审查。',
          '- 转场建议 0.25—0.35 秒，包含在各镜时间内；模板特写以平移、边框强调为主，避免大幅放大破坏文字清晰度。',
          '', '配音全文另见“01_演讲稿”，本文件不混排配音稿。']
(STORY/'分镜脚本.md').write_text('\n'.join(story),encoding='utf-8')

manifest = {'version':'V3','duration_seconds':60,'width':1920,'height':1080,'subtitles':False,
            'scenes':[{'id':r[0],'start':r[1],'end':r[2],'title':r[3], 'image':f'01_主分镜_1080p/{r[0]}_{r[3]}.png'} for r in rows],
            'template_crops':[{'file':f'04_模板卡片原像素/{name}.png','rect':list(rect),'display_scale':1.0} for name,_,rect in crop_specs]}
(ASSETS/'素材索引.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
asset_lines=['# 图片素材索引｜V3','', '所有主分镜及补充分镜均为 1920×1080 PNG，无配音字幕。','',
             '- 01_主分镜_1080p：8 张主分镜，文件编号与脚本镜号一致。',
             '- 02_补充分镜_1080p：2 张模板段镜头、2 张分析段镜头，共 4 张。',
             '- 03_原始截图：本次提供的两张模板原图，保留原尺寸。',
             '- 04_模板卡片原像素：6 张从原图裁切的卡片，不缩放，可供重排。',
             '- 00_分镜总览.jpg：用于快速审查，不作为视频画面源。',
             '- 审查画廊.html：按时间顺序查看全部 12 张分镜图。','',
             '模板画面属于编辑排版：从真实模板截图取出卡片并组成三列，保留原卡片内容。']
(ASSETS/'素材说明.md').write_text('\n'.join(asset_lines),encoding='utf-8')

contact=Image.new('RGB',(1980,2580),'#e8ecf5')
text(contact,(40,24),'ABACUSLab｜V3 含模板 · 无字幕版',38,INK,True)
text(contact,(40,85),'60 秒 / 8 个分镜 / 主画面 1920 × 1080 / 模板卡片原像素特写',25,MUTED)
for i,row in enumerate(rows):
    num,a,b,title,voice,shot,screen,im=row
    x,y=30+(i%2)*975,150+(i//2)*605
    text(contact,(x+8,y),f'{num}  {title}    {tc(a)}–{tc(b)}',27,INK,True)
    contact.paste(im.resize((945,532),Image.Resampling.LANCZOS),(x,y+39))
contact.save(ASSETS/'00_分镜总览.jpg',quality=95)

sequence=[(MAIN/'01_开场.png',0,5),(EXTRA/'02a_模板库总览.png',5,7),(EXTRA/'02b_基础计算模板特写.png',7,11),(MAIN/'02_计算模板.png',11,15)]
sequence += [(MAIN/f'{r[0]}_{r[3]}.png',r[1],r[2]) for r in rows[2:5]]
sequence += [(MAIN/'06_分析与验证.png',40,43),(EXTRA/'06b_局限说明.png',43,46),(EXTRA/'06c_验证建议.png',46,49)]
sequence += [(MAIN/f'{r[0]}_{r[3]}.png',r[1],r[2]) for r in rows[6:]]
gallery=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ABACUSLab V3 素材审查</title>',
         '<style>body{margin:0;background:#edf0f7;color:#15203b;font:18px "Microsoft YaHei",sans-serif}main{max-width:1440px;margin:auto;padding:36px}section{margin:38px 0}img{width:100%;border-radius:12px}small,p{color:#69758d}a{color:#5865ed}</style><main>',
         '<h1>ABACUSLab · V3 含模板 · 无字幕版</h1><p>按播放顺序列出全部镜头。点击图片查看 1920×1080 原图。演讲稿、分镜脚本、素材分别归档。</p>']
for path,a,b in sequence:
    rel=path.relative_to(ASSETS).as_posix()
    gallery.append(f'<section><h2>{path.stem} <small>{tc(a)}–{tc(b)}</small></h2><a href="{rel}"><img loading="lazy" src="{rel}"></a></section>')
gallery.append('</main></html>')
(ASSETS/'审查画廊.html').write_text('\n'.join(gallery),encoding='utf-8')

index=['# ABACUSLab 最新审查交付｜V3 含模板·无字幕版','',
       '本版恢复模板介绍，继续使用“材料计算”定位和“从一句话开始”的开场；保留配音，取消配音字幕。总时长 60 秒。','',
       '| 内容 | 文件位置 |','|---|---|',
       '| 演讲稿（带时间） | [01_演讲稿/演讲稿_含时间.md](01_演讲稿/演讲稿_含时间.md) |',
       '| 纯配音文本 | [01_演讲稿/演讲稿_纯配音.txt](01_演讲稿/演讲稿_纯配音.txt) |',
       '| 分镜脚本 | [02_分镜脚本/分镜脚本.md](02_分镜脚本/分镜脚本.md) |',
       '| 图片总览 | [03_图片素材/00_分镜总览.jpg](03_图片素材/00_分镜总览.jpg) |',
       '| 逐张审查 | [03_图片素材/审查画廊.html](03_图片素材/审查画廊.html) |',
       '| 素材说明 | [03_图片素材/素材说明.md](03_图片素材/素材说明.md) |',
       '', '图片按镜号命名：8 张主分镜、4 张补充分镜、2 张模板原图、6 张原像素卡片。模板段为总览、基础计算特写、材料性质特写三种画面。',
       '', '这是供审查的文案与静态图片交付。配音时长为拟定安排，最终视频尚未重新合成。旧版文件仍在 revisions 中，当前请以本目录 V3 为准。']
(ROOT/'00_从这里开始.md').write_text('\n'.join(index),encoding='utf-8')

for folder in [SPEECH,STORY,ASSETS]:
    with zipfile.ZipFile(ROOT/f'{folder.name}.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in folder.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())

assert rows[0][1]==0 and rows[-1][2]==60
assert all(a[2]==b[1] for a,b in zip(rows,rows[1:]))
assert all(a[2]==b[1] for a,b in zip(sequence,sequence[1:]))
for p in list(MAIN.glob('*.png'))+list(EXTRA.glob('*.png')):
    with Image.open(p) as im: assert im.size==(1920,1080)
print(json.dumps({'root':str(ROOT),'main_images':len(list(MAIN.glob('*.png'))),'extra_images':len(list(EXTRA.glob('*.png'))),'card_crops':len(cards),'seconds':60},ensure_ascii=False))
