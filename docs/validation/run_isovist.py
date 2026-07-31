import numpy as np, json, time, sys
from cnfa_algs.los import segment_is_free
from cnfa_algs.plan import isovist_fields, PlanGrid, FREE, OBST
from cnfa_algs.adapters.structured3d_adapter import annotation_to_plangrid

# ---- engine-style thin ray march (mirrors isovist_fields inner loop) ----
def march_visible(grid, a, b):
    r0,c0=a; r1,c1=b
    dr_,dc_=r1-r0,c1-c0; dist=np.hypot(dr_,dc_)
    if dist==0: return True
    ur,uc=dr_/dist,dc_/dist; rr,cc=float(r0),float(c0); step=0
    Hn,Wn=grid.shape
    while True:
        step+=1; rr+=ur; cc+=uc; ri,ci=int(round(rr)),int(round(cc))
        if (ri,ci)==(r1,c1): return True
        if ri<0 or ri>=Hn or ci<0 or ci>=Wn: return False
        if grid[ri,ci]!=FREE: return False
        if step>4*(Hn+Wn): return False

def agree(grid, pairs):
    same=diff=march_leaks=0
    for a,b in pairs:
        ref=segment_is_free(grid,a,b,exempt_endpoints=True)
        mar=march_visible(grid,a,b)
        if ref==mar: same+=1
        else:
            diff+=1
            if mar and not ref: march_leaks+=1   # march sees THROUGH a wall los blocks
    return same,diff,march_leaks

rng=np.random.default_rng(7)
def sample_pairs(grid,n=1500):
    fc=np.argwhere(grid==FREE)
    if len(fc)<2: return []
    idx=rng.integers(0,len(fc),(n,2))
    return [((int(fc[i][0]),int(fc[i][1])),(int(fc[j][0]),int(fc[j][1]))) for i,j in idx if i!=j]

report={"analytic":[], "structured3d":[]}

# ================= ANALYTIC KNOWN GEOMETRIES =================
# (1) open convex room
g=np.full((60,60),FREE,np.int8); g[0,:]=OBST; g[-1,:]=OBST; g[:,0]=OBST; g[:,-1]=OBST
s,d,l=agree(g,sample_pairs(g)); report["analytic"].append({"case":"open_room","agree":s,"disagree":d,"march_leaks_through_wall":l,"n":s+d})
# (2) axis-aligned partition with a doorway gap
g2=g.copy(); g2[10:50,30]=OBST; g2[28:32,30]=FREE   # vertical wall, gap in middle
s,d,l=agree(g2,sample_pairs(g2)); report["analytic"].append({"case":"partition_with_doorway","agree":s,"disagree":d,"march_leaks_through_wall":l,"n":s+d})
# (3) THE diagonal wall (adversarial): does the thin march leak where los blocks?
g3=np.full((40,40),FREE,np.int8)
for i in range(40): g3[i,i]=OBST
s,d,l=agree(g3,sample_pairs(g3)); report["analytic"].append({"case":"diagonal_wall_adversarial","agree":s,"disagree":d,"march_leaks_through_wall":l,"n":s+d})

# isovist_fields correctness on a known room: open cell should be MORE open than an alcove cell
gA=np.full((60,60),FREE,np.int8); gA[0,:]=OBST; gA[-1,:]=OBST; gA[:,0]=OBST; gA[:,-1]=OBST
gA[10:50,20]=OBST; gA[10:50,40]=OBST; gA[10,20:41]=OBST   # a three-sided alcove pocket top
f=isovist_fields(PlanGrid(gA,0.05), n_rays=72, stride=2)
open_center=float(np.nanmean(f["openness_raw_m"][40:55,25:55]))   # open lower area
open_alcove=float(np.nanmean(f["openness_raw_m"][12:18,25:35]))   # inside pocket
report["isovist_monotonicity"]={"open_area_mean_radial_m":round(open_center,3),
   "alcove_mean_radial_m":round(open_alcove,3),
   "open_gt_alcove": bool(open_center>open_alcove)}

# ================= STRUCTURED3D REAL GROUND-TRUTH GEOMETRY =================
import glob
for sc in sorted(glob.glob("scenes/*.json")):
    try:
        t0=time.time(); pg=annotation_to_plangrid(sc, grid_n=160)
        free=int((pg.grid==FREE).sum()); obst=int((pg.grid==OBST).sum()); tot=pg.grid.size
        f=isovist_fields(pg, n_rays=64, stride=3)
        op=f["openness_raw_m"]; finite_on_free=int(np.isfinite(op[pg.grid==FREE]).sum())
        report["structured3d"].append({"scene":sc.split('/')[-1].replace('.json',''),
            "cell_m":round(float(pg.cell_m),4),"free_frac":round(free/tot,3),"obst_frac":round(obst/tot,3),
            "isovist_finite_on_free_frac":round(finite_on_free/max(free,1),3),
            "openness_median_m":round(float(np.nanmedian(op[pg.grid==FREE])),3) if free else None,
            "ran_ok":True,"secs":round(time.time()-t0,1)})
    except Exception as e:
        report["structured3d"].append({"scene":sc,"ran_ok":False,"error":repr(e)[:200]})

print(json.dumps(report,indent=2))
