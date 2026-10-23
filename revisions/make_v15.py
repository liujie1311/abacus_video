"""V15: natural-pace narration, no airy transition sweeps, scenario-aligned AI copy."""
from pathlib import Path
from functools import lru_cache
import sys, json, shutil, inspect, re, subprocess
import numpy as np
from PIL import Image, ImageDraw
import make_v14_reference_intro as prev

v = prev.v
BASE = v.BASE
ROOT = BASE / '交付_V15_210秒_铝合金融化场景_自然语速'
WORK = ROOT / '制作文件'; AUDIO = ROOT / '音频'; STILL = ROOT / '分镜预览'; ASSETS = ROOT / '素材'
for p in (ROOT, WORK, AUDIO, STILL, ASSETS): p.mkdir(parents=True, exist_ok=True)
DEST = ROOT / 'ABACUSLab_V15_3分30秒_铝合金研究场景.mp4'
v.ROOT, v.WORK, v.AUDIO, v.STILL, v.DEST = ROOT, WORK, AUDIO, STILL, DEST
v.VOICE = WORK / 'voice'
v.VOICE.mkdir(parents=True, exist_ok=True)
v.PLAN = ROOT

ENTRIES = [
 (0,15,'从微观结构，到材料性能，每一次探索，都需要可靠的计算工具。ABACUSLab，连接材料计算与分析的研究平台。'),
 (15,40,'面向不同的研究需求，平台汇集多种常用计算模板。从基础计算，到多步骤分析，把计算方法组织成可以复用的流程。让研究有据可循，让新的计算，不必每次都从头准备。'),
 (40,60,'围绕不同研究目标，按项目组织计算任务。已有方案可以继续使用，也可以调整和复用。让一次次计算积累为清晰的研究过程，让不同任务井然有序。'),
 (60,80,'统一管理计算任务，实时掌握运行进展，让计算过程清晰可追踪。从整体进度，到关键环节，需要了解的信息集中呈现，帮助研究者及时作出判断。'),
 (80,100,'结构转换、输入文件准备与参数配置，在工具箱中集中完成。连接不同计算环节，减少反复整理与手工衔接，让准备工作更加顺畅。'),
 (100,120,'从态密度到光学响应，多种物性可视化工具，把计算结果转化为直观的图像。观察差异，理解变化，让数据成为继续探索的依据。'),
 (120,145,'研究还可以从一个具体问题开始。比如，想了解铝合金的融化行为，可以先描述研究目标。智能体辅助梳理计算思路、所需条件与待确认的问题，让研究问题逐步变成清晰的研究方案。'),
 (145,170,'方案明确后，平台可协助组织计算任务、查看执行进展，并衔接绘图工具。这里展示的是平台各环节的功能示例，研究者可以回到具体任务和数据中逐项核对，让计算过程更有条理。'),
 (170,195,'面对图表，AI可以辅助归纳主要变化、说明可能的解释，并提示结论边界与后续验证方向。具体判断仍需结合材料体系、计算设置和原始数据。让分析成为研究的起点，而不是结论的替代。'),
 (195,210,'从模板与任务管理，到计算分析与智能协助。ABACUSLab，让材料计算更简单，把更多精力，留给研究与发现。')]
v.ENTRIES = ENTRIES

# The inherited generator applied a slow synthesis rate before atempo processing.
# V15 synthesizes at the voice's natural rate; duration fitting happens only if needed.
voice_src = inspect.getsource(v.voices).replace("rate='-8%'", "rate='+0%'")
exec(compile(voice_src, '<v15_voices>', 'exec'), v.__dict__)

# Build an explicitly editorial prompt card; do not alter the source screenshot or
# make changed copy look like a historical product conversation.
prompt = Image.new('RGB', (1120, 410), '#ffffff')
d = ImageDraw.Draw(prompt)
d.rounded_rectangle((3,3,1117,407),radius=24,fill='#ffffff',outline='#dbe4f2',width=3)
d.rounded_rectangle((28,26,1092,382),radius=16,fill='#fbfcff',outline='#cdd8eb',width=2)
font = v.font(34, False)
d.text((65,61),'研究目标示例',font=v.font(23,True),fill='#5368eb')
d.text((65,127),'我想研究铝合金的融化行为，',font=font,fill='#25334d')
d.text((65,184),'应该如何设计计算与分析流程？',font=font,fill='#25334d')
d.rounded_rectangle((65,280,325,337),radius=14,fill='#eef2ff')
d.text((84,293),'演示文案 · 非历史对话',font=v.font(20,False),fill='#627fab')
prompt.save(ASSETS/'AI研究目标_编辑示意.png')
v.IMG['question'] = prompt

# V13's scene variant, with clearer editorial labeling for separate feature examples.
old_scene = prev.prev.scene
def scene(kind,t,span):
    if kind == 'question':
        im = old_scene(kind,t,span)
        v.enter(im,(113,351),'研究铝合金的融化行为',t,.15,62)
        v.label(im,'研究目标示例',117,472,t,.5)
        return im
    if kind == 'complete':
        im = old_scene(kind,t,span)
        return im
    if kind == 'msd':
        im = old_scene(kind,t,span)
        # Keep the real chart intact while clearly separating it from the alloy prompt.
        v.text(im,(114,630),'平台图表功能示例',25,v.BLUE,True)
        return im
    return prev.prev.scene(kind,t,span)
v.scene = scene
base_frame = prev.prev.frame
def frame(t):
    if t < 7:
        return prev.first_frames(t)
    return base_frame(t)
v.frame = frame

# Preserve the established 210-second picture timeline and copy the revised script.
timeline = ROOT / '台词时间轴.md'
topics=['平台定位','模板库','项目与任务管理','工作流监控','工具协同','物性分析','AI：铝合金融化研究目标','AI：计算与绘图功能示例','AI：图表分析与结论边界','品牌收束']
durations=[15,25,20,20,20,20,25,25,25,15]
def fmt(s): return f'{s//60:02d}:{s%60:02d}'
rows=['# ABACUSLab 宣传片｜V15旁白与时间轴','','| 时间 | 时长 | 主题 | 旁白全文 |','|---|---:|---|---|']
for i,((a,b,copy),topic) in enumerate(zip(ENTRIES,topics)):
    rows.append(f'| {fmt(a)}—{fmt(b)} | {durations[i]}秒 | {topic} | {copy} |')
timeline.write_text('\n'.join(rows)+'\n',encoding='utf-8')

# Patch only mix behavior: enter promptly, synthesize at natural rate, and omit
# the filtered-noise whooshes that created an inhaling/sucking transition sound.
src = inspect.getsource(v.mix)
src = src.replace('start=a+(1.6 if i==0 else .65);available=b-start-.7',
                  'start=a+(0.45 if i==0 else .55);available=b-start-1.0')
src = src.replace('speed=max(.86,len(data)/sr/available)', 'speed=max(1.0,len(data)/sr/available)')
src = re.sub(r'    # Soft airy transitions at chapter boundaries, independent of any UI action\.\n.*?    timeline=np.arange\(n\)/sr',
             '    # Chapter transitions use music continuity and picture dissolves only.\n    timeline=np.arange(n)/sr', src, flags=re.S)
exec(compile(src, '<v15_mix>', 'exec'), v.__dict__)

def docs():
    (ROOT/'V15修改说明.md').write_text('''# V15 修改说明

- AI研究目标示例改为“研究铝合金的融化行为”，并明确标注为编辑示意，不冒充历史对话。
- AI旁白讲清研究目标、计算思路、所需条件与待确认问题；后续用“平台功能示例”提示切换，避免暗示其他图表就是该铝合金案例的结果。
- 重新合成统一自然语速中文男声；开场尽早进入旁白，不再整体慢放。
- 删除配乐中的滤波噪声扫音，转场由音乐延续和画面叠化完成。
- 总时长210秒，沿用V14参考片头、蓝白视觉和平台实际截图。

旁白台词见“台词时间轴.md”；检查记录见“成片检查.json”。
''',encoding='utf-8')

def final():
    v.run(['-y','-i',str(WORK/'picture.mp4'),'-i',str(WORK/'mixed.wav'),'-map','0:v','-map','1:a',
           '-c:v','copy','-af','loudnorm=I=-17:TP=-3:LRA=9,aresample=48000,alimiter=limit=0.78:level=false:latency=true',
           '-ar','48000','-c:a','aac','-b:a','192k','-t','210','-movflags','+faststart',str(DEST)])

def check():
    info=subprocess.run([v.FF,'-hide_banner','-i',str(DEST)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
    assert '1920x1080' in info and '30 fps' in info and 'h264' in info and 'aac' in info, info
    decoded=subprocess.run([v.FF,'-v','error','-i',str(DEST),'-f','null','-'],capture_output=True,text=True)
    assert decoded.returncode==0 and not decoded.stderr, decoded.stderr[:1000]
    pcm=subprocess.check_output([v.FF,'-v','error','-i',str(DEST),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1'])
    audio=np.frombuffer(pcm,np.float32).reshape(-1,2);duration=len(audio)/48000;peak=float(abs(audio).max())
    assert abs(duration-210)<.1 and peak<.98,(duration,peak)
    checks=json.loads((WORK/'配音时间核验.json').read_text(encoding='utf-8'))
    assert len(checks)==10 and all(x['speed_adjust']==1.0 for x in checks)
    for x,(a,b,_) in zip(checks,ENTRIES): assert a < x['start'] < x['end'] < b,(x,a,b)
    times=[4,11,26,44,71,85,104,116,124,132,139,149,164,174,182,191,198,206]
    sheet=Image.new('RGB',(1440,6*300),'#e7edf6')
    for i,t in enumerate(times):
        raw=subprocess.check_output([v.FF,'-v','error','-ss',str(t),'-i',str(DEST),'-frames:v','1','-vf','scale=480:270','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        im=Image.frombytes('RGB',(480,270),raw);x=i%3*480;y=i//3*300
        v.text(sheet,(x+10,y+3),f'{t//60:02d}:{t%60:02d}',20);sheet.paste(im,(x,y+30))
    sheet.save(ROOT/'成片抽帧检查.jpg',quality=95)
    report={'duration_seconds':duration,'resolution':'1920x1080','fps':30,'video_codec':'H.264','audio_codec':'AAC','decode_errors':0,
            'audio_peak_linear':peak,'narration_sections':len(checks),'all_speed_adjustments':1.0,'shots':len(v.SHOTS),
            'size_mb':round(DEST.stat().st_size/1048576,1),'transition_noise_sweeps_removed':True,
            'checks':'Full decode, duration, audio peak, narration boundaries, natural-speed metadata and contact sheet.'}
    (ROOT/'成片检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'previews'
    docs()
    if mode=='voice':
        import asyncio
        asyncio.run(v.voices())
    elif mode=='mix': v.mix()
    elif mode=='previews': v.previews()
    elif mode=='picture': v.picture()
    elif mode=='final': final()
    elif mode=='check': check()
