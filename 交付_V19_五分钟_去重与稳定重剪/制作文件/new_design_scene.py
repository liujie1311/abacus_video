from pathlib import Path
import importlib.util,bpy,math
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent
spec=importlib.util.spec_from_file_location('model',BASE/'交付_V18_五分钟_按方案实景重制/制作文件/build_concept_3d.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.reset()
for group in range(3):
    cx=(group-1)*3.15
    m.box((cx,0,.03),(2.7,2.7,.14),m.white)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if group==2 and i==1 and j==0 and k==2:continue
                loc=(cx+(i-1)*.7,(j-1)*.7,.7+k*.7)
                mat=m.teal if group==1 and (i+j+k)%4==0 else m.blue
                m.sphere(loc,.16,mat)
                if i<2:m.rod(loc,(loc[0]+.7,loc[1],loc[2]),.025,m.pale)
                if j<2:m.rod(loc,(loc[0],loc[1]+.7,loc[2]),.025,m.pale)
                if k<2 and not(group==2 and i==1 and j==0 and k==1):m.rod(loc,(loc[0],loc[1],loc[2]+.7),.025,m.pale)
bpy.context.scene.render.filepath=str(ROOT/'素材/设计候选_新构图.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'素材/设计候选_新构图.blend'))
