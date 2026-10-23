from pathlib import Path
import shutil,json,hashlib
from PIL import Image,ImageDraw,ImageFont

script_dir=Path(__file__).resolve().parent
base=script_dir.parent if script_dir.name=='制作文件' else script_dir
out=base/'五分钟宣传片_补充素材_20261023'
for part in ['01_已有平台素材','02_新增科研场景','03_新增动画','04_真实算例待补','05_预览与索引','制作文件']:
    (out/part).mkdir(parents=True,exist_ok=True)
plan=base/'宣传片方案_210秒_20261019'
sources=list((plan/'06_补充素材与AI复核/原图').glob('*.png'))+list((plan/'05_用户新截图筛选/主选裁切').glob('*.png'))
sources += [plan/'04_平台截图素材/用户手册历史截图/10_能带绘制.png',plan/'04_平台截图素材/用户手册历史截图/12_结构展示.png']
items=[]
for src in sources:
    if not src.exists():continue
    name=('历史手册_' if '历史截图' in str(src) else '')+src.name
    dest=out/'01_已有平台素材'/name
    shutil.copy2(src,dest)
    with Image.open(dest) as im:w,h=im.size
    items.append({'name':name,'source':str(src),'file':str(dest),'size':[w,h],'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'kind':'历史手册截图' if '历史' in name else '用户已有平台截图','use':'独立功能示例；不同任务不拼成同一案例'})
(out/'05_预览与索引/已有素材来源.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
sheet=Image.new('RGB',(1600,((len(items)+2)//3)*350),'#0b1528');d=ImageDraw.Draw(sheet)
for i,r in enumerate(items):
    im=Image.open(r['file']).convert('RGB');im.thumbnail((510,285));x=15+(i%3)*530;y=15+(i//3)*350;sheet.paste(im,(x+(510-im.width)//2,y));d.text((x,y+292),r['name'],font=font,fill='white')
sheet.save(out/'05_预览与索引/已有素材总览.jpg',quality=90)
print(json.dumps({'output':str(out),'copied':len(items),'contact':str(out/'05_预览与索引/已有素材总览.jpg')},ensure_ascii=False))
