from pathlib import Path
import subprocess,sys,json,re
from PIL import Image,ImageDraw,ImageFont
script_dir=Path(__file__).resolve().parent
if script_dir.name=='制作文件':
    root=script_dir.parent.parent
    pack=script_dir.parent
else:
    root=script_dir.parent.parent
    pack=script_dir.parent
base=root
sys.path.insert(0,str(base/'packages'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
clips=sorted((pack/'03_新增动画').glob('*.mp4'))
results=[]
for path in clips:
    info=subprocess.run([ff,'-hide_banner','-i',str(path)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
    m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',info);duration=int(m[1])*3600+int(m[2])*60+float(m[3]) if m else None
    if 'Video: h264' not in info or '1920x1080' not in info:raise RuntimeError(f'Bad video stream: {path}')
    subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(path),'-f','null','NUL'],check=True)
    preview=pack/'05_预览与索引'/f'{path.stem}.jpg'
    if not preview.exists():raise FileNotFoundError(preview)
    results.append({'file':str(path.relative_to(pack)),'seconds':duration,'resolution':'1920x1080','decode':'pass'})
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
cols=2;cw,ch=960,565
sheet=Image.new('RGB',(cols*cw,((len(clips)+cols-1)//cols)*ch),'#081329');d=ImageDraw.Draw(sheet)
for i,path in enumerate(clips):
    im=Image.open(pack/'05_预览与索引'/f'{path.stem}.jpg').convert('RGB');im.thumbnail((cw-30,ch-65))
    x=(i%cols)*cw+15;y=(i//cols)*ch+10
    sheet.paste(im,(x+(cw-30-im.width)//2,y));d.text((x,y+ch-49),path.stem,font=font,fill='white')
contact=pack/'05_预览与索引/新增动画总览.jpg';sheet.save(contact,quality=91)
report={'animation_count':len(results),'total_seconds':sum(r['seconds'] for r in results),'all_decode_checks_passed':True,'animations':results,'contact_sheet':str(contact)}
(pack/'05_预览与索引/成品核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
