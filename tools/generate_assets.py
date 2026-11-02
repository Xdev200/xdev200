import os, math
import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','assets')
BG='#0b0f1e'; PANEL='#121a33'; BORDER='#2a3560'; OR='#ff7a1a'; RED='#e2383f'; PU='#9d6bff'; TX='#e8ecf8'; MU='#8a94b8'
SANS="'Segoe UI', Ubuntu, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO="ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

def defs():
    return f'''<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0f1e"/><stop offset="1" stop-color="#151036"/></linearGradient>
<linearGradient id="fire" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{OR}"/><stop offset=".55" stop-color="{RED}"/><stop offset="1" stop-color="{PU}"/></linearGradient>
<linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16203f"/><stop offset="1" stop-color="#0f1530"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'''

# original motifs
def swirl(cx,cy,r,color=OR,sw=3,cls='spin'):
    # Archimedean spiral path
    pts=[]
    for i in range(0,200):
        t=i/199*4*math.pi; rr=r*i/199
        pts.append(f"{cx+rr*math.cos(t):.1f},{cy+rr*math.sin(t):.1f}")
    return f'<g class="{cls}" style="transform-origin:{cx}px {cy}px"><circle cx="{cx}" cy="{cy}" r="{r+6}" fill="none" stroke="{color}" stroke-opacity=".25" stroke-width="1.5"/><polyline filter="url(#glow)" points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/></g>'

def shuriken(cx,cy,s,color=MU,cls='spin'):
    p=f"M0,-{s} L{s*.22},-{s*.22} L{s},0 L{s*.22},{s*.22} L0,{s} L-{s*.22},{s*.22} L-{s},0 L-{s*.22},-{s*.22} Z"
    return f'<g transform="translate({cx},{cy})"><g class="{cls}"><path d="{p}" fill="{color}"/><circle r="{s*.16}" fill="{BG}"/></g></g>'

def leaf(x,y,s,color,delay,dur=9):
    return f'<g transform="translate({x},{y})"><path class="leaf" style="animation-delay:{delay}s;animation-duration:{dur}s" d="M0,0 C{s*.6},-{s*.5} {s*1.2},-{s*.2} {s*1.4},0 C{s*1.2},{s*.2} {s*.6},{s*.5} 0,0 Z" fill="{color}" opacity=".0"/></g>'

def emblem(cx,cy,r,color=TX):
    # custom symbol: angle brackets around an X-shaped flame mark inside a ring
    return f'''<g transform="translate({cx},{cy})" fill="none" stroke="{color}" stroke-width="{r*.12:.1f}" stroke-linecap="round" stroke-linejoin="round">
<circle r="{r}" stroke-opacity=".9"/>
<path d="M{-r*.75:.1f},{-r*.35:.1f} L{-r*1.05:.1f},0 L{-r*.75:.1f},{r*.35:.1f}"/><path d="M{r*.75:.1f},{-r*.35:.1f} L{r*1.05:.1f},0 L{r*.75:.1f},{r*.35:.1f}"/>
<path d="M{-r*.4:.1f},{-r*.45:.1f} L{r*.4:.1f},{r*.45:.1f} M{r*.4:.1f},{-r*.45:.1f} L{-r*.4:.1f},{r*.45:.1f}"/>
<circle cy="{-r*.62:.1f}" r="{r*.08:.1f}" fill="{color}" stroke="none"/></g>'''

def headband(x,y,w,h):
    return f'''<g transform="translate({x},{y})"><rect x="-60" y="{h*.3:.0f}" width="{w+120}" height="{h*.4:.0f}" rx="4" fill="{RED}" opacity=".85"/>
<rect width="{w}" height="{h}" rx="8" fill="url(#plate)" stroke="#c8cfe6" stroke-width="2"/>
<circle cx="10" cy="10" r="3" fill="#7d86a8"/><circle cx="{w-10}" cy="10" r="3" fill="#7d86a8"/><circle cx="10" cy="{h-10}" r="3" fill="#7d86a8"/><circle cx="{w-10}" cy="{h-10}" r="3" fill="#7d86a8"/>
{emblem(w/2,h/2,h*.3,'#2b3355')}
<clipPath id="plateclip"><rect width="{w}" height="{h}" rx="8"/></clipPath><g clip-path="url(#plateclip)"><rect class="shine" width="30" height="{h}" fill="#fff" opacity=".25"/></g></g>'''

STYLE=f'''<style>
.spin{{animation:spin 8s linear infinite;transform-box:fill-box;transform-origin:center}}
.spinr{{animation:spin 14s linear infinite reverse;transform-box:fill-box;transform-origin:center}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.twinkle{{animation:tw 3s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
.leaf{{animation:drift 9s linear infinite}}
@keyframes drift{{0%{{opacity:0;transform:translate(0,0) rotate(0)}}10%{{opacity:.9}}90%{{opacity:.8}}100%{{opacity:0;transform:translate(-260px,190px) rotate(540deg)}}}}
.fadeup{{animation:fu .9s ease-out both}}
@keyframes fu{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
.pulse{{animation:pl 2.4s ease-in-out infinite}}
@keyframes pl{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
.shine{{animation:sh 4s ease-in-out infinite}}
@keyframes sh{{0%{{transform:translateX(-40px)}}60%,100%{{transform:translateX(420px)}}}}
.t{{font-family:{SANS};fill:{TX}}}
.m{{font-family:{MONO};fill:{MU}}}
</style>'''

def svg(w,h,body,title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">
<title>{title}</title>
<defs>{defs()}<linearGradient id="plate" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eef1fa"/><stop offset="1" stop-color="#9aa3c2"/></linearGradient></defs>
{STYLE}
{body}
</svg>'''

def frame(w,h,ep,label):
    return f'''<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="url(#panel)" stroke="{BORDER}" stroke-width="2"/>
<rect x="1" y="1" width="{w-2}" height="4" rx="2" fill="url(#fire)"/>
<text x="32" y="40" class="m" font-size="13" letter-spacing="2" fill="{OR}" style="fill:{OR}">{ep} // {label}</text>'''

def stars(w,h,n=40,seed=7):
    import random; r=random.Random(seed); out=[]
    for i in range(n):
        out.append(f'<circle class="twinkle" style="animation-delay:{r.random()*3:.2f}s" cx="{r.random()*w:.0f}" cy="{r.random()*h:.0f}" r="{r.choice([.8,1.1,1.5])}" fill="#fff"/>')
    return '\n'.join(out)

# 1 HERO
W,H=1000,340
hero=f'''<rect width="{W}" height="{H}" rx="20" fill="url(#bg)"/>
{stars(W,H,55)}
<circle cx="820" cy="120" r="150" fill="{PU}" opacity=".08"/><circle cx="820" cy="120" r="95" fill="{OR}" opacity=".07"/>
{swirl(820,135,62,OR,4,'spin')}
{shuriken(930,270,18,'#5b6690','spinr')}{shuriken(690,60,11,'#5b6690','spin')}
{leaf(980,20,26,OR,0)}{leaf(900,-10,20,'#2fd48a',2.5)}{leaf(760,0,22,PU,5)}{leaf(620,-20,18,OR,6.8)}
<rect x="0" y="0" width="{W}" height="6" rx="3" fill="url(#fire)"/>
<g class="fadeup"><rect x="48" y="44" width="300" height="28" rx="14" fill="{RED}" opacity=".18" stroke="{RED}" stroke-opacity=".6"/>
<text x="62" y="63" class="m" font-size="13" letter-spacing="2" style="fill:#ffb08a">EPISODE 01 · THE ORIGIN ARC</text></g>
<g class="fadeup" style="animation-delay:.25s"><text x="48" y="138" class="t" font-size="50" font-weight="800">Madhusudan Das</text>
<text x="48" y="182" class="t" font-size="30" font-weight="700" style="fill:url(#fire)" fill="url(#fire)">aka Maddy</text></g>
<g class="fadeup" style="animation-delay:.5s"><text x="48" y="226" class="t" font-size="19" style="fill:#c9d0ea">Developer turned Entrepreneur · Full-Stack &amp; Mobile</text></g>
<g class="fadeup" style="animation-delay:.75s"><path transform="translate(48,250)" d="M8,0 C3.6,0 0,3.6 0,8 C0,14 8,22 8,22 C8,22 16,14 16,8 C16,3.6 12.4,0 8,0 Z" fill="{OR}"/><circle cx="56" cy="258" r="3" fill="{BG}"/>
<text x="74" y="266" class="m" font-size="15">Jamshedpur, India</text>
<text x="250" y="266" class="m" font-size="15" style="fill:{PU}">github.com/Xdev200</text></g>
{headband(700,232,240,62)}
<text x="48" y="315" class="m pulse" font-size="12" letter-spacing="1.5">&#9654; NOW PLAYING — next episode loading…</text>'''
open(f'{OUT}/hero.svg','w').write(svg(W,H,hero,"Madhusudan Das (Maddy) — Developer turned Entrepreneur, Full-Stack and Mobile, Jamshedpur"))

# 2 NINJA WAY
W,H=1000,330
items=[('Web apps that feel alive','MERN and Next.js builds: dashboards, SaaS, marketing sites',OR,'web'),
       ('Mobile apps in both villages','Kotlin for Android, Swift / SwiftUI for iOS, Flutter for both',RED,'mob'),
       ('AI tools that do real work','Agents, automations and data tools that save hours, not demos',PU,'ai')]
def icon(kind,x,y,c):
    if kind=='web': return f'<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="2.2"><rect x="2" y="4" width="28" height="22" rx="3"/><path d="M2,10 H30"/><path d="M11,16 L8,19 L11,22 M21,16 L24,19 L21,22"/></g>'
    if kind=='mob': return f'<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="2.2"><rect x="8" y="1" width="16" height="28" rx="3"/><circle cx="16" cy="24" r="1.4" fill="{c}"/></g>'
    return f'<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="2.2"><path d="M16,2 L19,12 L29,15 L19,18 L16,28 L13,18 L3,15 L13,12 Z"/></g>'
rows=''
for i,(a,b,c,k) in enumerate(items):
    y=110+i*62
    rows+=f'''<g class="fadeup" style="animation-delay:{.2+i*.25}s"><rect x="360" y="{y-28}" width="46" height="46" rx="12" fill="{c}" opacity=".14" stroke="{c}" stroke-opacity=".5"/>{icon(k,367,y-21,c)}
<text x="424" y="{y-4}" class="t" font-size="18" font-weight="700">{a}</text><text x="424" y="{y+16}" class="m" font-size="13">{b}</text></g>'''
# original scroll motif
scroll=f'''<g transform="translate(60,70)">
<rect x="10" y="18" width="220" height="200" rx="6" fill="#efe3c6"/>
<g opacity=".55" stroke="#8c6b3f" stroke-width="2" stroke-linecap="round">
<path d="M40,60 H200"/><path d="M40,85 H180"/><path d="M40,110 H195"/><path d="M40,135 H160"/><path d="M40,160 H190"/></g>
<g transform="translate(120,190)">{emblem(0,0,18,RED)}</g>
<rect x="0" y="6" width="240" height="20" rx="10" fill="#7a3b1f"/><rect x="0" y="210" width="240" height="20" rx="10" fill="#7a3b1f"/>
<rect class="pulse" x="-6" y="10" width="10" height="12" rx="3" fill="{OR}"/><rect class="pulse" x="236" y="214" width="10" height="12" rx="3" fill="{OR}"/>
<text x="120" y="45" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="3" fill="#7a3b1f">SECRET SCROLL</text></g>
{shuriken(720,50,12,'#5b6690','spin')}'''
nw=f'''{frame(W,H,'EP.02','MY NINJA WAY')}
{scroll}
<text x="360" y="62" class="t" font-size="28" font-weight="800">Code it. Ship it. Own it.</text>
{rows}
<g class="fadeup" style="animation-delay:1s"><rect x="360" y="276" width="600" height="34" rx="10" fill="{RED}" opacity=".12" stroke="{RED}" stroke-opacity=".5"/>
<text x="378" y="298" class="t" font-size="14" font-style="italic" style="fill:#ffd2bf">“My ninja code: no shortcut is worth a broken build.”</text></g>'''
open(f'{OUT}/ninja-way.svg','w').write(svg(W,H,nw,"My ninja way — web apps, mobile apps and AI tools"))

# 3 JUTSU STACK
tech=[('TypeScript','TS','#3178c6'),('JavaScript','JS','#f7df1e'),('React','Re','#61dafb'),('Next.js','N','#e8ecf8'),('Node.js','Nd','#5fa04e'),('MongoDB','Mg','#47a248'),
('MySQL','My','#4479a1'),('Tailwind','Tw','#38bdf8'),('HTML / CSS','H5','#e34f26'),('PHP','Ph','#8892bf'),('Kotlin','Kt','#a97bff'),('Swift','Sw','#f05138'),
('Dart / Flutter','Fl','#02569b'),('Python','Py','#ffd43b'),('AWS','AW','#ff9900'),('Vercel','▲','#e8ecf8'),('Supabase','Sb','#3ecf8e'),('Docker','Dk','#2496ed')]
W,H=1000,420
tiles=''
for i,(n,ab,c) in enumerate(tech):
    col,row=i%6,i//6
    x=40+col*155; y=96+row*100
    tiles+=f'''<g class="fadeup" style="animation-delay:{i*.06:.2f}s"><rect x="{x}" y="{y}" width="140" height="82" rx="14" fill="#0f1530" stroke="{c}" stroke-opacity=".55" stroke-width="1.5"/>
<rect x="{x+14}" y="{y+14}" width="34" height="34" rx="9" fill="{c}" opacity=".18"/><text x="{x+31}" y="{y+37}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" fill="{c}">{ab}</text>
<text x="{x+14}" y="{y+70}" class="t" font-size="14" font-weight="600">{n}</text></g>'''
js=f'''{frame(W,H,'EP.03','JUTSU ARSENAL')}
<text x="32" y="76" class="t" font-size="26" font-weight="800">Tools I train with</text>
<text x="968" y="40" text-anchor="end" class="m" font-size="12" letter-spacing="1.5">{len(tech)} TECHNIQUES MASTERED</text>
{shuriken(940,72,14,OR,'spin')}
{tiles}'''
open(f'{OUT}/jutsu-stack.svg','w').write(svg(W,H,js,"Jutsu arsenal — tech stack"))

# 4 NINJA ID
langs=[('TypeScript',8,'#3178c6'),('HTML',6,'#e34f26'),('JavaScript',5,'#f7df1e'),('Kotlin',4,'#a97bff'),('Python',2,'#ffd43b'),('Dart',1,'#02569b')]
W,H=1000,440
mx=max(v for _,v,_ in langs)
bars=''
for i,(n,v,c) in enumerate(langs):
    y=260+i*26
    bw=300*v/mx
    bars+=f'''<text x="420" y="{y+11}" class="m" font-size="13">{n}</text><rect x="530" y="{y}" width="300" height="12" rx="6" fill="#1c2546"/>
<rect x="530" y="{y}" width="{bw:.0f}" height="12" rx="6" fill="{c}"><animate attributeName="width" from="0" to="{bw:.0f}" dur="1.4s" begin="{i*.15:.2f}s" fill="freeze"/></rect>
<text x="{540+300}" y="{y+11}" class="m" font-size="12">{v} repo{'s' if v>1 else ''}</text>'''
stats=[('49','PUBLIC REPOS',OR),('20','FOLLOWERS',RED),('16','FOLLOWING',PU),('2020','JOINED',"#2fd48a")]
sb=''
for i,(v,l,c) in enumerate(stats):
    x=420+i*140
    sb+=f'''<g class="fadeup" style="animation-delay:{.2+i*.15}s"><rect x="{x}" y="120" width="126" height="88" rx="14" fill="#0f1530" stroke="{c}" stroke-opacity=".5"/>
<text x="{x+63}" y="165" text-anchor="middle" class="t" font-size="30" font-weight="800" style="fill:{c}">{v}</text><text x="{x+63}" y="192" text-anchor="middle" class="m" font-size="11" letter-spacing="1.5">{l}</text></g>'''
card=f'''<g transform="translate(190,60)"><g style="animation:sway 5s ease-in-out infinite;transform-origin:0px 0px">
<path d="M-34,-12 L-12,20 M34,-12 L12,20" stroke="{RED}" stroke-width="10" stroke-linecap="round"/>
<rect x="-14" y="14" width="28" height="18" rx="4" fill="#9aa3c2"/>
<rect x="-130" y="30" width="260" height="330" rx="18" fill="#f3efe6"/>
<rect x="-130" y="30" width="260" height="64" rx="18" fill="url(#fire)"/><rect x="-130" y="76" width="260" height="18" fill="url(#fire)"/>
<text x="0" y="60" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="3" fill="#fff">SHINOBI DEV LICENSE</text>
<text x="0" y="80" text-anchor="middle" font-family="{MONO}" font-size="10" letter-spacing="2" fill="#ffe7d6">VILLAGE OF JAMSHEDPUR</text>
<circle cx="0" cy="150" r="46" fill="#1a2245"/>{emblem(0,150,26,OR)}
<text x="0" y="230" text-anchor="middle" font-family="{SANS}" font-size="22" font-weight="800" fill="#1a2245">Madhusudan Das</text>
<text x="0" y="252" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#5b6690">@Xdev200</text>
<g font-family="{MONO}" font-size="11" fill="#1a2245"><text x="-108" y="290">RANK</text><text x="108" y="290" text-anchor="end" font-weight="700" fill="{RED}">JŌNIN · FULL-STACK</text>
<text x="-108" y="312">CLASS</text><text x="108" y="312" text-anchor="end" font-weight="700">FOUNDER / BUILDER</text>
<text x="-108" y="334">ID</text><text x="108" y="334" text-anchor="end" font-weight="700">XD-200-2020</text></g>
</g></g>
<style>@keyframes sway{{0%,100%{{transform:rotate(-2.5deg)}}50%{{transform:rotate(2.5deg)}}}}</style>'''
nid=f'''{frame(W,H,'EP.04','NINJA REGISTRATION')}
{card}
<text x="420" y="94" class="t" font-size="26" font-weight="800">Mission stats from the field</text>
{sb}
<text x="420" y="246" class="m" font-size="12" letter-spacing="1.5" style="fill:{OR}">CHAKRA NATURE · TOP LANGUAGES</text>
{bars}
<text x="968" y="425" text-anchor="end" class="m" font-size="10">snapshot Nov 2026 · live numbers below</text>'''
open(f'{OUT}/ninja-id.svg','w').write(svg(W,H,nid,"Ninja registration card and GitHub stats for Xdev200"))

# 7 CONNECT
W,H=1000,230
links=[('LinkedIn','in/madhusudan-das-8552ba196','#0a66c2'),('X','@xdev_200','#e8ecf8'),('Hashnode','xdev.hashnode.dev','#2962ff'),('Discord','MADDY#6870','#5865f2')]
lk=''
for i,(n,h,c) in enumerate(links):
    x=40+i*232
    lk+=f'''<g class="fadeup" style="animation-delay:{.15*i}s"><rect x="{x}" y="120" width="216" height="74" rx="14" fill="#0f1530" stroke="{c}" stroke-opacity=".6"/>
<circle cx="{x+30}" cy="157" r="12" fill="{c}" opacity=".85"/><text x="{x+52}" y="152" class="t" font-size="16" font-weight="700">{n}</text><text x="{x+52}" y="172" class="m" font-size="10">{h}</text></g>'''
cn=f'''{frame(W,H,'EP.07','JOIN THE SQUAD')}
{stars(W,H,25,3)}
<text x="32" y="86" class="t" font-size="28" font-weight="800">Let’s build the next episode together</text>
{swirl(930,78,26,PU,3,'spin')}
{lk}'''
open(f'{OUT}/connect.svg','w').write(svg(W,H,cn,"Connect with Maddy — LinkedIn, X, Hashnode, Discord"))
print('ok')
