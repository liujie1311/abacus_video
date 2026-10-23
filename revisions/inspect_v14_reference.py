from pathlib import Path
import sys,subprocess,io,json
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
src=Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/msg/video/2026-10/0da312f692b46fe2d0afac91646097cf.mp4')
out=BASE/'交付_V14_210秒_参考节奏片头/参考分析'
out.mkdir(parents=True,exist_ok=True)
info=subprocess.run([ff,'-hide_banner','-i',str(src)],capture_output=True).stderr.decode('utf-8','replace')
print(info)
times=[0,.25,.5,.75,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,5.9,6.3]
sheet=Image.new('RGB',(1600,4*258),'#edf2fa');font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
for i,t in enumerate(times):
    raw=subprocess.check_output([ff,'-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
    im=Image.open(io.BytesIO(raw)).convert('RGB');im.save(out/f'{t:04.2f}s.jpg',quality=95)
    x=i%4*400;y=i//4*258
    im.thumbnail((400,225));sheet.paste(im,(x+(400-im.width)//2,y+30))
    ImageDraw.Draw(sheet).text((x+8,y+3),f'{t:.2f}s',font=font,fill='#152340')
sheet.save(out/'前6秒逐帧参考.jpg',quality=95)
print(out/'前6秒逐帧参考.jpg')
