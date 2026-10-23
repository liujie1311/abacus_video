"""Reference-inspired six-second opening; preserve approved light palette and audio."""
from pathlib import Path
from functools import lru_cache
import sys,math,shutil,json,subprocess,hashlib,time
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import make_v13_light as prev
v=prev.v
BASE=v.BASE;W,H=v.W,v.H;FPS=30
SOURCE=prev.DEST
ROOT=BASE/'交付_V14_210秒_参考节奏片头'
WORK=ROOT/'制作文件';ASSETS=ROOT/'素材'
for p in [ROOT,WORK,ASSETS]:p.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'ABACUSLab_3分30秒_参考片头_浅色男声版.mp4'
REF=Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/msg/video/2026-10/0da312f692b46fe2d0afac91646097cf.mp4')
LOGIN_SCREEN=ASSETS/'用户登录页截图.png'
if not LOGIN_SCREEN.exists():
    shutil.copy2('C:/Users/13118/AppData/Local/Temp/codex-clipboard-eb0f910e-3bf0-4432-a368-2225b3caa42c.png',LOGIN_SCREEN)
source=Image.open(LOGIN_SCREEN).convert('RGB')
card=source.crop(tuple(round(z*(source.width if i%2==0 else source.height)) for i,z in enumerate((.4488,.2771,.6005,.7031))))
card=card.resize((390,round(390*card.height/card.width)),Image.Resampling.LANCZOS).convert('RGBA')
mask=Image.new('L',card.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,card.width-1,card.height-1),8,fill=255);card.putalpha(mask)
card.save(ASSETS/'登录卡片_真实截图裁切.png')
shadow=Image.new('RGBA',(470,card.height+100));ImageDraw.Draw(shadow).rounded_rectangle((40,35,430,35+card.height),13,fill=(45,72,108,65));shadow=shadow.filter(ImageFilter.GaussianBlur(20))
xx=np.arange(W,dtype=np.float32);strength=.18+.77/(1+np.exp((xx-865)/145))
VEIL=Image.new('RGBA',(W,H),'#f2f6fd');VEIL.putalpha(Image.fromarray(np.repeat((strength*255).astype('uint8')[None,:],H,axis=0)))

def reveal(im,s,x,y,size,t,delay,duration,color,bold=True):
    p=v.ease((t-delay)/duration)
    if p<=0:return
    sp=v.sprite(s,size,color,bold).copy()
    # A soft leading edge reveals complete glyphs without a typewriter cursor.
    edge=p*(sp.width+70)-35
    ramp=np.clip((edge-np.arange(sp.width))/65+.5,0,1)
    if p>=.999:ramp[:]=1
    alpha=np.asarray(sp.getchannel('A'),dtype=np.float32)*ramp[None,:]
    sp.putalpha(Image.fromarray(alpha.astype('uint8')))
    im.paste(sp,(round(x+12*(1-p)),round(y+10*(1-p))),sp)

def opening(t):
    # Actual login artwork, with a light text-side veil and a slow camera move.
    p=v.ease(min(t,6)/6);scale=1.012+.018*p
    im=prev.LOGIN.transform((W,H),Image.Transform.AFFINE,(1/scale,0,(W-W/scale)/2-6*p,0,1/scale,(H-H/scale)/2),Image.Resampling.BICUBIC)
    im.paste(VEIL,(0,0),VEIL)
    a=v.ease(t/1.4);cx=1110+round(18*(1-a));cy=245+round(15*(1-a))-round(3*math.sin(t*.65))
    im.paste(shadow,(cx-40,cy-22),shadow);im.paste(card,(cx,cy),card)
    reveal(im,'MATERIALS × AI',111,253,24,t,.08,.7,'#627fab')
    reveal(im,'ABACUSLab',103,331,104,t,.28,1.22,v.BLUE)
    reveal(im,'材料计算与分析',109,498,49,t,1.22,.78,v.INK)
    reveal(im,'一体化研究平台',109,567,49,t,1.77,.76,v.INK)
    reveal(im,'让材料计算更简单',113,706,30,t,2.55,.9,'#5c7398',False)
    return im

@lru_cache(1)
def held_intro():return opening(6)
def first_frames(t):
    if t<6:return opening(t)
    if t<6.85:
        p=v.ease((t-6)/.85)
        old=held_intro().transform((W,H),Image.Transform.AFFINE,(1,0,18*p,0,1,0),Image.Resampling.BILINEAR)
        new=prev.scene('home',t-6,9)
        return Image.blend(old,new,p)
    return prev.frame(t)

def previews():
    times=[0,.4,.8,1.3,1.9,2.6,3.6,5.6,6.2,6.55,6.85,7]
    sheet=Image.new('RGB',(1600,3*255),'#e8eff8')
    for i,t in enumerate(times):
        im=first_frames(t);im.save(WORK/f'opening_{t:.2f}.jpg',quality=95)
        x=i%4*400;y=i//4*255;v.text(sheet,(x+9,y+2),f'{t:.2f}s',20)
        sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),(x,y+30))
    sheet.save(ROOT/'片头与首页衔接预览.jpg',quality=95)
    docs();print('Opening previews ready',flush=True)

def head():
    proc=subprocess.Popen([v.FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-an','-c:v','ffv1','-level','3','-threads','6',str(WORK/'opening_7s.mkv')],stdin=subprocess.PIPE)
    try:
        for i in range(210):
            proc.stdin.write(first_frames(i/FPS).tobytes())
            if i%60==0:print(f'Opening {i/FPS:g}/7 s',flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('Opening render failed')
    print('Opening rendered',flush=True)

def final():
    v.run(['-y','-i',str(WORK/'opening_7s.mkv'),'-i',str(SOURCE),'-filter_complex','[0:v]setpts=PTS-STARTPTS[h];[1:v]trim=start_frame=210,setpts=PTS-STARTPTS[t];[h][t]concat=n=2:v=1:a=0[v]','-map','[v]','-map','1:a:0','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-threads','6','-r','30','-c:a','copy','-t','210','-movflags','+faststart',str(DEST)])
    for seconds,name in [(6,'片头6秒_参考节奏_浅色版.mp4'),(9,'片头到首页9秒预览.mp4')]:
        v.run(['-y','-i',str(DEST),'-t',str(seconds),'-c:v','libx264','-crf','18','-preset','fast','-c:a','copy','-movflags','+faststart',str(ROOT/name)])
    print('FINAL',DEST,flush=True)

def docs():
    (ROOT/'片头调整说明.md').write_text('''# V14｜参考视频前6秒的节奏与构图

参考观察：左侧品牌文字从左向右显现，副标题依次出现；右侧登录界面作为产品入口；约第6秒柔和转至首页。

本次实现：
- 0—1.5秒：登录页分子背景轻推近，左侧ABACUSLab柔边显现。
- 1.2—2.5秒：平台定位分两行递进显示。
- 2.6—3.5秒：口号淡入；之后留出稳定阅读时间。
- 6—6.85秒：缓动位移与叠化，衔接现有首页镜头。
- 采用浅色渐变衬底、蓝色品牌字；右侧采用用户提供登录截图中的真实卡片，不改变UI内容。
- 继续使用中文男声，保持3分30秒；不加回额外旋转晶格或底部进度条。

借鉴构图与出字节奏，没有直接拼接参考视频画面或配音。7秒以后的镜头取自V13；主视频音轨直接沿用V13，无再次合成或变声。

预览：片头6秒_参考节奏_浅色版.mp4、片头到首页9秒预览.mp4。
''',encoding='utf-8')
    (WORK/'片头来源.json').write_text(json.dumps({'reference_file':str(REF),'reference_sha256':hashlib.sha256(REF.read_bytes()).hexdigest(),'reference_scope':'first 6 seconds','borrowed':['left-aligned brand layout','staggered soft text reveal','right-side real login card','homepage dissolve'],'reference_footage_used':False,'palette':'light blue and white','progress_bar':False,'source_video':str(SOURCE),'login_screenshot':str(LOGIN_SCREEN),'audio':'stream copied from V13'},ensure_ascii=False,indent=2),encoding='utf-8')

def check():
    v.ROOT=ROOT;v.WORK=WORK;v.DEST=DEST
    shutil.copy2(prev.WORK/'配音时间核验.json',WORK/'配音时间核验.json')
    # Read-only media checks shared with the approved cut.
    exec(compile((Path(__file__).parent/'check_v12_210.py').read_text(encoding='utf-8'),'check_v12_210.py','exec'),{'__name__':'__check__'})
    def audiohash(path):
        raw=subprocess.check_output([v.FF,'-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','adts','pipe:1'])
        return hashlib.sha256(raw).hexdigest()
    assert audiohash(SOURCE)==audiohash(DEST),'Audio changed'
    checks=[]
    for t in [8,38,105,151,207]:
        frames=[]
        for path in [SOURCE,DEST]:
            b=subprocess.check_output([v.FF,'-v','error','-ss',str(t),'-i',str(path),'-frames:v','1','-vf','scale=480:270','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
            frames.append(np.frombuffer(b,np.uint8).astype(np.float32))
        mae=float(np.mean(abs(frames[0]-frames[1])));assert mae<2.5,(t,mae);checks.append({'time':t,'mean_pixel_difference_255_scale':mae})
    report=json.loads((ROOT/'成片检查.json').read_text(encoding='utf-8'));report.update({'audio_bitstream_identical_to_v13':True,'after_7s_frame_samples':checks})
    (ROOT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if mode=='previews':previews()
    elif mode=='head':head()
    elif mode=='final':final()
    elif mode=='check':check()
