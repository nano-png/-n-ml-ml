import sys; sys.path.insert(0,'.')
from sfxlib import *
import numpy as np
DUR=51.5; N=int(SR*DUR)
def lp(x,a):
    y=np.zeros_like(x)
    for k in range(1,len(x)): y[k]=y[k-1]+a*(x[k]-y[k-1])
    return y
def env_ad(n,a,d): t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/d)
music=np.zeros(N); fx=np.zeros(N); amb=np.zeros(N)
def put(buf,sig,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if 0<=i<N: buf[i:j]+=sig[:j-i]*g
note=lambda m:440*2**((m-69)/12)
# ---------- PART 1 (0-22.6): suspense drone + heartbeat, archaic feel ----------
def drone(d,root=45):
    n=int(d*SR); t=np.arange(n)/SR
    lfo=0.6+0.4*np.sin(2*np.pi*0.18*t)
    s=(np.sin(2*np.pi*note(root)*t)+0.6*np.sin(2*np.pi*note(root+7)*t)+0.35*np.sin(2*np.pi*note(root+12)*t*1.002))*lfo
    e=np.minimum(1,t/1.5)*np.minimum(1,(d-t)/1.2)
    return s*e
put(music,drone(22.4,45),0.0,0.5)
def heart():
    n=int(0.5*SR); t=np.arange(n)/SR
    b=np.sin(2*np.pi*55*t)*np.exp(-t*22)
    return b+np.roll(b,int(0.18*SR))*0.7
for k in range(int(22/0.85)):
    tt=0.2+k*0.85
    if tt<22: put(music,heart(),tt,0.55)
# oud-like plucks (Hijaz flavour) during history scenes
hijaz=[57,58,61,62,64,65,68,69]  # A Bb C# D E F G# A
def pluck(m,d=0.9):
    n=int(d*SR); t=np.arange(n)/SR; f=note(m)
    s=np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*2*f*t)+0.25*np.sin(2*np.pi*3*f*t)
    return s*np.exp(-t*4.5)*np.minimum(1,t/0.003)
seq=[0,1,2,1,3,2,1,0, 4,3,2,3,1,2,1,0, 0,2,3,4,5,4,3,2]
t0=4.6
for i,s_ in enumerate(seq):
    tt=t0+i*0.72
    if tt<21.6: put(music,pluck(hijaz[s_]),tt,0.33)
# ---------- PART 2 (22.6-47.2): modern pulse 100bpm ----------
bpm=100; beat=60/bpm
def kick():
    n=int(0.35*SR); t=np.arange(n)/SR; f=55+100*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*8)
def hat():
    n=int(0.05*SR); x=rng.standard_normal(n); return (x-lp(x,0.3))*np.exp(-np.arange(n)/SR*70)*0.5
def clap():
    n=int(0.18*SR); t=np.arange(n)/SR; x=rng.standard_normal(n); return (x-lp(x,0.12))*np.exp(-t*20)*0.7
def padc(ms,d):
    n=int(d*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for m in ms:
        for det in (-0.15,0,0.15): s+=np.sin(2*np.pi*note(m)*(1+det/100)*t)
    return s*np.minimum(1,t/0.25)*np.minimum(1,(d-t)/0.3)/len(ms)/3
prog_ch=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]
bassn=[45,41,36,43]
tt=22.6; bi=0
while tt<47.2:
    barlen=4*beat
    put(music,padc(prog_ch[bi%4],barlen+0.2),tt,0.5)
    n=int(barlen*SR); x=np.arange(n)/SR
    put(music,np.sin(2*np.pi*note(bassn[bi%4])*x)*np.exp(-x*1.4)*0.7,tt,1)
    for k in range(4):
        b=tt+k*beat
        problem = 28.4<=b<33.4      # half-time, darker
        build = 32.0<=b<33.6        # riser zone
        if not problem or k in (0,):
            put(music,kick(),b,0.85)
        if not problem and k in (1,3): put(music,clap(),b,0.45)
        if not problem: put(music,hat(),b+beat/2,0.35)
    tt+=barlen; bi+=1
# ending chord
put(music,padc([57,60,64,69],4.2),47.2,0.8)
music=lp(music,0.4); music/=np.max(np.abs(music))
# ---------- SFX ----------
def impact(d=1.2,g=1):
    n=int(d*SR); t=np.arange(n)/SR; f=50+70*np.exp(-t*10)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3)+rng.standard_normal(n)*np.exp(-t*25)*0.5)*g
def rustle(d=0.45):
    n=int(d*SR); x=rng.standard_normal(n); y=x-lp(x,0.08)
    am=np.abs(lp(rng.standard_normal(n),0.002))*8
    return y*np.minimum(1,am)*np.sin(np.pi*np.linspace(0,1,n))*0.8
def scribble(d=0.45):
    n=int(d*SR); t=np.arange(n)/SR; x=rng.standard_normal(n); y=lp(x,0.25)-lp(x,0.04)
    return y*(0.5+0.5*np.sign(np.sin(2*np.pi*11*t)))*np.sin(np.pi*np.linspace(0,1,n))*2.2
def stamp():
    n=int(0.35*SR); t=np.arange(n)/SR
    return np.sin(2*np.pi*90*t)*np.exp(-t*18)+rng.standard_normal(n)*np.exp(-t*60)*0.6
def camelbell(f=780):
    n=int(1.4*SR); t=np.arange(n)/SR
    s=sum(a*np.sin(2*np.pi*f*r*t) for r,a in [(1,1),(2.76,.5),(5.4,.25),(8.9,.12)])
    return s*np.exp(-t*3)*np.minimum(1,t/0.002)
def tear(d=0.9):
    n=int(d*SR); x=rng.standard_normal(n); crack=(rng.random(n)<0.02)*rng.standard_normal(n)*4
    y=lp(x,0.5)-lp(x,0.06)+crack; return y*np.linspace(0.3,1,n)*np.minimum(1,(n-np.arange(n))/SR/0.08)*0.8
def riser(d=1.6):
    n=int(d*SR); t=np.arange(n)/SR; f=180+1500*(t/d)**2
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*0.4+lp(rng.standard_normal(n),0.25)*1.4)*(t/d)**1.6
def womp():
    n=int(0.9*SR); t=np.arange(n)/SR; f=np.linspace(240,110,n)
    return np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*0.25*np.exp(-t*2.5)
def notif():
    a=ding(1760,.18); b=ding(2349,.35); return np.concatenate([a[:int(.12*SR)],b])
def sparkle():
    s=np.zeros(int(1.2*SR))
    for k in range(9):
        d=ding(rng.uniform(2500,4200),0.35)*0.4; i=int(k*0.1*SR); s[i:i+len(d)]+=d[:len(s)-i]
    return s
def murmur(d,g=1):
    n=int(d*SR); x=np.zeros(n)
    for f0 in (300,550,800,1100):
        y=rng.standard_normal(n); y=lp(y,f0/SR*6)-lp(y,f0/SR*2)
        x+=y*(0.5+0.5*np.sin(2*np.pi*rng.uniform(2,5)*np.arange(n)/SR+rng.uniform(0,6)))
    e=np.minimum(1,np.arange(n)/SR/0.6)*np.minimum(1,(n-np.arange(n))/SR/0.6)
    return x*e*g
def wind(d):
    n=int(d*SR); y=lp(rng.standard_normal(n),0.01)*10
    return y*np.minimum(1,np.arange(n)/SR/1.0)*np.minimum(1,(n-np.arange(n))/SR/1.0)
# hook
put(fx,impact(1.4),0.05,1.0)
for k in range(10): put(fx,tick(),0.3+k*0.4,0.35)
for h in (0.8,1.8): put(fx,scribble(0.4),h,0.55)
put(fx,impact(0.9),2.6,0.4)
# map
put(fx,rustle(0.6),4.35,0.7); put(amb,wind(6.2),4.4,0.6)
put(fx,scribble(0.5),5.2,0.5)
for k in range(5): put(fx,camelbell(760+k*20),5.4+k*0.7,0.3)
put(fx,stamp(),6.6,0.8); put(fx,stamp(),6.9,0.5); put(fx,stamp(),8.2,0.6)
put(fx,whoosh(0.6),8.6,0.35)
# khans
put(fx,rustle(0.6),10.55,0.7)
put(fx,scribble(0.45),11.3,0.5)
put(amb,murmur(6.0,1.0),11.2,0.9)
for b in (12.4,13.4,14.4): put(fx,pop(800,450,.09),b,0.45)
put(fx,scribble(0.5),15.5,0.5)
# proverb
put(fx,rustle(0.5),17.35,0.6)
put(fx,impact(1.6),18.1,0.7); put(fx,camelbell(520),18.15,0.4)
put(fx,scribble(0.5),18.9,0.55)
# tear transition
put(fx,tear(0.95),21.65,0.9); put(fx,impact(1.0),22.55,0.6)
# modern
put(fx,whoosh(0.6),22.7,0.4); put(fx,whoosh(0.8),23.2,0.45)
put(fx,pop(1200,500,.12),23.9,0.5); put(fx,stamp(),24.2,0.4)
put(fx,pop(),24.5,0.35); put(fx,pop(500,250),24.9,0.3)
put(fx,scribble(0.45),26.4,0.5); put(fx,notif(),26.2,0.45)
# problem
put(fx,womp(),28.5,0.6)
for i in range(10): put(fx,pop(900,600,.05),29.0+i*0.12,0.25)
for i in range(10): put(fx,tick(),30.6+i*0.1,0.35)
put(fx,ding(1568,.5),30.9,0.4)
put(fx,scribble(0.5),31.9,0.5)
put(fx,riser(1.6),32.0,0.7)
# solution
put(fx,impact(1.4),33.6,1.0); put(fx,sparkle(),33.7,0.6)
put(fx,whoosh(0.6),34.0,0.4)
put(fx,whoosh(0.9),35.3,0.3); put(fx,tap(),36.4,1.0); put(fx,ding(2093,.5),36.55,0.35)
for i,m in enumerate([1046.5,1174.7,1318.5,1568,2093,2637]): put(fx,ding(m,.6),37.0+i*0.18,0.28)
# info
put(fx,pop(900,400,.12),40.6,0.5); put(fx,scribble(0.5),41.9,0.5)
put(fx,whoosh(0.5),42.8,0.35); put(fx,whoosh(0.5),43.6,0.35); put(fx,ding(1318.5,.6),43.7,0.4)
put(fx,scribble(0.5),45.3,0.5)
# end
put(fx,whoosh(0.7),47.1,0.5); put(fx,chime(),47.3,0.7)
# ---- insert 5s cashier scene at 40.4 ----
CA=40.4; L=5.0; ci=int(CA*SR); Ln=int(L*SR)
seg_music=music[int((CA-L)*SR):ci].copy()
seg_fx=np.zeros(Ln); seg_amb=np.zeros(Ln)
def sp(buf,sig,t,g=1.0):
    i=int(t*SR); j=min(Ln,i+len(sig))
    if 0<=i<Ln: buf[i:j]+=sig[:j-i]*g
sp(seg_fx,whoosh(0.6),0.0,0.45); sp(seg_fx,scribble(0.5),0.7,0.5)
sp(seg_fx,whoosh(0.7),0.3,0.4); sp(seg_fx,stamp(),0.85,0.6); sp(seg_fx,stamp(),1.0,0.5)
sp(seg_fx,impact(0.8),1.5,0.5); sp(seg_fx,stamp(),1.55,0.8)
sp(seg_fx,scribble(0.65),2.0,0.6); sp(seg_fx,pop(900,500,.1),2.5,0.45)
sp(seg_fx,ding(2637,0.6)*0.6+ding(3136,0.6)*0.5,2.9,0.35); sp(seg_fx,scribble(0.45),3.4,0.5)
sp(seg_amb,murmur(5.0,0.8),0.0,0.6)
music=np.concatenate([music[:ci],seg_music,music[ci:]])
fx=np.concatenate([fx[:ci],seg_fx,fx[ci:]])
amb=np.concatenate([amb[:ci],seg_amb,amb[ci:]])
N=len(music)
fx/=np.max(np.abs(fx)); amb/=max(1e-9,np.max(np.abs(amb)))
mix=music*0.34+amb*0.18+fx*0.85
fo=int(1.2*SR); mix[-fo:]*=np.linspace(1,0,fo)
mix/=np.max(np.abs(mix))*1.08
with wave.open("reel7_sfx.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print("ok")
