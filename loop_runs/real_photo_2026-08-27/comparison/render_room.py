#!/usr/bin/env python3
"""render_room.py — structural render of a room.v0_3-semantic JSON from its packet camera.

Deterministic, stdlib+Pillow only. Draws the room shell and apertures with painter's
algorithm + near-plane clipping. NOT a photoreal render: a structural visualization of
exactly what the reconstruction claims, from exactly the declared camera.
Usage: render_room.py room.json camera.json out.png
"""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont

room = json.load(open(sys.argv[1])); cam = json.load(open(sys.argv[2]))
W, H = cam["image_wh"]; g = room["geometry"]
RW, RD, CH = g["width_m"], g["depth_m"], g["ceiling_height_m"]
C = cam["position_m"]; FOV = cam["fov_deg"]
fy = (H/2)/math.tan(math.radians(FOV/2)); fx = fy
NEAR = 0.2

def to_cam(p):  # camera at C looking -z; right=+x, up=+y
    return (p[0]-C[0], p[1]-C[1], C[2]-p[2])

def clip_near(poly):
    out=[]; n=len(poly)
    for i in range(n):
        a,b = poly[i], poly[(i+1)%n]
        ain, bin_ = a[2]>=NEAR, b[2]>=NEAR
        if ain: out.append(a)
        if ain != bin_:
            t=(NEAR-a[2])/(b[2]-a[2])
            out.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1]), NEAR))
    return out

def project(p): return (W/2 + fx*p[0]/p[2], H/2 - fy*p[1]/p[2])

img = Image.new("RGB",(W,H),(238,236,232)); dr = ImageDraw.Draw(img,"RGBA")
def poly3d(pts, fill, outline=None, width=2):
    cp = clip_near([to_cam(p) for p in pts])
    if len(cp)<3: return None
    pp=[project(p) for p in cp]
    dr.polygon(pp, fill=fill, outline=outline)
    if outline:
        for i in range(len(pp)): dr.line([pp[i],pp[(i+1)%len(pp)]],fill=outline,width=width)
    return pp

# shell, far to near
poly3d([(0,0,0),(RW,0,0),(RW,CH,0),(0,CH,0)],(226,222,214),(180,176,168))          # north wall
poly3d([(0,0,0),(0,0,RD),(0,CH,RD),(0,CH,0)],(218,214,206),(180,176,168))          # west wall
poly3d([(RW,0,0),(RW,0,RD),(RW,CH,RD),(RW,CH,0)],(222,218,210),(180,176,168))      # east wall
poly3d([(0,CH,0),(RW,CH,0),(RW,CH,RD),(0,CH,RD)],(232,230,226),(200,196,190))      # ceiling
poly3d([(0,0,0),(RW,0,0),(RW,0,RD),(0,0,RD)],(206,196,182),(184,174,160))          # floor
for zz in range(0,int(RD)+1,2):                                                     # floor lines
    cp=clip_near([to_cam((0,0.001,zz)),to_cam((RW,0.001,zz))])
    if len(cp)>=2: dr.line([project(cp[0]),project(cp[1])],fill=(188,178,164,140),width=1)

def wall_pts(ap):
    u0 = ap["u_m"]; u1 = u0 + ap["width_m"]; y0, y1 = ap["sill_m"], ap["sill_m"]+ap["height_m"]
    if ap["wall"]=="east":
        cz=RD/2; z0,z1 = cz+u0, cz+u1
        z0,z1 = max(0,min(RD,z0)), max(0,min(RD,z1))
        return [(RW-0.01,y0,z0),(RW-0.01,y0,z1),(RW-0.01,y1,z1),(RW-0.01,y1,z0)], "east"
    if ap["wall"]=="west":
        cz=RD/2; z0,z1 = cz+u0, cz+u1
        return [(0.01,y0,z0),(0.01,y0,z1),(0.01,y1,z1),(0.01,y1,z0)], "west"
    cx=RW/2; x0,x1 = cx+u0, cx+u1                                                   # north
    return [(x0,y0,0.01),(x1,y0,0.01),(x1,y1,0.01),(x0,y1,0.01)], "north"

labels=[]
for ap in room.get("apertures",[]):
    pts,_ = wall_pts(ap)
    if ap["kind"] in ("glazed_wall","window","glass_partition","clerestory","skylight"):
        pp = poly3d(pts,(150,196,222,150),(96,140,170),3)
        if pp:  # mullions
            n=6
            for i in range(1,n):
                t=i/n
                a=tuple(pts[0][k]+t*(pts[1][k]-pts[0][k]) for k in range(3))
                b=tuple(pts[3][k]+t*(pts[2][k]-pts[3][k]) for k in range(3))
                cp=clip_near([to_cam(a),to_cam(b)])
                if len(cp)>=2: dr.line([project(cp[0]),project(cp[1])],fill=(96,140,170,180),width=2)
    else:
        pp = poly3d(pts,(122,96,72,255),(84,64,46),3)
    if pp:
        cx=sum(p[0] for p in pp)/len(pp); cy=min(p[1] for p in pp)
        labels.append((cx,cy,f'{ap["id"]}: {ap["kind"]} → {ap["wall"]}'))

# furniture: dimensioned boxes on the floor (the platform's own representation —
# parametric placeholders sized by Neufert priors, NOT meshes; drawn honestly as such)
FURN_COLORS = {"chair":(176,120,80),"desk":(140,100,70),"sofa":(160,90,80),
               "table":(150,110,75),"bookcase":(120,90,60),"divider":(150,150,140),
               "reception_desk":(130,105,90)}
def draw_box(x0,z0,x1,z1,h,color,label=None):
    y0,y1=0,h
    faces = [  # far, left, right, top (painter-ish for a camera looking -z)
        [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],
        [(x0,y0,z0),(x0,y0,z1),(x0,y1,z1),(x0,y1,z0)],
        [(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)],
        [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],
    ]
    shade=[1.0,0.85,0.85,1.12]; pp_last=None
    for f,sh in zip(faces,shade):
        c=tuple(min(255,int(v*sh)) for v in color)
        pp=poly3d(f,c+(255,),tuple(int(v*0.6) for v in color),2)
        if pp: pp_last=pp
    return pp_last

for fobj in room.get("furniture", []):
    cat = str(fobj.get("category", fobj.get("element","?")))
    x = fobj.get("x_m"); z = fobj.get("y_m")   # platform: y_m is along-depth
    w = fobj.get("width_m", 0.6); d = fobj.get("depth_m", 0.6); h = fobj.get("height_m", 0.75)
    if x is None or z is None: continue
    color = FURN_COLORS.get(cat, (150,120,95))
    pp = draw_box(x-w/2, z-d/2, x+w/2, z+d/2, h, color)
    if pp:
        cx=sum(q[0] for q in pp)/len(pp); cy=min(q[1] for q in pp)
        labels.append((cx, cy, f'{fobj.get("id","?")}: {cat}'))

def load_font(paths, size):  # first path that opens wins; DejaVu stays first so Linux output is unchanged
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except Exception: pass
    return ImageFont.load_default()

font = load_font(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                  "/System/Library/Fonts/Supplemental/DejaVuSans-Bold.ttf",
                  "/System/Library/Fonts/Supplemental/Arial Bold.ttf"], 20)
foot_font = load_font(["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                       "/System/Library/Fonts/Supplemental/DejaVuSans.ttf",
                       "/System/Library/Fonts/Supplemental/Arial.ttf"], 15)
for cx,cy,txt in labels:
    tw = dr.textlength(txt,font=font)
    x=max(8,min(W-tw-8,cx-tw/2)); y=max(8,cy-34)
    dr.rectangle([x-6,y-4,x+tw+6,y+26],fill=(30,30,30,180))
    dr.text((x,y),txt,fill=(255,255,255),font=font)
foot=f'structural render · room.v0_3-semantic · camera {C} fov {FOV}° · NOT a photoreal render'
dr.rectangle([0,H-30,W,H],fill=(30,30,30,200)); dr.text((10,H-25),foot,fill=(230,230,230),font=foot_font)
img.save(sys.argv[3])
print("rendered", sys.argv[3])
