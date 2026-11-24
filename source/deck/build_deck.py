"""Build the deck + notes PDF for one language from base-deck-FR.pptx.
Usage: python3 deck/build_deck.py en|fr|es|de   (needs output/XX/demo1..3 videos first)
Edit notes in deck/notes_<lang>.py (dict N: slide number -> text)."""
import os, sys, shutil, zipfile, subprocess, importlib.util
from pptx import Presentation
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
L=sys.argv[1]; U=L.upper(); OUT=os.path.join(ROOT,'output',U)
spec=importlib.util.spec_from_file_location('n',os.path.join(HERE,f'notes_{L}.py')); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
W=os.path.join(ROOT,'build',f'deck-{L}'); shutil.rmtree(W,ignore_errors=True)
zipfile.ZipFile(os.path.join(HERE,'base-deck-FR.pptx')).extractall(W)
med=os.path.join(W,'ppt','media')
v1,v2,v3=[os.path.join(OUT,f) for f in (f'demo1-proof-agent-{U}.mp4',f'demo2-dataforge-{U}.mp4',f'demo3-vscode-{U}.mp4')]
if L=='en' and not os.path.exists(v1): v1=os.path.join(ROOT,'assets','demo1-original-EN.mp4')
# slide 6 -> media1, slide 8 -> media2 (poster image17), slide 9 -> media3 (poster image18)
for src,dst in ((v1,'media1.mp4'),(v2,'media2.mp4'),(v3,'media3.mp4')): shutil.copy(src,os.path.join(med,dst))
subprocess.run(['ffmpeg','-v','error','-y','-ss','3','-i',v2,'-frames:v','1','-update','1',os.path.join(med,'image17.png')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-ss','2','-i',v3,'-frames:v','1','-vf','scale=1920:1200','-update','1',os.path.join(med,'image18.png')],check=True)
raw=W+'.pptx'
with zipfile.ZipFile(raw,'w',zipfile.ZIP_DEFLATED) as z:
    for d,_,fs in os.walk(W):
        for f in fs: p=os.path.join(d,f); z.write(p,os.path.relpath(p,W))
p=Presentation(raw)
for i,s in enumerate(p.slides,1): s.notes_slide.notes_text_frame.text=m.N[i]
deck=os.path.join(OUT,f'talk-build-once-run-on-any-agent-{U}.pptx'); p.save(deck)
lab={'en':'Slide','fr':'Slide','es':'Diapositiva','de':'Folie'}[L]
subprocess.run([sys.executable,os.path.join(HERE,'mkpdf.py'),deck,os.path.join(OUT,f'talk-build-once-run-on-any-agent-{U}-notes.pdf'),lab],check=True)
print('deck',deck)
