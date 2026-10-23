from pathlib import Path
import sys, subprocess, io, json
from PIL import Image, ImageDraw, ImageFont
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
src=Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/temp/RWTemp/2026-10/6ea7a038d3773238854af0517874d6cf/61c75743c8b37a1cf4def0c577fb2979.mp4')
out=BASE/'交付_V5_60秒_AI演示优先/04_视频成片/制作文件'
out.mkdir(parents=True,exist_ok=True)
p=subprocess.run([ff,'-hide_banner','-i',str(src)],capture_output=True)
print(p.stderr.decode('utf-8','replace'))
times=[0,.5,1.5,3,5,10,15,20,25,30,35,40,45,50,55,59]
contact=Image.new('RGB',(1280,800),'#e9edf5')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
for i,t in enumerate(times):
    raw=subprocess.check_output([ff,'-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=320:180','-f','image2pipe','-vcodec','png','pipe:1'])
    if not raw: continue
    im=Image.open(io.BytesIO(raw));x=i%4*320;y=i//4*200
    contact.paste(im,(x,y+20));ImageDraw.Draw(contact).text((x+7,y),f'{t}s',font=font,fill='#15203b')
contact.save(out/'参考视频抽帧.jpg',quality=95)
print(out/'参考视频抽帧.jpg')
