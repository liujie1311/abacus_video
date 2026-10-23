"""Local Blender scene construction. Original concept renders, no AI API or measured data."""
import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'素材/本地三维概念图'
OUT.mkdir(parents=True,exist_ok=True)
random.seed(24)

def material(name,color,metal=0,rough=.3,transmission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    p.inputs['Transmission Weight'].default_value=transmission
    return m

def finish(o,mat,bevel=0):
    o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Soft manufactured edges','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def box(loc,size,mat,bevel=.06):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object
    o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,mat,bevel)

def sphere(loc,r,mat,scale=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=r,location=loc);o=bpy.context.object
    if scale:o.scale=scale
    for p in o.data.polygons:p.use_smooth=True
    return finish(o,mat)

def cyl(loc,r,depth,mat,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc);o=bpy.context.object
    if rot:o.rotation_euler=rot
    return finish(o,mat,.025)

def rod(a,b,r,mat):
    v=Vector(b)-Vector(a);o=cyl((Vector(a)+Vector(b))/2,r,v.length,mat)
    o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return o

def ring(loc,major,minor,mat,rot=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,location=loc,major_radius=major,minor_radius=minor)
    o=bpy.context.object
    if rot:o.rotation_euler=rot
    return finish(o,mat)

def reset():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.materials):bpy.data.materials.remove(m)
    global white,silver,blue,teal,pale,glass,amber,cloud
    white=material('Porcelain white',(.86,.90,.96),.05,.3)
    silver=material('Brushed aluminium',(.55,.66,.78),.65,.28)
    blue=material('Research blue',(.16,.30,.65),.30,.27)
    teal=material('Research cyan',(.13,.62,.69),.25,.28)
    pale=material('Pale blue',(.58,.74,.89),.12,.3)
    glass=material('Electron density glass',(.23,.64,.78),.02,.23,.55)
    cloud=bpy.data.materials.new('Continuous electron density cloud');cloud.use_nodes=True
    nodes=cloud.node_tree.nodes;nodes.clear();links=cloud.node_tree.links
    out=nodes.new('ShaderNodeOutputMaterial');volume=nodes.new('ShaderNodeVolumePrincipled')
    volume.inputs['Color'].default_value=(.13,.48,.78,1)
    tex=nodes.new('ShaderNodeTexCoord');dist=nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,.5)
    ramp=nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.10;ramp.inputs['From Max'].default_value=.5
    ramp.inputs['To Min'].default_value=4;ramp.inputs['To Max'].default_value=0
    links.new(tex.outputs['Generated'],dist.inputs[0]);links.new(dist.outputs['Value'],ramp.inputs[0])
    links.new(ramp.outputs[0],volume.inputs['Density']);links.new(volume.outputs[0],out.inputs['Volume'])
    amber=material('Warm material accent',(.80,.60,.30),.45,.3)
    plane=material('Light backdrop',(.91,.94,.985),0,.7)
    floor=box((0,0,-.20),(200,200,.22),plane,.0)
    floor.is_shadow_catcher=True
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    try:
        cp=bpy.context.preferences.addons['cycles'].preferences
        cp.compute_device_type='CUDA';cp.get_devices()
        for d in cp.devices:d.use=d.type!='CPU'
        if any(d.type!='CPU' for d in cp.devices):scene.cycles.device='GPU'
    except Exception as e:print('CPU rendering',e,flush=True)
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.85,.91,1,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
    for name,loc,power,size in [('Key',(1,-4,9),1600,7),('Fill',(-7,-1,5),1100,6),('Rim',(3,5,7),1500,5)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
        o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc
        o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
    camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata)
    scene.collection.objects.link(cam);cam.location=(8,-12,8)
    cam.rotation_euler=(Vector((0,0,1.25))-cam.location).to_track_quat('-Z','Y').to_euler()
    camdata.type='ORTHO';camdata.ortho_scale=11.3;scene.camera=cam
    scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.film_transparent=True
    scene.view_settings.view_transform='AgX'
    scene.render.threads_mode='FIXED';scene.render.threads=6

def lattice(origin=(0,0,1.5),kind='fcc',spacing=.53,n=5,r=.16,links=False):
    pts=[]
    for i in range(n):
        for j in range(n):
            for k in range(n if kind!='layer' else 2):
                if kind=='fcc' and (i+j+k)%2:continue
                p=(origin[0]+(i-(n-1)/2)*spacing,origin[1]+(j-(n-1)/2)*spacing,origin[2]+(k-(n-1)/2)*spacing)
                pts.append(p);sphere(p,r,blue if kind=='fcc' else (teal if (i+j+k)%4==0 else silver))
    if links:
        for i,a in enumerate(pts):
            for b in pts[i+1:]:
                dist=(Vector(a)-Vector(b)).length
                if spacing*.95<dist<spacing*1.45:rod(a,b,.022,pale)

def energy():
    # Exploded electrode layers and discrete active-material particles.
    for z,m,thick in [(.18,silver,.16),(.72,blue,.20),(1.55,white,.12),(2.25,teal,.18),(2.85,silver,.12)]:
        box((0,0,z),(4.7,3.1,thick),m)
    for i in range(10):
        for j in range(7):
            sphere((-2.05+i*.45,-1.25+j*.40,1.05+random.random()*.1),.14,blue)
            sphere((-2.05+i*.45,-1.25+j*.40,2.47+random.random()*.08),.12,teal)
    for x in [-1.4,1.4]:box((x,2.0,2.84),(1,.9,.12),silver)

def wafer():
    cyl((0,0,.25),3.12,.20,silver)
    cyl((0,0,.37),3.03,.035,pale)
    for i in range(-5,6):
        for j in range(-5,6):
            x=i*.52;y=j*.52
            if x*x+y*y<7.25:
                box((x,y,.405),(.46,.46,.035),blue if (i+j)%3 else teal,.014)
                box((x,y,.43),(.24,.25,.02),pale,.008)
    box((3.1,-2,.52),(1.5,1.4,.22),silver)
    box((3.1,-2,.66),(1.25,1.15,.07),blue)
    for i in range(7):
        box((2.58+i*.17,-2.77,.53),(.055,.33,.04),amber,.006)

def composite():
    for k in range(5):
        z=.25+k*.49;box((0,0,z),(5.2,3.1,.18),silver if k%2==0 else pale)
        for j in range(24):
            y=-1.42+j*.123
            rod((-2.48,y,z+.15),(2.48,y,z+.15),.032,blue if k%2 else teal)
        for j in range(17):
            x=-2.4+j*.30;rod((x,-1.48,z+.19),(x,1.48,z+.19),.023,pale)

def candidates():
    for i in range(3):
        x=(i-1)*3.1;cyl((x,0,.04),1.28,.15,white)
        lattice((x,0,1.35),'fcc' if i==0 else 'layer' if i==1 else 'cube',.44,4,.12,True)

def preparation():
    box((0,.4,.10),(6.2,3.6,.24),white)
    # Bench tube furnace, open channel and a ceramic sample boat in front.
    box((.8,1,1.1),(3.7,1.65,1.75),white,.18)
    cyl((.8,0,1.35),.70,3.2,silver,(0,math.pi/2,0))
    for x in [-.85,2.45]:
        ring((x,0,1.35),.55,.14,white,(0,math.pi/2,0))
    cyl((2.48,0,1.35),.49,.035,pale,(0,math.pi/2,0))
    box((-1.3,-1.15,.46),(2.8,.8,.27),white)
    for x in [-2.3,-1.6,-.9]:box((x,-1.15,.66),(.47,.48,.12),teal)
    rod((-3,1,.25),(-3,1,3.3),.11,silver)
    rod((-3,1,3.3),(-1.65,-.75,3.3),.09,white)
    cyl((-1.65,-.75,2.8),.13,.95,silver)
    cyl((-1.65,-.75,2.15),.035,.37,teal)

def characterization():
    box((.5,.6,.25),(4.3,2.8,.5),white)
    box((1,1,1.55),(2.2,1.65,2.1),white,.16)
    cyl((-.1,-.35,3.0),.46,2.0,white)
    for z in [2.25,2.6,3.4,3.8]:cyl((-.1,-.35,z),.51,.10,silver)
    cyl((-.1,-.35,1.6),.30,.7,silver)
    cyl((-.1,-.35,.92),.95,.24,silver)
    box((-.1,-.35,1.09),(.75,.68,.13),teal)
    rod((-.1,-.35,1.2),(-.1,-.35,1.4),.03,teal)
    # Raised side lens illustrates a microstructural region without a fake UI.
    ring((-2.4,-.1,1.7),.88,.10,silver,(math.pi/2,0,0))
    for i in range(15):
        a=i*2.4;r=.65*math.sqrt(i/15)
        sphere((-2.4+r*math.cos(a),-.1,1.7+r*math.sin(a)),.12,teal if i%3 else blue)

def testing():
    box((0,0,.20),(4.8,2.6,.40),white,.13)
    for x in [-1.85,1.85]:
        cyl((x,0,2.4),.16,4.4,silver)
        cyl((x,0,.56),.30,.22,blue)
    box((0,0,4.4),(4.4,.9,.37),white)
    box((0,0,3.65),(4.1,1.05,.44),pale)
    for z in [1.02,3.14]:box((0,0,z),(1.08,.85,.65),silver)
    # Dog-bone sample: wide ends and narrow gauge section.
    box((0,0,2.08),(.34,.13,1.35),teal,.07)
    for z in [1.37,2.8]:box((0,0,z),(.78,.15,.40),teal,.08)

def adjustment():
    box((0,0,.18),(5.9,3.4,.36),white,.14)
    for i in range(3):
        for j in range(2):
            x=-1.9+i*1.85;y=-.65+j*1.3
            cyl((x,y,.45),.57,.18,pale)
            box((x,y,.61),(.64,.56,.13),[silver,teal,blue][i])
    rod((-2.2,1.5,.68),(2.4,1.5,.68),.08,silver)
    for x in [-1,1.2]:box((x,1.2,.70),(.16,1,.23),silver)
    box((1.15,1.5,.87),(.72,.55,.24),white)

def macro_atoms():
    for z,m in [(.25,silver),(.52,pale),(.8,teal)]:box((-1.55,.3,z),(2.7,2.9,.19),m)
    lattice((1.3,0,1.7),'fcc',.70,5,.18,True)

def electrons(density=False):
    pts=[(-1.65,0,1.8),(0,0,1.8),(1.65,0,1.8),(0,1.65,1.8),(0,-1.65,1.8)]
    for p in pts:sphere(p,.25,silver)
    for x,y,z in pts:
        sphere((x,y,z),.85,glass if density else cloud,(1.17,.9,1.15))
    for p in pts[1:]:rod(pts[0],p,.032,pale)
    if density:
        for i in range(5):
            ring((0,0,.25+i*.18),2.5-i*.31,.033,teal)
        box((0,0,.25),(5.2,4.3,.055),pale,.04)
    else:
        for p in [(-.8,0,1.8),(.8,0,1.8),(0,.8,1.8),(0,-.8,1.8)]:sphere(p,.62,cloud,(1.2,.8,.8))

def state(liquid=False):
    if not liquid:lattice((0,0,1.6),'fcc',.67,5,.23,False)
    else:
        pts=[];tries=0
        while len(pts)<63 and tries<20000:
            tries+=1;p=Vector((random.uniform(-1.6,1.6),random.uniform(-1.6,1.6),random.uniform(.3,3.0)))
            if all((p-q).length>.51 for q in pts):pts.append(p);sphere(p,.23,blue)

BUILDERS={'G01':energy,'G02':wafer,'G03':composite,'G04':candidates,'G05':preparation,'G06':characterization,'G07':testing,'G08':adjustment,'G09':macro_atoms,'G10':lambda:electrons(False),'G11':lambda:electrons(True),'G12':lambda:state(False),'G13':lambda:state(True),'G14':candidates}

def main():
    selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(BUILDERS)
    overwrite='--overwrite' in selected
    if overwrite:selected.remove('--overwrite')
    raw=OUT/'render_raw';raw.mkdir(exist_ok=True)
    for key in selected:
        dest=raw/f'{key}.png'
        if dest.exists() and not overwrite:print('EXISTS',key,flush=True);continue
        reset();BUILDERS[key]()
        if key=='G07':
            cam=bpy.context.scene.camera
            cam.rotation_euler=(Vector((0,0,2))-cam.location).to_track_quat('-Z','Y').to_euler()
        bpy.context.scene.render.filepath=str(dest)
        print('RENDER',key,flush=True);bpy.ops.render.render(write_still=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'{key}.blend'))
        print('READY',key,flush=True)
    (OUT/'制作来源.json').write_text(json.dumps({'method':'Blender local procedural 3D modelling and Cycles rendering','api_used':False,'scientific_status':'Conceptual illustrations; not experimental records, trajectories, charge-density calculations or material performance data.','assets':[p.name for p in OUT.glob('G*.png')]},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
