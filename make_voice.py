import sys,asyncio,json,time
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'packages'))
import edge_tts
sys.stdout.reconfigure(encoding='utf-8')
async def main():
 timeline=json.loads((BASE/'timeline.json').read_text(encoding='utf-8'))
 (BASE/'voice').mkdir(exist_ok=True)
 for i,entry in enumerate(timeline):
  dest=BASE/'voice'/f'{i:02d}.mp3'
  if dest.exists() and dest.stat().st_size>2000:continue
  text=entry['text'].replace('ABACUSLAB','ABACUS LAB')
  await asyncio.wait_for(edge_tts.Communicate(text,'zh-CN-XiaoxiaoNeural',rate='+8%').save(str(dest)),timeout=60)
  print('Voice',i,entry['text'],flush=True)
asyncio.run(main())
