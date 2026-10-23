from pathlib import Path
import shutil
B=Path(__file__).resolve().parent.parent
P=B/'交付_V19_五分钟_去重与稳定重剪';R=B/'交付_V20_五分钟_连续AI与动态MSD'
for p in ['制作文件','音频','素材','分镜预览']: (R/p).mkdir(parents=True,exist_ok=True)
shutil.copytree(P/'素材',R/'素材',dirs_exist_ok=True)
for p in ['中文字幕.srt','制作文件/captions.ass','制作文件/原始镜头索引.json','音频/五分钟_男声旁白.wav','音频/五分钟_背景配乐.wav']:
    shutil.copy2(P/p,R/p)
src=(P/'制作文件/build_v19.py').read_text(encoding='utf-8').replace('V19','V20').replace('去重稳定重剪版','连续演示与动态MSD版')
src=src.replace("(43,50,'screen','pyatb_body','连接微观结构与专业计算','ABACUS · 国产开源第一性原理计算软件')", "(43,50,'principles','principles','从微观结构，理解材料性质','ABACUS · 国产开源第一性原理计算软件')")
src=src.replace("(108,111,'screen','config_body','计算参数，可视化配置','核对输入设置'),\n (111,115,'result_overview','results_overview','计算结果，转化为直观图表','态密度 · 光学响应 · 结果分析'),", "(108,115,'config_full','config_full','计算参数，可视化配置','选择计算类型 · 配置参数 · 预览输入文件'),")
start=src.index(" (115,125,");end=src.index(" (215,225,",start)
src=src[:start]+''' (115,125,'raw','case_question','从一个研究问题开始','铝合金熔化行为研究'),
 (125,138,'raw','ai_conditions','把研究目标，转化为计算方案','梳理体系、温度和计算步骤'),
 (138,150,'raw','ai_review','确认计算条件','检查结构、势函数与模拟设置'),
 (150,162,'tasks','case_task','查看计算任务与执行状态','300 K 与 1600 K · 两组温度条件'),
 (162,172,'feedback','ai_feedback','从计算任务，到结果图表','查看完成反馈与绘图入口'),
 (172,190,'atoms_new','atoms_new','固态振动与熔融态扩散','从原子运动，理解两种状态的差异'),
 (190,205,'msd_dynamic','msd_dynamic','不同温度下的均方位移（MSD）','300 K 固态与 1600 K 熔融态对照'),
 (205,215,'analysis','analysis','从结果分析，走向进一步验证','归纳主要变化，明确下一步研究方向'),
'''+src[end:]
src=src.replace('案例二｜电子结构与物性分析','电子结构与物性分析')
src=src.replace('def scene(i,t):','def base_scene(i,t):')
extension=(B/'revisions/v20_visuals.py').read_text(encoding='utf-8')
pos=src.index('@lru_cache(8)\ndef end_frame')
src=src[:pos]+extension+'\n\n'+src[pos:]
src=src.replace("'111–115 秒为结果入口概览，280–287 秒为明确标识的功能回顾；不重播完整案例段'", "'仅280–287秒为功能回顾；研究提问、条件确认、任务、结果各出现一次'")
src=src.replace("('中段去重预览_100秒',115,100)","('AI与动态MSD预览_100秒',115,100)")
(R/'制作文件/build_v20.py').write_text(src,encoding='utf-8')
parts=[
 (105,115,'结构转换与参数配置，衔接不同计算环节。选择计算类型，检查参数，并预览生成的输入文件。'),
 (115,125,'想研究铝合金的熔化行为，可以向智能体描述目标，比较材料在不同温度下的原子运动特征。'),
 (125,138,'智能体根据研究目标梳理计算方案，列出材料体系、温度条件与执行步骤。研究人员可以逐项检查，让计算任务有明确的依据。'),
 (138,150,'计算之前，还需要核对初始结构、势函数、模拟时长和输出设置。这些条件会影响结果，也是研究人员需要确认的重点。'),
 (150,162,'方案明确后，在任务界面查看执行情况。这里展示了三百开尔文和一千六百开尔文两组任务，计算状态与任务名称集中呈现。'),
 (162,172,'任务完成后，通过反馈中的结果文件与绘图入口，继续查看不同温度下的运动特征，让计算与分析自然衔接。'),
 (172,190,'先用原子运动示意理解两种状态。固态中，原子保持有序排列，在平衡位置附近振动。熔融态中，原子持续迁移，近邻关系不断变化。标记原子的运动路径，可以直观看出这种差异。'),
 (190,205,'再看实际的均方位移曲线。三百开尔文的紫色曲线接近平台，对应固态的局域振动；一千六百开尔文的绿色曲线明显上升，体现熔融态的扩散特征。'),
 (205,215,'智能体辅助归纳结果，并提出进一步验证的方向。要更准确地判断熔点，还需要加密温度扫描，并核对原始数据。')]
voice=(P/'制作文件/align_narration.py').read_text(encoding='utf-8')
a=voice.index('PARTS=[');b=voice.index('\ndef pcm',a);voice=voice[:a]+'PARTS='+repr(parts)+voice[b:]
voice=voice.replace("if path.exists() and meta.exists():continue","if path.exists() and meta.exists() and json.loads(meta.read_text(encoding='utf-8'))['text']==spoken:continue")
voice=voice.replace("'案例配音逐镜对齐.json'","'连续演示配音对齐.json'")
(R/'制作文件/align_narration.py').write_text(voice,encoding='utf-8')
print('V20_PREPARED',flush=True)
