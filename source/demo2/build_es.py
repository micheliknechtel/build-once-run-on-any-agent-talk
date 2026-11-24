import subprocess as sp, textwrap, struct
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
A=lambda f:_os.path.join(ROOT,'assets',f)
LANG='es'
WORK=_os.path.join(ROOT,'build','demo2-'+LANG); _os.makedirs(WORK,exist_ok=True); _os.chdir(WORK)
OUT=_os.path.join(ROOT,'output',LANG.upper()); _os.makedirs(OUT,exist_ok=True)
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1920,1080,30
BG=(13,17,23); PANEL=(22,27,34); WHITE=(240,246,252); GREY=(139,148,158)
GREEN=(126,231,135); YEL=(255,214,102); ORA=(255,166,87); BLUE=(121,192,255)
B=lambda s:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',s)
R=lambda s:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',s)
U=lambda s:ImageFont.truetype('/Library/Fonts/Arial Unicode.ttf',s)
M=lambda s:ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',s)
def dur(f): return float(sp.check_output(f'ffprobe -v error -show_entries format=duration -of csv=p=0 {f}',shell=True))
SR=48000
import re
PHON=[('gh','ge hache'),('DuckDB','duck de be'),('CLI','ce ele i'),('Copilot','cópilot'),('dataforge','data forch'),('forge-init','forch init'),('forge-builder','forch bilder'),('pull request','pul ricuest')]
def phon(t):
    for a,b in PHON: t=re.sub(r'(?<![\w-])'+re.escape(a)+r'(?![\w-])',b,t,flags=re.I)
    return t
def tts(i,txt):
    txt=phon(txt)
    sp.run(['say','-v','Mónica','-r','175','-o',f'a{i}.aiff',txt],check=True)
    raw=sp.check_output(['ffmpeg','-v','error','-i',f'a{i}.aiff','-f','s16le','-ac','1','-ar',str(SR),'-'])
    return raw

def frame_base(step,title):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    if step:
        tw=d.textlength(step,font=B(30))
        d.rounded_rectangle((60,48,60+tw+40,98),radius=25,fill=(35,134,54))
        d.text((80,73),step,font=B(30),fill=WHITE,anchor='lm')
        d.text((60+tw+70,73),title,font=B(52),fill=WHITE,anchor='lm')
    return im,d
def subtitle(d,txt):
    lines=textwrap.wrap(txt,62)
    h=len(lines)*52+40; y0=H-h-30
    d.rounded_rectangle((100,y0,W-100,H-30),radius=18,fill=(0,0,0))
    for k,l in enumerate(lines): d.text((W/2,y0+20+k*52+24),l,font=B(40),fill=WHITE,anchor='mm')
def terminal(d,lines,typed=None,box=(60,130,1860,850),fs=30):
    x0,y0,x1,y1=box
    d.rounded_rectangle(box,radius=16,fill=PANEL,outline=(48,54,61),width=2)
    for k,c in enumerate([(255,95,86),(255,189,46),(39,201,63)]): d.ellipse((x0+24+k*30,y0+18,x0+42+k*30,y0+36),fill=c)
    y=y0+60; lh=int(fs*1.45)
    for idx,(st,tx) in enumerate(lines):
        if typed is not None and idx==len(lines)-1 and st=='cmd': tx=tx[:typed]
        if st=='cmd':
            d.text((x0+30,y),'$',font=M(fs),fill=GREEN); d.text((x0+30+fs,y),tx,font=M(fs),fill=WHITE)
            if typed is not None and idx==len(lines)-1: 
                cx=x0+30+fs+d.textlength(tx,font=M(fs)); d.rectangle((cx+2,y+2,cx+fs*0.6,y+fs+4),fill=WHITE)
        elif st=='note': d.text((x0+30,y),tx,font=B(fs+4),fill=ORA)
        elif st=='blank': pass
        else:
            col={'out':GREY,'ok':GREEN,'hi':YEL,'w':WHITE}[st]
            d.text((x0+30,y),tx,font=U(fs) if st=='ok' else M(fs),fill=col)
        y+=lh
def shot(im,src,box,maxw,maxh,x,y):
    s=Image.open(src).convert('RGB').crop(box); f=min(maxw/s.width,maxh/s.height)
    s=s.resize((int(s.width*f),int(s.height*f)),Image.LANCZOS); im.paste(s,(x,y))
    ImageDraw.Draw(im).rectangle((x-2,y-2,x+s.width+1,y+s.height+1),outline=(48,54,61),width=3)
    return x+s.width
def side(d,x,heading,items,y=170):
    d.text((x,y),heading,font=B(40),fill=GREEN); y+=80
    for it in items:
        for k,l in enumerate(textwrap.wrap(it,24)):
            d.text((x,y),('•  ' if k==0 else '    ')+l,font=B(36),fill=WHITE); y+=52
        y+=18
def checklist(d,x,phases,done,y=150):
    for k,p in enumerate(phases):
        yy=y+k*92; ok=k<done
        d.rounded_rectangle((x,yy,x+760,yy+76),radius=14,fill=(35,134,54) if ok else PANEL,outline=(48,54,61),width=2)
        d.ellipse((x+20,yy+16,x+64,yy+60),fill=WHITE if ok else (48,54,61))
        if ok: d.line([(x+30,yy+38),(x+40,yy+49),(x+56,yy+27)],fill=(35,134,54),width=6)
        d.text((x+90,yy+38),f'{k+1}. {p}',font=B(36),fill=WHITE if ok else GREY,anchor='lm')

IS=A('issue-1.png'); PR=A('pr-2.png')
def intro(t,s):
    im,d=frame_base(None,None)
    d.text((W/2,380),'Demo 2 · dataforge, de verdad',font=B(96),fill=WHITE,anchor='mm')
    d.text((W/2,500),'Un repo real  ·  una issue real  ·  Copilot CLI',font=B(48),fill=GREEN,anchor='mm')
    d.text((W/2,580),'github.com/micheliknechtel/support-desk-dataforge',font=R(38),fill=GREY,anchor='mm')
    return im,d
MAN=[('cmd','cat dataforge.manifest.yaml'),('out','project:'),('out','  name: "support-desk"'),('out','platform:'),('hi','  engine: "duckdb"'),('out','  duckdb_dir: "warehouse"'),('out','overrides:'),('out','  naming:'),('out','    verbs: ["resolve"]')]
INIT=[('cmd','copilot -p "initialize dataforge"'),('out','● skill(forge-init)'),('out',"I'll discover the local DuckDB zones and metric-store conventions…")]
INIT2=INIT+[('blank',''),('ok','✓ Initialized Dataforge — created dataforge.manifest.resolved.yaml'),('ok','✓ Discovered 2 DuckDB zones, the service_delivery domain,'),('ok','   and account / workspace / user grains. No unresolved items.')]
ISS=[('cmd','gh issue create --title "Add incident lifecycle metrics" --label metric-request'),('ok','https://github.com/micheliknechtel/support-desk-dataforge/issues/1')]
ISS2=ISS+[('blank',''),('cmd','copilot -p "build the metrics in issue #1"'),('out','● skill(forge-builder)')]
PH=['Leer la issue','Explorar la base de datos','Diseñar las métricas','Crear las 6 tablas','Escribir los pipelines','Probar','Desplegar + pull request']
REAL=['Read phase-1-issue-intake.md','Shell  five discovery queries','Shell  prove both metric expressions','Create Incident_Account_…Daily.sql','Shell  compile all six schemas','Create Incident_Metrics_…Daily.py','Shell  rerun focused test suite','Shell  deploy + reconcile 2 zones','Shell  commit, push, gh pr create','Shell  comment + close issue #1']
VER=[('cmd','gh issue view 1 --json state'),('ok','CLOSED')]
SQL='duckdb zone1.duckdb "SELECT metric_name, SUM(metric_value) …"'
TAB=[('w','┌──────────────────────────────┬───────┐'),('w','│ metric_name                  │ total │'),('w','├──────────────────────────────┼───────┤'),('hi','│ total_incident_create_count  │   261 │'),('hi','│ total_incident_resolve_count │    54 │'),('w','└──────────────────────────────┴───────┘')]
def T(step,title,lines,note=None,typed=False):
    def f(t,s):
        im,d=frame_base(step,title); L=list(lines)+([('blank',''),('note',note)] if note else [])
        n=None
        if typed:
            cmd=[l for l in lines if l[0]=='cmd'][-1][1]; n=min(len(cmd),int(t*28))
            if n<len(cmd): L=lines[:max(i for i,l in enumerate(lines) if l[0]=='cmd')+1]
            else: n=None
        terminal(d,L,typed=n); return im,d
    return f
def IMG(step,title,src,box,head,items):
    def f(t,s):
        im,d=frame_base(step,title); x=shot(im,src,box,1180,700,60,140); side(d,x+50,head,items); return im,d
    return f
def PHASES(done,nreal,note=None):
    def f(t,s):
        im,d=frame_base('PASO 5','forge-builder ejecuta 7 fases')
        checklist(d,60,PH,done,y=140)
        L=[('out',r) for r in REAL[:nreal]]
        if note: L+= [('blank',''),('note',note)]
        terminal(d,L,box=(880,140,1860,780),fs=22); return im,d
    return f
def GPS(stage):
    def f(t,s):
        im,d=frame_base('ÉTAPE 1','Pourquoi un manifeste ?')
        def card(x,head,sub,lines,col):
            d.rounded_rectangle((x,150,x+840,560),radius=24,fill=PANEL,outline=col,width=4)
            d.text((x+420,215),head,font=B(54),fill=col,anchor='mm')
            d.text((x+420,290),sub,font=B(40),fill=WHITE,anchor='mm')
            for k,l in enumerate(lines): d.text((x+420,380+k*60),l,font=R(38),fill=GREY,anchor='mm')
        card(80,'Les skills',"= le GPS",['comment travailler','aucun nom propre','identiques partout'],GREEN)
        if stage>=2: card(1000,'Le manifeste',"= l'adresse",['où travailler','le projet, la base,','les mots du métier'],YEL)
        if stage>=3:
            d.rounded_rectangle((80,600,920,760),radius=20,fill=(35,40,48))
            d.text((500,645),'Procore',font=B(44),fill=WHITE,anchor='mm'); d.text((500,710),'construction · Databricks',font=R(38),fill=YEL,anchor='mm')
            d.rounded_rectangle((1000,600,1840,760),radius=20,fill=(35,40,48))
            d.text((1420,645),'Ma démo',font=B(44),fill=WHITE,anchor='mm'); d.text((1420,710),'support client · DuckDB',font=R(38),fill=YEL,anchor='mm')
            d.text((960,800),'→ les mêmes 4 skills',font=B(44),fill=GREEN,anchor='mm')
        return im,d
    return f

PARTS=[(None,None),('PARTE 1 · LA PREPARACIÓN',(31,111,235)),('PARTE 2 · LAS SKILLS TRABAJAN',(35,134,54)),('PARTE 3 · COMPROBAR EL RESULTADO',(191,135,0)),('PARTE 4 · CAMBIAR DE PLATAFORMA',(218,54,51))]
PSUB=['', 'Todavía no trabaja ninguna skill', 'Las skills toman el relevo', 'Las skills han terminado', '¿Y si pasamos a Databricks?']
def P(n,fn):
    def f(t,s):
        im,d=fn(t,s); lab,col=PARTS[n]
        tw=d.textlength(lab,font=B(26))
        d.rounded_rectangle((W-60-tw-36,20,W-60,62),radius=21,fill=col)
        d.text((W-60-tw/2-18,41),lab,font=B(26),fill=WHITE,anchor='mm'); return im,d
    return f
def CARD(n):
    def f(t,s):
        im,d=frame_base(None,None); lab,col=PARTS[n]
        num,name=lab.split(' · ')
        d.rounded_rectangle((W/2-220,260,W/2+220,350),radius=45,fill=col)
        d.text((W/2,305),num,font=B(52),fill=WHITE,anchor='mm')
        d.text((W/2,450),name,font=B(84),fill=WHITE,anchor='mm')
        d.text((W/2,560),PSUB[n],font=B(48),fill=col if n!=3 else (230,180,40),anchor='mm')
        return im,d
    return f
def PLAN(t,s):
    im,d=frame_base(None,None)
    d.text((W/2,170),'La demo en 4 partes',font=B(72),fill=WHITE,anchor='mm')
    for k in range(1,5):
        lab,col=PARTS[k]; num,name=lab.split(' · '); y=270+k*0+ (k-1)*120
        d.rounded_rectangle((380,y,640,y+80),radius=40,fill=col); d.text((510,y+40),num,font=B(36),fill=WHITE,anchor='mm')
        d.text((680,y+40),name.capitalize() if False else name,font=B(44),fill=WHITE,anchor='lm')
    return im,d
S=[
 ("Demo dos. Todo lo que vais a ver es real: un repo de GitHub real, una issue real, y Copilot CLI ejecutando las skills.",intro),
 ("La demo tiene cuatro partes: preparo el proyecto, las skills hacen el trabajo, comprobamos el resultado y, por último, cambiamos de base de datos.",PLAN),
 ("Primero, la preparación. Todavía no trabaja ninguna skill.",CARD(1)),
 ("Paso uno: preparo el proyecto. Escribo un manifest pequeño, solo unas líneas: el proyecto se llama support-desk, y la base de datos es DuckDB.",P(1,T('PASO 1',"Escribo el manifest",MAN,typed=True))),
 ("¿Por qué importa esto? Las skills no contienen ninguna información del proyecto. Solo dicen cómo trabajar.",P(1,T('PASO 1',"Escribo el manifest",MAN,note='# El proyecto vive aquí. Las skills: solo cómo trabajar.'))),
 ("Ahora empieza la demo. A partir de aquí, las skills hacen el trabajo.",CARD(2)),
 ("Paso dos: le pido a Copilot que inicialice dataforge.",P(2,T('PASO 2',"El agente completa el manifest",INIT,typed=True))),
 ("La skill forge-init mira dentro de la base de datos y completa el manifest con lo que encuentra: dos zonas y tres niveles de detalle.",P(2,T('PASO 2',"El agente completa el manifest",INIT2,note="# Yo escribo la dirección, el agente dibuja el mapa."))),
 ("Paso tres: creo la issue de soporte, con el comando gh.",P(2,T('PASO 3','La issue',ISS,typed=True))),
 ("Aquí está. Pide contar las incidencias abiertas y resueltas, igual que con los tickets.",P(2,IMG('PASO 3','La issue (#1)',IS,(170,190,1100,745),'Lo que pide el negocio:',['incidencias abiertas','incidencias resueltas','vistas como tickets','en las dos zonas']))),
 ("Esta petición es vaga, a propósito: no doy instrucciones técnicas. Le toca al agente convertir esta necesidad en un pipeline.",P(2,IMG('PASO 3','La issue (#1)',IS,(170,190,1100,745),'Lo que pide el negocio:',['incidencias abiertas','incidencias resueltas','vistas como tickets','en las dos zonas','→ vaga, a propósito','→ sin instrucciones técnicas']))),
 ("Paso cuatro: una sola frase a Copilot: construye las métricas de la issue número uno.",P(2,T('PASO 4',"Le paso la issue al agente",[('cmd','copilot -p "build the metrics in issue #1"'),('out','● skill(forge-builder)')],typed=True))),
 ("Paso cinco: la skill forge-builder ejecuta siete fases.",P(2,PHASES(0,1))),
 ("Lee la issue, explora la base de datos y diseña las métricas.",P(2,PHASES(3,3))),
 ("Crea las tablas, escribe los pipelines y los prueba.",P(2,PHASES(6,7))),
 ("Después despliega en las dos zonas y abre una pull request.",P(2,PHASES(7,10))),
 ("En la realidad, esto tardó once minutos. En directo, un humano aprueba cada paso.",P(2,PHASES(7,10,'⏱ 11 min 27 s (real)'))),
 ("Las skills han terminado. Ahora, comprobemos el resultado.",CARD(3)),
 ("Paso seis: el resultado, directamente en la issue.",P(3,IMG('PASO 6',"El resultado, en la issue",IS,(186,1008,1095,1530),"El agente escribió:",['6 tablas por zona','4 meses de historial','cifras = la fuente']))),
 ("El agente explica lo que hizo: seis tablas por zona, cuatro meses de historial y cifras idénticas a la fuente. Después cierra la issue.",P(3,IMG('PASO 6',"El resultado, en la issue",IS,(186,1008,1095,1530),"El agente escribió:",['6 tablas por zona','4 meses de historial','cifras = la fuente','→ issue cerrada']))),
 ("Paso siete: también abre una pull request.",P(3,IMG('PASO 7','Pull request #2',PR,(192,192,1062,800),'En la PR:',['15 archivos','+625 líneas','tests superados']))),
 ("No está fusionada: un humano la revisa y decide.",P(3,IMG('PASO 7','Pull request #2',PR,(192,192,1062,800),'En la PR:',['15 archivos','+625 líneas','tests superados','→ decide un humano']))),
 ("Paso ocho: lo compruebo yo mismo. La issue está cerrada.",P(3,T('PASO 8','Lo compruebo yo mismo',VER,typed=True))),
 ("Y en la base de datos: doscientas sesenta y una incidencias creadas, cincuenta y cuatro resueltas.",P(3,T('PASO 8','Lo compruebo yo mismo',VER+[('blank',''),('cmd',SQL)]+TAB,typed=True))),
 ("Una última pregunta: ¿y si mañana pasamos a Databricks?",CARD(4)),
 ("Solo cambia una línea en el manifest. Las cuatro skills no cambian.",P(4,T('EXTRA','¿Y con Databricks?',[('out','platform:'),('ok','  engine: "databricks"')],note='# Una línea. Las 4 skills no cambian.'))),
 ("Esa es la idea: escribes las skills una vez, y funcionan en todas partes.",P(4,T('EXTRA','¿Y con Databricks?',[('out','platform:'),('ok','  engine: "databricks"')],note='# Escritas una vez. Funcionan en todas partes.'))),
]
audio=bytearray()
ff=sp.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','video.mp4'],stdin=sp.PIPE)
for i,(txt,fn) in enumerate(S):
    raw=tts(i,txt); a=len(raw)/2/SR
    lead=0.4; tail=1.0; D=lead+a+tail
    audio+=b'\0\0'*int(lead*SR)+raw+b'\0\0'*(int(D*SR)-int(lead*SR)-len(raw)//2)
    n=int(round(D*FPS)); cache={}
    for k in range(n):
        im,d=fn(k/FPS,i); subtitle(d,txt); b=im.tobytes()
        ff.stdin.write(b)
    print(i,round(D,1),flush=True)
ff.stdin.close(); ff.wait()
open('audio.raw','wb').write(audio)
sp.run('ffmpeg -y -v error -i video.mp4 -f s16le -ar 48000 -ac 1 -i audio.raw -c:v copy -c:a aac -b:a 160k -shortest out.mp4',shell=True,check=True)
import shutil; shutil.copy('out.mp4',_os.path.join(OUT,'demo2-dataforge-ES.mp4'))
print('done',dur('out.mp4'))
