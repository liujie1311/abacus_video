import urllib.request,json,concurrent.futures,io,zipfile,time,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
data=json.load(urllib.request.urlopen('https://pypi.org/pypi/imageio-ffmpeg/json',timeout=20))
f=next(f for f in data['urls'] if f['filename'].endswith('win_amd64.whl'))
print('bytes',f['size'],flush=True)
size=f['size'];parts=12;step=(size+parts-1)//parts
def get(i):
 lo=i*step;hi=min(size-1,(i+1)*step-1)
 req=urllib.request.Request(f['url'],headers={'Range':f'bytes={lo}-{hi}'})
 with urllib.request.urlopen(req,timeout=25) as r:
  if r.status!=206:raise RuntimeError('No range support')
  result=r.read()
 print('Part',i,len(result),flush=True)
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:blob=b''.join(ex.map(get,range(parts)))
assert len(blob)==size
zipfile.ZipFile(io.BytesIO(blob)).extractall(BASE/'packages')
print('FFMPEG READY',flush=True)
