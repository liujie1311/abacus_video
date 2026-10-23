from pathlib import Path
import sys,json,asyncio,time
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent
sys.path.insert(0,str(BASE/'packages'))
import edge_tts
VOICE=ROOT/'制作文件/voice'
VOICE.mkdir(exist_ok=True)
async def main():
    sections=json.loads((ROOT/'制作文件/原稿章节.json').read_text(encoding='utf-8'))
    assert len(sections)==8,len(sections)
    for i,entry in enumerate(sections):
        p=VOICE/f'{i:02d}.mp3';meta=VOICE/f'{i:02d}.json'
        if p.exists() and meta.exists() and p.stat().st_size>10000:continue
        spoken=entry['text'].replace('ABACUSLab','ABACUS LAB')
        if i==4:spoken=spoken.replace('以铝合金熔化行为研究为例。','以铝合金熔化行为研究为例，看看平台如何衔接计算与分析。')
        start=time.time();events=[]
        async def generate():
            communication=edge_tts.Communicate(spoken,'zh-CN-YunjianNeural',rate='+0%',pitch='-2Hz',boundary='WordBoundary')
            with p.open('wb') as f:
                async for c in communication.stream():
                    if c['type']=='audio':f.write(c['data'])
                    elif c['type'] in ['WordBoundary','SentenceBoundary']:events.append(c)
        await asyncio.wait_for(generate(),timeout=55)
        meta.write_text(json.dumps({'text':entry['text'],'spoken_text':spoken,'voice':'zh-CN-YunjianNeural','rate':'+0%','events':events},ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'VOICE {i+1}/8 | {len(events)} boundaries | {time.time()-start:.1f}s',flush=True)
if __name__=='__main__':asyncio.run(main())
