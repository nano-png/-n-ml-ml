# Reel 08 sound design: new palette (no whoosh/pop/tap/ding/chime/tick/cash/stamp/tear from earlier reels)
import numpy as np, wave
SR = 44100
import json
WP = json.load(open('warp.json'))
DUR = WP['scenes'][-1]['N'] + WP['scenes'][-1]['L']
def M(t):
    for q in WP['scenes']:
        if q['a'] <= t < q['b'] or q is WP['scenes'][-1]:
            K = q.get('k', WP['k'])
            D = q['b'] - q['a']; H = q['L'] - D * K; o = t - q['a']; fa = q['f'] - q['a']
            return q['N'] + (o * K if o < fa else fa * K + H + (o - fa) * K)
rng = np.random.default_rng(88)

def T(d): return np.arange(int(d * SR)) / SR
from scipy.signal import lfilter
def lp(x, a): return lfilter([a], [1, a - 1], x)
def hp(x, a): return x - lp(x, a)
def put(buf, sig, t, g=1.0, raw=False):
    if not raw: t = M(t)
    i = int(t * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i] * g
def mid(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- instruments ----------------
def ks(f, d=1.2, bright=0.5, damp=0.996):
    """Karplus-Strong plucked string."""
    n = int(d * SR); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p); buf = lp(buf, bright)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = damp * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * np.minimum(1, np.arange(n) / 40)
def k808(g=1.0, d=0.55):
    t = T(d); f = 48 + 110 * np.exp(-t * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5)
    s = np.tanh(s * 1.6)
    click = rng.standard_normal(len(t)) * np.exp(-t * 900) * 0.25
    return (s + click) * g
def rim():
    t = T(0.08)
    n = hp(rng.standard_normal(len(t)), 0.25) * np.exp(-t * 160)
    tone = np.sin(2 * np.pi * 1750 * t) * np.exp(-t * 90) + np.sin(2 * np.pi * 520 * t) * np.exp(-t * 70) * 0.6
    return n * 0.5 + tone * 0.6
def shaker(acc=1.0):
    t = T(0.07)
    env = np.minimum(1, t / 0.012) * np.exp(-t * 60)
    return hp(rng.standard_normal(len(t)), 0.6) * env * 0.35 * acc
def bass(f, d):
    t = T(d)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(s * 1.3) * np.minimum(1, t / 0.01) * np.exp(-t * 2.2)
def pad(ms, d, g=1.0):
    t = T(d); s = np.zeros(len(t))
    for m in ms:
        f = mid(m)
        for det in (-0.25, 0.25):
            ff = f * 2 ** (det / 12 / 8)
            for h in range(1, 6):
                s += np.sin(2 * np.pi * ff * h * t + h) / (h ** 1.6)
    s = lp(s, 0.06)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)
    return s / np.max(np.abs(s)) * env * g

# ---------------- sfx ----------------
def subboom(g=1.0):
    t = T(1.6); f = 32 + 90 * np.exp(-t * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    air = lp(rng.standard_normal(len(t)), 0.05) * np.exp(-t * 6) * 0.5
    return np.tanh((s + air) * 1.4) * g
def keyclick(pitch=1.0):
    t = T(0.05)
    n = hp(rng.standard_normal(len(t)), 0.35) * np.exp(-t * 320)
    body = np.sin(2 * np.pi * 380 * pitch * t) * np.exp(-t * 140)
    return n * 0.6 + body * 0.5
def clack(pitch=1.0, g=1.0):
    """mechanical counter wheel click"""
    t = T(0.045)
    n = hp(rng.standard_normal(len(t)), 0.5) * np.exp(-t * 500)
    r = (np.sin(2 * np.pi * 1250 * pitch * t) + 0.6 * np.sin(2 * np.pi * 3150 * pitch * t)) * np.exp(-t * 180)
    return (n * 0.7 + r * 0.45) * g
def heavyclack():
    t = T(0.25); c = clack(0.7, 1.4)
    out = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 22) * 0.8
    out[:len(c)] += c
    return out
def thud():
    t = T(0.7); f = 90 * np.exp(-t * 1.2)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * np.minimum(1, t / 0.005)
def glitch(d=0.25, seed=1):
    r = np.random.default_rng(seed)
    n = int(d * SR); out = np.zeros(n)
    src = np.sin(2 * np.pi * 220 * T(0.05)) * 0.5 + r.standard_normal(int(0.05 * SR)) * 0.4
    i = 0
    while i < n:
        L = int(r.uniform(0.008, 0.03) * SR)
        seg = src[:L] if L <= len(src) else np.resize(src, L)
        q = r.choice([4, 8, 16]); seg = np.round(seg * q) / q          # bitcrush
        if r.random() < 0.3: seg = seg * 0
        out[i:i + L] = seg[:max(0, min(L, n - i))]; i += L
    return out * np.minimum(1, (n - np.arange(n)) / 400)
def zip_(d=0.22, f0=300, f1=2400, g=1.0):
    t = T(d); f = f0 * (f1 / f0) ** (t / d)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR + 3 * np.sin(2 * np.pi * 60 * t))
    n = hp(rng.standard_normal(len(t)), 0.3) * 0.5
    env = np.sin(np.pi * t / d) ** 1.5
    return (s * 0.35 + n) * env * g
def swell(d=1.25):
    t = T(d)
    tail = lp(rng.standard_normal(len(t)), 0.08) * np.exp(-t * 3.2)
    tone = sum(np.sin(2 * np.pi * mid(m) * t) for m in (65, 68, 72)) * np.exp(-t * 2.5) * 0.25
    return ((tail + tone) / 1.5)[::-1]
def glint():
    t = T(0.6); f = 2400 + 2600 * t / 0.6
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.6) ** 2 * 0.25
def airhit():
    t = T(1.8)
    n = lp(rng.standard_normal(len(t)), 0.35) * np.exp(-t * 2.5)
    return n * np.minimum(1, t / 0.004) * 0.7
def lockin():
    a = np.sin(2 * np.pi * 880 * T(0.09)) * np.exp(-T(0.09) * 30)
    b = np.sin(2 * np.pi * 1320 * T(0.35)) * np.exp(-T(0.35) * 9)
    out = np.zeros(int(0.5 * SR)); out[:len(a)] += a * 0.6; i = int(0.075 * SR); out[i:i + len(b)] += b * 0.7
    t = T(0.5); out += np.sin(2 * np.pi * 120 * t) * np.exp(-t * 18) * 0.7
    return out
def marimba(f):
    t = T(0.5)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 3.93 * f * t) * np.exp(-t * 30)) * np.exp(-t * 9) * np.minimum(1, t / 0.002)
def blip(f=1200):
    t = T(0.08)
    return np.sin(2 * np.pi * f * t + 2 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 40)) * np.exp(-t * 45) * 0.5
def wood(f=700):
    t = T(0.18)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2.7 * f * t)) * np.exp(-t * 38) * np.minimum(1, t / 0.001)

# ---------------- music (112 bpm, F minor) ----------------
BPM = 112; B = 60 / BPM; BAR = 4 * B
mus = np.zeros(int(SR * DUR)); drum = np.zeros_like(mus); kicks = []
CH = [(53, 56, 60), (49, 53, 56), (56, 60, 63), (51, 55, 58)]   # Fm Db Ab Eb
ROOT = [41, 37, 44, 39]
def chord_at(t): return int(t // BAR) % 4
def in_(t, a, b): return M(a) <= t < M(b)
MUTE = [(M(10.85), M(11.15)), (M(14.75), M(15.0))]
def muted(t): return any(a <= t < b for a, b in MUTE)

# pad bed
for bi in range(int(DUR / BAR) + 1):
    t0 = bi * BAR
    if t0 >= DUR: break
    d = min(BAR + 0.3, DUR - t0)
    g = 0.35 if t0 < M(15) else 0.45
    put(mus, pad(CH[bi % 4], d, g), t0, raw=True)
# arp (KS plucks), 8ths
arp_pat = [0, 1, 2, 1, 2, 0, 1, 2]
for k in range(int(DUR / (B / 2))):
    t = k * B / 2
    if muted(t) or t >= M(27.6): continue
    if t < M(3.0) and k % 4 != 0: continue
    c = CH[chord_at(t)]; m = c[arp_pat[k % 8]] + 12
    g = 0.22 if t < M(15) else 0.3
    if M(25) <= t: g = 0.2
    put(mus, ks(mid(m), 0.9, 0.45 + 0.1 * (k % 2)), t, g, raw=True)
# drums
for k in range(int(DUR / (B / 4))):
    t = k * B / 4; beat = k // 4; sub = k % 4; bb = beat % 4
    if muted(t): continue
    kick = False
    if in_(t, 3.0, 8.0) and sub == 0 and bb == 0: kick = True
    if in_(t, 8.0, 12.0) and sub == 0: kick = True
    if in_(t, 15.0, 25.0) and sub == 0: kick = True
    if in_(t, 25.0, 27.0) and sub == 0 and bb == 0: kick = True
    if kick: put(drum, k808(0.9), t, raw=True); kicks.append(t)
    if (in_(t, 3.0, 12.0) or in_(t, 15.0, 25.0)) and sub == 0 and bb in (1, 3): put(drum, rim(), t, 0.45, raw=True)
    if in_(t, 3.0, 12.0) and sub in (0, 2): put(drum, shaker(1.0 if sub == 2 else 0.6), t, raw=True)
    if (in_(t, 12.0, 14.75) or in_(t, 15.0, 25.0)) : put(drum, shaker(1.0 if sub == 2 else 0.55), t, raw=True)
# bass
for k in range(int(DUR / (B / 2))):
    t = k * B / 2
    if muted(t): continue
    if (in_(t, 8.0, 12.0) or in_(t, 15.0, 25.0)) and (k % 8 in (0, 3, 4, 6)):
        put(mus, bass(mid(ROOT[chord_at(t)]), B * 0.9), t, 0.55, raw=True)
# sidechain duck
duck = np.ones_like(mus)
for kt in kicks:
    i = int(kt * SR); n = int(0.3 * SR); j = min(len(duck), i + n)
    duck[i:j] = np.minimum(duck[i:j], 0.45 + 0.55 * (np.arange(j - i) / n))
mus *= duck
# hard mutes with tiny fades
for a, b in MUTE:
    i, j = int(a * SR), int(b * SR); f = 200
    mus[i:j] = 0; drum[i:j] = 0
    mus[i - f:i] *= np.linspace(1, 0, f); drum[i - f:i] *= np.linspace(1, 0, f)

# ---------------- sfx timeline ----------------
fx = np.zeros_like(mus)
put(fx, subboom(0.9), 0.0); put(fx, keyclick(), 0.05, 0.8); put(fx, keyclick(1.2), 0.85, 0.8)
put(fx, zip_(0.25), 1.5, 0.6); put(fx, glitch(0.28, 3), 2.15, 0.7)
# S2
put(fx, wood(420), 3.0, 0.8); put(fx, keyclick(), 3.05, 0.7)
def eo3(x): return 1 - (1 - x) ** 3
def counter_clicks(a, b, v0, v1, pitch, g):
    last = -1; lastv = None
    for i in range(int((b - a) * SR / 64) + 1):
        t = a + i * 64 / SR; x = min(1, max(0, (t - a) / (b - a)))
        v = round(v0 + (v1 - v0) * eo3(x))
        if lastv is not None and v != lastv and t - last >= 0.032:
            put(fx, clack(pitch * (1 + 0.04 * ((v % 3) - 1)), g), t); last = t
        lastv = v
counter_clicks(3.5, 5.6, 0, 120, 1.0, 0.55)
put(fx, clack(1.0, 0.9), 5.62)
put(fx, zip_(0.18, 600, 1800, 0.35), 5.75)
put(fx, heavyclack(), 6.15, 0.8); put(fx, heavyclack(), 6.45, 0.8); put(fx, thud(), 6.5, 0.7)
put(fx, keyclick(0.9), 6.85, 0.7)
# S3
put(fx, wood(420), 8.0, 0.8); put(fx, keyclick(), 8.05, 0.7); put(fx, keyclick(1.1), 8.55, 0.7)
for i in range(6): put(fx, keyclick(0.9 + 0.08 * i), 9.0 + i * 0.3, 0.55)
put(fx, glitch(0.3, 7), 10.85, 0.9); put(fx, thud(), 11.15, 0.8); put(fx, keyclick(0.8), 11.2, 0.6)
# S4
put(fx, wood(420), 12.0, 0.8); put(fx, keyclick(), 12.05, 0.7)
put(fx, zip_(0.2, 400, 1600, 0.4), 12.33); put(fx, zip_(0.2, 400, 1600, 0.4), 12.58)
for i in range(14): put(fx, blip(700 + i * 90), 12.75 + i * 0.065, 0.35)
put(fx, keyclick(1.1), 13.7, 0.7)
put(fx, swell(1.22), 13.53, 0.8)
put(fx, zip_(0.28, 200, 3000, 0.7), 14.72)
# S5 reveal
put(fx, subboom(1.0), 15.0); put(fx, airhit(), 15.0, 0.55)
put(fx, keyclick(), 15.02, 0.5); put(fx, glint(), 15.7, 0.9)
put(fx, zip_(0.35, 250, 900, 0.35), 16.35)
put(fx, lockin(), 17.2, 1.0)
for i, m in enumerate((77, 80, 82, 84, 87)): put(fx, marimba(mid(m)), 17.65 + i * 0.13, 0.45)
for i in range(6): put(fx, keyclick(1.4), 18.37 + i * 0.07, 0.25)
put(fx, zip_(0.3, 900, 250, 0.3), 18.85)
put(fx, keyclick(), 19.15, 0.6)
counter_clicks(19.3, 20.7, 2, 18, 1.25, 0.5)
put(fx, lockin(), 20.72, 0.45)
# S6 offer
put(fx, zip_(0.3, 300, 1500, 0.5), 20.95); put(fx, wood(420), 21.0, 0.6)
put(fx, glint(), 21.6, 0.7)
for i, t in enumerate((21.45, 21.75, 22.05)): put(fx, blip(1000 + 150 * i), t, 0.6)
put(fx, wood(640), 22.7, 0.9); put(fx, wood(860), 23.0, 0.9)
put(fx, lockin(), 23.6, 0.5)
# S7 end
put(fx, subboom(0.55), 25.0); put(fx, airhit(), 25.0, 0.35)
put(fx, keyclick(), 25.4, 0.6); put(fx, wood(860), 25.75, 0.8); put(fx, keyclick(0.9), 26.15, 0.5)
put(fx, sum(ks(mid(m), 2.5, 0.5, 0.998) for m in (65, 68, 72, 77)), 26.4, 0.35)

mix = mus * 0.55 + drum * 0.5 + fx * 1.0
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.15)
mix /= np.max(np.abs(mix)) * 1.06
fo = int(0.7 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
with wave.open("reel8_sfx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok", len(mix) / SR, M(14.6), M(14.75), M(15.0), M(25.0), 41*B)
