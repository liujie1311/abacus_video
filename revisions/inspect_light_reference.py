from pathlib import Path
import subprocess, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageOps
BASE=Path(__file__).resolve().parent.parent
ROOT=BASE/'五分钟宣传片_浅色素材修订_20261023'
OUT=ROOT/'预览与核验'
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
SRC=Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/msg/video/2026-10/0da312f692b46fe2d0afac91646097cf.mp4')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
times=[0,3,7,12,17,22,27,32,37,42,48,56]
sheet=Image.new('RGB',(1600,1020),'#edf2fc')
for i,t in enumerate(times):
    p=OUT/f'参考片_{t:02d}秒.jpg'
    subprocess.run([FF,'-v','error','-y','-ss',str(t),'-i',str(SRC),'-frames:v','1','-q:v','2',str(p)],check=True)
    im=ImageOps.fit(Image.open(p),(520,292))
    x=10+(i%3)*530;y=10+(i//3)*250
    im=ImageOps.fit(im,(510,215))
    sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x,y+217),f'{t:02d} 秒',font=font,fill='#233451')
sheet.save(OUT/'用户参考片_时间线.jpg',quality=92)
print(str(OUT/'用户参考片_时间线.jpg'))
