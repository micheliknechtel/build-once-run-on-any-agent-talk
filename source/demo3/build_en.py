import subprocess as sp, textwrap, re, os
import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
sys.path.insert(0, ROOT)
from speech import synthesize
from narration import narration_text, scene_duration, write_audio_track, write_manifest
A=lambda f:_os.path.join(ROOT,'assets',f)
LANG='en'
WORK=_os.path.join(ROOT,'build','demo3-'+LANG)
OUT=_os.path.join(ROOT,'output',LANG.upper())
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
SRC=A('demo3-screen-recording.mov')
W,H=1920,1200; VW,VH,VX=1600,1000,160; S=VW/1440
B=lambda s:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',s)
U=lambda s:ImageFont.truetype('/Library/Fonts/Arial Unicode.ttf',s)
WHITE=(240,246,252)
PARTS={1:('PART 1 · VS CODE FINDS THE SKILLS',(31,111,235)),2:("PART 2 · THE HUMAN STAYS IN CONTROL",(35,134,54)),
       3:('PART 3 · EVERYTHING IS REVIEWABLE',(191,135,0)),4:('PART 4 · THE MESSAGE',(218,54,51))}
PHON=[('/forge','slash forge'),('DuckDB','duck D B'),('SQL','S Q L'),('PR','P R')]
def phon(t):
    t=t.replace('/forge', 'slash forge')
    for a,b in PHON: t=re.sub(r'(?<![\w-])'+re.escape(a)+r'(?![\w-])',b,t,flags=re.I)
    return t

def dur(f): return float(sp.check_output(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{f}"',shell=True))
def band(i,part,sub,speed=None):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle((0,VH,W,H),fill=(13,17,23,255))
    if part:
        t,c=PARTS[part]; tw=d.textlength(t,font=B(30))
        d.rounded_rectangle((40,VH+14,40+tw+40,VH+60),radius=23,fill=c); d.text((60,VH+37),t,font=B(30),fill=WHITE,anchor='lm')
    if speed: d.text((W-40,VH+37),f'▶▶ sped up ×{speed}',font=U(30),fill=(255,214,102),anchor='rm')
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
 dict(card=('DEMO 3','Same folder, same skills, another agent: VS Code',A('demo3-card-start.png')),part=None,
      say="Demo three. Same folder, same skills, but another agent: Copilot in VS Code. Nothing was rewritten."),
 dict(a=29,b=41,k=1,part=1,sub="I type /forge: the 4 skills are there. VS Code finds them on its own, from their name and description.",boxes=[((978,530,1412,612),0.5,99)]),
 dict(a=44,b=60,k=3,part=2,sub="I ask: count the incidents in DuckDB… then open a pull request right away."),
 dict(a=60,b=86,k=8,part=2,sub="I ask: count the incidents in DuckDB… then open a pull request right away."),
 dict(a=86,b=98,k=1,part=2,sub="Before each command, VS Code asks for permission. A DuckDB read: I allow it.",boxes=[((1158,450,1422,725),0,99),((1164,700,1260,724),5,99)]),
 dict(a=98,b=298,k=20,part=2,sub="The agent follows the forge skills: it reads, checks, validates the manifest…"),
 dict(a=298,b=314,k=1,part=2,sub="The agent wants to commit and open a pull request, too early. I refuse (Skip). Permissions are decided by the tool, not by the skill.",
      boxes=[((1158,400,1422,695),0,9.5),((1260,668,1326,694),9.5,13.5)]),
 dict(a=317,b=329,k=1,part=2,sub="Result: 207 unresolved incidents, 54 resolved. And the PR was not created.",boxes=[((1160,484,1422,526),1,99)]),
 dict(a=336,b=358,k=4,part=3,sub="In the terminal, I run the program that prepares the work…"),
 dict(a=358,b=372,k=1,part=3,sub="The program only writes SQL. It never touches the database. Only the forge-dbx skill talks to the warehouse: you can review everything first.",boxes=[((362,525,1135,840),0,99)]),
 dict(a=380,b=392,k=1,part=4,sub="In the manifest, duckdb becomes databricks. One line. No skill, phase or hook changes.",boxes=[((380,518,640,544),5.5,99)]),
 dict(a=392,b=398,k=1,part=4,sub="You write the skills once, and they work on any agent.",boxes=[((380,518,640,544),0,99)]),
 dict(card=('Build once, run on any agent','Same skills · another agent · one line to switch engine',A('demo3-card-end.png')),part=None,pause=3.5),
]
def build():
    _os.makedirs(WORK,exist_ok=True); _os.chdir(WORK)
    parts=[]
    cues=[]
    offset=0
    previous_subtitle=None
    for i,s in enumerate(SEG):
        ad=0
        text=narration_text(s,previous_subtitle)
        previous_subtitle=s.get('sub')
        if text:
            synthesize(phon(text),LANG,f'a{i}.wav'); ad=dur(f'a{i}.wav')
        out=f'seg{i}.mp4'
        if 'card' in s:
            card(i,*s['card']); D=scene_duration(s.get('pause',0),ad,tail=0.9)
            vin=['-loop','1','-t',f'{D}','-i',f'card{i}.png']; vf='format=yuv420p'
        else:
            band(i,s['part'],s.get('sub'),s['k'] if s['k']>1 else None)
            vd=(s['b']-s['a'])/s['k']; D=scene_duration(vd,ad)
            fl=[f"setpts=(PTS-STARTPTS)/{s['k']}","fps=30","crop=2880:1800:72:82",f"scale={VW}:{VH}:flags=lanczos",f"pad={W}:{H}:{VX}:0:color=0x0d1117"]
            if D>vd: fl.append(f"tpad=stop_mode=clone:stop_duration={D-vd+0.1}")
            fl+= [box(*bx) for bx in s.get('boxes',[])]
            vin=['-ss',str(s['a']),'-t',str(s['b']-s['a']),'-i',SRC,'-i',f'band{i}.png']
            vf=f"[0:v]{','.join(fl)}[v];[v][1:v]overlay=0:0,format=yuv420p"
        fc=f"[0:v]{vf}[vo]" if 'card' in s else f"{vf}[vo]"
        sp.run(['ffmpeg','-v','error','-y',*vin,'-filter_complex',fc,'-map','[vo]','-an','-t',f'{D}','-r','30',
                '-c:v','libx264','-preset','medium','-crf','20',out],check=True)
        cues.append(dict(text=text, spoken_text=phon(text) if text else None,
            subtitle=s.get('sub'), wav=_os.path.abspath(f'a{i}.wav') if text else None,
            start=offset, duration=D, audio_start=offset+0.3, audio_duration=ad))
        offset+=D
        parts.append(out); print(i,round(D,1),flush=True)
    open('list.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
    write_audio_track(cues,'voice.wav')
    sp.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','list.txt','-i','voice.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',_os.path.join(OUT,'demo3-vscode-EN.mp4')],check=True)
    write_manifest(_os.path.join(OUT,f'demo3-vscode-{LANG.upper()}.mp4'),LANG,cues)
    print('total',dur(_os.path.join(OUT,'demo3-vscode-EN.mp4')))

if __name__=='__main__':
    build()
