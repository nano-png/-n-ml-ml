import numpy as np, sys
from PIL import Image, ImageFilter
from scipy import ndimage as nd
src="/home/user/-n-ml-ml/brand/source/"
for name in ["p_small","p_large"]:
    im=np.array(Image.open(src+name+".jpg").convert("RGB")).astype(int)
    if name=="p_large":
        reg=im[1415:1460,840:935]; lum=reg.mean(axis=2)
        light=reg[lum>200].reshape(-1,3); fill=np.median(light,axis=0) if len(light) else np.array([235,235,235])
        reg[lum<200]=fill; im[1415:1460,840:935]=reg
    cand=im.min(axis=2)>=244
    lab,n=nd.label(cand)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(border))
    fg=~bg
    if name=="p_large":
        yy,xx=np.mgrid[0:fg.shape[0],0:fg.shape[1]]
        yl=1485-(xx-1208)*(190/480)
        fg&=~((xx>1150)&(yy>yl))
    fg0=fg.copy(); fg=nd.binary_opening(fg,iterations=7)
    fl,fn=nd.label(fg)
    sizes=nd.sum(fg,fl,range(1,fn+1))
    order=np.argsort(sizes)[::-1]
    print(name,[int(sizes[i]) for i in order[:6]])
    keep=np.zeros_like(fg)
    for i in order:
        if sizes[i]>150000: keep|=fl==(i+1)
    keep=nd.binary_dilation(keep,iterations=7)&fg0; keep=nd.binary_opening(keep,iterations=2); keep=nd.binary_fill_holes(keep)
    a=Image.fromarray((keep*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    rgba=Image.fromarray(im.astype(np.uint8)).convert("RGBA"); rgba.putalpha(a)
    bb=rgba.getbbox(); rgba=rgba.crop(bb); rgba.save(f"{name}_cut.png"); print(bb)
    # per-stand separation
    sl=nd.find_objects(nd.label(keep)[0])
    for k,s in enumerate(sl):
        c=Image.fromarray(im.astype(np.uint8)).convert("RGBA"); c.putalpha(a)
        sub=c.crop((s[1].start,s[0].start,s[1].stop,s[0].stop)); sub.save(f"{name}_{k}.png"); print(" part",k,sub.size)
