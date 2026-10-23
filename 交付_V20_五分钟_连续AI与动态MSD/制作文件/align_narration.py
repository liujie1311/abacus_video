"""Align case narration to the five shot windows; reuse the other seven chapters."""
from pathlib import Path
import asyncio,json,sys,subprocess,re,html,wave
import numpy as np
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'packages'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000
PARTS=[(105, 115, '结构转换与参数配置，衔接不同计算环节。选择计算类型，检查参数，并预览生成的输入文件。'), (115, 125, '想研究铝合金的熔化行为，可以向智能体描述目标，比较材料在不同温度下的原子运动特征。'), (125, 138, '智能体根据研究目标梳理计算方案，列出材料体系、温度条件与执行步骤。研究人员可以逐项检查，让计算任务有明确的依据。'), (138, 150, '计算之前，还需要核对初始结构、势函数、模拟时长和输出设置。这些条件会影响结果，也是研究人员需要确认的重点。'), (150, 162, '方案明确后，在任务界面查看执行情况。这里展示了三百开尔文和一千六百开尔文两组任务，计算状态与任务名称集中呈现。'), (162, 172, '任务完成后，通过反馈中的结果文件与绘图入口，继续查看不同温度下的运动特征，让计算与分析自然衔接。'), (172, 190, '先用原子运动示意理解两种状态。固态中，原子保持有序排列，在平衡位置附近振动。熔融态中，原子持续迁移，近邻关系不断变化。标记原子的运动路径，可以直观看出这种差异。'), (190, 205, '再看实际的均方位移曲线。三百开尔文的紫色曲线接近平台，对应固态的局域振动；一千六百开尔文的绿色曲线明显上升，体现熔融态的扩散特征。'), (205, 215, '智能体辅助归纳结果，并提出进一步验证的方向。要更准确地判断熔点，还需要加密温度扫描，并核对原始数据。')]
def pcm(p):return np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(p),'-ar',str(SR),'-ac','1','-f','f32le','pipe:1']),np.float32).copy()
def wav(p,data):
    with wave.open(str(p),'wb') as f:
        f.setnchannels(1 if data.ndim==1 else data.shape[1]);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(data,-.97,.97)*32767).astype('<i2').tobytes())
def seconds(s):
    h,m,q=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(q)
def stamp(t,ass=False):
    ms=round(t*1000)
    if ass:return f'{ms//3600000}:{ms//60000%60:02d}:{ms//1000%60:02d}.{ms//10%100:02d}'
    return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
async def main():
    folder=ROOT/'制作文件/voice_aligned';folder.mkdir(exist_ok=True)
    for i,(_,_,spoken) in enumerate(PARTS):
        path=folder/f'{i:02d}.mp3';meta=path.with_suffix('.json')
        if path.exists() and meta.exists() and json.loads(meta.read_text(encoding='utf-8'))['text']==spoken:continue
        events=[]
        async def generate():
            events.clear()
            with path.open('wb') as out:
                async for c in edge_tts.Communicate(spoken.replace('ABACUSLab','ABACUS LAB'),'zh-CN-YunjianNeural',rate='+0%',pitch='-2Hz',boundary='WordBoundary').stream():
                    if c['type']=='audio':out.write(c['data'])
                    elif c['type']=='WordBoundary':events.append(c)
        for attempt in range(3):
            try:await asyncio.wait_for(generate(),55);break
            except Exception:
                if attempt==2:raise
        meta.write_text(json.dumps({'text':spoken,'events':events},ensure_ascii=False),encoding='utf-8')
        print('VOICE_CASE',i+1,flush=True)
    captions=[]
    for block in (ROOT/'中文字幕.srt').read_text(encoding='utf-8').strip().split('\n\n'):
        lines=block.splitlines();a,b=map(seconds,lines[1].split(' --> '))
        if not any(x<=a<y for x,y,_ in PARTS):captions.append([a,b,' '.join(lines[2:])])
    voice=pcm(ROOT/'音频/五分钟_男声旁白.wav');report=[]
    for a,b,_ in PARTS:voice[a*SR:b*SR]=0
    for i,(a,b,spoken) in enumerate(PARTS):
        spoken=spoken.replace('ABACUSLab','ABACUS LAB')
        path=folder/f'{i:02d}.mp3';data=pcm(path);events=json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))['events']
        active=np.flatnonzero(abs(data)>.003);lo=max(0,int(active[0])-.045*SR);hi=min(len(data),int(active[-1])+.12*SR);lo=int(lo);data=data[lo:int(hi)]
        start=a+.25;available=b-start-.35;speed=max(.94,len(data)/SR/available)
        if speed>1.20:raise ValueError(('Narration too dense',i,speed))
        data=np.frombuffer(subprocess.check_output([FF,'-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0','-af',f'atempo={speed:.7f}','-f','f32le','pipe:1'],input=data.tobytes()),np.float32).copy()
        data*=min(.15/max(float(np.sqrt(np.mean(data**2))),.001),.83/max(float(abs(data).max()),.001))
        pos=round(start*SR);voice[pos:pos+len(data)]=data
        cursor=0;phrase='';pstart=None
        new=[]
        for j,e in enumerate(events):
            word=html.unescape(e['text']);found=spoken.lower().find(word.lower(),cursor)
            if found<0:found=cursor
            stop=found+len(word)
            while stop<len(spoken) and not spoken[stop].isalnum():stop+=1
            piece=spoken[cursor:stop].strip();cursor=stop;phrase+=piece
            if pstart is None:pstart=start+(e['offset']/1e7-lo/SR)/speed
            pend=start+((e['offset']+e['duration'])/1e7-lo/SR)/speed
            if (len(phrase)>=9 and any(c in piece for c in '，。；：')) or len(phrase)>=32 or j==len(events)-1:
                new.append([max(a,pstart),min(b-.15,pend+.1),phrase.replace('ABACUS LAB','ABACUSLab')]);phrase='';pstart=None
        for j in range(len(new)-1):new[j][1]=min(new[j][1],new[j+1][0]-.02)
        captions.extend(new);report.append({'start':a,'end':b,'voice_end':start+len(data)/SR,'speed':speed,'text':spoken})
    wav(ROOT/'音频/五分钟_男声旁白.wav',voice)
    music=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(ROOT/'音频/五分钟_背景配乐.wav'),'-ar',str(SR),'-ac','2','-f','f32le','pipe:1']),np.float32).reshape(-1,2)
    wav(ROOT/'制作文件/mixed.wav',voice[:,None]+music)
    captions.sort()
    (ROOT/'中文字幕.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(captions)),encoding='utf-8')
    ass=ROOT/'制作文件/captions.ass';header=ass.read_text(encoding='utf-8').split('Dialogue:')[0]
    ass.write_text(header+'\n'.join(f'Dialogue: 0,{stamp(a,True)},{stamp(b,True)},Default,,0,0,0,,{s}' for a,b,s in captions),encoding='utf-8')
    (ROOT/'制作文件/案例配音逐镜对齐.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('ALIGNED',json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':asyncio.run(main())
