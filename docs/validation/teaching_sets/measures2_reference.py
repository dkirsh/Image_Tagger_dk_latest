# Reference algorithms for the new tagger measures + existing ones, for teaching-set selection.
# Self-contained numpy/cv2 (portable for Codex). 
import numpy as np, cv2, io
from PIL import Image
def load(path, n=256):
    im=Image.open(path).convert("RGB").resize((n,n)); return np.asarray(im), cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2GRAY)
def edge_density(g): return float((cv2.Canny(g,100,200)>0).mean())
def contrast_energy(g):
    ce=0.0
    for k in (3,7,15):
        m=cv2.blur(g.astype(np.float32),(k,k)); v=cv2.blur(g.astype(np.float32)**2,(k,k))-m*m
        ce+=np.sqrt(np.clip(v,0,None)).mean()
    return float(ce/3)
def subband_entropy(g):
    se=0.0; cur=g.astype(np.float32)
    for _ in range(3):
        d=cv2.pyrDown(cur); u=cv2.pyrUp(d,dstsize=(cur.shape[1],cur.shape[0]))
        lap=np.abs(cur-u).ravel(); lap=lap/(lap.sum()+1e-9); lap=lap[lap>0]
        se+=float(-(lap*np.log2(lap)).sum()); cur=d
    return se
def n_colors(rgb): return int(len(np.unique((rgb//32).reshape(-1,3),axis=0)))
def png_size(a):
    b=io.BytesIO(); Image.fromarray(a.astype(np.uint8)).save(b,"PNG"); return len(b.getvalue())
def arrangement_disorder(g):
    # coarse-scale: compressibility of the big-structure map vs its own permutation.
    coarse=cv2.resize(g,(48,48),interpolation=cv2.INTER_AREA)
    s=png_size(coarse); rng=np.random.default_rng(0)
    perm=coarse.ravel().copy(); rng.shuffle(perm); sp=png_size(perm.reshape(48,48))
    return float(s/ (sp+1e-9))   # ordered<<1 ; scattered ~1  -> higher = more disordered
def spectral_discomfort(g):
    # fraction of amplitude-spectrum energy in the mid-high band (1/f-departure proxy)
    F=np.abs(np.fft.fftshift(np.fft.fft2(g.astype(np.float32)))); H,W=F.shape
    yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt((yy-H/2)**2+(xx-W/2)**2)/(0.5*min(H,W))
    tot=F.sum()+1e-9; return float(F[(r>0.35)&(r<=1.0)].sum()/tot)
def all_measures(path):
    rgb,g=load(path)
    return dict(edge_density=edge_density(g), contrast_energy=contrast_energy(g),
               subband_entropy=subband_entropy(g), n_colors=n_colors(rgb),
               arrangement_disorder=arrangement_disorder(g), spectral_discomfort=spectral_discomfort(g))
