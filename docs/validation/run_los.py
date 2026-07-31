import numpy as np, json, hashlib
from los import segment_is_free, line_supercover
FREE=1; OBST=2; checks=[]
def rec(name, ok): checks.append({"check":name,"pass":bool(ok)}); 
# 1 open grid
g=np.full((20,20),FREE,np.int8)
rec("open_diagonal_free", segment_is_free(g,(0,0),(19,19)))
rec("open_row_free", segment_is_free(g,(10,0),(10,19)))
# 2 orthogonal wall blocks
g2=np.full((20,20),FREE,np.int8); g2[:,10]=OBST
rec("orthogonal_wall_blocks", not segment_is_free(g2,(10,2),(10,18)))
# 3 THE diagonal-wall S1 guarantee: 0 leaks
g3=np.full((11,11),FREE,np.int8)
for i in range(11): g3[i,i]=OBST
leaks=sum(1 for a,b in [((0,3),(3,0)),((1,4),(4,1)),((2,6),(6,2)),((0,5),(5,0))] if segment_is_free(g3,a,b))
rec("diagonal_wall_zero_leaks", leaks==0)
# 4 endpoint exemption
g4=np.full((10,10),FREE,np.int8); g4[:,0]=OBST
rec("window_endpoint_exempt_visible", segment_is_free(g4,(5,3),(5,0),exempt_endpoints=True))
rec("wall_endpoint_blocks_without_exempt", not segment_is_free(g4,(5,3),(5,0),exempt_endpoints=False))
# 5 supercover superset
cells=line_supercover(0,0,5,3)
rec("supercover_has_endpoints", (0,0) in cells and (5,3) in cells)
allpass=all(c["pass"] for c in checks)
print(json.dumps({"predicate":"los.segment_is_free (isovist LOS primitive)","n_checks":len(checks),"all_pass":allpass,"checks":checks,"leaks_through_diagonal_wall":leaks}, indent=2))
