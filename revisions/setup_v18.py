from pathlib import Path
import shutil,json
BASE=Path(__file__).resolve().parent.parent;OLD=BASE/'交付_V17_五分钟_浅色完整审看版';ROOT=BASE/'交付_V18_五分钟_按方案实景重制'
for n in ['制作文件','音频','分镜预览','素材/视频帧','素材/精选实景']:(ROOT/n).mkdir(parents=True,exist_ok=True)
for name in ['mix_five_minute.py','make_narration.py','原稿章节.json']:
    shutil.copy2(OLD/'制作文件'/name,ROOT/'制作文件'/name)
shutil.copytree(OLD/'制作文件/voice',ROOT/'制作文件/voice',dirs_exist_ok=True)
sections=json.loads((ROOT/'制作文件/原稿章节.json').read_text(encoding='utf-8'))
sections[1]['text']='第一性原理计算，从原子和电子层面研究材料；AI辅助规划与分析。ABACUSLab，由合肥综合性国家科学中心人工智能研究院开发，以中国科学技术大学团队牵头研发的国产开源软件ABACUS为核心，融合专业计算、标准流程与人工智能，支持材料研究。'
(ROOT/'制作文件/原稿章节.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2),encoding='utf-8')
# Keep the old cached voice in an explicitly named archive before replacing chapter 2.
for ext in ['mp3','json']:
    p=ROOT/f'制作文件/voice/01.{ext}'
    if p.exists() and not (ROOT/f'制作文件/voice/01_v17_archive.{ext}').exists():p.rename(ROOT/f'制作文件/voice/01_v17_archive.{ext}')
# Fill exact plan chapter lengths with pitch-preserving modest rate correction where necessary.
p=ROOT/'制作文件/mix_five_minute.py';s=p.read_text(encoding='utf-8')
s=s.replace('BOUNDS=[0,44,86,130,163,225,252,281,300]','BOUNDS=[0,40,70,115,155,215,250,280,300]')
s=s.replace("start=a+.65;end=start+len(data)/SR",'''start=a+.55;available=b-start-.75
        speed=max(.88,len(data)/SR/available)
        if speed>1.12:raise ValueError(('Narration too dense',i,speed))
        if abs(speed-1)>.001:
            data=np.frombuffer(subprocess.check_output([FF,'-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0','-af',f'atempo={speed:.7f}','-f','f32le','pipe:1'],input=data.tobytes()),np.float32).copy()
        end=start+len(data)/SR''')
s=s.replace("start+event['offset']/1e7-lo/SR","start+(event['offset']/1e7-lo/SR)/speed")
s=s.replace("start+(event['offset']+event['duration'])/1e7-lo/SR","start+((event['offset']+event['duration'])/1e7-lo/SR)/speed")
s=s.replace("'speed_adjust':1.0","'speed_adjust':speed")
p.write_text(s,encoding='utf-8')
print('V18 ready')
