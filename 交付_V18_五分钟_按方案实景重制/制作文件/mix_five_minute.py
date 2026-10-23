from pathlib import Path
import sys,json,subprocess,wave,math,re,html
import numpy as np
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'packages'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000;DUR=300
BOUNDS=[0,40,70,115,155,215,250,280,300]
def wav(path,data):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(data.shape[1] if data.ndim==2 else 1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(data,-.97,.97)*32767).astype('<i2').tobytes())
def stamp(t,ass=False):
    ms=round(t*1000)
    return f'{ms//3600000:01d}:{ms//60000%60:02d}:{ms//1000%60:02d}.{ms//10%100:02d}' if ass else f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
def main():
    n=SR*DUR;voice=np.zeros(n,np.float32);duck=np.ones(n,np.float32);report=[];captions=[]
    source=json.loads((ROOT/'制作文件/原稿章节.json').read_text(encoding='utf-8'))
    for i,(a,b) in enumerate(zip(BOUNDS,BOUNDS[1:])):
        p=ROOT/f'制作文件/voice/{i:02d}.mp3';meta=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))
        data=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(p),'-ac','1','-ar',str(SR),'-f','f32le','pipe:1']),np.float32).copy()
        active=np.flatnonzero(abs(data)>.003);lo=max(0,int(active[0])-.05*SR);hi=min(len(data),int(active[-1])+.14*SR);lo=int(lo);hi=int(hi);data=data[lo:hi]
        start=a+.55;available=b-start-.75
        speed=max(.88,len(data)/SR/available)
        if speed>1.12:raise ValueError(('Narration too dense',i,speed))
        if abs(speed-1)>.001:
            data=np.frombuffer(subprocess.check_output([FF,'-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0','-af',f'atempo={speed:.7f}','-f','f32le','pipe:1'],input=data.tobytes()),np.float32).copy()
        end=start+len(data)/SR
        assert end<b-.30,(i,end,b)
        rms=float(np.sqrt(np.mean(data**2)));peak=float(abs(data).max());data*=min(.15/max(rms,.001),.83/max(peak,.001))
        pos=round(start*SR);voice[pos:pos+len(data)]=data
        ds=max(0,pos-14400);de=min(n,pos+len(data)+24000);duck[ds:pos]=np.linspace(1,.30,pos-ds);duck[pos:pos+len(data)]=.30;duck[pos+len(data):de]=np.linspace(.30,1,de-pos-len(data))
        # Word boundaries locate every caption in the synthesized audio, retaining source punctuation.
        spoken=meta['spoken_text'];cursor=0;phrases=[];phrase='';pstart=None;pend=None
        events=meta['events']
        for j,event in enumerate(events):
            word=html.unescape(event['text']);found=spoken.lower().find(word.lower(),cursor)
            if found<0:found=cursor
            nextpos=found+len(word)
            while nextpos<len(spoken) and not spoken[nextpos].isalnum() and spoken[nextpos] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':nextpos+=1
            piece=spoken[cursor:nextpos].strip();cursor=nextpos
            if pstart is None:pstart=start+(event['offset']/1e7-lo/SR)/speed
            pend=start+((event['offset']+event['duration'])/1e7-lo/SR)/speed
            phrase+=piece
            boundary=(len(phrase)>=9 and any(c in piece for c in '，。；！？')) or len(phrase)>=40 or j==len(events)-1
            if boundary:
                phrases.append([max(a,pstart),min(b-.2,pend+.12),phrase.replace('ABACUS LAB','ABACUSLab').replace('ABACUSLAB','ABACUSLab')]);phrase='';pstart=None
        for j,p in enumerate(phrases):
            if j+1<len(phrases):p[1]=min(p[1],phrases[j+1][0]-.02)
            if p[1]>p[0]:captions.append(p)
        report.append({'chapter':i+1,'title':source[i]['chapter'].split('（')[0],'start':a,'end':b,'voice_start':start,'voice_end':end,'speed_adjust':speed,'voice':'zh-CN-YunjianNeural','text':meta['spoken_text'].replace('ABACUS LAB','ABACUSLab')})
    music=np.zeros((n,2),np.float32);chords=[[50,57,62,65,69],[46,53,58,62,65],[53,60,65,69,72],[48,55,60,64,67]]
    for bar in range(50):
        st=bar*6*SR;ln=min(round(7.5*SR),n-st);tt=np.arange(ln,dtype=np.float32)/SR;env=np.minimum(1,tt/1.5)*np.minimum(1,(7.5-tt)/1.8);chord=chords[bar%4]
        lift=.8 if bar*6<44 or bar*6>281 else 1
        for j,note in enumerate(chord):
            f=440*2**((note-69)/12)
            for ch in range(2):music[st:st+ln,ch]+=(np.sin(2*np.pi*f*(1+(ch*2-1)*.0009)*tt+j*.7)+.16*np.sin(2*np.pi*f*2*tt))*env*.011*lift
        for k in range(8):
            pst=round((bar*6+k*.75)*SR);pn=min(round(1.7*SR),n-pst)
            if pn<=0:continue
            pt=np.arange(pn,dtype=np.float32)/SR;f=440*2**((chord[[0,2,3,4,2,3,1,4][k]]+12-69)/12)
            arp=(np.sin(2*np.pi*f*pt)+.15*np.sin(2*np.pi*f*2*pt))*(1-np.exp(-pt*90))*np.exp(-pt*3.5)*.022*lift
            music[pst:pst+pn,k%2]+=arp
    timeline=np.arange(n,dtype=np.float32)/SR;fade=np.minimum(1,timeline/2.0)*np.minimum(1,(DUR-timeline)/3.0);music*=duck[:,None]*fade[:,None]
    wav(ROOT/'音频/五分钟_男声旁白.wav',voice);wav(ROOT/'音频/五分钟_背景配乐.wav',music);wav(ROOT/'制作文件/mixed.wav',voice[:,None]+music)
    (ROOT/'制作文件/配音与章节时间轴.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    srt=chr(10)+chr(10)
    (ROOT/'中文字幕.srt').write_text(srt.join(f'{i+1}'+chr(10)+stamp(a)+' --> '+stamp(b)+chr(10)+s for i,(a,b,s) in enumerate(captions)),encoding='utf-8')
    # Light subtitle box; no dark title strip or progress bar.
    header='[Script Info]'+chr(10)+'ScriptType: v4.00+'+chr(10)+'PlayResX: 1920'+chr(10)+'PlayResY: 1080'+chr(10)+'WrapStyle: 2'+chr(10)+chr(10)+'[V4+ Styles]'+chr(10)+'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding'+chr(10)+'Style: Default,Microsoft YaHei,34,&H00442718,&H00442718,&H00FFF9F5,&H00FFF9F5,0,0,0,0,100,100,0,0,3,7,0,2,70,70,30,1'+chr(10)+chr(10)+'[Events]'+chr(10)+'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text'+chr(10)
    (ROOT/'制作文件/captions.ass').write_text(header+chr(10).join(f'Dialogue: 0,{stamp(a,True)},{stamp(b,True)},Default,,0,0,0,,{s}' for a,b,s in captions),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2));print('CAPTIONS',len(captions),'AUDIO',DUR)
if __name__=='__main__':main()
