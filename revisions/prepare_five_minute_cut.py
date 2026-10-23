from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent.parent
ROOT=BASE/'交付_V17_五分钟_浅色完整审看版'
for name in ['制作文件','音频','分镜预览','素材']:(ROOT/name).mkdir(parents=True,exist_ok=True)
source=Path('C:/Users/13118/xwechat_files/wxid_zml5uciivw6v22_70bd/msg/file/2026-10/ABACUSLab_五分钟宣传视频制作方案.md')
md=source.read_text(encoding='utf-8')
sections=[]
for ch in md.split(chr(10)+'## ')[1:]:
    if '### 旁白（可直接朗读）' not in ch:continue
    title=ch.splitlines()[0];body=ch.split('### 旁白（可直接朗读）')[1].split('**剪辑提示：**')[0]
    text=' '.join(body.split()).strip();sections.append({'chapter':title,'text':text,'characters':len([c for c in text if 0x4e00<=ord(c)<=0x9fff])})
(ROOT/'制作文件/原稿章节.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2),encoding='utf-8')
doc=source.parent/'5分钟解说词.docx'
with zipfile.ZipFile(doc) as z:
    root=ET.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    text=chr(10).join(''.join(p.itertext()) for p in root.findall('.//w:p',ns))
(ROOT/'制作文件/解说词文档提取.txt').write_text(text,encoding='utf-8')
print(json.dumps(sections,ensure_ascii=False,indent=2))
print('TOTAL',sum(s['characters'] for s in sections))
