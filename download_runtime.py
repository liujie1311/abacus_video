import sys,urllib.request,json,zipfile,io,concurrent.futures
from pathlib import Path
from pip._vendor.packaging.tags import sys_tags
from pip._vendor.packaging.utils import parse_wheel_filename
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
dst=Path(__file__).parent/'packages'; dst.mkdir(exist_ok=True)
tags=list(sys_tags());rank={t:i for i,t in enumerate(tags)}
def get(name):
 data=json.load(urllib.request.urlopen('https://pypi.org/pypi/'+name+'/json',timeout=20))
 candidates=[]
 for f in data['urls']:
  if f['filename'].endswith('.whl'):
   ts=parse_wheel_filename(f['filename'])[3]
   best=min([rank[t] for t in ts if t in rank] or [999999])
   if best<999999:candidates.append((best,f))
 f=min(candidates,key=lambda x:x[0])[1]
 print('Downloading '+f['filename'],flush=True)
 blob=urllib.request.urlopen(f['url'],timeout=30).read()
 zipfile.ZipFile(io.BytesIO(blob)).extractall(dst)
 print('Ready '+name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 list(ex.map(get,['imageio-ffmpeg','edge-tts','aiohttp','aiosignal','attrs','frozenlist','multidict','propcache','yarl','aiohappyeyeballs','tabulate','certifi','typing_extensions','idna']))
