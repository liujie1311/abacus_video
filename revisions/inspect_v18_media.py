from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,re
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'交付_V18_五分钟_按方案实景重制';OUT=ROOT/'素材/网络原始素材'
files=list(OUT.glob('*.jpg'))+list(OUT.glob('*.png'));sheet=Image.new('RGB',(1600,((len(files)+3)//4)*300),'#f5f7fe');f=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
for i,p in enumerate(files):
    im=Image.open(p).convert('RGB');print(p.name,im.size);im=ImageOps.contain(im,(392,260));x=i%4*400;y=i//4*300;sheet.paste(im,(x+(400-im.width)//2,y));ImageDraw.Draw(sheet).text((x+10,y+265),p.name,font=f,fill='#14223f')
sheet.save(ROOT/'网络素材初选.jpg',quality=94)
p=OUT/'NASA_使用说明.html'
if p.exists():
    s=re.sub('<[^>]+>',' ',p.read_text(encoding='utf-8'));s=re.sub(r'\s+',' ',s)
    for q in ['copyright','commercial','endorsement','credit']:
        for m in list(re.finditer(q,s,re.I))[:4]:print(s[max(0,m.start()-130):m.start()+550])
