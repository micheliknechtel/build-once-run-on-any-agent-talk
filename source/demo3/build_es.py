import subprocess as sp, textwrap, re, os
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
A=lambda f:_os.path.join(ROOT,'assets',f)
LANG='es'
WORK=_os.path.join(ROOT,'build','demo3-'+LANG); _os.makedirs(WORK,exist_ok=True); _os.chdir(WORK)
OUT=_os.path.join(ROOT,'output',LANG.upper()); _os.makedirs(OUT,exist_ok=True)
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
SRC=A('demo3-screen-recording.mov')
W,H=1920,1200; VW,VH,VX=1600,1000,160; S=VW/1440
B=lambda s:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',s)
U=lambda s:ImageFont.truetype('/Library/Fonts/Arial Unicode.ttf',s)
WHITE=(240,246,252)
PARTS={1:('PARTE 1 · VS CODE ENCUENTRA LAS SKILLS',(31,111,235)),2:("PARTE 2 · EL HUMANO MANTIENE EL CONTROL",(35,134,54)),
       3:('PARTE 3 · TODO SE PUEDE REVISAR',(191,135,0)),4:('PARTE 4 · EL MENSAJE',(218,54,51))}
PHON=[('forge-dbx','fordje dé-bé-ixe'),('forge','fordje'),('VS Code','vi-èss caude'),('Copilot','co-païlote'),('pull request','poule ri-couest'),('skills','skiles'),('skill','skile'),('SQL','èss-kiou-èl'),('DuckDB','deuk-dé-bé'),('duckdb','deuk-dé-bé'),('databricks','déta-brixe'),('hook','houk'),('commit','co-mitte')]
PHON=[('DuckDB','duck de be'),('duckdb','duck de be'),('SQL','ese cu ele'),('forge-dbx','forch de be equis'),('forge','forch'),('pull request','pul ricuest')]
def phon(t):
    for a,b in PHON: t=re.sub(r'(?<![\w-])'+re.escape(a)+r'(?![\w-])',b,t,flags=re.I)
    return t
def dur(f): return float(sp.check_output(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{f}"',shell=True))
def band(i,part,sub,speed=None):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle((0,VH,W,H),fill=(13,17,23,255))
    if part:
        t,c=PARTS[part]; tw=d.textlength(t,font=B(30))
        d.rounded_rectangle((40,VH+14,40+tw+40,VH+60),radius=23,fill=c); d.text((60,VH+37),t,font=B(30),fill=WHITE,anchor='lm')
    if speed: d.text((W-40,VH+37),f'▶▶ acelerado ×{speed}',font=U(30),fill=(255,214,102),anchor='rm')
    if sub:
        ls=textwrap.wrap(sub,80)
        for k,l in enumerate(ls): d.text((W/2,VH+100+k*44+(22 if len(ls)==1 else 0)),l,font=B(34),fill=WHITE,anchor='mm')
    im.save(f'band{i}.png')
def card(i,title,sub,frame):
    bg=Image.open(frame).convert('RGB').resize((W,H)).filter(ImageFilter.GaussianBlur(12)); bg=ImageEnhance.Brightness(bg).enhance(0.25)
    d=ImageDraw.Draw(bg)
    d.text((W/2,H/2-60),title,font=B(76),fill=WHITE,anchor='mm'); d.text((W/2,H/2+40),sub,font=B(40),fill=(121,192,255),anchor='mm')
    bg.save(f'card{i}.png')
def box(b,t0,t1,col='0xFFD400'):
    x0,y0,x1,y1=b; X=int(VX+x0*S); Y=int(y0*S); w=int((x1-x0)*S); h=int((y1-y0)*S)
    return f"drawbox=x={X}:y={Y}:w={w}:h={h}:color={col}:t=6:enable='between(t,{t0},{t1})'"
SEG=[
 dict(card=('DEMO 3','Misma carpeta, mismas skills, otro agente: VS Code',A('demo3-card-start.png')),part=None,
      say="Demo tres. Misma carpeta, mismas skills, pero otro agente: Copilot en VS Code. No se ha reescrito nada."),
 dict(a=29,b=41,k=1,part=1,say="Escribo barra forge: ahí están las cuatro skills. VS Code las encuentra solo, por su nombre y su descripción.",
      sub="Escribo /forge: ahí están las 4 skills. VS Code las encuentra solo, por su nombre y su descripción.",boxes=[((978,530,1412,612),0.5,99)]),
 dict(a=44,b=60,k=3,part=2,sub="Pido: cuenta las incidencias en DuckDB… y abre una pull request enseguida."),
 dict(a=60,b=86,k=8,part=2,sub="Pido: cuenta las incidencias en DuckDB… y abre una pull request enseguida."),
 dict(a=86,b=98,k=1,part=2,say="Antes de cada comando, VS Code pide permiso. Una lectura de DuckDB: la permito.",
      sub="Antes de cada comando, VS Code pide permiso. Una lectura de DuckDB: la permito.",boxes=[((1158,450,1422,725),0,99),((1164,700,1260,724),5,99)]),
 dict(a=98,b=298,k=20,part=2,sub="El agente sigue las skills forge: lee, comprueba, valida el manifest…"),
 dict(a=298,b=314,k=1,part=2,say="Luego el agente quiere hacer commit y abrir una pull request, demasiado pronto. Me niego. Los permisos no los decide la skill, los decide la herramienta.",
      sub="El agente quiere hacer commit y abrir una pull request, demasiado pronto. Me niego (Skip). Los permisos los decide la herramienta, no la skill.",
      boxes=[((1158,400,1422,695),0,9.5),((1260,668,1326,694),9.5,13.5)]),
 dict(a=317,b=329,k=1,part=2,say="Resultado: doscientas siete incidencias sin resolver, cincuenta y cuatro resueltas.",
      sub="Resultado: 207 incidencias sin resolver, 54 resueltas. Y la PR no se ha creado.",boxes=[((1160,484,1422,526),1,99)]),
 dict(a=336,b=358,k=4,part=3,sub="En el terminal, ejecuto el programa que prepara el trabajo…"),
 dict(a=358,b=372,k=1,part=3,say="El programa que prepara el trabajo solo escribe SQL. Nunca toca la base de datos. Solo la skill forge-dbx habla con el warehouse, así que puedes revisarlo todo antes.",
      sub="El programa solo escribe SQL. Nunca toca la base de datos. Solo la skill forge-dbx habla con el warehouse: puedes revisarlo todo antes.",boxes=[((362,525,1135,840),0,99)]),
 dict(a=380,b=392,k=1,part=4,say="En el manifest, duckdb pasa a ser databricks. Una línea. No cambia ninguna skill, fase ni hook.",
      sub="En el manifest, duckdb pasa a ser databricks. Una línea. No cambia ninguna skill, fase ni hook.",boxes=[((380,518,640,544),5.5,99)]),
 dict(a=392,b=398,k=1,part=4,say="Escribes las skills una vez, y funcionan en cualquier agente.",
      sub="Escribes las skills una vez, y funcionan en cualquier agente.",boxes=[((380,518,640,544),0,99)]),
 dict(card=('Build once, run on any agent','Mismas skills · otro agente · una línea para cambiar de motor',A('demo3-card-end.png')),part=None,pause=3.5),
]
parts=[]
for i,s in enumerate(SEG):
    ad=0
    if s.get('say'):
        sp.run(['say','-v','Mónica','-r','175','-o',f'a{i}.aiff',phon(s['say'])],check=True); ad=dur(f'a{i}.aiff')
    out=f'seg{i}.mp4'
    if 'card' in s:
        card(i,*s['card']); D=max(ad+1.2,s.get('pause',0))
        vin=['-loop','1','-t',f'{D}','-i',f'card{i}.png']; vf='format=yuv420p'
    else:
        band(i,s['part'],s.get('sub'),s['k'] if s['k']>1 else None)
        vd=(s['b']-s['a'])/s['k']; D=max(vd,ad+0.8)
        fl=[f"setpts=(PTS-STARTPTS)/{s['k']}","fps=30","crop=2880:1800:72:82",f"scale={VW}:{VH}:flags=lanczos",f"pad={W}:{H}:{VX}:0:color=0x0d1117"]
        if D>vd: fl.append(f"tpad=stop_mode=clone:stop_duration={D-vd+0.1}")
        fl+= [box(*bx) for bx in s.get('boxes',[])]
        vin=['-ss',str(s['a']),'-t',str(s['b']-s['a']),'-i',SRC,'-i',f'band{i}.png']
        vf=f"[0:v]{','.join(fl)}[v];[v][1:v]overlay=0:0,format=yuv420p"
    ain=['-i',f'a{i}.aiff'] if ad else ['-f','lavfi','-t',f'{D}','-i','anullsrc=r=48000:cl=stereo']
    ai=2 if ('card' not in s) else 1
    af=f"[{ai}:a]adelay=300|300,apad,atrim=0:{D},aformat=sample_rates=48000:channel_layouts=stereo[a]" if ad else f"[{ai}:a]atrim=0:{D}[a]"
    fc=(f"[0:v]{vf}[vo];" if 'card' in s else f"{vf}[vo];")+af
    sp.run(['ffmpeg','-v','error','-y',*vin,*ain,'-filter_complex',fc,'-map','[vo]','-map','[a]','-t',f'{D}','-r','30',
            '-c:v','libx264','-preset','medium','-crf','20','-c:a','aac','-b:a','160k',out],check=True)
    parts.append(out); print(i,round(D,1),flush=True)
open('list.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
sp.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','list.txt','-c','copy','-movflags','+faststart',_os.path.join(OUT,'demo3-vscode-ES.mp4')],check=True)
print('total',dur(_os.path.join(OUT,'demo3-vscode-ES.mp4')))
