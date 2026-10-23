import os, sys, json, importlib.util
from pathlib import Path
root = Path('C:/Users/PC/Desktop/\u7d20\u6750/\u7d20\u6750')
print(sys.version)
print(json.dumps([{'path':str(p),'bytes':p.stat().st_size} for p in root.rglob('*') if p.is_file()],ensure_ascii=True,indent=2))
print({m:bool(importlib.util.find_spec(m)) for m in ['PIL','numpy','imageio_ffmpeg','cv2','edge_tts','scipy','pyttsx3']})
for p in [Path('C:/Users/PC/Desktop/AGENTS.md'),Path('C:/Users/PC/Desktop/xs/AGENTS.md')]:
    if p.exists(): print(p.read_text(encoding='utf-8'))
print('BIN', list(Path('C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback').glob('*')))
