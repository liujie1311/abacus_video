from pathlib import Path
import urllib.request,urllib.parse,re,json,html,concurrent.futures,hashlib,sys
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'交付_V18_五分钟_按方案实景重制'
OUT=ROOT/'素材/网络原始素材';OUT.mkdir(parents=True,exist_ok=True)
FILES=[('battery','Lithium Battery Research at Adelphi Lab Center.jpg'),('wafer','Silicon wafer researcher.jpg'),('manufacture','A semiconductor wafer being removed from processing equipment.jpg'),('sem','Electron microscope at Oak Ridge National Lab. (7209791480).jpg'),('prep','Scientist prepares samples in laboratory using various tools and equipment.jpg'),('tensile','Tensile test - steel sample.ogv'),('composite','Glare honeycomb.jpg'),('blade','F100 TURBINE BLADE - NARA - 17497755.jpg')]
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'ABACUSLab-video-materials/1.0 (educational media attribution research)'})
    with urllib.request.urlopen(req,timeout=30) as f:return f.read()
def one(entry):
    key,title=entry;url='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(title.replace(' ','_'));record={'key':key,'title':title,'page':url}
    try:
        h=fetch(url).decode('utf-8');(OUT/f'{key}_source.html').write_text(h,encoding='utf-8')
        m=re.search(r'class="fullMedia"[\s\S]{0,900}?href="([^"]+)"',h)
        if not m:raise RuntimeError('No original link')
        direct=html.unescape(m.group(1));record['download']=direct
        path=OUT/(key+Path(title).suffix);path.write_bytes(fetch(direct));record.update({'file':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'ok':True})
        for field in ['Artist','LicenseShortName','LicenseUrl']:
            record[field]='Review saved source page'
    except Exception as e:record.update({'ok':False,'error':str(e)})
    print(json.dumps(record,ensure_ascii=False),flush=True);return record
if __name__=='__main__':
    if '--download-video' in sys.argv:
        ids={'mechanical':'jsc2021m000812_WSTF-Mechanical Impact','solar':'GRC-2022-CM-0188.13'}
        records=[]
        for key,id in ids.items():
            try:
                collection='https://images-assets.nasa.gov/video/'+urllib.parse.quote(id)+'/collection.json';urls=json.loads(fetch(collection))
                options=[u for u in urls if u.lower().endswith('.mp4')]
                print(json.dumps({'key':key,'options':options}),flush=True)
                url=next((u for u in options if '~medium.' in u),next((u for u in options if '~small.' in u),options[0]))
                url=urllib.parse.quote(url.replace('http://','https://'),safe=':/%~')
                path=OUT/(key+'.mp4')
                if path.exists() and path.stat().st_size>1000000:
                    records.append({'key':key,'id':id,'collection':collection,'download':url,'file':str(path),'bytes':path.stat().st_size,'ok':True});continue
                with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as src,path.open('wb') as dest:
                    while chunk:=src.read(1024*1024):dest.write(chunk)
                records.append({'key':key,'id':id,'collection':collection,'download':url,'file':str(path),'bytes':path.stat().st_size,'ok':True})
                print(json.dumps(records[-1]),flush=True)
            except Exception as e:print(str(e),flush=True)
        (OUT/'NASA_视频记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
        sys.exit()
    if '--download-nasa' in sys.argv:
        chosen={'energy':'GRC-2019-C-09534','wafer':'GRC-2015-C-00598','composite':'MSFC-1700849','prep':'KSC-20221102-PH-KLS01_0089','sample':'KSC-20221102-PH-KLS01_0085','sem':'1300931','xps':'1300929','manufacture':'MSFC-1600394'}
        entries=[]
        for p in OUT.glob('*.json'):
            try:
                d=json.loads(p.read_text(encoding='utf-8'))
                if isinstance(d,list):entries.extend(x for x in d if isinstance(x,dict) and 'id' in x)
            except Exception:pass
        def download(kv):
            key,id=kv;record=next(x.copy() for x in entries if x['id']==id)
            try:
                urls=json.loads(fetch(record['collection']));options=[u for u in urls if u.lower().endswith(('.jpg','.png','.jpeg'))]
                url=next((u for u in options if '~large.' in u),next((u for u in options if '~orig.' in u),options[0]))
                data=fetch(url);p=OUT/(key+Path(urllib.parse.urlparse(url).path).suffix);p.write_bytes(data)
                record.update(key=key,file=str(p),download=url,ok=True,sha256=hashlib.sha256(data).hexdigest())
                print(json.dumps({'key':key,'id':id,'bytes':len(data),'ok':True}),flush=True)
            except Exception as e:record.update(key=key,ok=False,error=str(e));print(str(e),flush=True)
            return record
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:r=list(pool.map(download,chosen.items()))
        (OUT/'NASA_素材记录.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
        for url in ['https://www.nasa.gov/nasa-brand-center/images-and-media/','https://www.nasa.gov/nasa-brand-center/']:
            try:(OUT/'NASA_使用说明.html').write_bytes(fetch(url));break
            except Exception as e:print(str(e),flush=True)
        sys.exit()
    if '--video-search' in sys.argv:
        for q in ['materials testing','composites','solar cells','electron microscope']:
            try:
                data=json.loads(fetch('https://images-api.nasa.gov/search?'+urllib.parse.urlencode({'q':q,'media_type':'video','page_size':5})))
                items=[{'id':x['data'][0]['nasa_id'],'title':x['data'][0]['title'],'description':x['data'][0].get('description',''),'collection':x['href']} for x in data['collection']['items']]
                (OUT/('video_'+q.replace(' ','_')+'.json')).write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
                print(json.dumps({'q':q,'items':items},ensure_ascii=False),flush=True)
            except Exception as e:print(str(e),flush=True)
        sys.exit()
    if '--nasa' in sys.argv:
        queries=['solar cells','silicon wafer','composite material','tensile testing','scanning electron microscope','materials processing','metal sample preparation']
        def search(q):
            url='https://images-api.nasa.gov/search?'+urllib.parse.urlencode({'q':q,'media_type':'image','page_size':8})
            try:
                data=json.loads(fetch(url));items=[]
                for entry in data['collection']['items']:
                    d=entry['data'][0];items.append({'id':d['nasa_id'],'title':d['title'],'description':d.get('description',''),'credit':d.get('secondary_creator',''),'links':entry.get('links',[]),'collection':entry['href']})
                (OUT/(q.replace(' ','_')+'.json')).write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
                return {'query':q,'items':[{'id':x['id'],'title':x['title'],'description':x['description'][:700],'credit':x['credit']} for x in items]}
            except Exception as e:return {'query':q,'error':str(e)}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for r in pool.map(search,queries):print(json.dumps(r,ensure_ascii=False),flush=True)
        sys.exit()
    if '--probe' in sys.argv:
        urls=['https://images-api.nasa.gov/search?q=materials%20laboratory&media_type=image&page_size=5','https://www.pexels.com/photo/person-holding-laboratory-flask-256262/','https://images.pexels.com/photos/256262/pexels-photo-256262.jpeg?w=1920','https://www.energy.gov/science/articles','https://www.flickr.com/photos/departmentofenergy/7209791480','https://upload.wikimedia.org']
        def probe(url):
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
                with urllib.request.urlopen(req,timeout=12) as f:data=f.read()
                name='probe_'+str(urls.index(url));(OUT/name).write_bytes(data)
                return {'url':url,'ok':True,'bytes':len(data),'saved':name,'sample':data[:300].decode('utf-8',errors='replace') if b'<' in data[:10] or b'{' in data[:10] else 'binary'}
            except Exception as e:return {'url':url,'error':str(e)}
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            for r in pool.map(probe,urls):print(json.dumps(r,ensure_ascii=False),flush=True)
        sys.exit()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:r=list(pool.map(one,FILES))
    (OUT/'下载与来源记录.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
