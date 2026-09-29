import numpy as np, wave
SR=44100
rng=np.random.default_rng(7)
def whoosh(d=0.55):
    n=int(d*SR); x=rng.standard_normal(n); y=np.zeros(n)
    a=np.concatenate([np.linspace(0.02,0.25,n//2),np.linspace(0.25,0.02,n-n//2)])
    for k in range(1,n): y[k]=y[k-1]+a[k]*(x[k]-y[k-1])
    return y*np.sin(np.pi*np.linspace(0,1,n))**2*3
def pop(f0=700,f1=300,d=0.08):
    n=int(d*SR); t=np.arange(n)/SR; f=np.linspace(f0,f1,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*45)
def tap():
    n=int(0.18*SR); t=np.arange(n)/SR
    return rng.standard_normal(n)*np.exp(-t*400)*0.6+np.sin(2*np.pi*110*t)*np.exp(-t*25)+np.sin(2*np.pi*1760*t)*np.exp(-t*60)*0.4
def ding(f,d=0.7):
    n=int(d*SR); t=np.arange(n)/SR
    s=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)+0.12*np.sin(2*np.pi*3.01*f*t)
    return s*np.exp(-t*6)*np.minimum(1,t/0.004)
def chime(): return sum(ding(f,1.6)*g for f,g in [(1046.5,.6),(1318.5,.5),(1568,.45),(2093,.3)])
def tick(): 
    n=int(0.03*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*2400*t)*np.exp(-t*200)
def cash():
    return ding(2637,0.6)*0.6+ding(3136,0.6)*0.5
def build(events,dur,out):
    tr=np.zeros(int(SR*dur))
    for sig,t,g in events:
        i=int(t*SR); j=min(len(tr),i+len(sig)); tr[i:j]+=sig[:j-i]*g
    tr/=np.max(np.abs(tr))*1.12
    fo=int(0.6*SR); tr[-fo:]*=np.linspace(1,0,fo)
    with wave.open(out,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((tr*32767).astype(np.int16).tobytes())
