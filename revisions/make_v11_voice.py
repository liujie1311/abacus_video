"""Replace the transition narration, preserving V10's encoded video."""
import asyncio
import hashlib
import json
import shutil
import subprocess
import sys
import numpy as np
import make_v9_reorder as p

ROOT = p.BASE/'交付_V11_60秒_物性计算衔接文案'
OUT = ROOT/'04_视频成片'
WORK = OUT/'制作文件'
VOICE = WORK/'voice'
BASE10 = p.BASE/'交付_V10_60秒_去小字_更新平台画面'
SOURCE = BASE10/'04_视频成片/ABACUSLab_V10_60秒_去小字_更新平台画面_无字幕.mp4'
DEST = OUT/'ABACUSLab_V11_60秒_物性计算衔接文案_无字幕.mp4'
TEXT = '有了这些模板，进行物性计算，只需向 AI 说出你的需求。'
ENTRIES = list(p.ENTRIES)
ENTRIES[2] = (16,23,TEXT)
for folder in [ROOT/'01_演讲稿', ROOT/'02_分镜脚本', ROOT/'03_素材', ROOT/'05_音频', VOICE]:
    folder.mkdir(parents=True,exist_ok=True)
for i in range(7):
    if i != 2:
        shutil.copy2(p.VOICE/f'{i:02d}.mp3',VOICE/f'{i:02d}.mp3')
p.v.ROOT = ROOT
p.v.WORK = WORK
p.v.VOICE = VOICE
p.v.ENTRIES = ENTRIES

async def voice():
    import edge_tts
    await asyncio.wait_for(edge_tts.Communicate(TEXT,'zh-CN-YunjianNeural',rate='-5%').save(str(VOICE/'02.mp3')),timeout=50)
    print('New transition voice ready',flush=True)

def build():
    p.v.mix_audio(60)
    p.m.run(['-y','-i',str(SOURCE),'-i',str(WORK/'配音与音乐.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','volume=0.8','-c:a','aac','-b:a','192k','-t','60','-movflags','+faststart',str(DEST)])
    rows = ['# V11 演讲稿｜60 秒','','普通话男声；无配音字幕。','','| 时间（秒） | 配音内容 |','|---|---|']
    rows += [f'| {a}—{b} | {text} |' for a,b,text in ENTRIES]
    (ROOT/'01_演讲稿/演讲稿_含时间.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    (ROOT/'01_演讲稿/演讲稿_纯配音.txt').write_text('\n\n'.join(text for _,_,text in ENTRIES)+'\n',encoding='utf-8')
    storyboard = (BASE10/'02_分镜脚本/分镜脚本_含时间.md').read_text(encoding='utf-8').replace('# V10','# V11')
    storyboard += '\n16—23 秒配音更新为：'+TEXT+'\n画面继续以金属熔化研究作为物性计算的具体示例。\n'
    (ROOT/'02_分镜脚本/分镜脚本_含时间.md').write_text(storyboard,encoding='utf-8')
    shutil.copy2(BASE10/'03_素材/分镜总览.jpg',ROOT/'03_素材/分镜总览.jpg')
    (ROOT/'03_素材/素材说明.txt').write_text('本版画面与 V10 完全一致，原始素材及六秒开场位于：\n'+str(BASE10/'03_素材')+'\n',encoding='utf-8')
    p.m.run(['-y','-ss','13','-i',str(DEST),'-t','12','-vn','-c:a','libmp3lame','-b:a','192k',str(ROOT/'05_音频/衔接配音试听_13至25秒.mp3')])
    print('DONE',DEST,flush=True)

def check():
    def output(args):return subprocess.check_output([p.FF,'-v','error',*args])
    def video_hash(path):
        return hashlib.sha256(output(['-i',str(path),'-map','0:v:0','-c','copy','-f','h264','pipe:1'])).hexdigest()
    assert video_hash(DEST)==video_hash(SOURCE)
    report = json.loads((WORK/'配音检查.json').read_text(encoding='utf-8'))
    assert report[2]['text']==TEXT and report[2]['end']<23
    for take,(_,end,_) in zip(report,ENTRIES):assert take['end']<end
    old_report=json.loads((p.WORK/'配音检查.json').read_text(encoding='utf-8'))
    assert all(report[i]==old_report[i] for i in range(7) if i!=2)
    pcm=np.frombuffer(output(['-i',str(DEST),'-f','f32le','-ar','16000','-ac','1','pipe:1']),np.float32)
    assert abs(len(pcm)/16000-60)<.08 and float(abs(pcm).max())<.98
    old_mix=np.frombuffer(output(['-i',str(p.WORK/'配音与音乐.wav'),'-f','f32le','-ar','48000','pipe:1']),np.float32).reshape(-1,2)
    new_mix=np.frombuffer(output(['-i',str(WORK/'配音与音乐.wav'),'-f','f32le','-ar','48000','pipe:1']),np.float32).reshape(-1,2)
    assert np.array_equal(old_mix[:16*48000],new_mix[:16*48000])
    assert np.array_equal(old_mix[23*48000:],new_mix[23*48000:])
    result={'duration':len(pcm)/16000,'video_identical_to_v10':True,'other_narration_and_music_unchanged':True,'transition':report[2],'audio_peak':float(abs(pcm).max())}
    (OUT/'成片检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    if sys.argv[1]=='voice':asyncio.run(voice())
    elif sys.argv[1]=='build':build()
    elif sys.argv[1]=='check':check()
