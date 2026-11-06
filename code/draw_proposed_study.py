"""Publication schematic of the proposed study; no simulated data or results.
Source: live Google Doc, Section 7, retrieved 5 November 2026.
Rebuild with the bundled Python runtime (ReportLab), then render with pdftoppm.
"""
from pathlib import Path
import json, math
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Polygon, PolyLine
from reportlab.graphics import renderPDF, renderSVG
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import toColor

ROOT=Path(__file__).resolve().parents[1]
(ROOT/'figures').mkdir(exist_ok=True)
import reportlab
VERA=Path(reportlab.__file__).parent/'fonts'
W,H=760,1010
FONT=Path('/System/Library/Fonts/Supplemental')
for name,file in [('StudySans','Arial.ttf'),('StudyBold','Arial Bold.ttf')]:
    fallback='VeraBd.ttf' if name=='StudyBold' else 'Vera.ttf'
    font_path=FONT/file if (FONT/file).exists() else VERA/fallback
    pdfmetrics.registerFont(TTFont(name,str(font_path)))
D=Drawing(W,H)
INK='#183647'; MUTED='#526872'; TEAL='#176B88'; BORDER='#CFDADE'
PALE='#F3F7F8'; BLUE='#E7F1F5'; GREEN='#E8F2EF'; AMBER='#936223'; CREAM='#FBF5EA'
record=[]
def text(x,y,s,size=13,bold=False,color=INK,anchor='start'):
    font='StudyBold' if bold else 'StudySans'
    D.add(String(x,H-y,s,fontName=font,fontSize=size,fillColor=toColor(color),textAnchor=anchor))
    record.append({'text':s,'x':x,'baseline_top':y,'size':size,'font':font})
def lines(x,y,ss,size=13,leading=18,**kw):
    for i,s in enumerate(ss):text(x,y+i*leading,s,size,**kw)
def rect(x,y,w,h,fill='white',stroke=BORDER,r=9):
    D.add(Rect(x,H-y-h,w,h,rx=r,ry=r,fillColor=toColor(fill),strokeColor=toColor(stroke) if stroke else None,strokeWidth=.8))
def line(x1,y1,x2,y2,color=BORDER,width=1):
    D.add(Line(x1,H-y1,x2,H-y2,strokeColor=toColor(color),strokeWidth=width))
def arrow(x1,y1,x2,y2,color=TEAL):
    line(x1,y1,x2,y2,color,1.4)
    a=math.atan2(y2-y1,x2-x1);length=6;spread=3
    p=[(x2,y2),(x2-length*math.cos(a)+spread*math.sin(a),y2-length*math.sin(a)-spread*math.cos(a)),(x2-length*math.cos(a)-spread*math.sin(a),y2-length*math.sin(a)+spread*math.cos(a))]
    D.add(Polygon([v for x,y in p for v in (x,H-y)],fillColor=toColor(color),strokeColor=None))
def heading(n,x,y,title):
    D.add(Circle(x+13,H-y+5,12.5,fillColor=toColor(TEAL),strokeColor=None))
    text(x+13,y,str(n),13,True,'white','middle');text(x+35,y,title,15,True)

rect(0,0,W,H,stroke=None,r=0)
text(24,27,'PROPOSED STUDY',11.5,True,TEAL)
text(24,57,'Measuring chemical safety and refusal',24,True)
text(24,80,'Hold the chemical question fixed. Vary the inputs. Measure each outcome separately.',13,color=MUTED)

rect(24,96,712,54,PALE,stroke=None)
text(40,117,'Before testing',12.5,True)
text(143,117,'Prespecify sampling, outcomes, comparisons and analysis.',12.5)
text(40,137,'Develop prompts and scoring rules on a separate set of entities.',12.5,color=MUTED)

rect(24,166,712,108)
heading(1,40,192,'Select and verify the chemical questions')
text(40,217,'60 entities   /   30 prespecified chemical-family blocks   /   1 protective question per entity',14,True)
text(40,239,'Verify identities, reference answers and required coverage. Document structural and question diversity.',12.5)
text(40,259,'Include ordinary and hazard-associated mentions; hazard category guides sampling, not refusal labels.',12.5,color=MUTED)

line(380,274,380,289,TEAL,1.4);line(277,289,638,289,TEAL,1.4)
arrow(277,289,277,304);arrow(638,289,638,304,AMBER)

rect(24,304,506,234)
heading(2,40,330,'Vary the inputs')
text(40,351,'Same entity and safety question in all six conditions.',12.5,color=MUTED)
text(40,374,'Initial identifier',10.5,True,color=MUTED)
start=112;cw=132;gap=4
headers=['No help','Identity bridge','Bridge + facts']
fills=[PALE,BLUE,GREEN]
for j,(title,fill) in enumerate(zip(headers,fills)):
    x=start+j*(cw+gap)
    text(x+cw/2,374,title,12,True,anchor='middle')
    for i in range(2):
        y=389+i*55
        rect(x,y,cw,47,fill,stroke=None,r=5)
        body=[['No added','information'],['Name + SMILES','link only'],['Link + verified','safety facts']][j]
        lines(x+cw/2,y+19,body,12.2,16,anchor='middle')
text(40,418,'Name',13,True);text(40,473,'SMILES',13,True)
text(40,519,'The bridge supplies the identifier pair, without the requested safety fact.',11.8,color=MUTED)

rect(548,304,188,234,CREAM,stroke='#E3D5BD')
text(564,325,'SECONDARY MEASURE',10.5,True,AMBER)
text(564,349,'Test recognition',15,True)
lines(564,370,['Separate fresh sessions'],11.8,color=MUTED)
lines(564,398,['60 entities','× 2 identifiers','× 2 model snapshots'],13,18)
text(564,455,'240 probe calls',16,True,AMBER)
lines(564,480,['No probe or answer is','passed to the main task.'],12,16)
lines(564,518,['Recognition does not','select the main sample.'],11.4,14,color=MUTED)

arrow(277,538,277,558)
rect(24,558,506,112)
heading(3,40,584,'Run each condition')
text(513,584,'1,440 calls',13,True,TEAL,'end')
text(40,606,'2 fixed model snapshots × 2 generations per condition',12.7,True)
text(40,625,'Fresh sessions; randomized order; fixed reasoning and decoding settings.',12)
text(40,643,'Equal output budgets and tool access.',12)
text(40,660,'Baselines: identifier lookup · fact retrieval · abstain-all.',11.8,color=MUTED)

rect(548,558,188,112,PALE,stroke=None)
text(564,592,'1,680',28,True,TEAL)
text(564,611,'planned model calls',12)
text(564,634,'1,440 main + 240 probes',12)
text(564,655,'Design only; no results.',11.5,color=MUTED)

arrow(277,670,277,698)
rect(24,698,712,128)
heading(4,40,724,'Record and score every initiated task')
xs=[40,213,386,559]
titles=['Refusal','Answer quality','Appropriateness','Technical status']
bodies=[['What was withheld,','stated reason, uncertainty'],['Attempt, correctness,','required coverage'],['Policy-based judgment;','mixed or unclear cases'],['Missing outputs, blocks,','parsing and tool failures']]
for x,title,body in zip(xs,titles,bodies):
    text(x,750,title,12.7,True)
    lines(x,769,body,11.9,16)
for x in [201,374,547]:line(x,740,x,792)
text(40,812,'Two human raters; agreement before adjudication. A technical failure is recorded separately from refusal.',12,color=MUTED)

arrow(380,826,380,852)
rect(24,852,712,124)
heading(5,40,878,'Compare conditions and estimate uncertainty')
text(40,902,'Identifier: name vs SMILES, without help.',12.4)
text(40,921,'Bridge: linked pair vs no help.',12.4)
text(40,940,'Facts: bridge + facts vs bridge alone.',12.4)
line(378,892,378,947)
lines(394,902,['Average repeats; pair conditions within each entity.','Report bridge and fact effects by initial identifier.','Resample family blocks; prespecify Holm adjustment.','Report all-task success and attempted-answer accuracy.'],11.6,15)
text(40,964,'These contrasts estimate input effects; they do not uniquely identify the internal cause of a refusal.',11.7,color=MUTED)

text(24,996,'Scope: legitimate safety questions. Unsafe compliance and experimental execution need separate studies.',11.8,color=MUTED)

assert 60*2*3*2*2==1440 and 60*2*2==240 and 1440+240==1680
# Check every text span lies within the page, independent of the visual check.
for r in record:
    width=pdfmetrics.stringWidth(r['text'],r['font'],r['size'])
    assert 0<r['baseline_top']<H
    assert width<W-32, r['text']
(ROOT/'output/pdf').mkdir(parents=True,exist_ok=True)
renderPDF.drawToFile(D,str(ROOT/'figures/proposed-study-schematic.pdf'))
renderSVG.drawToFile(D,str(ROOT/'figures/proposed-study-schematic.svg'))
(ROOT/'figures/proposed-study-schematic-layout.json').write_text(json.dumps(record,indent=2))
print('Created vector PDF and SVG; design counts checked.')
