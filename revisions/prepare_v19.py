from pathlib import Path
import json,subprocess,sys,shutil
from PIL import Image
B=Path(__file__).resolve().parent.parent;R=B/'交付_V19_五分钟_去重与稳定重剪';P=B/'交付_V18_五分钟_按方案实景重制'
for s in ['制作文件','素材','分镜预览','音频']:(R/s).mkdir(parents=True,exist_ok=True)
FF=B/'packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
jobs=[
 ('ai_conditions',B.parent/'屏幕录制 2026-10-15 161830.mp4',1.3,.35,(.249,.16,.766,.81)),
 ('ai_review',B.parent/'屏幕录制 2026-10-16 111243.mp4',3.5,2.0,(.245,.07,.775,.88)),
 ('case_question',Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/msg/video/2026-10/0da312f692b46fe2d0afac91646097cf.mp4'),19.1,4.8,(.211,.225,.790,.922)),
 ('case_plan',Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/msg/video/2026-10/0da312f692b46fe2d0afac91646097cf.mp4'),31.8,1.3,(.208,.225,.787,.851)),
 ('case_task',Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/msg/video/2026-10/0da312f692b46fe2d0afac91646097cf.mp4'),34.3,1.6,(.045,.32,.955,.902))]
records=[]
for key,path,start,length,crop in jobs:
    folder=R/'素材'/key;folder.mkdir(exist_ok=True)
    if not list(folder.glob('*.jpg')) or '--refresh' in sys.argv:
        subprocess.run([str(FF),'-v','error','-y','-ss',str(start),'-i',str(path),'-t',str(length),'-vf','fps=30,scale=1920:1080','-q:v','2',str(folder/'%04d.jpg')],check=True)
    records.append({'key':key,'source':str(path),'start':start,'duration':length,'crop':crop,'frames':round(length*30),'fps':30})
(R/'制作文件/原始镜头索引.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['登录页原始背景.png']:
    shutil.copy2(B/'交付_V13_210秒_登录背景_浅色无进度条/素材'/name,R/'素材'/name)
shutil.copy2(B/'交付_V14_210秒_参考节奏片头/素材/登录卡片_真实截图裁切.png',R/'素材/登录卡片.png')
for p in [R/'素材/登录页原始背景.png',R/'素材/登录卡片.png']:print(p.name,Image.open(p).size,flush=True)
print('READY',len(records),flush=True)
