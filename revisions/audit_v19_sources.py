from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import subprocess,io
B=Path(__file__).resolve().parent.parent
R=B/'交付_V19_五分钟_去重与稳定重剪';(R/'制作文件').mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
hist=B/'宣传片方案_210秒_20261019/04_平台截图素材/用户手册历史截图'
paths=list(hist.glob('*.png'))+list(B.parent.glob('*.png'))
sheet=Image.new('RGB',(1800,((len(paths)+2)//3)*380),'#f5f7fe')
for i,p in enumerate(paths):
    im=ImageOps.contain(Image.open(p).convert('RGB'),(590,330))
    x=i%3*600;y=i//3*380;sheet.paste(im,(x+(600-im.width)//2,y));ImageDraw.Draw(sheet).text((x+6,y+334),p.name[:32],font=font,fill='#182744')
sheet.save(R/'制作文件/可用原始画面核查.jpg',quality=94)
ff=B/'packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
sources=list(B.parent.glob('*.mp4'))
for k,p in enumerate(sources):
    sheet=Image.new('RGB',(1600,3*250),'#f5f7fe')
    for i,t in enumerate([.2,.8,1.5,2,2.7,3.5,4.2,5,5.8,6.5,7.5,8.5]):
        raw=subprocess.run([str(ff),'-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=390:220','-f','image2pipe','-vcodec','png','pipe:1'],capture_output=True).stdout
        if not raw:continue
        im=Image.open(io.BytesIO(raw));x=i%4*400;y=i//4*250;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+6,y+221),f'{t:.1f}s',font=font,fill='#182744')
    sheet.save(R/f'制作文件/录屏{k+1}核查.jpg',quality=92)
print(R)
