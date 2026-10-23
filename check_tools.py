import os,sys,subprocess,importlib.util,urllib.request,time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
print({m:bool(importlib.util.find_spec(m)) for m in ['win32com','comtypes','requests','cv2']},flush=True)
print({k:v for k,v in os.environ.items() if any(x in k.lower() for x in ['proxy','pip_'])},flush=True)
try:
 r=subprocess.run(['powershell.exe','-NoProfile','-Command','Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name }'],capture_output=True,timeout=15)
 print(r.returncode,r.stdout.decode('utf-8','replace'),r.stderr.decode('utf-8','replace'),flush=True)
except Exception as e: print(repr(e),flush=True)
for u in ['https://pypi.org/pypi/imageio-ffmpeg/json','https://speech.platform.bing.com']:
 try:
  r=urllib.request.urlopen(u,timeout=10); print(u,r.status,flush=True)
 except Exception as e: print(u,repr(e),flush=True)
