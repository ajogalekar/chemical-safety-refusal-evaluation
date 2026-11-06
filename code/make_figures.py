"""Regenerate Figures 1 and 2 from the released analysis outputs.
Requires ReportLab. Does not rebuild the manuscript or change analysis inputs.
"""
from pathlib import Path
import csv,json
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Circle,Polygon
from reportlab.graphics import renderSVG,renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
P=Path(__file__).resolve().parents[1]
(P/'figures').mkdir(exist_ok=True)
F=Path('/System/Library/Fonts/Supplemental')
V=Path(reportlab.__file__).parent/'fonts'
for name,mac,fallback in [('Sans','Arial.ttf','Vera.ttf'),('SansBold','Arial Bold.ttf','VeraBd.ttf')]:
    path=F/mac if (F/mac).exists() else V/fallback
    pdfmetrics.registerFont(TTFont(name,str(path)))
navy=colors.HexColor('#183647');blue=colors.HexColor('#176B88');orange=colors.HexColor('#AE5F27');grey=colors.HexColor('#60727D');light=colors.HexColor('#E9EFF2')
def clean(s):return s.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u2212','-').replace('\u00a0',' ')
def txt(d,x,y,t,size=8,font='Sans',col=navy):d.add(String(x,y,clean(t),fontName=font,fontSize=size,fillColor=col))
def wrap_text(t,maxchars):
 words=t.split();out=[];line=''
 for w in words:
  if len(line+' '+w)>maxchars and line:out.append(line);line=w
  else:line=(line+' '+w).strip()
 if line:out.append(line)
 return out

def box(d,x,y,w,h,title,body,fill=light):
 d.add(Rect(x,y,w,h,rx=4,ry=4,fillColor=fill,strokeColor=None))
 txt(d,x+10,y+h-17,title,9,'SansBold')
 for i,l in enumerate(wrap_text(body,int(w/4.3))):txt(d,x+10,y+h-32-i*11,l,8)

def framework():
 d=Drawing(504,398)
 txt(d,0,386,'WHAT TO CHANGE AND WHAT TO MEASURE',11,'SansBold')
 box(d,0,302,248,70,'Experimentally varied','Identifier; identity aid; factual evidence; prompt; tools; declared resources')
 box(d,256,302,248,70,'Measured or unknown factors','Chemical family; literature coverage; similarity; expertise; training exposure')
 txt(d,0,283,'Record each outcome for every safety or refusal task',10,'SansBold')
 rows=[('1  Entity recognition','Was the intended entity resolved?'),('2  Factual access','Was the required fact available in the answer?'),('3  Refusal / abstention','What was withheld, and what reason was stated?'),('4  Answer quality','Correctness and required coverage scored separately.'),('5  Familiarity / novelty','Define the reference set; do not infer training exposure.'),('6  Feasibility','Can the task be completed within declared resources?')]
 for i,(title,body) in enumerate(rows):
  x=(i%2)*256;y=213-(i//2)*62
  box(d,x,y,248,54,title,body,colors.HexColor('#F2F5F6'))
 box(d,0,27,504,54,'7  Execution and experimental validation','Record all attempts, failures, analytical identity, yield, purity, repeatability, and human intervention.',colors.HexColor('#DFECE8'))
 txt(d,0,9,'Record these measurements separately; no internal sequence or combined score is assumed.',8,'Sans',grey)
 return d

def evidence():
 d=Drawing(504,488)
 txt(d,0,474,'A  ChemIDBench: paired identifier differences',10,'SansBold')
 txt(d,0,460,'Indication: name - SMILES     Benzene: SMILES - name',8,'Sans',grey)
 rows=list(csv.DictReader((P/'reanalysis/analysis/chemid_paired_reanalysis.csv').open()))
 names=list(dict.fromkeys(r['model'] for r in rows));x0=207;x1=489
 def xx(v):return x0+(x1-x0)*v/50
 for tick in range(0,51,10):
  x=xx(tick);d.add(Line(x,315,x,448,strokeColor=light,strokeWidth=.6));txt(d,x-4,301,str(tick),7)
 for i,name in enumerate(names):
  y=438-i*18
  txt(d,0,y-2,name.replace('Meta-',''),7.5)
  for j,r in enumerate([r for r in rows if r['model']==name]):
   yy=y+(-3 if j else 3);col=blue if j==0 else orange
   lo=float(r['paired_normal95_low_pp']);hi=float(r['paired_normal95_high_pp']);v=float(r['difference_pp'])
   d.add(Line(xx(lo),yy,xx(hi),yy,strokeColor=col,strokeWidth=1.2));d.add(Circle(xx(v),yy,2.2,fillColor=col,strokeColor=None))
 txt(d,x0,286,'Difference (percentage points); paired normal 95% intervals',7.3)
 d.add(Circle(4,281,2.3,fillColor=blue,strokeColor=None));txt(d,10,278,'Indication',7.5)
 d.add(Circle(79,281,2.3,fillColor=orange,strokeColor=None));txt(d,85,278,'Benzene detection',7.5)
 txt(d,0,252,'B  XSTest: same-model prompt interventions',10,'SansBold')
 r=json.loads((P/'reanalysis/analysis/xstest_paired_contrasts.json').read_text())['results']
 labs=['Llama 2: full refusal','Llama 2: any refusal','Mistral: full refusal','Mistral: any refusal']
 def bx(v):return x0+(x1-x0)*(v+40)/70
 for tick in [-40,-20,0,20,30]:
  x=bx(tick);d.add(Line(x,166,x,235,strokeColor=grey if tick==0 else light,strokeWidth=.5));txt(d,x-5,153,str(tick),7)
 for i,(a,lab) in enumerate(zip(r,labs)):
  y=225-i*17;lo,hi=[100*v for v in a['stratified_prompt_bootstrap95']];v=100*a['difference']
  txt(d,0,y-2,lab,8);d.add(Line(bx(lo),y,bx(hi),y,strokeColor=blue,strokeWidth=1.2));d.add(Circle(bx(v),y,2.2,fillColor=blue,strokeColor=None))
 txt(d,x0,138,'After - before (points); stratified prompt-bootstrap 95% intervals',7)
 txt(d,0,110,'C  DualChem: completed-run and initiated-task accuracy',10,'SansBold')
 vals=[('No tool: all 600 tasks',52.3,grey),('Web: 425 completed tasks',54.6,blue),('Web: all 600 initiated tasks',38.675,orange)]
 for i,(lab,v,col) in enumerate(vals):
  y=84-i*23;txt(d,0,y,lab,8);d.add(Rect(x0,y-2,v/60*(x1-x0-30),12,fillColor=col,strokeColor=None));txt(d,x0+v/60*(x1-x0-30)+5,y,f'{v:.1f}%',8)
 txt(d,0,6,'Panel C uses rounded aggregates; no uncertainty interval or paired tool test is available.',7.6,'Sans',grey)
 return d

for name,d in [('figure1',framework()),('figure2',evidence())]:
    renderSVG.drawToFile(d,str(P/'figures'/(name+'.svg')))
    renderPDF.drawToFile(d,str(P/'figures'/(name+'.pdf')))
print('Figures 1 and 2 generated as SVG and PDF.')
