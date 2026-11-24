import subprocess as sp, textwrap, struct
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
sys.path.insert(0, ROOT)
from speech import pcm
from narration import scene_duration, write_manifest
A=lambda f:_os.path.join(ROOT,'assets',f)
LANG='de'
WORK=_os.path.join(ROOT,'build','demo2-'+LANG)
OUT=_os.path.join(ROOT,'output',LANG.upper())
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
PHON=[('gh','G H'),('DuckDB','Dack D B'),('CLI','C L I'),('SQL','S Q L')]
def phon(t):
    for a,b in PHON: t=re.sub(r'(?<![\w-])'+re.escape(a)+r'(?![\w-])',b,t,flags=re.I)
    return t
def tts(i,txt):
    txt=phon(txt)
    return pcm(txt,LANG,f'a{i}.wav',SR)

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
    d.text((W/2,380),'Demo 2 · dataforge, ganz real',font=B(96),fill=WHITE,anchor='mm')
    d.text((W/2,500),'Ein echtes Repo  ·  ein echtes Issue  ·  Copilot CLI',font=B(48),fill=GREEN,anchor='mm')
    d.text((W/2,580),'github.com/micheliknechtel/support-desk-dataforge',font=R(38),fill=GREY,anchor='mm')
    return im,d
MAN=[('cmd','cat dataforge.manifest.yaml'),('out','project:'),('out','  name: "support-desk"'),('out','platform:'),('hi','  engine: "duckdb"'),('out','  duckdb_dir: "warehouse"'),('out','overrides:'),('out','  naming:'),('out','    verbs: ["resolve"]')]
INIT=[('cmd','copilot -p "initialize dataforge"'),('out','● skill(forge-init)'),('out',"I'll discover the local DuckDB zones and metric-store conventions…")]
INIT2=INIT+[('blank',''),('ok','✓ Initialized Dataforge — created dataforge.manifest.resolved.yaml'),('ok','✓ Discovered 2 DuckDB zones, the service_delivery domain,'),('ok','   and account / workspace / user grains. No unresolved items.')]
ISS=[('cmd','gh issue create --title "Add incident lifecycle metrics" --label metric-request'),('ok','https://github.com/micheliknechtel/support-desk-dataforge/issues/1')]
ISS2=ISS+[('blank',''),('cmd','copilot -p "build the metrics in issue #1"'),('out','● skill(forge-builder)')]
PH=['Issue lesen','Datenbank erkunden','Metriken entwerfen','Die 6 Tabellen erstellen','Pipelines schreiben','Testen','Deployen + Pull Request']
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
        im,d=frame_base('SCHRITT 5','forge-builder: 7 Phasen')
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

PARTS=[(None,None),('TEIL 1 · DIE VORBEREITUNG',(31,111,235)),('TEIL 2 · DIE SKILLS ARBEITEN',(35,134,54)),('TEIL 3 · DAS ERGEBNIS PRÜFEN',(191,135,0)),('TEIL 4 · PLATTFORMWECHSEL',(218,54,51))]
PSUB=['', 'Noch arbeitet kein Skill', 'Die Skills übernehmen', 'Die Skills sind fertig', 'Und wenn wir zu Databricks wechseln?']
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
    d.text((W/2,170),'Die Demo in 4 Teilen',font=B(72),fill=WHITE,anchor='mm')
    for k in range(1,5):
        lab,col=PARTS[k]; num,name=lab.split(' · '); y=270+k*0+ (k-1)*120
        d.rounded_rectangle((380,y,640,y+80),radius=40,fill=col); d.text((510,y+40),num,font=B(36),fill=WHITE,anchor='mm')
        d.text((680,y+40),name.capitalize() if False else name,font=B(44),fill=WHITE,anchor='lm')
    return im,d
S=[
 ("Demo zwei. Alles, was Sie gleich sehen, ist echt: ein echtes GitHub-Repo, ein echtes Issue, und Copilot CLI, das die Skills ausführt.",intro),
 ("Die Demo hat vier Teile: Ich bereite das Projekt vor, die Skills erledigen die Arbeit, wir prüfen das Ergebnis, und zum Schluss wechseln wir die Datenbank.",PLAN),
 ("Zuerst die Vorbereitung. Noch arbeitet kein Skill.",CARD(1)),
 ("Schritt eins: Ich bereite das Projekt vor. Ich schreibe ein kleines Manifest, nur ein paar Zeilen: Das Projekt heißt support-desk, und die Datenbank ist DuckDB.",P(1,T('SCHRITT 1',"Ich schreibe das Manifest",MAN,typed=True))),
 ("Warum ist das wichtig? Die Skills enthalten keine Informationen über das Projekt. Sie sagen nur, wie man arbeitet.",P(1,T('SCHRITT 1',"Ich schreibe das Manifest",MAN,note='# Das Projekt steht hier. Die Skills: nur wie man arbeitet.'))),
 ("Jetzt beginnt die Demo. Ab hier erledigen die Skills die Arbeit.",CARD(2)),
 ("Schritt zwei: Ich bitte Copilot, dataforge zu initialisieren.",P(2,T('SCHRITT 2',"Der Agent ergänzt das Manifest",INIT,typed=True))),
 ("Der Skill forge-init schaut in die Datenbank und ergänzt das Manifest mit dem, was er findet: zwei Zonen und drei Detailebenen.",P(2,T('SCHRITT 2',"Der Agent ergänzt das Manifest",INIT2,note="# Ich schreibe die Adresse, der Agent zeichnet die Karte."))),
 ("Schritt drei: Ich erstelle das Support-Issue, mit dem Befehl gh.",P(2,T('SCHRITT 3','Das Issue',ISS,typed=True))),
 ("Hier ist es. Es verlangt, offene und gelöste Incidents zu zählen, genau wie bei Tickets.",P(2,IMG('SCHRITT 3','Das Issue (#1)',IS,(170,190,1100,745),'Was das Business will:',['offene Incidents','gelöste Incidents','gleiche Sichten wie bei Tickets','in beiden Zonen']))),
 ("Diese Anfrage ist absichtlich vage: Ich gebe keine technischen Anweisungen. Der Agent muss diesen Bedarf in eine Pipeline verwandeln.",P(2,IMG('SCHRITT 3','Das Issue (#1)',IS,(170,190,1100,745),'Was das Business will:',['offene Incidents','gelöste Incidents','gleiche Sichten wie bei Tickets','in beiden Zonen','→ absichtlich vage','→ keine technischen Anweisungen']))),
 ("Schritt vier: ein einziger Satz an Copilot: Baue die Metriken aus Issue Nummer eins.",P(2,T('SCHRITT 4',"Ich übergebe das Issue an den Agenten",[('cmd','copilot -p "build the metrics in issue #1"'),('out','● skill(forge-builder)')],typed=True))),
 ("Schritt fünf: Der Skill forge-builder durchläuft sieben Phasen.",P(2,PHASES(0,1))),
 ("Er liest das Issue, erkundet die Datenbank und entwirft die Metriken.",P(2,PHASES(3,3))),
 ("Er erstellt die Tabellen, schreibt die Pipelines und testet sie.",P(2,PHASES(6,7))),
 ("Dann deployt er in beide Zonen und öffnet einen Pull Request.",P(2,PHASES(7,10))),
 ("In Wirklichkeit hat das elf Minuten gedauert. Live genehmigt ein Mensch jeden Schritt.",P(2,PHASES(7,10,'⏱ 11 min 27 s (real)'))),
 ("Die Skills sind fertig. Jetzt prüfen wir das Ergebnis.",CARD(3)),
 ("Schritt sechs: das Ergebnis, direkt im Issue.",P(3,IMG('SCHRITT 6',"Das Ergebnis im Issue",IS,(186,1008,1095,1530),"Der Agent schrieb:",['6 Tabellen pro Zone','4 Monate Historie','Zahlen = die Quelle']))),
 ("Der Agent erklärt, was er getan hat: sechs Tabellen pro Zone, vier Monate Historie, und Zahlen, die mit der Quelle identisch sind. Dann schließt er das Issue.",P(3,IMG('SCHRITT 6',"Das Ergebnis im Issue",IS,(186,1008,1095,1530),"Der Agent schrieb:",['6 Tabellen pro Zone','4 Monate Historie','Zahlen = die Quelle','→ Issue geschlossen']))),
 ("Schritt sieben: Er öffnet auch einen Pull Request.",P(3,IMG('SCHRITT 7','Pull Request #2',PR,(192,192,1062,800),'Im PR:',['15 Dateien','+625 Zeilen','Tests bestanden']))),
 ("Er ist nicht gemergt: Ein Mensch prüft ihn und entscheidet.",P(3,IMG('SCHRITT 7','Pull Request #2',PR,(192,192,1062,800),'Im PR:',['15 Dateien','+625 Zeilen','Tests bestanden','→ ein Mensch entscheidet']))),
 ("Schritt acht: Ich prüfe selbst. Das Issue ist tatsächlich geschlossen.",P(3,T('SCHRITT 8','Ich prüfe selbst',VER,typed=True))),
 ("Und in der Datenbank: 261 Incidents erstellt, 54 gelöst.",P(3,T('SCHRITT 8','Ich prüfe selbst',VER+[('blank',''),('cmd',SQL)]+TAB,typed=True))),
 ("Eine letzte Frage: Was, wenn wir morgen zu Databricks wechseln?",CARD(4)),
 ("Im Manifest ändert sich nur eine Zeile. Die vier Skills ändern sich nicht.",P(4,T('BONUS','Und Databricks?',[('out','platform:'),('ok','  engine: "databricks"')],note='# Eine Zeile. Die 4 Skills ändern sich nicht.'))),
 ("Darum geht es: Sie schreiben die Skills einmal, und sie funktionieren überall.",P(4,T('BONUS','Und Databricks?',[('out','platform:'),('ok','  engine: "databricks"')],note='# Einmal geschrieben. Funktioniert überall.'))),
]

def build():
    _os.makedirs(WORK,exist_ok=True); _os.makedirs(OUT,exist_ok=True); _os.chdir(WORK)
    segments=[tts(i,txt) for i,(txt,_) in enumerate(S)]
    audio=bytearray()
    cues=[]
    offset=0
    ff=sp.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','video.mp4'],stdin=sp.PIPE)
    try:
        for i,(txt,fn) in enumerate(S):
            raw=segments[i]; a=len(raw)/2/SR
            lead=0.4; tail=1.0; D=scene_duration(0,a,lead=lead,tail=tail,fps=FPS)
            samples=round(D*SR)
            audio+=b'\0\0'*int(lead*SR)+raw+b'\0\0'*(samples-int(lead*SR)-len(raw)//2)
            n=round(D*FPS)
            for k in range(n):
                im,d=fn(k/FPS,i); subtitle(d,txt)
                ff.stdin.write(im.tobytes())
            cues.append(dict(text=txt,spoken_text=phon(txt),wav=_os.path.abspath(f'a{i}.wav'),
                start=offset,duration=D,audio_start=offset+lead,audio_duration=a))
            offset+=D
            print(i,round(D,1),flush=True)
    finally:
        ff.stdin.close()
        returncode=ff.wait()
    if returncode:
        raise RuntimeError("ffmpeg failed to encode the demo video")
    open('audio.raw','wb').write(audio)
    sp.run(['ffmpeg','-y','-v','error','-i','video.mp4','-f','s16le','-ar',str(SR),'-ac','1','-i','audio.raw','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart','out.mp4'],check=True)
    import shutil
    output=_os.path.join(OUT,f'demo2-dataforge-{LANG.upper()}.mp4')
    shutil.copy('out.mp4',output)
    write_manifest(output,LANG,cues)
    print('done',dur('out.mp4'))

if __name__=='__main__':
    build()
