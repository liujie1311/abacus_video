"""Render static review artwork from the existing local project assets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json
import zipfile

BASE = Path(__file__).resolve().parents[1]
SRC = BASE.parent
OUT = BASE / 'revisions' / 'review_images_v2_no_subtitles'
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1920, 1080
BLUE, INK, MUTED, TEAL = '#5865ed', '#15203b', '#69758d', '#46b9ae'
FONTS = {}

def font(size, bold=False):
    key = size, bold
    if key not in FONTS:
        FONTS[key] = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc', size)
    return FONTS[key]

def text(im, xy, value, size=32, color=INK, bold=False, anchor=None):
    ImageDraw.Draw(im).text(xy, value, font=font(size, bold), fill=color, anchor=anchor)

def box(im, rect, fill='white', radius=20, outline=None, width=1):
    ImageDraw.Draw(im).rounded_rectangle(rect, radius, fill=fill, outline=outline, width=width)

def fit(im, src, rect):
    x, y, w, h = rect
    obj = src.copy()
    obj.thumbnail((w, h), Image.Resampling.LANCZOS)
    im.paste(obj, (x + (w - obj.width)//2, y + (h - obj.height)//2))

def open_asset(name):
    return Image.open(SRC / name).convert('RGB')

raw_logo = open_asset('86a62f81-69e0-4354-a45c-8c812c4133d6.png')
def cut_logo(rect):
    arr = np.array(raw_logo.crop(rect).convert('RGBA'))
    arr[np.min(arr[:, :, :3], axis=2) > 245, 3] = 0
    return Image.fromarray(arr)
LOGO = cut_logo((35, 12, 348, 106))
ICON = cut_logo((35, 12, 126, 106))
AGENT = open_asset('16e10cf0-f4ca-4407-8d2a-8cb7321086a3.png')
# Update the visible product positioning in the review artwork only.
ImageDraw.Draw(AGENT).rectangle((760, 725, 1440, 805), fill='white')
text(AGENT, (1095, 743), 'ABACUSLab 材料计算智能体', 43, '#b9212b', True, 'ma')
ANALYSIS = open_asset('17ca551a-694e-46b7-8861-0ff29629ef79.png')
CHART = open_asset('0252131c-9fe3-48d6-9f17-739ffb635336.png').crop((270, 325, 2060, 1390))
OPERATION = Image.open(BASE / 'previews' / '32.0.jpg').convert('RGB').crop((670, 208, 1790, 882))

yy, xx = np.mgrid[0:H, 0:W]
g = np.exp(-((xx-W*.78)**2/(W*.55)**2+(yy-H*.26)**2/(H*.8)**2))
LIGHT = Image.fromarray(np.stack([247-8*g, 249-10*g, 254-g], axis=-1).astype('uint8'))
gd = np.exp(-((xx-W*.73)**2/(W*.6)**2+(yy-H*.4)**2/(H*.8)**2))
DARK = Image.fromarray(np.stack([9+7*gd, 15+12*gd, 30+32*gd], axis=-1).astype('uint8'))

def base(index, dark=False):
    im = (DARK if dark else LIGHT).copy()
    if dark:
        text(im, (86, 49), 'ABACUSLab', 29, '#e4eaff', True)
        text(im, (1835, 56), 'MATERIALS × AI', 19, '#8f9fbc', anchor='ra')
    else:
        logo = LOGO.resize((235, 71), Image.Resampling.LANCZOS)
        im.paste(logo, (70, 30), logo)
        text(im, (1810, 62), '材料计算智能体', 22, MUTED, anchor='ra')
    ImageDraw.Draw(im).line((80, 128, 1840, 128), fill='#27334a' if dark else '#dce2f0')
    text(im, (82, 1016), f'{index:02d} / 07', 19, '#8e9ab0' if dark else MUTED)
    for n in range(7):
        x = 1540+n*42
        box(im, (x, 1032, x+27, 1036), BLUE if n == index-1 else ('#334057' if dark else '#d5dcec'), 2)
    return im

def label(im, value):
    text(im, (90, 165), value, 20, BLUE, True)

def intro():
    im = base(1, True)
    d = ImageDraw.Draw(im)
    for x in range(1000, 1850, 90):
        d.line((x, 215, x, 850), fill='#1d2b45')
    for y in range(225, 860, 80):
        d.line((980, y, 1840, y), fill='#1d2b45')
    text(im, (90, 263), 'MATERIALS COMPUTING', 22, '#8d9aff', True)
    text(im, (85, 352), '材料计算，', 84, 'white', True)
    text(im, (85, 470), '从一句话开始', 82, '#98a5ff', True)
    text(im, (91, 685), 'ABACUSLab', 34, 'white', True)
    text(im, (91, 744), '——让材料计算更简单', 34, '#b5c2dc')
    box(im, (1010, 327, 1800, 665), '#16223e', 28, '#354565', 2)
    text(im, (1052, 369), '说出你的计算目标', 25, '#a7b5d3')
    text(im, (1052, 444), '我想计算一下金属熔断', 40, 'white', True)
    cursor_x = 1064 + d.textlength('我想计算一下金属熔断', font=font(40, True))
    d.line((cursor_x, 455, cursor_x, 497), fill='#98a5ff', width=3)
    box(im, (1700, 562, 1760, 622), BLUE, 30)
    text(im, (1730, 564), '↑', 38, 'white', anchor='ma')
    for j, value in enumerate(['一句话', '计算思路', '结果分析']):
        x = 1012 + 270*j
        box(im, (x, 724, x+245, 788), '#15213b', 16, '#30415f')
        text(im, (x+122, 738), value, 26, '#c4cfff', anchor='ma')
        if j < 2:
            text(im, (x+257, 739), '→', 24, '#91a0ff', anchor='ma')
    return im

def question():
    im = base(2)
    label(im, '01  /  自然语言交互')
    text(im, (89, 292), '说出你的', 63, INK, True)
    text(im, (89, 390), '材料计算需求', 63, BLUE, True)
    text(im, (94, 570), '用自然语言，描述计算目标', 28, MUTED)
    text(im, (94, 628), '让一句话成为计算的起点', 28, MUTED)
    panel = AGENT.crop((74, 30, 2115, 1710)).resize((1050, 724), Image.Resampling.LANCZOS)
    box(im, (746, 178, 1828, 934), '#dfe4f1', 26)
    im.paste(panel, (762, 194))
    # The enlarged input is a callout based on the existing screenshot.
    box(im, (910, 744, 1696, 891), 'white', 0)
    box(im, (703, 618, 1813, 803), 'white', 22, '#b9212b', 3)
    text(im, (740, 654), '我想计算一下金属熔断', 43, INK)
    text(im, (741, 748), '附件    知识库', 20, MUTED)
    box(im, (1725, 720, 1781, 776), '#bb252e', 28)
    text(im, (1753, 720), '↑', 36, 'white', anchor='ma')
    text(im, (790, 854), '从描述需求开始', 23, BLUE)
    return im

def operation():
    im = base(3)
    label(im, '02  /  平台操作实录')
    text(im, (89, 290), '从需求', 62, INK, True)
    text(im, (89, 387), '到计算思路', 58, BLUE, True)
    for j, value in enumerate(['理解目标', '分析参数', '梳理流程']):
        y = 552+j*85
        box(im, (92, y, 520, y+62), 'white', 15, '#dce2f0')
        text(im, (116, y+12), f'{j+1:02d}', 26, BLUE, True)
        text(im, (174, y+11), value, 28, INK, True)
    box(im, (648, 189, 1812, 901), '#dce2ee', 24)
    im.paste(OPERATION, (670, 208))
    return im

def charts():
    im = base(4)
    label(im, '03  /  数据可视化')
    text(im, (88, 225), '复杂数据', 58, INK, True)
    text(im, (88, 310), '直观呈现', 58, BLUE, True)
    text(im, (92, 444), '不同温度下的', 27, MUTED)
    text(im, (92, 489), '均方位移（MSD）', 27, MUTED)
    for y, col, head, detail in [(587, '#70ac37', '1600 K', 'MSD 随时间上升'), (723, '#54206b', '300 K', 'MSD 呈平台')]:
        box(im, (93, y, 105, y+79), col, 5)
        text(im, (126, y-3), head, 35, col, True)
        text(im, (127, y+48), detail, 25, MUTED)
    box(im, (554, 190, 1836, 915), 'white', 26, '#dfe4ee')
    fit(im, CHART, (580, 201, 1226, 680))
    text(im, (592, 881), '示例结果 · 300 K 与 1600 K 对比', 19, MUTED)
    return im

def results(active=0):
    im = base(5)
    label(im, '04  /  分析与验证')
    text(im, (87, 220), '看懂结果，明确下一步', 54, INK, True)
    choices = [('结论', '300 K 呈平台，1600 K 呈扩散'), ('局限', '两点对比，不等于精确熔点'), ('下一步验证', '加密温度扫描，扩大体系验证')]
    for j, (head, detail) in enumerate(choices):
        y = 344+j*176
        box(im, (88, y, 717, y+145), 'white', 22, BLUE if j == active else '#e0e5f0', 3 if j == active else 1)
        text(im, (118, y+20), head, 35, BLUE if j == active else INK, True)
        text(im, (118, y+82), detail, 25, MUTED)
    box(im, (769, 310, 1839, 901), 'white', 24, '#dfe4f1')
    text(im, (805, 339), ['分析结论', '结果的适用范围', '建议的下一步'][active], 25, BLUE, True)
    crops = [(190, 75, 1470, 290), (190, 320, 1470, 785), (190, 815, 1470, 1085)]
    fit(im, ANALYSIS.crop(crops[active]), (802, 398, 1004, 414))
    text(im, (803, 857), 'AI 分析原文 · 局部放大', 19, MUTED)
    return im

def montage():
    im = base(6)
    label(im, '05  /  流程回顾')
    text(im, (960, 226), '从一句话，到结果分析', 56, INK, True, 'ma')
    names = ['提出需求', '查看图表', '理解结果']
    secondary = ['AI 对话', '数据图表', '结果分析']
    for i in range(3):
        x = 102+i*590
        box(im, (x, 360, x+534, 850), 'white', 24, '#d9dff0', 2)
        box(im, (x+22, 384, x+512, 712), '#f7f8fd', 16)
        if i == 0:
            text(im, (x+267, 421), 'ABACUSLab', 29, BLUE, True, 'ma')
            box(im, (x+48, 512, x+486, 643), 'white', 15, '#b9212b', 2)
            text(im, (x+69, 535), '我想计算一下金属熔断', 28, INK)
            text(im, (x+456, 593), '↑', 27, '#b9212b', True, 'ma')
        elif i == 1:
            fit(im, CHART, (x+30, 395, 474, 304))
        else:
            for j, value in enumerate(['分析结论', '说明局限', '验证建议']):
                y = 416+j*89
                box(im, (x+49, y, x+485, y+62), 'white', 12, '#e0e5f1')
                text(im, (x+74, y+13), f'0{j+1}', 24, BLUE, True)
                text(im, (x+141, y+12), value, 27, INK, True)
        text(im, (x+267, 737), names[i], 35, BLUE, True, 'ma')
        text(im, (x+267, 793), secondary[i], 22, MUTED, anchor='ma')
        if i < 2:
            text(im, (x+561, 560), '→', 38, BLUE, anchor='ma')
    return im

def outro():
    im = LIGHT.copy()
    icon = ICON.resize((104, 108), Image.Resampling.LANCZOS)
    im.paste(icon, (908, 190), icon)
    text(im, (960, 333), 'ABACUSLab', 88, BLUE, True, 'ma')
    text(im, (960, 462), '材料计算智能体', 38, INK, True, 'ma')
    ImageDraw.Draw(im).line((808, 548, 1112, 548), fill='#c5cff2', width=2)
    text(im, (960, 594), '让材料计算更简单', 65, INK, True, 'ma')
    text(im, (960, 742), '从一句话开始', 34, BLUE, anchor='ma')
    return im

scenes = [
    ('01_开场', '00:00–00:05', intro()),
    ('02_自然语言提问', '00:05–00:14', question()),
    ('03_平台操作', '00:14–00:24', operation()),
    ('04_数据可视化', '00:24–00:35', charts()),
    ('05_分析与验证', '00:35–00:45', results()),
    ('06_流程回顾', '00:45–00:54', montage()),
    ('07_品牌片尾', '00:54–01:00', outro()),
]
for name, timecode, im in scenes:
    im.save(OUT / f'{name}.png')
results(1).save(OUT / '05b_局限说明.png')
results(2).save(OUT / '05c_验证建议.png')

contact = Image.new('RGB', (1980, 2580), '#e8ecf5')
text(contact, (40, 24), 'ABACUSLab｜60 秒宣传片 · 分镜审查 V2 · 无字幕版', 38, INK, True)
text(contact, (40, 85), '材料计算，从一句话开始。    1920 × 1080 / 7 个分镜', 25, MUTED)
for i, (name, timecode, im) in enumerate(scenes):
    x, y = 30+(i%2)*975, 150+(i//2)*605
    text(contact, (x+8, y), f'{name.replace("_", "  ")}    {timecode}', 27, INK, True)
    thumb = im.resize((945, 532), Image.Resampling.LANCZOS)
    contact.paste(thumb, (x, y+39))
# Put concise review information in the unused eighth tile.
x, y = 1035, 2020
text(contact, (x, y), '本版修改', 35, INK, True)
for j, value in enumerate(['01  开场改为“从一句话开始”', '02  删除模板库介绍及模板卡片', '03  定位统一为“材料计算智能体”', '04  片尾：让材料计算更简单', '05  全片取消配音字幕']):
    text(contact, (x, y+79+j*62), value, 27, MUTED)
contact.save(OUT / '00_分镜总览.jpg', quality=95)

manifest = {'size': [1920,1080], 'subtitles': False, 'scenes': [{'file': f'{n}.png', 'time': t} for n,t,_ in scenes],
            'additional': ['05b_局限说明.png', '05c_验证建议.png'],
            'note': 'Static review artwork. The input and summary are designed callouts; operation and scientific plots use existing project assets.'}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

gallery = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ABACUSLab 分镜审查</title>',
           '<style>body{margin:0;background:#edf0f7;color:#15203b;font:18px "Microsoft YaHei",sans-serif}main{max-width:1440px;margin:auto;padding:36px}h1{font-size:30px}section{margin:36px 0}img{width:100%;display:block;border-radius:12px;box-shadow:0 8px 40px #15203b15}p{color:#69758d}a{color:#5865ed}</style><main>',
           '<h1>ABACUSLab · 60 秒宣传片分镜审查 V2 · 无字幕版</h1><p>7 个分镜，1920 × 1080。点击图片查看原图。第 5 镜另附局限与验证建议两个状态。全片取消配音字幕，保留画面标题、界面文字及图表标注。</p>']
for n,t,_ in scenes:
    gallery.append(f'<section><h2>{n.replace("_", " · ")} <small>{t}</small></h2><a href="{n}.png"><img src="{n}.png"></a></section>')
    if n.startswith('05_'):
        for other in ['05b_局限说明', '05c_验证建议']:
            gallery.append(f'<details><summary>{other}</summary><a href="{other}.png"><img src="{other}.png"></a></details>')
gallery.append('</main></html>')
(OUT / '审查画廊.html').write_text('\n'.join(gallery), encoding='utf-8')
zip_path = OUT.parent / 'ABACUSLab_分镜素材图_V2_无字幕.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        z.write(p, arcname=f'ABACUSLab_分镜素材图_V2_无字幕/{p.name}')
for n,t,im in scenes:
    assert im.size == (1920,1080)
print(json.dumps({'output': str(OUT), 'images': 9, 'zip': str(zip_path)}, ensure_ascii=False))
