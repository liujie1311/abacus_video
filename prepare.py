from pathlib import Path
from PIL import Image, ImageDraw
import os, shutil, json
root=Path('C:/Users/PC/Desktop/\u7d20\u6750/\u7d20\u6750')
out=Path(__file__).parent
canvas=Image.new('RGB',(1400,1000),'#dddddd')
d=ImageDraw.Draw(canvas)
for i,p in enumerate(root.glob('*.png')):
 im=Image.open(p).convert('RGB'); print(p.name,im.size)
 im.thumbnail((690,450)); x=(i%2)*700; y=(i//2)*500
 canvas.paste(im,(x,y+35)); d.text((x+10,y+10),p.name,fill='black')
canvas.save(out/'assets_contact.jpg')
for base in ['C:/ffmpeg','C:/Program Files','C:/Users/PC/AppData/Local/Microsoft/WinGet/Packages','C:/Users/PC/AppData/Local/Programs','C:/Users/PC/.cache']:
 for r,ds,fs in os.walk(base):
  for f in fs:
   if f.lower() in ['ffmpeg.exe','ffprobe.exe','python.exe','espeak.exe']: print(os.path.join(r,f))
print('FONTS',[p.name for p in Path('C:/Windows/Fonts').glob('*') if any(s in p.name.lower() for s in ['msyh','simhei','segoe','deng'])])
