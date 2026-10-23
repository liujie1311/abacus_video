from pathlib import Path
import json
from PIL import ImageFont
ROOT=Path(__file__).resolve().parent.parent
report=json.loads((ROOT/'制作文件/配音与章节时间轴.json').read_text(encoding='utf-8'))
shots=json.loads((ROOT/'制作文件/镜头时间线.json').read_text(encoding='utf-8'))
def stamp(t):return f'{int(t)//60:02d}:{int(t)%60:02d}'
rows=['# ABACUSLab｜五分钟浅色审看版','','总时长：05:00。以用户提供的五分钟方案和解说词为叙事基础，保留自然语速，按实际旁白长度调整章节边界。','','| 时间 | 章节 |','|---|---|']
for c in report:rows.append(f"| {stamp(c['start'])}—{stamp(c['end'])} | {c['title']} |")
rows+=['','## 旁白全文','']
for c in report:rows += [f"### {stamp(c['start'])}—{stamp(c['end'])}｜{c['title']}",'',c['text'],'']
(ROOT/'五分钟分镜与解说词.md').write_text(chr(10).join(rows),encoding='utf-8')
readme='''# ABACUSLab｜V17 五分钟浅色完整审看版

## 观看文件

主文件：ABACUSLab_V17_五分钟_浅色审看版_含字幕.mp4

- 5 分钟，1920×1080，16:9，30 fps，H.264 / AAC。
- 全片浅蓝白风格，39 个镜头；男声旁白、背景配乐、中文字幕。
- 按用户提供的五分钟方案和解说词制作，章节边界依自然语速重排，不强行加速语音。
- 铝合金案例采用用户提供的参考片展示顺序与名称，衔接提问、计算规划、任务、MSD 图表和结果分析。

## 本版特点

开头使用立体原子、材料领域和结构概念动画；平台能力采用现有真实界面截图与动态排版。图表维持原曲线和坐标，保留阅读时间。片尾浅色收束，无黑屏和深色转场。

## 随附内容

- 五分钟分镜总览.jpg：各镜头排布预览。
- 成片实际画面核验.jpg：从最终 MP4 抽取的实际画面。
- 五分钟分镜与解说词.md：章节时间与完整解说词。
- 中文字幕.srt：可编辑外部字幕，按语音词级时间信息对齐。
- 音频：独立男声旁白、背景配乐。
- 成片检查.json：视频全量解码、时长、编码、音频峰值等检查结果。
- 制作文件：Python 渲染、混音脚本及镜头和语音时间轴。需要工作区 packages 和同级浅色素材包，可在本工作区继续编辑生成。

## 来源记录

叙事与旁白来自用户提供的《ABACUSLab_五分钟宣传视频制作方案.md》《5分钟解说词.docx》。案例开头增加“看看平台如何衔接计算与分析”，帮助连接后续展示。平台开发单位、软件研发背景及模板数量沿用原稿，未作新增宣传主张。

截图源为同级 五分钟宣传片_补充素材_20261023/01_已有平台素材；原子和流程画面为本次原创程序概念动画；参考片源为用户所给 0da312f692b46fe2d0afac91646097cf.mp4。

本版遵循用户已确认的“现有截图与概念动画”制作方式，不等待补充轨迹或计算日志。影片标题采用“铝合金熔化行为研究”作为研究场景；原始分析截图中的纯 Al 内容仍保留，没有更改数据，也不新增合金组成或声称不同任务属于同一次实验。电子结构图表作为独立功能示例，未拼造同一材料的数据链。

新制作动画为原生 1080p。参考片源为 720p，已等比放大用于展示。

## 重生成顺序

1. 制作文件/make_narration.py：生成男声旁白（已缓存，已有文件不重复发送）。
2. 制作文件/mix_five_minute.py：旁白、配乐和字幕。
3. 制作文件/build_film.py prepare / previews / picture / final / verify：参考素材、分镜、无声画面、最终成片及核验。
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',34)
text=(ROOT/'中文字幕.srt').read_text(encoding='utf-8')
entries=[b.splitlines() for b in text.strip().split(chr(10)+chr(10))]
widths=[{'id':b[0],'text':b[2],'width':round(font.getlength(b[2]))} for b in entries]
assert max(p['width'] for p in widths)<1780,widths
assert shots[0][0]==0 and shots[-1][1]==300
assert all(a[1]==b[0] for a,b in zip(shots,shots[1:]))
result={'timeline_contiguous':True,'duration_seconds':300,'shots':len(shots),'chapters':len(report),'captions':len(entries),'maximum_caption_width':max(p['width'] for p in widths),'narration_all_natural_speed':all(r['speed_adjust']==1 for r in report),'narration_inside_chapters':all(r['start']<=r['voice_start']<r['voice_end']<r['end'] for r in report)}
(ROOT/'制作文件/时间轴与字幕核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
