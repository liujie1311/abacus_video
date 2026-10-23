# V20 scene overrides. Included in the standalone build script at preparation.
PURPLE='#734388';GREEN='#5b9f46'

@lru_cache(1)
def principles_canvas():
    im=bg();d=ImageDraw.Draw(im)
    # Illustrative density field; no computed quantity or numerical scale is implied.
    yy,xx=np.mgrid[-1:1:430j,-1:1:430j]
    field=sum(np.exp(-((xx-x)**2+(yy-y)**2)/.12) for x,y in [(-.36,-.3),(.38,-.26),(-.02,.35)])
    z=np.clip(field/field.max(),0,1);rgba=np.zeros((430,430,4),np.uint8)
    rgba[:,:,:3]=[102,169,194];rgba[:,:,3]=(z*165).astype(np.uint8)
    rings=(np.mod(z,.13)<.008)&(z>.08);rgba[rings,:3]=[87,133,183];rgba[rings,3]=130
    fieldim=Image.fromarray(rgba);im.paste(fieldim,(745,360),fieldim)
    for row in range(4):
        for col in range(4):
            x=235+col*83+row*21;y=403+row*83
            if col<3:d.line((x,y,x+83,y),fill='#cbd5e7',width=3)
            if row<3:d.line((x,y,x+21,y+83),fill='#cbd5e7',width=3)
            sp=l.sphere(22,0);im.paste(sp,(x-22,y-22),sp)
    for x in [659,1235]:
        d.line((x,575,x+55,575),fill='#a8b9d8',width=3);d.polygon([(x+55,575),(x+44,568),(x+44,582)],fill='#a8b9d8')
    for j,label in enumerate(['总能量与受力','电子态与成键','材料性质']):
        txt(im,(1480,445+j*105),label,33,INK,True,'mm')
    for x,label in [(390,'原子结构'),(960,'电子分布'),(1480,'性质分析')]:txt(im,(x,838),label,35,BLUE,True,'mm')
    return im

@lru_cache(1)
def chart_layers():
    chart=ImageOps.contain(IMG['msd'],(1280,675),Image.Resampling.LANCZOS).convert('RGB')
    a=np.asarray(chart);dark=a.max(axis=2)<105
    rows=np.where(dark.sum(axis=1)>chart.width*.5)[0]
    top,bottom=int(rows[0]),int(rows[-1])
    cols=np.where(dark[top:bottom+1].sum(axis=0)>(bottom-top)*.70)[0]
    left,right=int(cols[0]),int(cols[-1])
    z=a.astype(int)
    colored=((z[:,:,1]-z[:,:,0]>17)&(z[:,:,1]-z[:,:,2]>8))|((z[:,:,0]-z[:,:,1]>16)&(z[:,:,2]-z[:,:,1]>15))
    mask=np.asarray(Image.fromarray((colored*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)))>0
    mask[:top+2]=False;mask[bottom-1:]=False;mask[:,:left+2]=False;mask[:,right-1:]=False
    mask[top:top+int((bottom-top)*.20),left:left+int((right-left)*.26)]=False
    clean=a.copy();clean[mask]=255
    return chart,Image.fromarray(clean),(left,top,right,bottom),mask

def dynamic_msd(im,t):
    chart,blank,(left,top,right,bottom),_=chart_layers()
    progress=max(0,min(1,(t-.7)/7.5));cut=round(left+(right-left)*progress)
    panel=blank.copy();panel.paste(chart.crop((0,0,cut,chart.height)),(0,0))
    if progress>=1:panel=chart.copy()
    x,y=550,283;im.paste(panel,(x,y));d=ImageDraw.Draw(im)
    if .01<progress<1:d.line((x+cut,y+top+2,x+cut,y+bottom-2),fill='#b6c8db',width=1)
    for yy,col,title,line1,line2 in [(375,PURPLE,'300 K · 固态','原子局域振动','MSD 接近平台'),(650,GREEN,'1600 K · 熔融态','原子扩散迁移','MSD 随时间上升')]:
        d.rounded_rectangle((90,yy,495,yy+205),radius=18,fill='white',outline=col,width=2)
        txt(im,(115,yy+24),title,32,col,True);txt(im,(115,yy+87),line1,28,INK);txt(im,(115,yy+141),line2,25,MUTED)
    note(im,'原始曲线 · 沿时间轴逐步展示')

BASE_ATOMS=np.array([(col*74+(row%2)*37-203.5,row*66-132) for row in range(5) for col in range(6)],float)

@lru_cache(1)
def liquid_frames():
    rng=np.random.default_rng(420);p=BASE_ATOMS.copy()+rng.normal(0,5,BASE_ATOMS.shape);vel=rng.normal(0,30,p.shape)
    frames=[]
    # Confined, repulsive particles illustrate rearrangement only, not an MD trajectory.
    for n in range(1200):
        vel=.985*vel+rng.normal(0,6,p.shape)
        delta=p[:,None,:]-p[None,:,:];dist=np.linalg.norm(delta,axis=2);np.fill_diagonal(dist,1e9)
        force=np.maximum(0,55-dist)[:,:,None]*delta/np.maximum(dist[:,:,None],1)
        vel+=force.sum(axis=1)*.40;vel=np.clip(vel,-85,85);p+=vel/30
        for ax,lim in [(0,240),(1,172)]:
            bad=np.abs(p[:,ax])>lim;vel[bad,ax]*=-.8;p[:,ax]=np.clip(p[:,ax],-lim,lim)
        if n>=600:frames.append(p.copy())
    return np.asarray(frames)

@lru_cache(8)
def atom_sprite(col,marked=False):
    r=24;size=2*r+4;yy,xx=np.mgrid[:size,:size];dx=(xx-r-2)/r;dy=(yy-r-2)/r;rr=dx*dx+dy*dy
    base=np.array(tuple(int(col[i:i+2],16) for i in (1,3,5)),float)
    z=np.sqrt(np.maximum(0,1-rr));shade=np.clip(.48+.36*z-.25*dx-.3*dy,.25,1.2)
    rgb=np.clip(base[None,None,:]*shade[:,:,None]+np.exp(-((dx+.35)**2+(dy+.38)**2)/.08)[:,:,None]*100,0,255)
    alpha=np.clip((1-rr)*r*1.5,0,1)*255
    return Image.fromarray(np.dstack([rgb,alpha]).astype(np.uint8))

def atoms_scene(im,t):
    d=ImageDraw.Draw(im);ids=np.arange(len(BASE_ATOMS));tick=min(599,max(0,round(t*30)))
    solid=BASE_ATOMS+np.column_stack([np.sin(t*7+ids)*3.8,np.cos(t*6.2+ids*1.3)*3.8]);liq=liquid_frames()[tick]
    for side,(points,col,title,caption) in enumerate([(solid,PURPLE,'固态','有序排列 · 平衡位置附近振动'),(liq,GREEN,'熔融态（液态）','近邻持续变化 · 原子扩散迁移')]):
        cx=510+900*side;cy=595
        d.rounded_rectangle((cx-345,340,cx+345,842),radius=30,fill='#ffffff',outline='#e0e6ef',width=2)
        txt(im,(cx,302),title,38,col,True,'mm')
        if side==0:
            for x,y in BASE_ATOMS:d.ellipse((cx+x-6,cy+y-6,cx+x+6,cy+y+6),outline='#bac4d5',width=1)
        tagged=[8,19]
        for k in tagged:
            if side==0:
                ts=np.linspace(max(0,t-3),t,45);track=BASE_ATOMS[k]+np.column_stack([np.sin(ts*7+k)*3.8,np.cos(ts*6.2+k*1.3)*3.8])
            else:track=liquid_frames()[max(0,tick-105):tick+1:3,k]
            if len(track)>1:d.line([(round(cx+x),round(cy+y)) for x,y in track],fill=col,width=3)
        for k,(x,y) in enumerate(points):
            sp=atom_sprite(col if k in tagged else '#7798c8');im.paste(sp,(round(cx+x-26),round(cy+y-26)),sp)
            if k in tagged:d.ellipse((cx+x-28,cy+y-28,cx+x+28,cy+y+28),outline=col,width=2)
        txt(im,(cx,890),caption,29,col,True,'mm')
    txt(im,(960,955),'彩色标记与轨迹，帮助比较同一原子的运动',24,MUTED,anchor='mm')

def scene(i,t):
    a,b,mode,key,title,sub=SHOTS[i]
    if mode not in ['principles','config_full','tasks','atoms_new','msd_dynamic']:return base_scene(i,t)
    im=bg();tag='平台实际画面'
    if mode=='principles':im=principles_canvas().copy();tag='计算原理示意'
    elif mode=='config_full':
        screenshot(im,'config',(595,267,1130,708))
        for y,head,body in [(380,'计算类型','按研究目标选择'),(565,'参数配置','核对方法与精度'),(750,'输入预览','检查生成的文件')]:bullet(im,100,y,head,body)
    elif mode=='tasks':
        raw(im,'case_task',min(t,1.55),b-a)
    elif mode=='atoms_new':atoms_scene(im,t);tag='运动机制示意 · 非实际轨迹'
    elif mode=='msd_dynamic':dynamic_msd(im,t);tag='平台原始图表'
    header(im,title,sub,tag);return im
