from pathlib import Path
import sys,subprocess,json
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent;sys.path.insert(0,str(BASE/'packages'));import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();RAW=ROOT/'素材/网络原始素材';CROP=ROOT/'素材/精选实景'
CROPS={'energy':(.15,.13,.89,.90),'wafer':(.14,.10,.93,.89),'composite':(.02,.44,.57,.96),'manufacture':(.35,.34,.99,.87),'prep':(.04,.40,.81,.99),'sem':(.01,.06,.55,.82),'xps':(.025,.21,.55,.96),'sample':(.05,.46,.60,.73)}
records=[]
for key,box in CROPS.items():
    im=Image.open(RAW/(key+'.jpg')).convert('RGB');px=tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box));out=im.crop(px);out.save(CROP/(key+'.jpg'),quality=96);records.append({'key':key,'crop':px,'source':str(RAW/(key+'.jpg')),'treatment':'裁切仪器、材料和手部细节；不把公开素材中的人物或机构呈现为本平台团队'})
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22);sheet=Image.new('RGB',(1600,600),'#f5f7fe')
for i,key in enumerate(CROPS):
    im=ImageOps.contain(Image.open(CROP/(key+'.jpg')),(392,260));x=i%4*400;y=i//4*300;sheet.paste(im,(x+(400-im.width)//2,y));ImageDraw.Draw(sheet).text((x+10,y+265),key,font=font,fill='#14223f')
sheet.save(ROOT/'精选实景裁切.jpg',quality=95);(ROOT/'素材/裁切记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
v16=BASE/'交付_V16_210秒_MSD固液态对照标注/ABACUSLab_V16_3分30秒_MSD状态说明.mp4'
reference=Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/msg/video/2026-10/0da312f692b46fe2d0afac91646097cf.mp4')
CLIPS=[('old_home',v16,8,6),('old_templates',v16,15,8),('old_cards',v16,24,7),('old_reuse',v16,32,8),('old_project',v16,41,6),('old_workflow',v16,61,6),('old_config',v16,81,9),('old_pdos',v16,101,8),('old_optical',v16,111,8),('old_analysis',v16,171,8),('old_suggest',v16,180,7),('old_recap',v16,196,5),('old_msd',v16,161,8),('ref_prompt',reference,17,7),('ref_plan',reference,26,7),('ref_task',reference,36,2),('test',RAW/'mechanical.mp4',12,8),('test2',RAW/'mechanical.mp4',39,6)]
for key,path,start,dur in CLIPS:
    folder=ROOT/'素材/视频帧'/key;folder.mkdir(exist_ok=True)
    if len(list(folder.glob('*.jpg')))<dur*15:
        subprocess.run([FF,'-v','error','-y','-ss',str(start),'-i',str(path),'-t',str(dur),'-vf','fps=15,scale=1920:1080','-q:v','2',str(folder/'%04d.jpg')],check=True)
    print('PREPARED',key,flush=True)
(ROOT/'素材/复用视频时间索引.json').write_text(json.dumps([{'key':k,'source':str(p),'start':s,'duration':d,'frames_per_second':15} for k,p,s,d in CLIPS],ensure_ascii=False,indent=2),encoding='utf-8')
