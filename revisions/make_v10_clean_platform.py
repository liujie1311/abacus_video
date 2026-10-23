"""V9 revision: remove editorial small labels and show the supplied full platform."""
import json
import shutil
import sys
from PIL import Image
import make_v9_reorder as previous

s, v, m = previous.s, previous.v, previous.m
ROOT = previous.BASE / '交付_V10_60秒_去小字_更新平台画面'
OUT = ROOT / '04_视频成片'
WORK = OUT / '制作文件'
ASSETS = ROOT / '03_素材'
STILLS = ASSETS / '关键帧'
for folder in [ROOT/'01_演讲稿', ROOT/'02_分镜脚本', WORK, STILLS, ASSETS/'原始素材']:
    folder.mkdir(parents=True, exist_ok=True)
SOURCE = previous.DEST
DEST = OUT / 'ABACUSLab_V10_60秒_去小字_更新平台画面_无字幕.mp4'
HOMEFILE = ASSETS/'原始素材/新平台首页_用户图三.png'
if not HOMEFILE.exists():
    shutil.copy2('C:/Users/13118/AppData/Local/Temp/codex-clipboard-897e6208-e8c3-42e6-8f7c-2c788b03555a.png', HOMEFILE)
HOME = Image.open(HOMEFILE).convert('RGB')
REMOVED = {
    '材料结构示意', '平台操作实录', 'AI 分析原文 · 局部放大',
    '流程示意', '示例结果 · 原始曲线逐步展示', '物性类别示意',
    '示例结果 · 300 K / 1600 K', '金属熔点计算 · 执行记录',
    '平台引擎 · 首页实截',
}
original_txt = m.txt
def clean_txt(im, xy, text, *args, **kwargs):
    if text not in REMOVED:
        return original_txt(im, xy, text, *args, **kwargs)
for module in [previous, s, v, m]:
    module.txt = clean_txt

def platform(t):
    im = s.base(1, t)
    # Fit the complete supplied screenshot; subtle movement never crops its edges.
    width = round(1720 + 24*s.smooth(t/2.5))
    height = round(width*HOME.height/HOME.width)
    obj = HOME.resize((width, height), Image.Resampling.LANCZOS)
    x, y = (1920-width)//2, 155+(866-height)//2
    s.rr(im, (x-9,y-9,x+width+9,y+height+9), 'white', 16, '#dce2f0')
    im.paste(obj, (x,y))
    return im

previous.SCENES = [(a,b,platform if a==6 else fn,c) for a,b,fn,c in previous.SCENES]
frame = previous.frame
v.WORK = WORK
v.frame = frame

def docs():
    rows = ['# V10 演讲稿｜60 秒', '', '沿用 V9 男声及音乐；无配音字幕。', '', '| 时间（秒） | 配音 |', '|---|---|']
    rows += [f'| {a}—{b} | {text} |' for a,b,text in previous.ENTRIES]
    (ROOT/'01_演讲稿/演讲稿_含时间.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    (ROOT/'01_演讲稿/演讲稿_纯配音.txt').write_text('\n\n'.join(text for _,_,text in previous.ENTRIES)+'\n',encoding='utf-8')
    descriptions = [
        '保留原六秒晶格旋转开场；ABACUSLab，AI 驱动的材料计算与设计平台。去除材料结构示意小字。',
        '用户图三完整平台截图，轻微推进；替换原引擎标志卡片画面。',
        '常用计算模板总览与卡片展示。',
        '以研究金属熔化行为为例，自然语言逐字输入。',
        'AI 理解需求、规划流程、配置参数、组织计算。',
        '真实任务执行状态；去除额外执行记录小字。',
        '300 K 与 1600 K 的 MSD 曲线动态绘制，保留坐标与图例；去除额外示例结果小字。',
        '展示主要发现、结论局限与验证建议；去除原文局部放大小字。',
        'ABACUSLab，让材料计算更简单。',
    ]
    rows = ['# V10 分镜脚本', '', '60 秒，1920×1080，30 fps；保持浅色动态风格，镜头间连续叠化，无黑场、无配音字幕。', '', '| 时间（秒） | 画面 |', '|---|---|']
    rows += [f'| {a}—{b} | {description} |' for (a,b,_,_),description in zip(previous.SCENES,descriptions)]
    rows += ['', '仅删除额外叠加的辅助标注。平台截图原有文字、主标题、图表坐标、科学局限说明保留。']
    (ROOT/'02_分镜脚本/分镜脚本_含时间.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    (WORK/'修改记录.json').write_text(json.dumps({'base':str(SOURCE),'removed_labels':sorted(REMOVED),'replacement_interval':[6,8.5],'replacement_source':str(HOMEFILE),'audio':'V9 audio stream copied unchanged'},ensure_ascii=False,indent=2),encoding='utf-8')

def previews():
    docs()
    times = [2,5,7.5,11,18,26,35,42,50,57]
    sheet = Image.new('RGB',(800,1280),'#e9edf5')
    for i,t in enumerate(times):
        im = frame(t)
        im.save(STILLS/f'{t:04.1f}s.png')
        x,y = i%2*400,i//2*256
        original_txt(sheet,(x+10,y+4),f'{t:g}s',20,s.INK)
        sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),(x,y+30))
    sheet.save(ASSETS/'分镜总览.jpg',quality=95)
    print('Previews ready',flush=True)

def final():
    m.run(['-y','-i',str(WORK/'picture.mp4'),'-i',str(SOURCE),'-map','0:v:0','-map','1:a:0','-c','copy','-t','60','-movflags','+faststart',str(DEST)])
    m.run(['-y','-i',str(DEST),'-t','6','-c:v','libx264','-crf','18','-preset','fast','-c:a','aac','-b:a','192k','-movflags','+faststart',str(ASSETS/'开场6秒_去小字.mp4')])
    print('DONE',DEST,flush=True)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv)>1 else 'previews'
    if mode == 'previews': previews()
    elif mode == 'picture': v.picture(60)
    elif mode == 'final': final()
