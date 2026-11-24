import sys
import os; HERE=os.path.dirname(os.path.abspath(__file__))
from pptx import Presentation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape
pdfmetrics.registerFont(TTFont('Ar','/System/Library/Fonts/Supplemental/Arial.ttf'))
deck,out,lab=sys.argv[1],sys.argv[2],sys.argv[3]
p=Presentation(deck)
st=ParagraphStyle('n',fontName='Ar',fontSize=10,leading=14,spaceAfter=6)
hd=ParagraphStyle('h',fontName='Ar',fontSize=9,textColor='#666666',spaceAfter=6)
doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=40,rightMargin=40,topMargin=36,bottomMargin=36)
el=[];n=len(p.slides)
for i,s in enumerate(p.slides):
    el.append(Paragraph(f'{lab} {i+1} / {n}',hd))
    w=A4[0]-80; el.append(Image(os.path.join(HERE,'slides',f'p-{i+1:02d}.png'),width=w,height=w*9/16)); el.append(Spacer(1,10))
    for para in s.notes_slide.notes_text_frame.text.split('\n'):
        if para.strip(): el.append(Paragraph(escape(para),st))
    if i<n-1: el.append(PageBreak())
doc.build(el); print('pdf',out)
