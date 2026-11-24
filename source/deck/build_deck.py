"""Build the deck + notes PDF for one language from base-deck-FR.pptx.
Usage: python3 deck/build_deck.py en|fr|es|de   (needs output/XX/demo1..3 videos first)
Edit notes in deck/notes_<lang>.py (dict N: slide number -> text)."""
import os, sys, shutil, zipfile, subprocess, importlib.util
from pptx import Presentation
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
L=sys.argv[1]; U=L.upper(); OUT=os.path.join(ROOT,'output',U)
spec=importlib.util.spec_from_file_location('n',os.path.join(HERE,f'notes_{L}.py')); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
W=os.path.join(ROOT,'build',f'deck-{L}'); shutil.rmtree(W,ignore_errors=True)
zipfile.ZipFile(os.path.join(HERE,'base-deck-FR.pptx')).extractall(W)
med=os.path.join(W,'ppt','media')
v1,v2,v3=[os.path.join(OUT,f) for f in (f'demo1-proof-agent-{U}.mp4',f'demo2-dataforge-{U}.mp4',f'demo3-vscode-{U}.mp4')]
for video in (v1,v2,v3):
    if not os.path.isfile(video):
        raise FileNotFoundError(f"Rebuild all three {U} demos before building the deck: {video}")
# Slides 6, 8, and 9 contain demos 1, 2, and 3.
for src,dst in ((v1,'media1.mp4'),(v2,'media2.mp4'),(v3,'media3.mp4')): shutil.copy(src,os.path.join(med,dst))
# Resolve the poster relationship for each movie, including demo 1.
base=Presentation(os.path.join(HERE,'base-deck-FR.pptx'))
previews=os.path.join(W,'previews'); os.makedirs(previews,exist_ok=True)
for slide_number,video in zip((6,8,9),(v1,v2,v3)):
    slide=base.slides[slide_number-1]
    movies=[shape for shape in slide.shapes if shape.shape_type==16]
    if len(movies)!=1:
        raise ValueError(f"Expected one demo movie on slide {slide_number}")
    movie=movies[0]
    rid=movie._element.xpath('.//a:blip')[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    poster=os.path.join(W,str(slide.part.rels[rid].target_part.partname).lstrip('/'))
    subprocess.run(['ffmpeg','-v','error','-y','-ss','2','-i',video,'-frames:v','1','-update','1',poster],check=True)
    # Only the movie rectangle changes; keep the existing rasterized slide outside it.
    preview=Image.open(os.path.join(HERE,'slides',f'p-{slide_number:02d}.png')).convert('RGB')
    x=round(movie.left/base.slide_width*preview.width)
    y=round(movie.top/base.slide_height*preview.height)
    width=round(movie.width/base.slide_width*preview.width)
    height=round(movie.height/base.slide_height*preview.height)
    preview.paste(Image.open(poster).convert('RGB').resize((width,height),Image.Resampling.LANCZOS),(x,y))
    preview.save(os.path.join(previews,f'p-{slide_number:02d}.png'))
raw=W+'.pptx'
with zipfile.ZipFile(raw,'w',zipfile.ZIP_DEFLATED) as z:
    for d,_,fs in os.walk(W):
        for f in fs:
            if d==previews: continue
            p=os.path.join(d,f); z.write(p,os.path.relpath(p,W))
p=Presentation(raw)
for i,s in enumerate(p.slides,1): s.notes_slide.notes_text_frame.text=m.N[i]
deck=os.path.join(OUT,f'talk-build-once-run-on-any-agent-{U}.pptx'); p.save(deck)
lab={'en':'Slide','fr':'Slide','es':'Diapositiva','de':'Folie'}[L]
subprocess.run([sys.executable,os.path.join(HERE,'mkpdf.py'),deck,os.path.join(OUT,f'talk-build-once-run-on-any-agent-{U}-notes.pdf'),lab,previews],check=True)
print('deck',deck)
