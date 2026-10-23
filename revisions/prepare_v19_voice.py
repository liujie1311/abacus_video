from pathlib import Path
B=Path(__file__).resolve().parent.parent;R=B/'交付_V19_五分钟_去重与稳定重剪'
source=(B/'交付_V18_五分钟_按方案实景重制/制作文件/align_case_narration.py').read_text(encoding='utf-8')
parts=[
 (0,10,'新材料的发现与设计，推动科技进步。从能源材料、半导体到先进结构材料，研究不断深入微观世界。'),
 (10,22,'潜在的材料空间十分广阔。不同元素的组合、不同原子的排列，带来多样的候选结构，也让寻找合适材料变得更加复杂。'),
 (22,32,'从材料制备、实验表征到性能测试，研究人员反复比较和调整方案。这些过程，需要投入大量时间与资源。'),
 (32,40,'材料性能源于原子结构与电子行为。理解机制，才能预测性质，探索设计。'),
 (70,85,'平台集成多种常用材料计算模板，涵盖结构优化、电子结构、分子动力学和材料物性。研究人员根据目标选择方法，查看模板说明与计算步骤。'),
 (85,95,'将基础计算和多步骤分析组织成可复用的工作流程，研究人员可以检查条件、调整方案，减少重复准备。'),
 (95,105,'平台支持按项目组织计算任务，集中查看运行状态，让计算记录和执行进展清晰可见。'),
 (105,115,'结构转换、输入准备与参数配置，衔接不同计算环节。态密度和光学响应等结果，可以通过图表直观呈现。'),
 (115,125,'在专业计算能力之上，ABACUSLab 引入 AI 智能体。研究人员可以用自然语言描述需求。'),
 (125,135,'AI 辅助梳理研究目标、计算思路和所需条件。研究人员可以检查完整方案，确认后续步骤。'),
 (135,145,'从任务反馈到结果入口，平台连接计算与分析环节。研究人员可以回到具体任务，逐项核对状态与文件。'),
 (145,155,'研究人员还可以检查参数、调整方案，并结合科学知识作出判断，让 AI 辅助与专业判断相结合。')]
begin=source.index('PARTS=[');end=source.index('\ndef pcm',begin)
source=source[:begin]+'PARTS='+repr(parts)+source[end:]
source=source.replace("ROOT/'制作文件/voice_case_aligned'","ROOT/'制作文件/voice_aligned'")
source=source.replace("if not 155<=a<215:captions.append", "if not any(x<=a<y for x,y,_ in PARTS):captions.append")
source=source.replace("voice[155*SR:215*SR]=0;report=[]", "report=[]\n    for a,b,_ in PARTS:voice[a*SR:b*SR]=0")
source=source.replace("if speed>1.25:","if speed>1.20:")
source=source.replace("spoken,'zh-CN-YunjianNeural'","spoken.replace('ABACUSLab','ABACUS LAB'),'zh-CN-YunjianNeural'")
# Boundary matching needs the spoken spelling, with display normalization afterwards.
source=source.replace("path=folder/f'{i:02d}.mp3';data=pcm(path)","spoken=spoken.replace('ABACUSLab','ABACUS LAB')\n        path=folder/f'{i:02d}.mp3';data=pcm(path)")
source=source.replace("new.append([max(a,pstart),min(b-.15,pend+.1),phrase])","new.append([max(a,pstart),min(b-.15,pend+.1),phrase.replace('ABACUS LAB','ABACUSLab')])")
source=source.replace("'案例配音逐镜对齐.json'","'重新对齐配音.json'")
source=source.replace("if path.exists() and meta.exists():continue", "if path.exists() and meta.exists() and json.loads(meta.read_text(encoding='utf-8'))['text']==spoken:continue")
start=source.index("    chapters=json.loads")
end=source.index("    print('ALIGNED'",start)
source=source[:start]+source[end:]
(R/'制作文件/align_narration.py').write_text(source,encoding='utf-8')
import shutil
for name in ['五分钟_男声旁白.wav','五分钟_背景配乐.wav']:
    shutil.copy2(B/'交付_V18_五分钟_按方案实景重制/音频'/name,R/'音频'/name)
print('SCRIPT_READY',len(parts))
