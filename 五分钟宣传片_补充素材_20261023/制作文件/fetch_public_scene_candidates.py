from pathlib import Path
import urllib.request,urllib.parse,json,concurrent.futures
SCRIPT_DIR=Path(__file__).resolve().parent
BASE=SCRIPT_DIR.parent if SCRIPT_DIR.name=='制作文件' else SCRIPT_DIR
ROOT=BASE/'五分钟宣传片_补充素材_20261023'
OUT=ROOT/'制作文件'
UA='ABACUSLabVideoAssetResearch/1.0 (educational production; source metadata retained)'
def find(q):
    args={'action':'query','format':'json','generator':'search','gsrsearch':q,'gsrnamespace':6,'gsrlimit':5,'prop':'imageinfo','iiprop':'url|size|extmetadata','iiurlwidth':1280}
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(args)
    try:
        req=urllib.request.Request(url,headers={'User-Agent':UA})
        with urllib.request.urlopen(req,timeout=25) as r:data=json.load(r)
        rows=[]
        for p in data.get('query',{}).get('pages',{}).values():
            i=p.get('imageinfo',[{}])[0];m=i.get('extmetadata',{})
            rows.append({'title':p['title'],'url':i.get('url'),'thumb':i.get('thumburl'),'width':i.get('width'),'height':i.get('height'),'page':i.get('descriptionurl'),'license':m.get('LicenseShortName',{}).get('value'),'license_url':m.get('LicenseUrl',{}).get('value'),'artist':m.get('Artist',{}).get('value'),'description':m.get('ImageDescription',{}).get('value'),'restrictions':m.get('Restrictions',{}).get('value')})
        return {'query':q,'candidates':rows}
    except Exception as e:return {'query':q,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    results=list(ex.map(find,['silicon wafer semiconductor','materials laboratory electron microscope','solar panel photovoltaic farm']))
(OUT/'公共科研画面候选.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
