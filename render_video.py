"""ABACUSLAB 60-second film. Run with the project's Python + local packages.
All UI and scientific figures come from the supplied assets. No simulated data.
"""
from pathlib import Path
import sys,math,json,subprocess,time
sys.path.insert(0,str(Path(__file__).parent/'packages'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import cv2

BASE=Path(__file__).resolve().parent
SRC=Path('C:/Users/PC/Desktop/\u7d20\u6750/\u7d20\u6750')
W,H,FPS=1920,1080,30
BLUE='#5865ed'; INK='#15203b'; MUTED='#69758d'; TEAL='#46b9ae'
FONT='C:/Windows/Fonts/msyh.ttc'; BOLD='C:/Windows/Fonts/msyhbd.ttc'
fonts={}
def ft(size,bold=False):
 key=(size,bold)
 if key not in fonts:fonts[key]=ImageFont.truetype(BOLD if bold else FONT,size)
 return fonts[key]
def txt(im,xy,s,size=32,color=INK,bold=False,anchor=None):
 ImageDraw.Draw(im).text(xy,s,font=ft(size,bold),fill=color,anchor=anchor,spacing=12)
def rr(im,box,fill='white',radius=20,outline=None,width=1):
 ImageDraw.Draw(im).rounded_rectangle(tuple(int(v) for v in box),radius,fill=fill,outline=outline,width=width)
def ease(v):
 v=max(0,min(1,v));return v*v*(3-2*v)
def mix(a,b,v):return a+(b-a)*v
def paste_fit(im,src,box,cover=False):
 x,y,w,h=map(int,box);rat=max(w/src.width,h/src.height) if cover else min(w/src.width,h/src.height)
 nw,nh=round(src.width*rat),round(src.height*rat)
 obj=src.resize((nw,nh),Image.Resampling.LANCZOS)
 if cover:obj=obj.crop(((nw-w)//2,(nh-h)//2,(nw+w)//2,(nh+h)//2));im.paste(obj,(x,y))
 else:im.paste(obj,(x+(w-nw)//2,y+(h-nh)//2))
def crop_pan(src,box,view):
 return src.crop(tuple(map(int,view))).resize(tuple(map(int,box)),Image.Resampling.LANCZOS)

template=Image.open(SRC/'86a62f81-69e0-4354-a45c-8c812c4133d6.png').convert('RGB')
agent=Image.open(SRC/'16e10cf0-f4ca-4407-8d2a-8cb7321086a3.png').convert('RGB')
analysis=Image.open(SRC/'17ca551a-694e-46b7-8861-0ff29629ef79.png').convert('RGB')
chart_raw=Image.open(SRC/'0252131c-9fe3-48d6-9f17-739ffb635336.png').convert('RGB')
logo=template.crop((35,12,348,106))
icon=template.crop((35,12,126,106))
def transparent_white(src):
 arr=np.array(src.convert('RGBA')); light=np.min(arr[:,:,:3],axis=2)>245
 arr[light,3]=0;return Image.fromarray(arr)
logo=transparent_white(logo);icon=transparent_white(icon)
chart=chart_raw.crop((270,325,2060,1390)).resize((1200,714),Image.Resampling.LANCZOS)
chart_arr=np.array(chart);colored=(chart_arr[:,:,1].astype(int)-chart_arr[:,:,0].astype(int)>18)|((chart_arr[:,:,0].astype(int)-chart_arr[:,:,1].astype(int)>20)&(chart_arr[:,:,2].astype(int)-chart_arr[:,:,1].astype(int)>15))
chart_blank=chart_arr.copy();chart_blank[colored]=255;chart_blank=Image.fromarray(chart_blank)
curve_mask=Image.fromarray((colored*255).astype('uint8'))

yy,xx=np.mgrid[0:H,0:W]
g=np.exp(-((xx-W*.78)**2/(W*.55)**2+(yy-H*.26)**2/(H*.8)**2))
bg=np.stack([247-8*g,249-10*g,254-1*g],axis=-1).astype('uint8')
LIGHT=Image.fromarray(bg)
gd=np.exp(-((xx-W*.73)**2/(W*.6)**2+(yy-H*.4)**2/(H*.8)**2))
DARK=Image.fromarray(np.stack([9+7*gd,15+12*gd,30+32*gd],axis=-1).astype('uint8'))
del xx,yy,g,gd,bg

def base(k,t,dark=False):
 im=(DARK if dark else LIGHT).copy();d=ImageDraw.Draw(im)
 if dark:
  txt(im,(86,50),'ABACUSLAB',28,'#e4eaff',True)
  txt(im,(1780,55),'SCIENCE × AI',18,'#7c8eae',anchor='ra')
 else:
  mark=logo.resize((235,71),Image.Resampling.LANCZOS);im.paste(mark,(70,30),mark)
  txt(im,(1810,62),'科学计算智能体',22,MUTED,anchor='ra')
 d.line((80,128,1840,128),fill='#27334a' if dark else '#dce2f0',width=1)
 # Discreet chapter markers.
 for n in range(7):
  x=1540+n*42
  rr(im,(x,1032,x+27,1036),BLUE if n==k else ('#334057' if dark else '#d5dcec'),2)
 txt(im,(82,1016),f'{k+1:02d} / 07',19,'#8e9ab0' if dark else MUTED)
 return im
def label(im,s,x=90,y=165):txt(im,(x,y),s,20,BLUE,True)
def subtitle(im,s):
 if not s:return
 d=ImageDraw.Draw(im);b=d.textbbox((0,0),s,font=ft(32));tw=b[2]-b[0]
 rr(im,((W-tw)//2-28,946,(W+tw)//2+28,1006),'#17213a',15)
 txt(im,(W//2,955),s,32,'white',anchor='ma')
def cursor(im,x,y,click=False):
 d=ImageDraw.Draw(im)
 if click:d.ellipse((x-22,y-22,x+22,y+22),outline='#b7bdfb',width=4)
 d.polygon([(x,y),(x+5,y+40),(x+16,y+28),(x+28,y+28)],fill='white',outline=INK,width=2)

record=[]
cap=cv2.VideoCapture(str(next(SRC.glob('*.mp4'))))
# Retain actual interaction, excluding browser chrome and personal controls.
for i in range(190):
 ok,fr=cap.read()
 if not ok:break
 rgb=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)
 record.append(Image.fromarray(rgb).crop((380,250,3190,1940)).resize((1120,674),Image.Resampling.LANCZOS))
cap.release()

def intro(t):
 im=base(0,t,True);d=ImageDraw.Draw(im)
 # Grid, abstract scientific traces and code as graphic elements.
 for x in range(970,1840,90):d.line((x,195,x,865),fill='#1d2b45',width=1)
 for y in range(215,900,80):d.line((950,y,1840,y),fill='#1d2b45',width=1)
 for q,col in [(0,'#58cabd'),(1,'#7683f4')]:
  pts=[]
  for j in range(int(540*ease((t+.4)/2))):
   x=1080+j*1.25; y=610-120*math.sin(j/90+q*1.7)-j*.27+q*140
   pts.append((x,y))
  if len(pts)>1:d.line(pts,fill=col,width=3)
 for j,s in enumerate(['SYSTEM / MATERIALS','temperature = [300, 1600]','trajectory → MSD','question → insight']):
  txt(im,(1120,230+j*45),s,21,'#5d7699')
 label(im,'A NEW START FOR SCIENTIFIC COMPUTING',90,267)
 txt(im,(85,340),'科研计算，',72,'#ffffff',True)
 txt(im,(85,450),'一定要从复杂的',65,'#ffffff',True)
 txt(im,(85,548),'代码开始吗？',78,'#91a0ff',True)
 txt(im,(91,735),'从提出问题开始',31,'#a8b6d0')
 # A restrained animated orbital motif.
 for j in range(9):
  a=j*2*math.pi/9+t*.08;x=1480+215*math.cos(a);y=700+75*math.sin(a)
  d.ellipse((x-5,y-5,x+5,y+5),fill='#7a8af0')
 return im

def workbench(t):
 im=base(1,t); label(im,'01  /  从问题出发')
 txt(im,(88,280),'科研计算，',66,INK,True)
 txt(im,(88,378),'从提出问题开始',62,BLUE,True)
 txt(im,(92,525),'一个平台，连接科研工作流',29,MUTED)
 for j,s in enumerate(['选择计算方向','提出科研问题','查看分析结果']):
  rr(im,(94,614+j*75,136,656+j*75),BLUE if t>j+.5 else '#d8ddef',12)
  txt(im,(115,618+j*75),str(j+1),24,'white',True,anchor='ma')
  txt(im,(157,618+j*75),s,28,INK)
 rr(im,(704,211,1842,862),'#dfe4f1',25)
 obj=crop_pan(template,(1114,625),(0+35*ease(t/7),0,3800-35*ease(t/7),1907))
 im.paste(obj,(716,223))
 rr(im,(1050,797,1698,887),'white',20,outline='#d8def0')
 txt(im,(1084,819),'模板  →  AI  →  计算  →  可视化',28,BLUE,True)
 return im

def templates(t):
 im=base(1,t);label(im,'TEMPLATE LIBRARY')
 txt(im,(88,205),'丰富模板，覆盖多类科研计算场景',48,INK,True)
 cats=['电子结构','输运','光学','磁性'];active=min(3,int(t/2.5))
 for j,s in enumerate(cats):
  x=1040+j*192
  rr(im,(x,170,x+175,229),BLUE if j==active else 'white',29,outline=None if j==active else '#dce1f0')
  txt(im,(x+87,181),s,26,'white' if j==active else MUTED,True,anchor='ma')
 # Pan across real cards at a readable magnification.
 left=720+int(850*ease(t/10))
 srcview=(left,390,left+2210,1570)
 rr(im,(82,303,1840,902),'#dfe4f1',24)
 obj=crop_pan(template,(1728,570),srcview);im.paste(obj,(97,317))
 return im

def question(t):
 im=base(2,t);label(im,'02  /  自然语言交互')
 txt(im,(89,297),'只需提出问题',60,INK,True)
 txt(im,(91,401),'AI 帮你梳理',51,BLUE,True)
 txt(im,(91,478),'计算思路',51,BLUE,True)
 txt(im,(94,648),'把科研目标，变成计算的起点',27,MUTED)
 # Actual UI screenshot with an animated magnification of its input.
 panel=agent.crop((74,30,2115,1710)).resize((1050,724),Image.Resampling.LANCZOS)
 im.paste(panel,(762,170))
 # Clear the original input field, then expand it into a motion callout.
 rr(im,(920,730,1710,866),'white',0)
 rr(im,(705,602,1815,787),'#fff',22,outline='#b9212b',width=3)
 prompt='我想计算一下金属熔断'
 chars=min(len(prompt),max(0,int((t-.6)*4.0)))
 txt(im,(742,640),prompt[:chars],43,INK)
 if chars<len(prompt) and int(t*3)%2==0:
  x=742+ImageDraw.Draw(im).textlength(prompt[:chars],font=ft(43));ImageDraw.Draw(im).line((x+3,645,x+3,691),fill='#be2935',width=2)
 rr(im,(1726,704,1782,760),'#bb252e',28)
 txt(im,(1754,705),'↑',36,'white',anchor='ma')
 txt(im,(742,733),'附件    知识库',20,MUTED)
 if t>4:
  cursor(im,1746,735,t<4.6)
  txt(im,(760,831),'正在理解需求',24,BLUE)
  for j in range(3):
   v=(math.sin(t*5-j)+1)/2; c=(int(160-72*v),int(170-70*v),235)
   ImageDraw.Draw(im).ellipse((948+j*22,840,958+j*22,850),fill=c)
 return im

def operation(t):
 im=base(2,t);label(im,'AI AGENT  /  平台操作实录')
 txt(im,(89,290),'从需求理解',58,INK,True)
 txt(im,(89,380),'到计算思路',58,BLUE,True)
 for j,s in enumerate(['理解目标','分析参数','组织计算流程']):
  y=550+j*86;rr(im,(92,y,520,y+62),'white',15,outline='#dce2f0')
  txt(im,(115,y+12),s,28,BLUE if t>j*1.2 else MUTED,True)
 rr(im,(648,189,1812,901),'#dce2ee',24)
 idx=min(len(record)-1,int(t/5.0*len(record)))
 im.paste(record[idx],(670,208))
 return im

def results(t):
 im=base(3,t);label(im,'03  /  分析与验证')
 txt(im,(87,215),'理解需求｜分析参数｜生成结论',47,INK,True)
 choices=[('结论','300 K 呈平台，1600 K 呈扩散'),('局限','两点对比，不等于精确熔点'),('建议的下一步','加密温度扫描，扩大体系验证')]
 active=min(2,int(t/3))
 for j,(a,b) in enumerate(choices):
  y=344+j*176;rr(im,(88,y,717,y+145),'white',22,outline=BLUE if j==active else '#e0e5f0',width=3 if j==active else 1)
  txt(im,(118,y+20),a,35,BLUE if j==active else INK,True)
  txt(im,(118,y+82),b,25,MUTED)
 rr(im,(769,310,1839,901),'white',24,outline='#dfe4f1')
 views=[(190,75,1470,290),(190,320,1470,785),(190,815,1470,1085)]
 # Source screenshot remains unaltered, enlarged around the named section.
 p=analysis.crop(views[active]);paste_fit(im,p,(802,337,1004,528))
 txt(im,(800,865),'AI 分析原文 · 局部放大',18,MUTED)
 return im

def charts(t):
 im=base(4,t);label(im,'04  /  数据可视化')
 txt(im,(88,220),'复杂数据',58,INK,True)
 txt(im,(88,305),'直观呈现',58,BLUE,True)
 txt(im,(92,441),'不同温度下的 MSD 曲线',25,MUTED)
 for y,col,head,detail in [(550,'#84c64f','1600 K','MSD 随时间上升'),(689,'#54206b','300 K','MSD 保持平台')]:
  rr(im,(93,y,105,y+79),col,5)
  txt(im,(126,y-3),head,35,col,True)
  txt(im,(127,y+48),detail,25,MUTED)
 rr(im,(554,190,1836,915),'white',26,outline='#dfe4ee')
 # Reveal only the original colored pixels; axes and ticks stay visible.
 panel=chart_blank.copy()
 cutoff=int(80+1080*ease(t/5.8))
 if t>=5.8:panel=chart.copy()
 else:
  panel.paste(chart.crop((0,0,cutoff,714)),(0,0))
 im.paste(panel,(590,196))
 txt(im,(593,889),'示例结果 · 300 K 与 1600 K 对比',18,MUTED)
 return im

def montage(t):
 im=base(5,t);label(im,'ONE PLATFORM / ONE WORKFLOW')
 txt(im,(W//2,207),'模板、AI、计算、可视化，一站式完成',48,INK,True,anchor='ma')
 cards=[template.crop((380,100,3800,1900)),agent.crop((70,30,2120,1710)),analysis,chart_raw.crop((270,325,2060,1390))]
 names=['模板库','AI 对话','结论分析','数据图表'];active=min(3,int(t/0.7))
 for j,src in enumerate(cards):
  x=100+j*438;y=358-12*math.sin(min(1,max(0,t-j*.15))*math.pi/2)
  rr(im,(x,y,x+407,y+477),'white',22,outline=BLUE if j==active else '#dce2f0',width=3 if j==active else 1)
  paste_fit(im,src,(x+18,y+24,371,342),cover=True)
  txt(im,(x+203,y+397),names[j],33,BLUE if j==active else INK,True,anchor='ma')
 return im

def outro(t):
 im=LIGHT.copy();d=ImageDraw.Draw(im)
 # Original logo artwork, extracted from the provided platform screenshot.
 mark=icon.resize((104,108),Image.Resampling.LANCZOS);im.paste(mark,(W//2-52,190),mark)
 txt(im,(W//2,333),'ABACUSLAB',83,BLUE,True,anchor='ma')
 txt(im,(W//2,458),'科学计算智能体',38,INK,True,anchor='ma')
 d.line((808,544,1112,544),fill='#c5cff2',width=2)
 txt(im,(W//2,587),'让科学计算更简单',61,INK,True,anchor='ma')
 txt(im,(W//2,718),'从提出问题，到得到结果',31,MUTED,anchor='ma')
 txt(im,(W//2,798),'让每一个科研想法快速开始',29,BLUE,anchor='ma')
 return im

SCENES=[(0,5,intro),(5,12,workbench),(12,22,templates),(22,30,question),(30,35,operation),(35,44,results),(44,53,charts),(53,56,montage),(56,60,outro)]
CUES=[
 (0.4,4.8,'科研计算，一定要从复杂的代码开始吗？'),
 (5.5,8.0,'现在，从一个问题开始'),(8.0,11.6,'就能快速进入科学计算流程'),
 (12.1,16.0,'ABACUSLAB 提供丰富的计算模板'),(16.0,21.5,'覆盖电子结构、输运、光学、磁性等科研场景'),
 (22.3,25.7,'只需要告诉 AI 你的计算目标'),(25.7,29.9,'比如，我想计算一下金属熔断'),
 (30.4,34.6,'从理解需求，到梳理计算思路'),
 (35.1,39.1,'分析关键参数，给出清晰结论'),(39.1,43.4,'同时说明局限，建议下一步验证'),
 (44.1,48.4,'从数据处理，到曲线绘制，再到结果分析'),(48.4,52.4,'让复杂数据变成直观图表'),
 (53.0,55.8,'模板、AI、计算、可视化')]

def frame(t):
 for idx,(a,b,fun) in enumerate(SCENES):
  if a<=t<b:
   im=fun(t-a)
   if idx>0 and t-a<.35:
    pa,pb,pfun=SCENES[idx-1];old=pfun(pb-pa-.001)
    im=Image.blend(old,im,ease((t-a)/.35))
   for sa,sb,s in CUES:
    if sa<=t<sb:subtitle(im,s);break
   return im
 return outro(4)

def main():
 (BASE/'previews').mkdir(exist_ok=True)
 preview_times=[2.5,8,15,20,26.5,32,36.5,39.5,42,48,54.5,58]
 contact=Image.new('RGB',(1440,1620),'white')
 for i,t in enumerate(preview_times):
  im=frame(t);im.save(BASE/'previews'/f'{t:04.1f}.jpg',quality=92)
  im.thumbnail((720,405));contact.paste(im,((i%2)*720,(i//2)*270)) if False else None
 # Contact sheet: four rows, three columns.
 contact=Image.new('RGB',(1440,1080),'white')
 for i,t in enumerate(preview_times):
  im=Image.open(BASE/'previews'/f'{t:04.1f}.jpg');im.thumbnail((480,270));contact.paste(im,((i%3)*480,(i//3)*270))
 contact.save(BASE/'storyboard.jpg',quality=95)
 def stamp(t):
  ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
 (BASE/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(CUES+[(56,60,'ABACUSLAB，让科学计算更简单')])),encoding='utf-8-sig')
 if '--preview' in sys.argv:return
 import imageio_ffmpeg
 ff=imageio_ffmpeg.get_ffmpeg_exe()
 cmd=[ff,'-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(BASE/'picture.mp4')]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 start=time.time()
 try:
  for n in range(60*FPS):
   p.stdin.write(frame(n/FPS).tobytes())
   if n%150==0:print(f'Render {n//FPS}/60 s, elapsed {time.time()-start:.1f}s',flush=True)
 finally:p.stdin.close()
 if p.wait()!=0:raise RuntimeError('Video encode failed')
 print('PICTURE COMPLETE',flush=True)
if __name__=='__main__':main()
