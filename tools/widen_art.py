#!/usr/bin/env python3
"""v009 카드 크기에 맞춰 v008 카드 그림(tools/art_v008/*.webp, 2배 해상도, 사방 10px 여백 포함)을 늘이고 줄여 src/art/ 에 써요.
아이콘이 찌그러지지 않도록 그림이 없는 띠(그라데이션만 있는 곳)만 늘립니다.  사용: python3 tools/widen_art.py"""
import numpy as np
from PIL import Image
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n): return Image.open(f'{R}/tools/art_v008/{n}.webp').convert('RGBA')
def save(im,n): im.save(f'{R}/src/art/{n}.webp','WEBP',quality=92,method=6); print(n,im.size)
def rs(im,w,h): return im.resize((w,h),Image.LANCZOS)
def hband(im,segs):
    """segs: [(src_x0,src_x1,dst_w)] 를 차례로 이어 붙여요(끝까지 이어지도록 사이는 그대로)"""
    W,H=im.size;parts=[];x=0
    for a,b,d in segs:
        if a>x:parts.append(im.crop((x,0,a,H)))
        parts.append(rs(im.crop((a,0,b,H)),d,H));x=b
    if x<W:parts.append(im.crop((x,0,W,H)))
    out=Image.new('RGBA',(sum(p.width for p in parts),H));cx=0
    for p in parts:out.paste(p,(cx,0));cx+=p.width
    return out
def vband(im,segs):
    return hband(im.transpose(Image.TRANSPOSE),segs).transpose(Image.TRANSPOSE)
# 홈 마스크 카드 297→345 : 아이콘이 가운데라 양쪽 빈 띠를 늘려요 (모서리 곡선 밖)
m=load('mask');m=hband(m,[(92,112,68),(524,548,72)]);assert m.size==(730,546);save(m,'mask')
# 기록 홈 큰 카드: 297→345, 시즌 253→240, 연필 192→190. 아이콘은 오른쪽이라 왼쪽 빈 띠를 늘리고, 시즌은 위쪽 빈 띠를 줄여요
s=load('rec_season');s=vband(s,[(90,186,70)]);s=hband(s,[(120,200,176)]);assert s.size==(730,520),s.size;save(s,'rec_season')
p=load('rec_pencil');p=vband(p,[(100,200,96)]);p=hband(p,[(120,200,176)]);assert p.size==(730,420),p.size;save(p,'rec_pencil')
# 홈 미니카드 143→166.5 : 아이콘(해·꽃가루…)이 오른쪽 아래라서 왼쪽의 빈 띠만 늘려요(그러면 아이콘이 오른쪽으로 23.5px 밀려요)
for n in ['home_weather','home_pollen','home_fine','home_ultra']:
    h=load(n);h=hband(h,[(70,80,57)]);assert h.size==(373,280),h.size;save(h,n)
