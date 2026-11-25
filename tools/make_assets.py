from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
assets = ROOT/'app/frontend/assets'
assets.mkdir(parents=True, exist_ok=True)
for variant, bg in enumerate(['#e0eadf','#e8e9d8','#e2e8ec']):
    image = Image.new('RGB',(1200,680),bg)
    d=ImageDraw.Draw(image)
    d.ellipse((300,565,910,630),fill='#c8d2c7')
    d.ellipse((810,-170,1370,400),fill='#edf2e9')
    d.rounded_rectangle((90,120,100,470),5,fill='#d0ddcc')
    d.rounded_rectangle((60,150,140,160),5,fill='#d0ddcc')
    for i in range(8):
        angle = (-160+i*22+variant*6)*math.pi/180
        end=(600+int(math.cos(angle)*(190 if variant!=1 else 140)),380+int(math.sin(angle)*250))
        d.line([(600,490),end],fill='#326248',width=10)
        leaf=Image.new('RGBA',(180,90))
        ld=ImageDraw.Draw(leaf)
        ld.ellipse((0,0,179,89),fill=['#19553c','#327153','#49845c'][i%3])
        ld.line((10,45,165,45),fill='#87a77c',width=3)
        leaf=leaf.rotate(-angle*180/math.pi,expand=True,resample=Image.Resampling.BICUBIC)
        image.paste(leaf,(end[0]-leaf.width//2,end[1]-leaf.height//2),leaf)
    d.polygon([(480,420),(730,420),(700,580),(515,580)],fill=['#bd754f','#e8d3ab','#d7a88b'][variant])
    d.rounded_rectangle((470,415,740,447),10,fill=['#d38a63','#f1dfbe','#e6b99e'][variant])
    image.resize((900,510),Image.Resampling.LANCZOS).save(assets/f'plant-{variant}.png')

image=Image.new('RGB',(1500,980),'#ffffff')
d=ImageDraw.Draw(image)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',30)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
boxes=[(60,120,470,355,'Category',['PK id : int','name : str']),
       (60,550,470,785,'Room',['PK id : int','name : str']),
       (620,120,1030,640,'Plant',['PK id : int','name, species : str','FK category_id : int','FK room_id : int','watering_days : int','price : float','last_watered : date','notes : str']),
       (1080,700,1470,950,'CareLog',['PK id : int','FK plant_id : int','action, note : str','performed_on : date'])]
d.text((60,35),'Jasyl — схема базы данных',font=bold,fill='#173b2c')
for x1,y1,x2,y2,title,fields in boxes:
    d.rounded_rectangle((x1,y1,x2,y2),15,fill='#f2f7f3',outline='#60866e',width=3)
    d.text((x1+22,y1+18),title,font=bold,fill='#173b2c')
    for i,line in enumerate(fields):d.text((x1+22,y1+75+43*i),line,font=font,fill='#253c30')
for points,label,pos in [([(470,240),(550,240),(550,270),(620,270)],'1 : N',(500,195)), ([(470,660),(570,660),(570,420),(620,420)],'1 : N',(485,680)), ([(900,640),(900,800),(1080,800)],'1 : N',(930,760))]:
    d.line(points,fill='#39724e',width=4)
    d.text(pos,label,font=small,fill='#173b2c')
image.save(ROOT/'docs/er-diagram.png')
