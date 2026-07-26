#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 index.m3u 中所有 cctv-* 频道的 URL 替换为央视官方腾讯云 CDN 直链，并生成独立 CCTV 官方源。"""
import re

SRC = "/workspace/index.m3u"
CDN = "ldncctvwbcdtxy.liveplay.myqcloud.com"
BASE = f"http://{CDN}/ldncctvwbcd/cdrmldcctv{{}}_1/index.m3u8"

# tvg-id -> 路径序号（仅非常规项需特殊映射）
SPECIAL = {"5+": "5p"}

def path_for(tvg_id: str) -> str:
    s = tvg_id.lower().replace("cctv-", "")
    return SPECIAL.get(s, s)

# ---------- 1. 处理 index.m3u ----------
with open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")

out = [lines[0]]  # 保留 #EXTM3U 头
out.append("# 央视官方直播源（cntv 腾讯云CDN直链，全国可播，无需签名/Referer）")
replaced = 0
i = 1
while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF"):
        m = re.search(r'tvg-id="([^"]+)"', line)
        tid = m.group(1) if m else ""
        if tid.lower().startswith("cctv-"):
            path = path_for(tid)
            url = BASE.format(path)
            out.append(line)
            # 下一行是旧 URL，替换之
            if i + 1 < len(lines):
                out.append(url)
                i += 2
                replaced += 1
                continue
        else:
            out.append(line)
            if i + 1 < len(lines):
                out.append(lines[i + 1])
            i += 2
            continue
    else:
        out.append(line)
        i += 1

with open(SRC, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"[index.m3u] 已替换 {replaced} 个央视频道为官方直链")

# ---------- 2. 生成独立 aptv_cctv官方.m3u ----------
channels = [
    ("cctv-1", "CCTV-1 综合"), ("cctv-2", "CCTV-2 财经"),
    ("cctv-3", "CCTV-3 综艺"), ("cctv-4", "CCTV-4 中文国际"),
    ("cctv-5", "CCTV-5 体育"), ("cctv-5+", "CCTV-5+ 体育赛事"),
    ("cctv-6", "CCTV-6 电影"), ("cctv-7", "CCTV-7 国防军事"),
    ("cctv-8", "CCTV-8 电视剧"), ("cctv-9", "CCTV-9 纪录"),
    ("cctv-10", "CCTV-10 科教"), ("cctv-11", "CCTV-11 戏曲"),
    ("cctv-12", "CCTV-12 社会与法"), ("cctv-13", "CCTV-13 新闻"),
    ("cctv-14", "CCTV-14 少儿"), ("cctv-15", "CCTV-15 音乐"),
    ("cctv-16", "CCTV-16 奥林匹克"), ("cctv-17", "CCTV-17 农业农村"),
]
blk = ['#EXTM3U x-tvg-url="http://epg.51zmt.top:8000/e.xml"',
       "# CCTV official live source via cntv Tencent CDN, no signature or referer required"]
for tid, name in channels:
    path = path_for(tid)
    url = BASE.format(path)
    logo = f"https://tb.zbds.top/logo/{tid.upper()}.png" if tid != "cctv-5+" else "https://tb.zbds.top/logo/CCTV-5+.png"
    blk.append(f'#EXTINF:-1 tvg-name="{tid}" tvg-id="{tid}" tvg-logo="{logo}" group-title="央视频道",{name}')
    blk.append(url)

with open("/workspace/aptv_cctv官方.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(blk) + "\n")

print(f"[aptv_cctv官方.m3u] 已生成 {len(channels)} 个央视官方频道")
