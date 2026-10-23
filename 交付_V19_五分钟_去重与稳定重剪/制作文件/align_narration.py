"""Align case narration to the five shot windows; reuse the other seven chapters."""
from pathlib import Path
import asyncio,json,sys,subprocess,re,html,wave
import numpy as np
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'packages'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000
PARTS=[(0, 10, '新材料的发现与设计，推动科技进步。从能源材料、半导体到先进结构材料，研究不断深入微观世界。'), (10, 22, '潜在的材料空间十分广阔。不同元素的组合、不同原子的排列，带来多样的候选结构，也让寻找合适材料变得更加复杂。'), (22, 32, '从材料制备、实验表征到性能测试，研究人员反复比较和调整方案。这些过程，需要投入大量时间与资源。'), (32, 40, '材料性能源于原子结构与电子行为。理解机制，才能预测性质，探索设计。'), (70, 85, '平台集成多种常用材料计算模板，涵盖结构优化、电子结构、分子动力学和材料物性。研究人员根据目标选择方法，查看模板说明与计算步骤。'), (85, 95, '将基础计算和多步骤分析组织成可复用的工作流程，研究人员可以检查条件、调整方案，减少重复准备。'), (95, 105, '平台支持按项目组织计算任务，集中查看运行状态，让计算记录和执行进展清晰可见。'), (105, 115, '结构转换、输入准备与参数配置，衔接不同计算环节。态密度和光学响应等结果，可以通过图表直观呈现。'), (115, 125, '在专业计算能力之上，ABACUSLab 引入 AI 智能体。研究人员可以用自然语言描述需求。'), (125, 135, 'AI 辅助梳理研究目标、计算思路和所需条件。研究人员可以检查完整方案，确认后续步骤。'), (135, 145, '从任务反馈到结果入口，平台连接计算与分析环节。研究人员可以回到具体任务，逐项核对状态与文件。'), (145, 155, '研究人员还可以检查参数、调整方案，并结合科学知识作出判断，让 AI 辅助与专业判断相结合。')]
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
