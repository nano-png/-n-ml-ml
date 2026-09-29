import numpy as np, wave
SR=44100; DUR=13.0
track=np.zeros(int(SR*DUR))
rng=np.random.default_rng(7)
def add(sig,t,gain=1.0):
    i=int(t*SR); j=min(len(track),i+len(sig)); track[i:j]+=sig[:j-i]*gain
def env(n,a=0.005,r=None):
    t=np.arange(n)/SR; e=np.ones(n)
    ai=int(a*SR); e[:ai]=np.linspace(0,1,ai) if ai>0 else 1
    return e
def whoosh(d=0.55):
    n=int(d*SR); x=rng.standard_normal(n)
    # moving lowpass via cumulative smoothing with varying alpha
    y=np.zeros(n); a=np.linspace(0.02,0.25,n); a=np.concatenate([a[:n//2],a[:n//2][::-1],[0.02]*(n-2*(n//2))])
    for k in range(1,n): y[k]=y[k-1]+a[k]*(x[k]-y[k-1])
    e=np.sin(np.pi*np.linspace(0,1,n))**2
    return y*e*3
def pop(f0=700,f1=300,d=0.08):
    n=int(d*SR); t=np.arange(n)/SR; f=np.linspace(f0,f1,n)
    ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.exp(-t*45)
def tap():
    n=int(0.18*SR); t=np.arange(n)/SR
    click=rng.standard_normal(n)*np.exp(-t*400)*0.6
    thump=np.sin(2*np.pi*110*t)*np.exp(-t*25)
    blip=np.sin(2*np.pi*1760*t)*np.exp(-t*60)*0.4
    return click+thump+blip
def ding(f,d=0.7):
    n=int(d*SR); t=np.arange(n)/SR
    s=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)+0.12*np.sin(2*np.pi*3.01*f*t)
    e=np.exp(-t*6)*np.minimum(1,t/0.004); return s*e
def chime():
    return sum(ding(f,1.6)*g for f,g in [(1046.5,.6),(1318.5,.5),(1568,.45),(2093,.3)])
add(whoosh(),0.15,0.5)
for i in range(5): add(pop(),0.62+i*0.12,0.35)
add(whoosh(0.5),4.05,0.45)
add(whoosh(0.9),4.9,0.25)
add(tap(),6.0,0.9)
add(ding(2093,0.4),6.15,0.25)
add(whoosh(0.5),7.25,0.45)
for i,f in enumerate([1046.5,1174.7,1318.5,1568,2093]): add(ding(f),7.6+i*0.24,0.45)
add(whoosh(0.6),10.3,0.5)
add(chime(),10.5,0.55)
track/=np.max(np.abs(track))*1.12
# gentle fade out
fo=int(0.6*SR); track[-fo:]*=np.linspace(1,0,fo)
pcm=(track*32767).astype(np.int16)
with wave.open("reel1_sfx.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wav ok")
