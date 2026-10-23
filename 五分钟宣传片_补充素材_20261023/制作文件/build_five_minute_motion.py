"""Original motion graphics and factual crops for a five-minute film asset pack.
Conceptual lattice and flow diagrams contain no invented scientific results.
"""
from pathlib import Path
from functools import lru_cache
import sys,math,json,subprocess,shutil,hashlib,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps
SCRIPT_DIR=Path(__file__).resolve().parent
BASE=SCRIPT_DIR.parent if SCRIPT_DIR.name=='制作文件' else SCRIPT_DIR
ROOT=BASE/'五分钟宣传片_补充素材_20261023'
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS=1920,1080,30
NAVY='#081329';CYAN='#69dce8';BLUE='#849bff';WHITE='#edf4ff';MUTED='#92a7c7'
@lru_cache(None)
def font(size,b=False):return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if b else 'C:/Windows/Fonts/msyh.ttc',size)
def text(im,xy,s,size=32,color=WHITE,b=False,anchor=None):ImageDraw.Draw(im).text(xy,s,font=font(size,b),fill=color,anchor=anchor)
def ease(x):x=min(1,max(0,x));return x*x*(3-2*x)
y,x=np.mgrid[0:H,0:W]
glow=np.exp(-((x-1370)/850)**2-((y-480)/650)**2)
BG=Image.fromarray(np.stack([8+5*glow,19+17*glow,41+29*glow],-1).astype('uint8'))
del x,y,glow
rng=np.random.default_rng(23);stars=rng.random((70,3))
def background(t):
    im=BG.copy();d=ImageDraw.Draw(im)
    for x,y,s in stars:
        px=(x*W+t*(2+3*s))%W;py=y*H;r=1+s
        d.ellipse((px-r,py-r,px+r,py+r),fill='#294562')
    return im
def base_title(im,title,subtitle,label):
    text(im,(100,78),'ABACUSLab',27,CYAN,True)
    text(im,(100,155),title,62,WHITE,True)
    if subtitle:text(im,(104,249),subtitle,30,MUTED)
    text(im,(1820,1018),label,22,MUTED,anchor='ra')
def arrow(d,a,b,color=CYAN,width=4,progress=1):
    ax,ay=a;bx,by=b;bx=ax+(bx-ax)*progress;by=ay+(by-ay)*progress
    d.line((ax,ay,bx,by),fill=color,width=width)
    ang=math.atan2(by-ay,bx-ax);length=14
    d.polygon([(bx,by),(bx-length*math.cos(ang-.5),by-length*math.sin(ang-.5)),(bx-length*math.cos(ang+.5),by-length*math.sin(ang+.5))],fill=color)
def lattice(im,t,cx,cy,scale,n=4,variant=0):
    pts=[];raw=[];a=.6+t*.14;b=.34
    for i in range(n):
        for j in range(n):
            for k in range(n):
                px=i-(n-1)/2;py=j-(n-1)/2;pz=k-(n-1)/2
                rx=px*math.cos(a)+pz*math.sin(a);rz=-px*math.sin(a)+pz*math.cos(a)
                ry=py*math.cos(b)-rz*math.sin(b);zz=py*math.sin(b)+rz*math.cos(b)
                perspective=1+zz*.035
                pts.append((cx+rx*scale*perspective,cy+ry*scale*perspective,zz));raw.append((i,j,k))
    d=ImageDraw.Draw(im)
    for p,(i,j,k) in enumerate(raw):
        for q in (p+n*n if i<n-1 else -1,p+n if j<n-1 else -1,p+1 if k<n-1 else -1):
            if q>=0:d.line((*pts[p][:2],*pts[q][:2]),fill='#315a7a',width=2)
    for p in sorted(range(len(pts)),key=lambda p:pts[p][2]):
        px,py,z=pts[p];r=max(5,scale*.095*(1+z*.07));c=CYAN if (p+variant)%7==0 else BLUE
        d.ellipse((px-r-4,py-r-4,px+r+4,py+r+4),fill='#203e5a')
        d.ellipse((px-r,py-r,px+r,py+r),fill=c)
        d.ellipse((px-r*.45,py-r*.65,px+r*.12,py-r*.1),fill='#e7fbff')
def card(im,box,title,sub,index,active=False):
    d=ImageDraw.Draw(im);x1,y1,x2,y2=box
    d.rounded_rectangle(box,24,fill='#112440',outline=CYAN if active else '#294363',width=3 if active else 2)
    d.rounded_rectangle((x1+28,y1+27,x1+77,y1+76),14,fill='#1d4663')
    text(im,(x1+52,y1+51),str(index),25,CYAN,True,'mm')
    text(im,((x1+x2)/2,y1+125),title,36,WHITE,True,'mm')
    text(im,((x1+x2)/2,y1+188),sub,25,MUTED,False,'mm')
def crystal(t,dur):
    im=background(t);base_title(im,'从材料结构，理解微观世界','结构 · 原子 · 相互作用','晶体结构概念示意')
    lattice(im,t,1320,610,128,4)
    text(im,(106,466),'微观结构',48,WHITE,True);text(im,(108,551),'为材料计算提供研究起点',31,MUTED)
    d=ImageDraw.Draw(im);d.line((108,652,586,652),fill='#345574',width=3)
    px=108+478*((t/dur)%1);d.ellipse((px-6,646,px+6,658),fill=CYAN)
    return im
def space(t,dur):
    im=background(t);base_title(im,'广阔的材料探索空间','组成与结构的组合，构成不同研究方向','概念示意 · 非实际候选材料与筛选结果')
    d=ImageDraw.Draw(im)
    for i in range(6):
        col=i%3;row=i//3;cx=370+590*col;cy=470+300*row
        active=int(t/1.5)%6==i
        d.rounded_rectangle((cx-230,cy-130,cx+230,cy+130),22,fill='#0e213b',outline=CYAN if active else '#233d5a',width=3 if active else 1)
        lattice(im,t+i,cx,cy,45,3,variant=i)
    return im
def research(t,dur):
    im=background(t);base_title(im,'材料研究，需要反复探索','从制备与表征，到性能测试和方案调整','研究流程概念示意')
    titles=[('材料制备','组成与工艺'),('实验表征','结构与特征'),('性能测试','目标与指标'),('调整方案','继续研究')]
    d=ImageDraw.Draw(im)
    for i,(title,sub) in enumerate(titles):
        x=100+i*440;card(im,(x,430,x+380,690),title,sub,i+1,int(t/2)%4==i)
        if i<3:arrow(d,(x+391,560),(x+430,560),progress=ease((t-i*.8)/1.2))
    d.line([(1610,720),(1610,810),(290,810),(290,720)],fill='#345a76',width=3)
    arrow(d,(290,765),(290,720),color='#345a76');text(im,(960,865),'观察差异 · 复核条件 · 迭代研究',32,MUTED,anchor='mm')
    return im
def ai(t,dur):
    im=background(t);base_title(im,'从研究问题，到计算方案','AI 辅助研究人员连接计算与分析环节','流程示意 · 实际执行能力以平台功能为准')
    titles=[('理解需求','研究目标与条件'),('规划流程','选择方法与模板'),('组织任务','研究人员确认'),('分析结果','归纳与验证建议')]
    d=ImageDraw.Draw(im)
    for i,(title,sub) in enumerate(titles):
        x=100+i*440;card(im,(x,430,x+380,700),title,sub,i+1,int(t/2.2)%4==i)
        if i<3:arrow(d,(x+391,565),(x+430,565),progress=ease((t-i*.7)/1.2))
    text(im,(960,830),'AI 智能辅助   +   专业计算   +   科学判断',38,CYAN,True,'mm')
    return im
def design(t,dur):
    im=background(t);base_title(im,'让计算，为设计提供依据','候选结构 → 计算验证 → 结果比较 → 进一步优化','设计流程概念示意 · 非自主材料发现演示')
    d=ImageDraw.Draw(im)
    for i,(title,sub) in enumerate([('候选结构','明确组成与结构'),('计算验证','采用可比较条件'),('结果比较','分析差异与依据'),('进一步优化','提出下一轮方案')]):
        x=100+i*440;card(im,(x,430,x+380,710),title,sub,i+1,int(t/2.5)%4==i)
        if i<3:arrow(d,(x+391,565),(x+430,565),progress=ease((t-i*.8)/1.3))
    text(im,(960,838),'计算结果支持研究判断',36,CYAN,True,'mm')
    return im
def loop(t,dur):
    # Integer-period geometry and particle-free backdrop give matching endpoints.
    im=BG.copy();phase=2*math.pi*t/dur
    lattice(im,math.sin(phase)*1.7,1480,540,85,4)
    text(im,(130,358),'ABACUSLab',95,WHITE,True)
    text(im,(137,503),'AI 驱动的材料计算与设计平台',42,CYAN,True)
    text(im,(140,639),'让材料计算更简单',46,WHITE,True)
    text(im,(142,721),'把更多精力，留给研究与发现。',30,MUTED)
    text(im,(1820,1018),'结构背景示意',22,MUTED,anchor='ra')
    return im
@lru_cache(None)
def msd_image():
    im=Image.open(ROOT/'01_已有平台素材/P02_MSD原图裁切.png').convert('RGB')
    im.thumbnail((1170,700),Image.Resampling.LANCZOS)
    return im
def aluminum(t,dur):
    im=background(t);base_title(im,'铝的熔化行为研究','通过不同温度下的 MSD 曲线，比较原子运动特征','已有算例图表 · 两个温度点不足以精确确定熔点')
    d=ImageDraw.Draw(im);d.rounded_rectangle((650,350,1840,1030),24,fill='white')
    chart=msd_image();im.paste(chart,(660+(1170-chart.width)//2,360+(650-chart.height)//2))
    text(im,(110,449),'300 K / 1600 K',42,CYAN,True)
    text(im,(112,542),'比较曲线变化',34,WHITE,True)
    text(im,(112,607),'观察原子运动特征',29,MUTED)
    text(im,(112,700),'结合条件解释结果',29,MUTED)
    text(im,(112,767),'继续开展验证',29,MUTED)
    return im
SPECS=[('M01_微观晶体结构_12秒',12,crystal,'00:32—00:50，宏观到微观过渡'),('M02_材料探索空间_10秒',10,space,'00:10—00:22，材料空间概念'),('M03_研发迭代流程_10秒',10,research,'00:22—00:32，研发迭代解释'),('M04_AI与计算流程_12秒',12,ai,'01:00—01:10 或 AI 章节过渡'),('M05_计算支撑设计_12秒',12,design,'04:10—04:40，设计探索章节'),('M06_品牌循环背景_10秒',10,loop,'片尾；也可取作片头过渡')]
CASE_SPEC=('M07_纯铝案例_MSD原图_10秒',10,aluminum,'02:35—03:35，铝的熔化行为案例')
def render(specs=SPECS):
    manifest=ROOT/'05_预览与索引/新增动画清单.json'
    result=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    for name,dur,fn,use in specs:
        dest=ROOT/'03_新增动画'/f'{name}.mp4';still=ROOT/'05_预览与索引'/f'{name}.jpg'
        fn(dur*.45,dur).save(still,quality=92)
        cmd=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for i in range(dur*FPS):p.stdin.write(fn(i/FPS,dur).tobytes())
        p.stdin.close();code=p.wait()
        if code:raise RuntimeError(f'encode failed {name}')
        result=[r for r in result if r['name']!=name]
        result.append({'name':name,'file':str(dest.relative_to(ROOT)),'preview':str(still.relative_to(ROOT)),'duration':dur,'width':W,'height':H,'fps':FPS,'source':'已有 MSD 原图＋本次编辑排版' if fn==aluminum else '本次原创程序动画','use':use,'boundary':'纯铝命名经用户确认；保留原曲线；未独立核验原始数据' if fn==aluminum else '概念示意；不是实验、MD轨迹或平台执行录屏','sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
        print(f'RENDERED {name}',flush=True)
    (ROOT/'05_预览与索引/新增动画清单.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
def crop_sources():
    N=ROOT/'01_已有平台素材';crops=[('N03_PDOS绘图结果.png','P01_PDOS原图裁切.png',(.414,.505,.677,.887)),('A03_MSD原始曲线.png','P02_MSD原图裁切.png',(.06,.19,.98,.98))]
    crop_notes=[]
    for src,name,box in crops:
        im=Image.open(N/src);pixel=tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box));im.crop(pixel).save(N/name);crop_notes.append({'source':src,'output':name,'crop':pixel,'treatment':'原像素裁切，不重绘、不平滑或修改曲线'})
    for idx,p in enumerate(BASE.parent.glob('屏幕录制 *.mp4'),1):
        dest=N/f'R0{idx}_原始平台录屏.mp4'
        shutil.copy2(p,dest)
    # Cut only spatially; preserve chronology and original playback speed.
    recording=BASE.parent/'屏幕录制 2026-10-15 161830.mp4'
    if recording.exists():
        dest=N/'R01_真实对话到MSD_去浏览器栏_1080p.mp4'
        subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-i',str(recording),'-vf','crop=3800:1860:0:130,scale=1920:940,pad=1920:1080:0:70:color=0x081329','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],check=True)
        crop_notes.append({'source':str(recording),'output':str(dest.relative_to(ROOT)),'treatment':'去除浏览器栏；原速原顺序；去原声；补上下边框','boundary':'只展示实际录到的对话到绘图跳转；不证明完整计算或铝合金组成'})
    (ROOT/'05_预览与索引/裁切记录.json').write_text(json.dumps(crop_notes,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='crops':crop_sources()
    elif len(sys.argv)>1 and sys.argv[1]=='case':render([CASE_SPEC])
    else:render()
