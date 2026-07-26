#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用实测可播的 aptv_cctv优选.m3u 替换 index.m3u 与 aptv_cctv官方.m3u 中的央视块。"""
import re
from pathlib import Path

WORK = Path("/workspace")
PREFERRED = WORK / "aptv_cctv优选.m3u"
INDEX = WORK / "index.m3u"
OFFICIAL = WORK / "aptv_cctv官方.m3u"

def parse_preferred():
    """返回 {tvg_id: (name, url)}"""
    mapping = {}
    lines = PREFERRED.read_text(encoding="utf-8").splitlines()
    extinf = None
    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            extinf = line
        elif extinf and line.startswith("http"):
            m = re.search(r'tvg-id="([^"]+)"', extinf)
            name = extinf.split(",")[-1].strip()
            if m:
                mapping[m.group(1)] = (name, line)
            extinf = None
    return mapping

def update_index(preferred):
    lines = INDEX.read_text(encoding="utf-8").splitlines()
    out = [lines[0]]  # #EXTM3U
    out.append("# 央视公开源优选（master+variant/切片 已实测 200，全国可播性优于官方直链）")
    i = 1
    replaced = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            m = re.search(r'tvg-id="([^"]+)"', line)
            tid = m.group(1) if m else ""
            if tid.lower().startswith("cctv-") and tid in preferred:
                name, url = preferred[tid]
                # 保留原 EXTINF 的 tvg-name/tvg-id/tvg-logo/group-title，只改显示名称
                new_inf = re.sub(r',[^,]*$', f',{name}', line)
                out.append(new_inf)
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
    INDEX.write_text("\n".join(out) + "\n", encoding="utf-8")
    return replaced

def update_official(preferred):
    """用优选内容覆盖 aptv_cctv官方.m3u，保留元数据格式"""
    lines = PREFERRED.read_text(encoding="utf-8").splitlines()
    lines[1] = "# 央视公开源优选（已实测可播，master + .ts 切片均 200）"
    OFFICIAL.write_text("\n".join(lines) + "\n", encoding="utf-8")

preferred = parse_preferred()
print(f"读取到 {len(preferred)} 个实测可播央视频道")
count = update_index(preferred)
print(f"index.m3u 已替换 {count} 个央视频道")
update_official(preferred)
print("aptv_cctv官方.m3u 已覆盖为实测可播源")
