import subprocess, numpy as np, os, sys, glob
from PIL import Image, ImageDraw, ImageFilter
C='/workspace/ghprofile/v2/chars'; O='/workspace/ghprofile/v2/build/gif'
def frames(mp4, ss, to, fps, tag):
    d=f'/tmp/fr_{tag}'; os.makedirs(d,exist_ok=True)
    for f in glob.glob(d+'/*'): os.remove(f)
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(ss),'-to',str(to),'-i',mp4,'-vf',f'fps={fps}',d+'/%03d.png'],check=True)
    return [Image.open(p).convert('RGB') for p in sorted(glob.glob(d+'/*.png'))]
def cutout(im):
    a=np.asarray(im).astype(int)
    white=(a.min(axis=2)>222)
    # flood from border over "white"
    h,w=white.shape; bg=np.zeros_like(white); stack=[]
    for x in range(w):
        for y in (0,h-1):
            if white[y,x]: stack.append((y,x))
    for y in range(h):
        for x in (0,w-1):
            if white[y,x]: stack.append((y,x))
    while stack:
        y,x=stack.pop()
        if bg[y,x] or not white[y,x]: continue
        bg[y,x]=True
        if y>0: stack.append((y-1,x))
        if y<h-1: stack.append((y+1,x))
        if x>0: stack.append((y,x-1))
        if x<w-1: stack.append((y,x+1))
    # eat bright fringe adjacent to bg (2px)
    m=Image.fromarray((bg*255).astype('uint8')).filter(ImageFilter.MaxFilter(5))
    near=np.asarray(m)>0
    fringe=near & (a.min(axis=2)>170)
    alpha=np.where(bg|fringe,0,255).astype('uint8')
    rgba=np.dstack([a.astype('uint8'),alpha])
    return Image.fromarray(rgba,'RGBA')
def save_gif(fr, path, ms):
    pal=[]
    out=[]
    for f in fr:
        # quantize keeping transparency index 255
        rgb=f.convert('RGB'); q=rgb.quantize(255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        p=q.copy(); px=np.array(p); al=np.asarray(f.getchannel('A'))
        px[al<128]=255; p=Image.fromarray(px,'P'); pl=q.getpalette()[:765]+[0,0,0]; p.putpalette(pl)
        out.append(p)
    out[0].save(path,save_all=True,append_images=out[1:],duration=ms,loop=0,transparency=255,disposal=2,optimize=False)
    print(path, os.path.getsize(path)//1024,'KB', len(out),'frames')
def fit(im, size, box=None):
    if box: im=im.crop(box)
    bb=im.getchannel('A').getbbox(); return im
tag=sys.argv[1]
if tag=='run':
    fr=[cutout(f) for f in frames(C+'/chibi_run2.mp4',0,3.0,15,'run')]
    fr=[f.resize((320,320),Image.LANCZOS) for f in fr]
    save_gif(fr,O+'/maddy-run.gif',66)
if tag=='walk':
    fr=[cutout(f) for f in frames(C+'/chibi_walk.mp4',0,3.0,10,'walk')]
    fr=[f.resize((240,240),Image.LANCZOS) for f in fr]
    save_gif(fr,O+'/maddy-walk.gif',100)
if tag=='dance':
    src=[cutout(f).resize((200,200),Image.LANCZOS) for f in frames(C+'/chibi_dance.mp4',0,3.0,10,'dance')]
    n=len(src); out=[]
    for i in range(n):
        c=Image.new('RGBA',(450,200),(0,0,0,0))
        L=src[(i+n//3)%n].resize((170,170),Image.LANCZOS); R=src[(i+2*n//3)%n].resize((170,170),Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)
        c.alpha_composite(L,(0,30)); c.alpha_composite(R,(280,30)); c.alpha_composite(src[i],(125,0)); out.append(c)
    save_gif(out,O+'/maddy-clone-dance.gif',100)
