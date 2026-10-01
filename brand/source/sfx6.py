import sys; sys.path.insert(0,'.')
from sfxlib import *
import numpy as np
DUR=36.5; N=int(SR*DUR)
def lp(x,a):
    y=np.zeros_like(x); 
    for k in range(1,len(x)): y[k]=y[k-1]+a*(x[k]-y[k-1])
    return y
def note(f): return 440*2**((f-69)/12)
# ---------- music: lofi 84 bpm, Am F C G ----------
bpm=84; beat=60/bpm; bar=4*beat
music=np.zeros(N)
def place(sig,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); 
    if i<N: music[i:j]+=sig[:j-i]*g
def pad(midis,d):
    n=int(d*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for m in midis:
        f=note(m)
        for det in (-0.12,0.0,0.12):
            s+=np.sin(2*np.pi*f*(1+det/100)*t)+0.3*np.sin(2*np.pi*2*f*t)
    env=np.minimum(1,t/0.35)*np.minimum(1,(d-t)/0.4)
    return s*env/len(midis)/3
def kick():
    n=int(0.35*SR); t=np.arange(n)/SR; f=60+90*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def hat():
    n=int(0.06*SR); x=rng.standard_normal(n); x=x-lp(x,0.3); return x*np.exp(-np.arange(n)/SR*60)*0.5
def snare():
    n=int(0.2*SR); t=np.arange(n)/SR; x=rng.standard_normal(n)
    return (x-lp(x,0.15))*np.exp(-t*18)*0.6+np.sin(2*np.pi*190*t)*np.exp(-t*25)*0.4
chords=[[57,60,64],[53,57,60],[48,52,55,60],[55,59,62]]  # Am F C G
bass=[45,41,36,43]
start=3.4
t0=start; bi=0
while t0<DUR-1.5:
    ch=chords[bi%4]; place(pad(ch,bar+0.3),t0,0.55)
    bn=int(bar*SR); tt=np.arange(bn)/SR; place(np.sin(2*np.pi*note(bass[bi%4])*tt)*np.exp(-tt*1.2)*0.6,t0,1)
    for k in range(4):
        bt=t0+k*beat
        drums = not (29.2<=bt<33.6) and bt>=8.4  # drums from scene C, break in warning
        if drums:
            if k in (0,2): place(kick(),bt,0.9)
            if k in (1,3): place(snare(),bt,0.5)
            place(hat(),bt+beat/2,0.35); place(hat(),bt,0.25)
    t0+=bar; bi+=1
music=lp(music,0.35)
# title intro drone 0-3.4
n=int(3.4*SR); tt=np.arange(n)/SR
music[:n]+=(np.sin(2*np.pi*110*tt)+0.5*np.sin(2*np.pi*164.8*tt))*np.minimum(1,tt/1.5)*0.25
# fade out end
fo=int(1.5*SR); music[-fo:]*=np.linspace(1,0,fo)
music/=np.max(np.abs(music))
# ---------- ambience ----------
amb=np.zeros(N)
def seg(a,b): return int(a*SR),int(b*SR)
i,j=seg(3.6,8.4); n=j-i; street=lp(rng.standard_normal(n),0.02)*6
env=np.minimum(1,np.arange(n)/SR/0.4)*np.minimum(1,(n-np.arange(n))/SR/0.4); amb[i:j]+=street*env*0.5
def crowd(d,g):
    n=int(d*SR); x=np.zeros(n)
    for f0 in (300,550,800,1100):
        y=rng.standard_normal(n); y=lp(y,f0/SR*6)-lp(y,f0/SR*2)
        am=0.5+0.5*np.sin(2*np.pi*rng.uniform(2,5)*np.arange(n)/SR+rng.uniform(0,6))
        x+=y*am
    e=np.minimum(1,np.arange(n)/SR/0.6)*np.minimum(1,(n-np.arange(n))/SR/0.6)
    return x*e*g
i,_=seg(6.2,0); c=crowd(2.2,1.2); amb[i:i+len(c)]+=c
i,_=seg(24.4,0); c=crowd(4.8,1.0)*np.linspace(0.3,1.4,int(4.8*SR)); amb[i:i+len(c)]+=c
amb/=max(1e-9,np.max(np.abs(amb)))
# ---------- SFX ----------
def riser(d=1.4):
    n=int(d*SR); t=np.arange(n)/SR; f=200+1400*(t/d)**2
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*0.4+lp(rng.standard_normal(n),0.2)*1.5)*(t/d)**1.5
def impact():
    n=int(1.2*SR); t=np.arange(n)/SR; f=55+60*np.exp(-t*12)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3)+rng.standard_normal(n)*np.exp(-t*20)*0.5
def doorbell(): return np.concatenate([ding(1318.5,0.45)[:int(.32*SR)],ding(1046.5,0.9)])
def register(): return np.concatenate([rng.standard_normal(int(.05*SR))*0.4,np.zeros(int(.03*SR))])[:]
def notif():
    a=ding(1760,.18); b=ding(2349,.35); return np.concatenate([a[:int(.12*SR)],b])
def flip():
    n=int(0.22*SR); x=rng.standard_normal(n); t=np.arange(n)/SR
    return (lp(x,0.4)-lp(x,0.05))*np.exp(-t*14)*2
def type_click(): 
    n=int(0.025*SR); t=np.arange(n)/SR; return rng.standard_normal(n)*np.exp(-t*300)*0.5
def warn():
    n=int(0.6*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*440*t)*0.6+np.sin(2*np.pi*466*t)*0.6)*np.exp(-t*4)
def sparkle():
    s=np.zeros(int(1.0*SR))
    for k in range(8):
        d=ding(rng.uniform(2500,4200),0.35)*0.4; i=int(k*0.09*SR); s[i:i+len(d)]+=d[:len(s)-i]
    return s
C5=[1046.5,1174.7,1318.5,1568,2093]
fx=np.zeros(N)
def F(sig,t,g):
    i=int(t*SR); j=min(N,i+len(sig)); fx[i:j]+=sig[:j-i]*g
for k in range(16): F(type_click(),0.45+k*0.07,0.5)         # title typing
F(whoosh(0.7),3.4,0.5)
F(whoosh(1.1),5.6,0.45)                                    # camera pan
F(impact(),8.35,0.6)
for a in (8.6,10.0,11.4):
    F(pop(800,500,.08),a+0.1,0.35)                          # speech
    F(ding(2637,0.5)*0.4+ding(3136,0.5)*0.3,a+0.55,0.5)     # register ka-ching
    F(doorbell(),a+1.0,0.45)                                 # door bell on leaving
F(notif(),13.5,0.6)
for k in range(16): F(type_click(),13.7+k*0.075,0.5)
F(pop(),15.0,0.35); F(pop(500,250),15.3,0.3)
F(riser(1.6),17.4,0.6)
F(impact(),19.0,0.9); F(sparkle(),19.2,0.6)
F(whoosh(0.9),20.4,0.3); F(tap(),21.5,1.0); F(ding(2093,.5),21.65,0.35)
for k,m in enumerate(C5): F(ding(m),21.9+k*0.14,0.3)
for t0 in (24.2,25.6,27.0):
    F(flip(),t0,0.7); F(cash(),t0+0.9,0.45)
F(warn(),29.25,0.6); F(impact(),30.4,0.55)
F(whoosh(0.7),33.6,0.5); F(chime(),33.8,0.6)
fx/=np.max(np.abs(fx))
mix=music*0.32+amb*0.22+fx*0.85
mix/=np.max(np.abs(mix))*1.08
with wave.open("reel6_sfx.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print("ok")
