from pathlib import Path
import cv2,json
from PIL import Image,ImageDraw
root=Path('C:/Users/PC/Desktop/\u7d20\u6750/\u7d20\u6750')
p=next(root.glob('*.mp4')); cap=cv2.VideoCapture(str(p))
fps=cap.get(cv2.CAP_PROP_FPS); count=cap.get(cv2.CAP_PROP_FRAME_COUNT)
print(json.dumps({'path':str(p),'fps':fps,'frames':count,'duration':count/fps,'w':cap.get(3),'h':cap.get(4)}))
canvas=Image.new('RGB',(1600,1350),'#ddd');d=ImageDraw.Draw(canvas)
for i in range(12):
 sec=(count/fps)*i/12; cap.set(cv2.CAP_PROP_POS_MSEC,sec*1000);ret,fr=cap.read()
 if ret:
  im=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)); im.thumbnail((790,190))
  x=(i%2)*800;y=(i//2)*225;canvas.paste(im,(x,y+25));d.text((x+10,y+5),str(round(sec,2))+' s',fill='black')
canvas.save(Path(__file__).parent/'recording_contact.jpg')
