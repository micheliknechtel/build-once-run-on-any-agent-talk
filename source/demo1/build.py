"""Dub the original English Proof Agent demo into another language.
Usage: python3 demo1/build.py fr|es|de   (edit <lang>.tsv: start_seconds<TAB>text)"""
import subprocess, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG=sys.argv[1] if len(sys.argv)>1 else 'fr'
VOICE={'fr':'Amélie','es':'Mónica','de':'Anna'}[LANG]
SRC=os.path.join(ROOT,'assets','demo1-original-EN.mp4'); END=223.15
WORK=os.path.join(ROOT,'build','demo1-'+LANG); os.makedirs(WORK,exist_ok=True)
OUT=os.path.join(ROOT,'output',LANG.upper()); os.makedirs(OUT,exist_ok=True)
rows=[l.split('\t',1) for l in open(os.path.join(ROOT,'demo1',LANG+'.tsv'),encoding='utf-8').read().strip().split('\n')]
inputs=[];filt=[]
for i,(s,t) in enumerate(rows):
    s=float(s); nxt=float(rows[i+1][0]) if i+1<len(rows) else END
    win=nxt-s-0.15; a=os.path.join(WORK,f'seg{i}.aiff')
    subprocess.run(['say','-v',VOICE,'-r','190','-o',a,t],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',a]))
    tempo=max(1.0,d/win)
    print(f'{i:2d} {s:6.2f} dur={d:5.2f} win={win:5.2f} tempo={tempo:.2f}'+('  <-- too long, shorten text' if tempo>1.3 else ''))
    inputs+=['-i',a]
    filt.append(f'[{i}:a]'+(f'atempo={tempo:.3f},' if tempo>1 else '')+f'aresample=44100,adelay={int(s*1000)}|{int(s*1000)}[a{i}]')
n=len(rows); m4a=os.path.join(WORK,'voice.m4a')
fc=';'.join(filt)+';'+''.join(f'[a{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0,apad,atrim=0:{END}[out]'
subprocess.run(['ffmpeg','-y','-v','error']+inputs+['-filter_complex',fc,'-map','[out]','-ac','2',m4a],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',SRC,'-i',m4a,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-shortest',os.path.join(OUT,f'demo1-proof-agent-{LANG.upper()}.mp4')],check=True)
print('done')
