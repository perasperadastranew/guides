# Звуковой дизайн по событиям маскота: python3 sfx.py out/events.json 24
import numpy as np, json, subprocess
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
import sys
SR=48000; DUR=float(sys.argv[2]); D=0; N=int(SR*DUR); out=np.zeros((N,2)); rng=np.random.default_rng(7)
def env(n,a=.01,r=.1):
    e=np.ones(n); na=max(1,int(a*SR)); nr=max(1,int(r*SR)); e[:na]=np.linspace(0,1,na); e[-nr:]*=np.linspace(1,0,nr)**2; return e
def bp(x,lo,hi): return sosfilt(butter(2,[lo,hi],btype='band',fs=SR,output='sos'),x)
def sweep(f0,f1,d,curve=1.0):
    t=np.arange(int(d*SR))/SR; f=f0+(f1-f0)*(t/d)**curve; return np.sin(2*np.pi*np.cumsum(f)/SR)
def put(x,t,g=1.0,pan=0.0):
    i=int(t*SR)
    if i<0 or i>=N: return
    x=x[:N-i]; out[i:i+len(x),0]+=x*g*(1-max(0,pan)); out[i:i+len(x),1]+=x*g*(1+min(0,pan))
def blip(): x=sweep(820,1350,.07)*np.exp(-np.arange(int(.07*SR))/SR*38); return x*.5
def pop(f=420): n=int(.11*SR); return sweep(f,f*1.9,.11,.6)*np.exp(-np.arange(n)/SR*30)*.6
def whoosh(d=.6,lo=500,hi=3500):
    n=int(d*SR); x=rng.standard_normal(n); t=np.arange(n)/n; y=np.zeros(n)
    for k in range(6):
        a,b=int(k*n/6),int((k+1)*n/6)+400; c=lo+(hi-lo)*np.sin(np.pi*(k+.5)/6); y[a:b]+=bp(x,c*.6,c*1.5)[a:b][:len(y[a:b])]
    return y*np.sin(np.pi*t)**2*.35
def scan(d):
    n=int(d*SR); t=np.arange(n)/SR; x=sweep(180,520,d,1.4)*.25+sweep(360,1040,d,1.4)*.1
    x*=(.7+.3*np.sin(2*np.pi*14*t)); x+=bp(rng.standard_normal(n),3000,7000)*.05; return x*env(n,.15,.3)
def scribble(d):
    n=int(d*SR); t=np.arange(n)/SR; x=bp(rng.standard_normal(n),1800,5200)*(.35+.65*np.abs(np.sin(2*np.pi*7.5*t+np.sin(t*9)))); return x*env(n,.04,.12)*.22
def fly(d):
    n=int(d*SR); t=np.arange(n)/SR; x=np.sin(2*np.pi*(260+40*np.sin(2*np.pi*.9*t))*t+2*np.sin(2*np.pi*11*t))*.12; x+=bp(rng.standard_normal(n),700,2200)*.06; return x*env(n,.2,.35)
def zap(): n=int(.3*SR); return (sweep(300,2400,.3,2)*.3+bp(rng.standard_normal(n),2000,8000)*.12)*env(n,.005,.2)
def tick(): n=int(.05*SR); return sweep(2400,1900,.05)*np.exp(-np.arange(n)/SR*90)*.45
def ding(f=880,d=.9): n=int(d*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*1.5*t)+.25*np.sin(2*np.pi*f*2.01*t))*np.exp(-t*5.5)*env(n,.004,.2)*.3
def thud(d=.35,f=75): n=int(d*SR); return sweep(f,f*.55,d,.5)*np.exp(-np.arange(n)/SR*9)*env(n,.008,.1)*.9
def rumble(d):
    n=int(d*SR); t=np.arange(n)/SR; return (bp(rng.standard_normal(n),60,260)*.6+np.sin(2*np.pi*58*t)*.3)*(.6+.4*np.sin(2*np.pi*23*t))*env(n,.08,.25)*.5
def stamp(): n=int(.18*SR); return (bp(rng.standard_normal(n),150,1800)*np.exp(-np.arange(n)/SR*28)*.7)+thud(.18,110)[:n]*.5
ev=json.load(open(sys.argv[1]))
# звук только на действия, на появления маскота — тишина
for t,k,d in ev:
    if k=='scan': put(scan(d+.4),t-.2,.8)
    elif k=='frame': put(scribble(.42),t,.7)
    elif k=='pen': put(scribble(d),t+.3,1.0)
    elif k=='fly': put(fly(d),t,.9)
    elif k=='grid': put(zap(),t+.12,.6)
    elif k=='meas': put(tick(),t+.05,.8); put(tick(),t+.3,.6)
    elif k=='ok': put(ding(988),t+.05,.9)
    elif k=='idea': put(ding(1319,.8),t+.08,.6)
    elif k=='morph': put(whoosh(.3,700,2200),t-.04,.5)
out=sosfilt(butter(2,4200,btype='low',fs=SR,output='sos'),out,axis=0)   # мягче, без звонких верхов
pk=np.abs(out).max() or 1; out*=10**(-16.5/20)/pk                    # эффекты тихие, фоном: пик около −16.5 дБ, музыку класть сверху
wavfile.write('sfx.wav',SR,(out*32767).astype(np.int16)); print('sfx.wav, peak',pk)
