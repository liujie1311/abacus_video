from pathlib import Path
import sys,json,subprocess,re
from PIL import Image,ImageDraw,ImageFont
script_dir=Path(__file__).resolve().parent
base=script_dir.parent if script_dir.name=='制作文件' else script_dir
sys.path.insert(0,str(base/'packages'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
out=base/'五分钟宣传片_补充素材_20261023/05_预览与索引'
srcroot=Path(r'C:\Users\13118\Desktop\素材')
files=[]
for p in srcroot.rglob('*'):
    if base in p.parents or not p.is_file():continue
    files.append({'file':str(p),'bytes':p.stat().st_size})
(out/'用户指定目录文件清单.json').write_text(json.dumps(files,ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
reports=[]
for n,p in enumerate(srcroot.glob('*.mp4')):
    meta=subprocess.run([ff,'-hide_banner','-i',str(p)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
    match=re.search(r'Duration: (\d+):(\d+):([\d.]+)',meta)
    duration=int(match[1])*3600+int(match[2])*60+float(match[3]) if match else 0
    sheet=Image.new('RGB',(1440,960),'#102038');d=ImageDraw.Draw(sheet)
    times=[duration*v for v in [.05,.22,.39,.56,.73,.90]]
    for i,t in enumerate(times):
        dest=out/f'原始录屏{n+1}_帧{i+1}.jpg'
        subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=960:-2',str(dest)],check=True)
        im=Image.open(dest);im.thumbnail((700,410));x=10+(i%2)*720;y=10+(i//2)*320;im.thumbnail((700,275));sheet.paste(im,(x,y));d.text((x,y+280),f'{t:.2f}s',font=font,fill='white')
    name=f'原始录屏{n+1}_总览.jpg';sheet.save(out/name,quality=90)
    reports.append({'file':str(p),'duration_seconds':duration,'metadata':meta,'contact':str(out/name)})
(out/'原始录屏检查.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files_outside_project':files,'recordings':[{'file':r['file'],'seconds':r['duration_seconds'],'contact':r['contact']} for r in reports]},ensure_ascii=False,indent=2))
