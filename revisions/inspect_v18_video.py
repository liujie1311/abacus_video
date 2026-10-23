from pathlib import Path
import subprocess,sys,re,io
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'交付_V18_五分钟_按方案实景重制';sys.path.insert(0,str(BASE/'packages'));import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
for key in ['solar','mechanical']:
    p=ROOT/f'素材/网络原始素材/{key}.mp4'
    if not p.exists():continue
    meta=subprocess.run([FF,'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr;print(meta[:800])
    match=re.search(r'Duration: (\d+):(\d+):([\d.]+)',meta);dur=int(match[1])*3600+int(match[2])*60+float(match[3]);times=list(range(0,int(dur)-1,max(1,int(dur/16))))
    sheet=Image.new('RGB',(1600,((len(times)+3)//4)*260),'#f5f7fe')
    for i,t in enumerate(times):
        raw=subprocess.check_output([FF,'-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=392:220','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);im=Image.frombytes('RGB',(392,220),raw)
        x=i%4*400;y=i//4*260;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+10,y+223),f'{key} {t}s',font=font,fill='#14223f')
    sheet.save(ROOT/f'{key}_视频选段.jpg',quality=95)
