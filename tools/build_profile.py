#!/usr/bin/env python3
"""Builds the animated profile cards in ../assets from the character art in ../art-src.
All artwork is original (generated for Xdev200). Fonts: Space Grotesk + JetBrains Mono (SIL OFL 1.1),
subset and embedded. Brand glyphs: simple-icons (CC0)."""
import html, base64, io, json, os, re, glob, subprocess, math, random
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.environ.get('ART_SRC', os.path.join(ROOT,'art-src'))
FONTS=os.environ.get('FONT_DIR', os.path.join(ROOT,'tools','fonts'))
SI=os.environ.get('SI_DIR','/tmp/si/package')
OUT=os.path.join(ROOT,'assets')

OR='#ff7a1a'; RED='#e2383f'; PU='#9d6bff'; AM='#ffb52e'; GR='#2fd48a'; BL='#4aa8ff'
TX='#eef1f7'; MU='#8b93a7'; LINE='#272e42'

def font_css():
    css=''
    for n in ['SG','SGM','JBM','JBMB']:
        b=base64.b64encode(open(f'{FONTS}/{n}.woff2','rb').read()).decode()
        css+=f"@font-face{{font-family:'{n}';src:url(data:font/woff2;base64,{b}) format('woff2')}}"
    return css
FONTCSS=font_css()
BASE=f"""{FONTCSS}
text{{font-family:'JBM',ui-monospace,Menlo,Consolas,monospace}}
.sg{{font-family:'SG','Segoe UI',Helvetica,Arial,sans-serif;font-weight:700}}
.sgm{{font-family:'SGM','Segoe UI',Helvetica,Arial,sans-serif;font-weight:500}}
.jb{{font-family:'JBM',ui-monospace,Menlo,Consolas,monospace}}
.jbb{{font-family:'JBMB',ui-monospace,Menlo,Consolas,monospace;font-weight:700}}
@keyframes up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@keyframes appear{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes left{{from{{opacity:0;transform:translateX(-14px)}}to{{opacity:1;transform:none}}}}
@keyframes turn{{to{{transform:rotate(360deg)}}}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
.up{{animation:up .7s cubic-bezier(.2,.8,.2,1) both}}
.ap{{animation:appear .8s ease both}}
.lf{{animation:left .7s cubic-bezier(.2,.8,.2,1) both}}
.turn{{transform-box:fill-box;transform-origin:center;animation:turn 10s linear infinite}}
.bob{{animation:bob 7s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important;transform:none!important}}}}
"""

def jpg(path, w, h, q=78, focus=(0.5,0.5), scale=1.5):
    im=Image.open(path).convert('RGB'); W,H=im.size; r=w/h
    if W/H>r: cw,ch=int(H*r),H
    else: cw,ch=W,int(W/r)
    x=int((W-cw)*focus[0]); y=int((H-ch)*focus[1])
    im=im.crop((x,y,x+cw,y+ch)).resize((int(w*scale),int(h*scale)),Image.LANCZOS)
    b=io.BytesIO(); im.save(b,'JPEG',quality=q,optimize=True,progressive=True)
    return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()

def icon(slug, size=20, color=None):
    p=f'{SI}/icons/{slug}.svg'
    if not os.path.exists(p): return None, None
    s=open(p).read(); d=re.search(r' d="([^"]+)"',s).group(1)
    meta=[x for x in json.load(open(f'{SI}/data/simple-icons.json')) if x.get('slug',slugify(x['title']))==slug]
    hexc='#'+meta[0]['hex'] if meta else '#ffffff'
    return d, hexc
def slugify(t):
    return re.sub(r'[^a-z0-9]','',t.lower().replace('+','plus').replace('.','dot').replace('&','and'))

def emblem(scale=1, color=OR, sw=2.2, op=1):
    # the <X> headband mark, centred on 0,0, ~24 units wide
    return (f'<g transform="scale({scale})" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}">'
            f'<path d="M-6-6 6 6M6-6-6 6"/><path d="M-10.5-5-15 0-10.5 5"/><path d="M10.5-5 15 0 10.5 5"/></g>')
def shuriken(color=OR, s=1, cls='turn', delay=0):
    p='M0-12 2.6-2.6 12 0 2.6 2.6 0 12-2.6 2.6-12 0-2.6-2.6Z'
    return f'<g class="{cls}" style="animation-delay:{delay}s"><g transform="scale({s})"><path d="{p}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linejoin="round" transform="rotate(22)"/><circle r="2.3" fill="none" stroke="{color}" stroke-width="1.4"/></g></g>'

def panel(w,h,pid,edge=(OR,PU)):
    return f'''<linearGradient id="{pid}p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#151a2c"/><stop offset="1" stop-color="#0f1320"/></linearGradient>
<linearGradient id="{pid}e" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{edge[0]}" stop-opacity=".55"/><stop offset=".5" stop-color="{LINE}"/><stop offset="1" stop-color="{edge[1]}" stop-opacity=".55"/></linearGradient>
<pattern id="{pid}d" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="12" cy="12" r=".9" fill="#fff" fill-opacity=".05"/></pattern>''', \
    f'''<rect width="{w}" height="{h}" rx="24" fill="url(#{pid}p)"/><rect width="{w}" height="{h}" rx="24" fill="url(#{pid}d)"/><rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="23.25" fill="none" stroke="url(#{pid}e)" stroke-width="1.5"/>'''

def svg(w,h,label,desc,defs,css,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{html.escape(label)}"><title>{html.escape(label)}</title><desc>{html.escape(desc)}</desc><defs><style>{BASE}{css}</style>
{defs}</defs>
{body}
</svg>'''

def fade_mask(mid,x,y,w,h,left=.22,right=None,top=None,bottom=.82):
    g=f'<linearGradient id="{mid}h" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset="{left}" stop-color="#fff"/>'
    g+=(f'<stop offset="{right}" stop-color="#fff"/><stop offset="1" stop-color="#000"/>' if right else '<stop offset="1" stop-color="#fff"/>')+'</linearGradient>'
    g+=f'<linearGradient id="{mid}v" x1="0" y1="0" x2="0" y2="1">'+(f'<stop offset="0" stop-color="#000"/><stop offset="{top}" stop-color="#fff"/>' if top else '<stop offset="0" stop-color="#fff"/>')+f'<stop offset="{bottom}" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
    g+=f'<mask id="{mid}H" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{mid}h)"/></mask>'
    g+=f'<mask id="{mid}V" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{mid}v)"/></mask>'
    return g

def particles(n, xr, yr, colors, cls, seed=1, rmax=2.2):
    r=random.Random(seed); out=''
    for i in range(n):
        out+=f'<circle class="{cls}" cx="{r.randint(*xr)}" cy="{r.randint(*yr)}" r="{r.uniform(1.2,rmax):.1f}" fill="{r.choice(colors)}" opacity="0" style="animation-delay:{r.uniform(0,6):.1f}s;animation-duration:{r.uniform(4.5,7.5):.1f}s"/>'
    return out

# ---------------------------------------------------------------- HERO
def hero():
    W,H=1280,560; VX,VY,VW,VH=668,30,556,492
    d=f'''<linearGradient id="nameG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AM}"/><stop offset=".5" stop-color="{OR}"/><stop offset="1" stop-color="#ff5c2b"/><animateTransform attributeName="gradientTransform" type="translate" values="-.3 0;.3 0;-.3 0" dur="8s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="barG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{OR}"/><stop offset="1" stop-color="{PU}"/></linearGradient>
{fade_mask('vm',VX,VY,VW,VH)}
<radialGradient id="orbO"><stop offset="0" stop-color="{OR}" stop-opacity=".30"/><stop offset="1" stop-color="{OR}" stop-opacity="0"/></radialGradient>
<radialGradient id="orbP"><stop offset="0" stop-color="{PU}" stop-opacity=".26"/><stop offset="1" stop-color="{PU}" stop-opacity="0"/></radialGradient>
<filter id="glow"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
<clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<clipPath id="hiC"><rect x="52" y="118" width="300" height="34"><animate attributeName="width" values="0;0;300" keyTimes="0;.38;1" dur="1.3s" fill="freeze" calcMode="spline" keySplines="0 0 1 1;.3 0 .2 1"/></rect></clipPath>
<clipPath id="nameC"><rect x="44" y="150" width="600" height="92"><animate attributeName="y" values="242;242;150" keyTimes="0;.52;1" dur="2s" fill="freeze" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1"/></rect></clipPath>
<clipPath id="termC"><rect x="52" y="52" width="440" height="24"><animate attributeName="width" values="0;440" dur="1s" fill="freeze"/></rect></clipPath>
<linearGradient id="hp" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0c0f1a"/><stop offset="1" stop-color="#0a0c14"/></linearGradient>
<linearGradient id="he" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{OR}" stop-opacity=".55"/><stop offset=".5" stop-color="{LINE}"/><stop offset="1" stop-color="{PU}" stop-opacity=".5"/></linearGradient>
<pattern id="hd" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="12" cy="12" r=".9" fill="#fff" fill-opacity=".05"/></pattern>'''
    css=f'''.role{{animation:role 13.2s cubic-bezier(.2,.8,.2,1) infinite}}
@keyframes role{{0%{{opacity:0;transform:translateY(14px)}}3.5%,21%{{opacity:1;transform:none}}24%,100%{{opacity:0;transform:translateY(-14px)}}}}
.rise{{animation:rise 5s ease-in-out infinite}}
@keyframes rise{{0%{{transform:none;opacity:0}}18%{{opacity:.8}}80%{{opacity:.5}}100%{{transform:translateY(-120px);opacity:0}}}}
.corner{{stroke-dasharray:54;animation:draw .7s ease both}}
@keyframes draw{{from{{stroke-dashoffset:54}}to{{stroke-dashoffset:0}}}}
.blink{{animation:blink 1.1s step-end infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.breathe{{animation:breathe 3.4s ease-in-out infinite}}
@keyframes breathe{{0%,100%{{opacity:.35}}50%{{opacity:.75}}}}'''
    # video frames
    d_=f'/tmp/hero_frames'; os.makedirs(d_,exist_ok=True)
    for f in glob.glob(d_+'/*'): os.remove(f)
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',f'{SRC}/hero_loop.mp4','-t','4.9','-vf','fps=10',f'{d_}/%03d.png'],check=True)
    fr=sorted(glob.glob(d_+'/*.png')); n=len(fr); dur=n/10
    imgs=''
    first=jpg(fr[0],VW,VH,q=60,scale=1.0)
    imgs+=f'<image x="{VX}" y="{VY}" width="{VW}" height="{VH}" href="{first}" preserveAspectRatio="xMidYMid slice"/>'
    for i,p in enumerate(fr[1:],1):
        k0=i/n; k1=(i+1)/n
        vals='0;1;0' if i<n-1 else '0;1'
        kt=f'0;{k0:.4f};{k1:.4f}' if i<n-1 else f'0;{k0:.4f}'
        imgs+=f'<image x="{VX}" y="{VY}" width="{VW}" height="{VH}" href="{jpg(p,VW,VH,q=56,scale=.85)}" opacity="0" preserveAspectRatio="xMidYMid slice"><animate attributeName="opacity" calcMode="discrete" values="{vals}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></image>'
    corners=''.join(f'<path class="corner" d="{p}" fill="none" stroke="{OR}" stroke-opacity=".85" stroke-width="2.4" stroke-linecap="round" style="animation-delay:{.35+i*.08:.2f}s"/>' for i,p in enumerate(['M702 84V54H732','M1222 84V54H1192','M702 444V474H732','M1222 444V474H1192']))
    roles=['Full-Stack Developer','Mobile App Builder','Developer turned Entrepreneur','AI Tools Tinkerer']
    rl=''.join(f'<text class="role jb" x="78" y="312" font-size="19" fill="{TX}" opacity="0" style="animation-delay:{2+i*3.3:.1f}s">{r}</text>' for i,r in enumerate(roles))
    pills=''
    for i,(v,l) in enumerate([('49','REPOS'),('20','STARS'),('20','FOLLOWERS')]):
        x=56+i*132
        pills+=f'<g class="up" style="animation-delay:{3+i*.12:.2f}s"><rect x="{x}" y="398" width="118" height="54" rx="12" fill="#fff" fill-opacity=".03" stroke="{LINE}"/><text class="sg" x="{x+14}" y="428" font-size="22" fill="{OR}">{v}</text><text class="jb" x="{x+14}" y="444" font-size="9" fill="{MU}" letter-spacing="1.6">{l}</text></g>'
    body=f'''<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#hp)"/><rect width="{W}" height="{H}" fill="url(#hd)"/>
<g filter="url(#soft)"><circle cx="200" cy="150" r="190" fill="url(#orbO)"/><circle cx="980" cy="430" r="230" fill="url(#orbP)"/><circle cx="640" cy="60" r="150" fill="url(#orbO)" opacity=".6"/></g>
<g transform="translate(300,330)" opacity=".04">{emblem(13,OR,2.1)}</g>
<g mask="url(#vmH)"><g mask="url(#vmV)">{imgs}</g></g>
{corners}
<g class="ap" style="animation-delay:.7s"><g transform="translate(728,452)">{shuriken(OR,.8)}</g>
<text class="jbb" x="746" y="457" font-size="11.5" fill="{TX}" letter-spacing="2">MADDY.MP4</text>
<text class="jb" x="1208" y="457" font-size="10.5" fill="{MU}" text-anchor="end" letter-spacing="1.4">JAMSHEDPUR · 10FPS · LOOP</text>
<rect x="724" y="470" width="484" height="3" rx="1.5" fill="#fff" fill-opacity=".1"/><rect x="724" y="470" width="0" height="3" rx="1.5" fill="url(#barG)"><animate attributeName="width" values="0;484" dur="{dur}s" repeatCount="indefinite"/></rect></g>
<text clip-path="url(#termC)" x="52" y="68" font-size="13"><tspan class="jbb" fill="{GR}">maddy@jamshedpur</tspan><tspan fill="{MU}">:~$ </tspan><tspan fill="{TX}">summon </tspan><tspan fill="{OR}">--profile</tspan></text>
<rect class="blink" x="497" y="56" width="7" height="15" fill="{GR}"/>
<text clip-path="url(#hiC)" class="sgm" x="52" y="144" font-size="26" fill="{TX}">Hi, I’m</text>
<g clip-path="url(#nameC)"><text class="sg" x="48" y="226" font-size="62" letter-spacing="-1" fill="url(#nameG)" filter="url(#glow)">Madhusudan Das</text></g>
<rect x="52" y="246" width="118" height="3.5" rx="1.75" fill="url(#barG)"><animate attributeName="width" values="0;0;118" keyTimes="0;.72;1" dur="2.6s" fill="freeze"/></rect>
<g class="ap" style="animation-delay:1.9s"><g transform="translate(60,306)">{emblem(.62,OR,2.6)}</g></g>
{rl}
<text class="sgm up" x="52" y="356" font-size="16" fill="{MU}" style="animation-delay:2.6s">Maddy · developer turned entrepreneur, shipping web apps,</text>
<text class="sgm up" x="52" y="378" font-size="16" fill="{MU}" style="animation-delay:2.7s">mobile apps and AI tools from Jamshedpur.</text>
{pills}
<g class="up" style="animation-delay:3.5s"><rect x="452" y="398" width="138" height="54" rx="12" fill="{GR}" fill-opacity=".08" stroke="{GR}" stroke-opacity=".4"/><circle cx="474" cy="418" r="4.5" fill="{GR}"><animate attributeName="opacity" values="1;.2;1" dur="1.7s" repeatCount="indefinite"/></circle><text class="jbb" x="486" y="422" font-size="9.5" fill="{GR}" letter-spacing="1.3">OPEN TO</text><text class="jbb" x="486" y="440" font-size="9.5" fill="{GR}" letter-spacing="1.3">COLLAB</text></g>
{particles(12,(60,620),(440,540),[OR,AM,PU],'rise',3)}
<g class="ap" style="animation-delay:4s"><text class="jb" x="52" y="500" font-size="11" fill="{MU}" letter-spacing="1.6">NINDO ·</text><text class="jb" x="124" y="500" font-size="11" fill="{OR}" letter-spacing=".6">Build it. Ship it. Then build the next one.</text></g>
</g>
<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="23.25" fill="none" stroke="url(#he)" stroke-width="1.5"/>'''
    return svg(W,H,'Madhusudan Das (Maddy) — Developer turned Entrepreneur','Animated hero: Maddy, an original anime ninja version of Madhusudan with an <X> headband, flashes a peace sign beside his name, cycling roles and GitHub stats.',d,css,body)

# ---------------------------------------------------------------- NINJA WAY
def ninja_way():
    W,H=1280,520
    pd,pb=panel(W,H,'a')
    d=pd+f'''<radialGradient id="warm"><stop offset="0" stop-color="{OR}" stop-opacity=".22"/><stop offset="1" stop-color="{OR}" stop-opacity="0"/></radialGradient>
<filter id="b60" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
{fade_mask('am',32,36,520,446,left=.06,right=.88,top=.06,bottom=.86)}
<clipPath id="artC"><rect x="32" y="36" width="520" height="446" rx="18"/></clipPath>'''
    art=jpg(f'{SRC}/ninjaway.jpg',520,446,q=80,focus=(.5,.2))
    rows=[(OR,'web','Web apps that scale','MERN and Next.js builds: dashboards, SaaS and marketing sites'),
          (PU,'mob','Mobile apps on both platforms','Kotlin for Android, Swift / SwiftUI for iOS, Flutter for both'),
          (AM,'ai','AI tools that do real work','Agents, automations and data tools in Python and TypeScript')]
    ic={'web':'<rect x="-9" y="-8" width="18" height="16" rx="2.5"/><path d="M-9-3.5h18M-4 1.5l-2.5 2.5L-4 6.5M4 1.5l2.5 2.5L4 6.5"/>',
        'mob':'<rect x="-5.5" y="-9" width="11" height="18" rx="2.5"/><path d="M-1.5 5.5h3"/>',
        'ai':'<path d="M0-9 2.2-2.2 9 0 2.2 2.2 0 9-2.2 2.2-9 0-2.2-2.2Z"/>'}
    r=''
    for i,(c,k,t,s) in enumerate(rows):
        y=176+i*76
        r+=f'<g class="lf" style="animation-delay:{.65+i*.16:.2f}s"><rect x="600" y="{y}" width="40" height="40" rx="12" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".35"/><g transform="translate(620,{y+20})" fill="none" stroke="{c}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{ic[k]}</g><text class="sg" x="656" y="{y+17}" font-size="17" fill="{TX}">{t}</text><text class="jb" x="656" y="{y+36}" font-size="12" fill="{MU}">{s}</text></g>'
    body=f'''{pb}
<circle cx="300" cy="300" r="240" fill="url(#warm)" filter="url(#b60)"/>
<g class="ap" style="animation-delay:.15s"><g class="bob"><g mask="url(#amH)"><g mask="url(#amV)"><image x="32" y="36" width="520" height="446" href="{art}" clip-path="url(#artC)" preserveAspectRatio="xMidYMid slice"/></g></g></g></g>
<g class="up" style="animation-delay:.2s"><text class="jbb" x="600" y="68" font-size="12" fill="{OR}" letter-spacing="2.1">// MY NINJA WAY</text>
<text class="sg" x="600" y="112" font-size="28" fill="{TX}" letter-spacing="-.4">Dream it — then ship it</text>
<text class="sgm" x="600" y="142" font-size="15" fill="{MU}">Full-stack developer turned entrepreneur, building products end to end.</text></g>
{r}
<g class="up" style="animation-delay:1.2s"><rect x="600" y="410" width="620" height="70" rx="14" fill="#fff" fill-opacity=".03" stroke="{LINE}"/><rect x="600" y="410" width="3.5" height="70" rx="1.75" fill="{OR}"/>
<text class="sg" x="624" y="441" font-size="17" fill="{TX}">“Build it. Ship it. Then build the next one.”</text>
<text class="jb" x="624" y="464" font-size="10.5" fill="{MU}" letter-spacing="1.5">NINDO · 49 REPOS · 20 STARS · 20 FOLLOWERS</text>
<g transform="translate(1190,445)">{shuriken(OR,.9)}</g></g>'''
    return svg(W,H,'My ninja way','Maddy stands with arms crossed beside three things he builds: web apps, mobile apps and AI tools.',d,'',body)

# ---------------------------------------------------------------- JUTSU STACK
TECH=[('TypeScript','typescript'),('JavaScript','javascript'),('React','react'),('Next.js','nextdotjs'),('Node.js','nodedotjs'),('MongoDB','mongodb'),
      ('MySQL','mysql'),('Tailwind','tailwindcss'),('HTML / CSS','html5'),('PHP','php'),('Kotlin','kotlin'),('Swift','swift'),
      ('Flutter','flutter'),('Python','python'),('AWS',None),('Vercel','vercel'),('Supabase','supabase'),('Docker','docker')]
def jutsu():
    W,H=1280,500
    pd,pb=panel(W,H,'j')
    d=pd+f'''<radialGradient id="orb"><stop offset="0" stop-color="#fff2c9" stop-opacity=".95"/><stop offset=".35" stop-color="{AM}" stop-opacity=".55"/><stop offset="1" stop-color="{OR}" stop-opacity="0"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffd27a" stop-opacity=".55"/><stop offset=".5" stop-color="{AM}" stop-opacity=".16"/><stop offset="1" stop-color="{AM}" stop-opacity="0"/></linearGradient>
<filter id="bb" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
{fade_mask('jm',0,0,400,500,left=.02,right=.82,top=.05,bottom=.86)}'''
    css='''.chip{animation:pop .55s cubic-bezier(.2,.8,.3,1.25) both;transform-box:fill-box;transform-origin:center}
@keyframes pop{0%{opacity:0;transform:translateX(-18px) scale(.82)}70%{opacity:1;transform:translateX(2px) scale(1.04)}100%{opacity:1;transform:none}}
.beam{animation:flick 4.5s ease-in-out infinite}
@keyframes flick{0%,100%{opacity:.5}18%{opacity:.78}30%{opacity:.42}52%{opacity:.82}70%{opacity:.55}}
.dust{animation:drift 7s linear infinite}
@keyframes drift{0%{transform:none;opacity:0}15%{opacity:.7}85%{opacity:.5}100%{transform:translate(42px,-26px);opacity:0}}'''
    art=jpg(f'{SRC}/jutsu.jpg',375,500,q=80)
    OX,OY=10+int(632*375/768),int(492*500/1024)  # orb position in card coords
    chips=''
    cw,ch,gx,gy=124,58,10,54; x0,y0=446,150
    for i,(name,slug) in enumerate(TECH):
        c,rw=i%6,i//6; x=x0+c*(cw+gx); y=y0+rw*(ch+gy)
        dpath,hexc=icon(slug) if slug else (None,'#ff9900')
        if slug=='nextdotjs' or slug=='vercel': hexc='#eef1f7'
        if dpath: g=f'<g transform="translate({x+14},{y+19}) scale(.83)"><path fill="{hexc}" d="{dpath}"/></g>'
        else: g=f'<text class="jbb" x="{x+24}" y="{y+34}" font-size="11" fill="{hexc}" text-anchor="middle">aws</text>'
        chips+=f'<g class="chip" style="animation-delay:{.5+i*.06:.2f}s"><rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="12" fill="{hexc}" fill-opacity=".07" stroke="{hexc}" stroke-opacity=".38"/>{g}<text class="jb" x="{x+46}" y="{y+34}" font-size="12.5" fill="{TX}">{name}</text></g>'
    beam=f'<polygon class="beam" points="{OX},{OY-6} 1280,40 1280,470 {OX},{OY+6}" fill="url(#beam)" filter="url(#bb)"/>'
    body=f'''{pb}
{beam}
<g class="ap" style="animation-delay:.1s"><g mask="url(#jmH)"><g mask="url(#jmV)"><image x="10" y="0" width="375" height="500" href="{art}" preserveAspectRatio="xMidYMid slice"/></g></g></g>
<circle cx="{OX}" cy="{OY}" r="34" fill="url(#orb)"><animate attributeName="r" values="30;38;30" dur="3.2s" repeatCount="indefinite"/></circle>
{particles(14,(OX+20,1200),(60,440),[AM,'#ffd27a',OR],'dust',7,1.8)}
<g class="up" style="animation-delay:.2s"><text class="jbb" x="446" y="58" font-size="12" fill="{AM}" letter-spacing="2.1">// JUTSU ARSENAL</text>
<text class="sg" x="446" y="100" font-size="28" fill="{TX}" letter-spacing="-.4">Tools I build with</text>
<text class="jb" x="1240" y="58" font-size="10.5" fill="{MU}" text-anchor="end" letter-spacing="1.8">{len(TECH)} TECHNIQUES MASTERED</text></g>
{chips}'''
    return svg(W,H,'Jutsu arsenal — my tech stack','Maddy holds a glowing orb whose light beam sweeps across his tech-stack chips.',d,css,body)

# ---------------------------------------------------------------- NINJA ID
def ninja_id():
    W,H=1280,620
    pd,pb=panel(W,H,'n')
    d=pd+f'''<linearGradient id="cardG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d1a24"/><stop offset="1" stop-color="#120f17"/></linearGradient>
<linearGradient id="cardE" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{OR}"/><stop offset="1" stop-color="{PU}"/></linearGradient>
<linearGradient id="foilG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="barO" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{OR}"/><stop offset="1" stop-color="{AM}"/></linearGradient>
<clipPath id="cardC"><rect x="38" y="148" width="310" height="440" rx="18"/></clipPath>
<clipPath id="picC"><rect x="125" y="198" width="136" height="150" rx="12"/></clipPath>'''
    css='''.swing{transform-box:view-box;transform-origin:193px -40px;animation:drop 2.5s cubic-bezier(.3,1,.5,1) both,sway 6.4s ease-in-out 2.5s infinite}
@keyframes drop{0%{transform:translateY(-660px)}22%{transform:none}42%{transform:rotate(3.2deg)}62%{transform:rotate(-2.1deg)}80%{transform:rotate(1.1deg)}100%{transform:rotate(0)}}
@keyframes sway{0%,100%{transform:rotate(-1.8deg)}50%{transform:rotate(1.8deg)}}
.foil{animation:foil 6.5s ease-in-out infinite}
@keyframes foil{0%{transform:translateX(-330px)}55%,100%{transform:translateX(370px)}}'''
    pic=jpg(f'{SRC}/portrait.jpg',136,150,q=82,focus=(.5,.15),scale=2)
    rnd=random.Random(5); bars=''; x=60
    while x<250:
        w=rnd.choice([1,1.5,2,3]); bars+=f'<rect x="{x}" y="532" width="{w}" height="18" fill="{TX}" fill-opacity=".75"/>'; x+=w+rnd.choice([1.5,2,2.5])
    strap=''.join(f'<text class="jbb" font-size="8.5" fill="#fff" fill-opacity=".8" letter-spacing="2" transform="translate(189,{-10+i*80}) rotate(90)">XDEV200 · SHINOBI</text>' for i in range(2))
    card=f'''<g class="swing">
<rect x="179" y="-40" width="28" height="186" fill="{RED}"/><rect x="179" y="-40" width="5" height="186" fill="#000" fill-opacity=".18"/>{strap}
<rect x="170" y="98" width="46" height="26" rx="6" fill="#9aa3b8"/><rect x="176" y="104" width="34" height="5" rx="2.5" fill="#5b6378"/>
<circle cx="193" cy="136" r="10" fill="none" stroke="#c2c8d6" stroke-width="4"/>
<rect x="38" y="148" width="310" height="440" rx="18" fill="url(#cardG)" stroke="url(#cardE)" stroke-width="1.6"/>
<g clip-path="url(#cardC)">
<rect x="38" y="148" width="310" height="34" fill="{OR}" fill-opacity=".1"/>
<g transform="translate(62,165)">{emblem(.5,OR,3)}</g><text class="jbb" x="80" y="169" font-size="10" fill="{OR}" letter-spacing="2">NINJA REGISTRATION</text><text class="jb" x="330" y="169" font-size="10" fill="{MU}" text-anchor="end">No. 0200</text>
<g transform="translate(78,262)">{shuriken(AM,.9)}</g>
<rect x="123" y="196" width="140" height="154" rx="13" fill="none" stroke="{OR}" stroke-width="2"/>
<image x="125" y="198" width="136" height="150" href="{pic}" clip-path="url(#picC)" preserveAspectRatio="xMidYMid slice"/>
<g transform="translate(300,250) rotate(-12)"><circle r="24" fill="none" stroke="{RED}" stroke-width="2" stroke-opacity=".8"/><circle r="19" fill="none" stroke="{RED}" stroke-width="1" stroke-opacity=".6"/><text class="jbb" y="-3" font-size="8" fill="{RED}" text-anchor="middle" letter-spacing="1">RANK</text><text class="sg" y="12" font-size="15" fill="{RED}" text-anchor="middle">S</text></g>
<text class="sg" x="193" y="384" font-size="25" fill="{TX}" text-anchor="middle">Madhusudan Das</text>
<text class="jbb" x="193" y="406" font-size="10.5" fill="{OR}" text-anchor="middle" letter-spacing="2.2">FULL-STACK SHINOBI</text>
<rect x="60" y="420" width="266" height="1" fill="#fff" fill-opacity=".08"/>
<g font-size="8.5" letter-spacing="1.4"><text class="jb" x="60" y="440" fill="{MU}">VILLAGE</text><text class="jb" x="200" y="440" fill="{MU}">BASE</text><text class="jb" x="60" y="480" fill="{MU}">CLASS</text><text class="jb" x="200" y="480" fill="{MU}">SINCE</text></g>
<g font-size="12"><text class="sgm" x="60" y="456" fill="{TX}">Jamshedpur</text><text class="sgm" x="200" y="456" fill="{TX}">India</text><text class="sgm" x="60" y="496" fill="{TX}">Founder · Builder</text><text class="sgm" x="200" y="496" fill="{TX}">2020</text></g>
{bars}
<circle cx="64" cy="570" r="3.5" fill="{GR}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle><text class="jbb" x="74" y="573" font-size="9" fill="{GR}" letter-spacing="1.5">ACTIVE DUTY</text><text class="jb" x="330" y="573" font-size="9.5" fill="{MU}" text-anchor="end">@Xdev200</text>
<rect class="foil" x="38" y="148" width="120" height="440" fill="url(#foilG)" transform="skewX(-18)"/>
</g></g>'''
    def count(x,y,final,steps,dur,pre=''):
        vals=[0]+[round(final*k/steps) for k in range(1,steps)]+[final]
        vals=sorted(set(vals)); n=len(vals); out=''
        for i,v in enumerate(vals):
            k0=i/n; k1=(i+1)/n; last=i==n-1
            if i==0: a=f'values="1;0" keyTimes="0;{k1:.4f}"'
            elif last: a=f'values="0;1" keyTimes="0;{k0:.4f}"'
            else: a=f'values="0;1;0" keyTimes="0;{k0:.4f};{k1:.4f}"'
            out+=f'<text class="sg" x="{x}" y="{y}" font-size="33" fill="{TX}" opacity="{1 if last else 0}">{v}{pre}<animate attributeName="opacity" calcMode="discrete" {a} dur="{dur}s" fill="freeze"/></text>'
        return out
    icons={'repo':'<path d="M-8-6h6l2 2h8v10h-16z"/>','star':'<path d="M0-8 2.4-2.6 8-2 3.8 1.8 5 7.6 0 4.8-5 7.6-3.8 1.8-8-2-2.4-2.6Z"/>',
           'follow':'<circle cx="-2" cy="-3" r="4"/><path d="M-9 8a7 7 0 0 1 14 0M7-4v6M4-1h6"/>','users':'<circle cx="0" cy="-4" r="4.5"/><path d="M-8 9a8 8 0 0 1 16 0"/>'}
    tiles=''
    for i,(v,l,c,ik) in enumerate([(49,'PUBLIC REPOS',OR,'repo'),(20,'STARS EARNED',AM,'star'),(16,'FOLLOWING',PU,'follow'),(20,'FOLLOWERS',GR,'users')]):
        x=420+i*208.5
        tiles+=f'<g class="up" style="animation-delay:{.7+i*.1:.1f}s"><rect x="{x}" y="134" width="194" height="94" rx="15" fill="#fff" fill-opacity=".03" stroke="{LINE}"/><rect x="{x+18}" y="148" width="20" height="3" rx="1.5" fill="{c}"/><g transform="translate({x+166},164)" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round" opacity=".9">{icons[ik]}</g>{count(x+18,196,v,5,2.2+i*.06)}<text class="jb" x="{x+18}" y="215" font-size="9.8" fill="{MU}" letter-spacing="1.5">{l}</text></g>'
    top=[('coding_panda_blog',2),('konnect2maddy',2),('Secure_Password_Manager',2),('Grow-Baby-Grow',1),('Hanoi',1),('ghost_trace',1)]
    mx=max(v for _,v in top); tb=''
    for i,(n_,v) in enumerate(top):
        y=300+i*34; w=max(14,200*v/mx)
        tb+=f'<text class="jb" x="440" y="{y+9}" font-size="11.5" fill="{TX}" fill-opacity=".85">{n_}</text><rect x="640" y="{y}" width="200" height="10" rx="5" fill="#fff" fill-opacity=".05"/><rect x="640" y="{y}" width="0" height="10" rx="5" fill="url(#barO)"><animate attributeName="width" values="0;{w:.0f}" dur="1.2s" begin="{1+i*.12:.2f}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/></rect><text class="jbb" x="{650+w:.0f}" y="{y+9}" font-size="11" fill="{TX}" opacity="0">{v}<animate attributeName="opacity" values="0;1" dur=".3s" begin="{2+i*.12:.2f}s" fill="freeze"/></text>'
    chakra=[(OR,'TAIJUTSU','React · Next.js · Node.js'),(PU,'GENJUTSU','Kotlin · Swift · Flutter apps'),(AM,'NINJUTSU','Python · AI tools · automation')]
    ck=''.join(f'<circle cx="918" cy="{338+i*52}" r="3" fill="{c}"/><text class="jbb" x="930" y="{342+i*52}" font-size="9.5" fill="{c}" letter-spacing="1.6">{t}</text><text class="sgm" x="930" y="{361+i*52}" font-size="12.5" fill="{TX}">{s}</text>' for i,(c,t,s) in enumerate(chakra))
    body=f'''{pb}
{card}
<g class="up" style="animation-delay:.3s"><text class="jbb" x="420" y="56" font-size="12" fill="{OR}" letter-spacing="2.1">// MISSION DASHBOARD</text>
<text class="sg" x="420" y="96" font-size="28" fill="{TX}" letter-spacing="-.4">Stats from the field</text>
<rect x="1082" y="52" width="158" height="28" rx="14" fill="{GR}" fill-opacity=".08" stroke="{GR}" stroke-opacity=".4"/><circle cx="1100" cy="66" r="3.5" fill="{GR}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle><text class="jbb" x="1112" y="70" font-size="10" fill="{GR}" letter-spacing="1.6">LIVE · NOV 2026</text></g>
{tiles}
<g class="up" style="animation-delay:1.1s"><rect x="420" y="250" width="456" height="296" rx="16" fill="#fff" fill-opacity=".03" stroke="{LINE}"/><text class="jbb" x="440" y="280" font-size="10" fill="{MU}" letter-spacing="1.8">TOP MISSIONS · STARS</text>{tb}<text class="jb" x="440" y="526" font-size="9.5" fill="{MU}">most-starred public repos · stars per repository</text></g>
<g class="up" style="animation-delay:1.3s"><rect x="896" y="276" width="344" height="196" rx="16" fill="#fff" fill-opacity=".03" stroke="{LINE}"/><text class="jbb" x="918" y="306" font-size="10" fill="{MU}" letter-spacing="1.8">CHAKRA NATURE</text>{ck}</g>
<g transform="translate(1210,560)" opacity=".7">{shuriken(PU,.8)}</g>'''
    return svg(W,H,'Ninja registration and mission dashboard','A swinging ninja ID badge for Madhusudan Das beside his GitHub stats, most-starred repos and skill areas.',d,css,body)

# ---------------------------------------------------------------- CONNECT
def connect():
    W,H=1280,440
    pd,pb=panel(W,H,'c',(RED,PU))
    d=pd+f'''<radialGradient id="rglow"><stop offset="0" stop-color="{RED}" stop-opacity=".2"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
<filter id="b50" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="50"/></filter>
{fade_mask('km',32,60,620,319,left=.04,right=.86,top=.05,bottom=.88)}<clipPath id="kC"><rect x="32" y="60" width="620" height="319" rx="18"/></clipPath>'''
    css='''.arrow{animation:nudge 1.9s ease-in-out infinite}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(5px)}}'''
    art=jpg(f'{SRC}/connect.jpg',620,319,q=80,focus=(.5,.3))
    xd,_=icon('x'); hd,hh=icon('hashnode'); dd,dh=icon('discord')
    li='<rect x="0" y="0" width="24" height="24" rx="4" fill="#0A66C2"/><text class="sg" x="12" y="18" font-size="15" fill="#fff" text-anchor="middle">in</text>'
    cards=[(BL,'LinkedIn','madhusudan-das-8552ba196',li),(TX,'X','@xdev_200',f'<path fill="#eef1f7" d="{xd}"/>'),
           (PU,'Hashnode','xdev.hashnode.dev',f'<path fill="{hh}" d="{hd}"/>'),(GR,'Discord','MADDY#6870',f'<path fill="{dh}" d="{dd}"/>')]
    cs=''
    for i,(c,t,h,g) in enumerate(cards):
        x=690+(i%2)*282; y=150+(i//2)*106
        cs+=f'<g class="up" style="animation-delay:{.8+i*.12:.2f}s"><rect x="{x}" y="{y}" width="268" height="92" rx="16" fill="#fff" fill-opacity=".03" stroke="{LINE}"/><rect x="{x}" y="{y}" width="268" height="92" rx="16" fill="none" stroke="{c}" stroke-opacity="0"><animate attributeName="stroke-opacity" values="0;.7;0;0" keyTimes="0;.06;.2;1" dur="7.2s" begin="{2+i*1.1:.1f}s" repeatCount="indefinite"/></rect><rect x="{x+16}" y="{y+22}" width="46" height="46" rx="13" fill="{c}" fill-opacity=".13"/><g transform="translate({x+27},{y+33})">{g}</g><text class="sg" x="{x+76}" y="{y+42}" font-size="16" fill="{TX}">{t}</text><text class="jb" x="{x+76}" y="{y+63}" font-size="11" fill="{MU}">{h}</text><g class="arrow" transform="translate({x+242},{y+46})" style="animation-delay:{i*.2:.1f}s"><path d="M-6 0h12M2-5l5 5-5 5" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g></g>'
    body=f'''{pb}
<circle cx="330" cy="230" r="230" fill="url(#rglow)" filter="url(#b50)"/>
<g class="ap" style="animation-delay:.2s"><g class="bob" style="animation-duration:8s"><g mask="url(#kmH)"><g mask="url(#kmV)"><image x="32" y="60" width="620" height="319" href="{art}" clip-path="url(#kC)" preserveAspectRatio="xMidYMid slice"/></g></g></g></g>
<g class="up" style="animation-delay:.3s"><text class="jbb" x="690" y="84" font-size="12" fill="{RED}" letter-spacing="2.1">// JOIN THE SQUAD</text>
<text class="sg" x="690" y="124" font-size="27" fill="{TX}" letter-spacing="-.4">Let’s build the next big thing</text></g>
{cs}
<g class="ap" style="animation-delay:1.6s"><circle cx="694" cy="398" r="3" fill="{OR}"/><text class="jb" x="706" y="402" font-size="11" fill="{MU}">Ping me on any channel · replies faster than a shadow clone</text></g>'''
    return svg(W,H,'Let’s connect','Maddy sits on temple steps between glowing code symbols, beside cards linking to LinkedIn, X, Hashnode and Discord.',d,css,body)

if __name__=='__main__':
    os.makedirs(OUT,exist_ok=True)
    for name,fn in [('hero',hero),('ninja-way',ninja_way),('jutsu-stack',jutsu),('ninja-id',ninja_id),('connect',connect)]:
        s=fn(); open(f'{OUT}/{name}.svg','w').write(s); print(name, len(s)//1024,'KB')
