"""Light login-background opening/ending; remove all editorial progress bars."""
from pathlib import Path
from functools import lru_cache
import sys,math,shutil,json,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageOps
import make_v12_210 as v

PREVIOUS=v.ROOT
SOURCE_VIDEO=v.DEST
ROOT=v.BASE/'交付_V13_210秒_登录背景_浅色无进度条'
WORK=ROOT/'制作文件';ASSETS=ROOT/'素材';STILL=ROOT/'分镜预览'
for p in [ROOT,WORK,ASSETS,STILL]:p.mkdir(parents=True,exist_ok=True)
BACKGROUND=ASSETS/'登录页原始背景.png'
if not BACKGROUND.exists():
    shutil.copy2('D:/projiect/Personal-workflow-tools/src/assets/logos/longinbg.png',BACKGROUND)
W,H=v.W,v.H
LOGIN=ImageOps.fit(Image.open(BACKGROUND).convert('RGB'),(W,H),method=Image.Resampling.LANCZOS)
yy,xx=np.mgrid[0:H,0:W]
veil=.28+.43*np.exp(-((xx-960)**2/690**2+(yy-515)**2/330**2))
VEIL=Image.new('RGBA',(W,H),'#f4f7fe');VEIL.putalpha(Image.fromarray((veil*255).astype('uint8')))
del xx,yy,veil

def login_background(t,ending=False):
    # Slow camera push on the actual login artwork; no new atom/cube overlay.
    p=v.ease(min(t,7)/7);scale=1+.028*p
    im=LOGIN.transform((W,H),Image.Transform.AFFINE,(1/scale,0,(W-W/scale)/2,0,1/scale,(H-H/scale)/2),Image.Resampling.BICUBIC)
    im.paste(VEIL,(0,0),VEIL)
    if ending:im=Image.blend(im,v.LIGHT,.15)
    return im

def brand(t,ending=False):
    im=login_background(t,ending)
    lines=[('ABACUSLab',355,112,v.BLUE,.15),
           ('让材料计算更简单' if ending else '连接材料计算与分析',527,57,v.INK,.5),
           ('把更多精力，留给研究与发现' if ending else '从微观结构，走向材料发现',650,32,'#4d6589',.9)]
    for s,y,size,col,delay in lines:
        x=(W-v.font(size,True).getlength(s))/2
        v.enter(im,(x,y),s,t,delay,size,col)
    return im

def aihero(t):
    im=v.background(t);v.chrome(im,'研究，也可以从一句话开始','AI AGENT',t)
    d=ImageDraw.Draw(im)
    for j in range(4):
        r=165+j*35+8*math.sin(t*.6+j)
        d.ellipse((1390-r,570-r*.75,1390+r,570+r*.75),outline=['#b4c4f2','#c4d7ee','#b4dbe8','#d4def4'][j],width=2)
        a=t*.45+j*1.57;x=1390+r*math.cos(a);y=570+r*.75*math.sin(a)
        d.ellipse((x-5,y-5,x+5,y+5),fill=v.BLUE)
    v.enter(im,(1230,443),'AI',t,.1,190,v.BLUE)
    v.enter(im,(105,398),'说出目标',t,.25,84,v.INK)
    v.enter(im,(110,536),'让智能体协助下一步',t,.65,46,v.BLUE)
    return im

old_scene=v.scene
def scene(kind,t,span):
    if kind=='intro':return brand(t)
    if kind=='outro':return brand(min(t,7),True)
    if kind=='aihero':return aihero(t)
    if kind in ['plan','aiflow','summary']:
        title,labels={
          'plan':('从研究目标，走向计算方案',['理解需求','梳理步骤','确认条件']),
          'aiflow':('连接计算与结果展示',['组织任务','查看进展','衔接绘图']),
          'summary':('让智能协助，贯穿研究过程',['提出目标','组织计算','绘图展示','分析结果'])}[kind]
        im=v.flow(t,title,labels,False)
        # Replace only the editorial chapter label, not any screenshot pixels.
        im.paste(v.LIGHT.crop((1350,20,1870,95)),(1350,20))
        v.text(im,(1830,56),'AI AGENT',22,v.MUTED,anchor='ra')
        return im
    return old_scene(kind,t,span)

SHOTS=[(0,6,'intro'),(6,15,'home')]+v.SHOTS[2:]
@lru_cache(32)
def lastframe(i):
    a,b,k=SHOTS[i];return scene(k,b-a,b-a)
def frame(t):
    idx=next((i for i,(a,b,k) in enumerate(SHOTS) if a<=t<b),len(SHOTS)-1)
    a,b,k=SHOTS[idx];local=t-a;im=scene(k,local,b-a)
    if idx and local<.85:
        p=v.ease(local/.85);old=lastframe(idx-1)
        old=old.transform((W,H),Image.Transform.AFFINE,(1,0,24*p,0,1,0),Image.Resampling.BILINEAR)
        im=Image.blend(old,im,p)
    # No timeline, bottom line, moving progress dot, or dark fades.
    if t<.75:im=Image.blend(login_background(0),im,v.ease(t/.75))
    return im

v.ROOT=ROOT;v.WORK=WORK;v.STILL=STILL;v.SHOTS=SHOTS;v.frame=frame
v.DEST=ROOT/'ABACUSLab_3分30秒_浅色登录背景_无进度条.mp4'
DEST=v.DEST
for name in ['配音时间核验.json']:
    shutil.copy2(PREVIOUS/'制作文件'/name,WORK/name)
shutil.copy2(PREVIOUS/'可选旁白字幕_句级估时.srt',ROOT/'可选旁白字幕_句级估时.srt')

def final():
    v.run(['-y','-i',str(WORK/'picture.mp4'),'-i',str(SOURCE_VIDEO),'-map','0:v:0','-map','1:a:0','-c','copy','-t','210','-movflags','+faststart',str(DEST)])
    v.run(['-y','-i',str(DEST),'-t','6','-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-movflags','+faststart',str(ROOT/'片头6秒_登录页背景.mp4')])
    print('FINAL',DEST,flush=True)

def docs():
    (ROOT/'修改说明.md').write_text('''# V13｜浅色登录背景版

- 片头0—6秒采用登录页原始分子背景图，不含登录框，缓慢推进。
- 移除上一版片头右侧单独旋转的晶格方块。
- 片尾采用同一浅蓝背景，呼应开场；AI段也统一为蓝白色。
- 全片移除底部进度条、进度光点；不再使用深色淡入淡出。
- 首页镜头从第6秒开始，整体仍为210秒；沿用上一版中文男声与音频。
- 原背景自带的分子结构属于图片内容；没有额外叠加晶格模型。

源背景来自平台src/assets/logos/longinbg.png，原图归档于素材目录。
主文件为ABACUSLab_3分30秒_浅色登录背景_无进度条.mp4；另附片头6秒单独预览。
''',encoding='utf-8')
    (WORK/'背景来源.json').write_text(json.dumps({'source':'D:/projiect/Personal-workflow-tools/src/assets/logos/longinbg.png','sha256':hashlib.sha256(BACKGROUND.read_bytes()).hexdigest(),'login_form_included':False,'additional_lattice_removed':True,'progress_bar':False},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'previews'
    if mode=='previews':v.previews();docs()
    elif mode=='picture':v.picture()
    elif mode=='final':final()
    elif mode=='check':
        # Reuse the same media checks against the updated output, not the old cut.
        exec(compile((Path(__file__).parent/'check_v12_210.py').read_text(encoding='utf-8'),'check_v12_210.py','exec'))
