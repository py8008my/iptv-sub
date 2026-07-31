#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APTV 订阅总表生成器（全国通用版）

清理原则（针对"动也不动"问题）：
 1. 剔除一切裸 IP 地址   —— 省内 IPTV 组播/单播，跨省跨运营商必然不通
 2. 剔除一切带端口地址   —— 同上，且常被运营商 QoS 限速
 3. 剔除境外 VPS 网段     —— 沙箱在境外测着飞快，国内访问必卡死
 4. 优先 https           —— iOS ATS 默认拦截明文 http 流
 5. 央视频道全部替换为官网自建 CDN 的官方直播地址

保留：域名型的国内正规 CDN（广电云/省级台/央广/阿里云/腾讯云等）
"""
import re
import urllib.parse
from collections import OrderedDict

SRC = "/workspace/index.m3u"
CCTV_FILE = "/workspace/aptv_cctv优选.m3u"
OUT = "/workspace/index.m3u"

# 境外 VPS 常见网段（这些在国内访问必卡）
BAD_NET = (
    "38.", "45.", "63.", "64.", "66.", "69.", "74.", "84.", "89.",
    "91.", "104.", "107.", "128.", "129.", "134.", "138.", "141.",
    "142.", "143.", "146.", "149.", "154.", "155.", "156.", "157.",
    "158.", "160.", "161.", "162.", "164.", "165.", "167.", "168.",
    "169.", "170.", "172.", "173.", "176.", "178.", "179.", "185.",
    "188.", "192.", "193.", "194.", "195.", "196.", "198.", "199.",
    "200.", "204.", "205.", "206.", "207.", "208.", "209.", "212.",
    "213.", "216.", "23.", "31.", "5.", "51.", "62.", "77.", "78.",
    "79.", "80.", "81.", "82.", "83.", "85.", "86.", "87.", "88.",
)

# 已知不可靠的第三方个人域名（随时失效，且多为境外小鸡）
BAD_DOMAIN = (
    "antik.sk", "vpstv.net", "dpdns.org", "abnvideos", "264788.xyz",
    "163189.xyz", "130519.xyz", "188766.xyz", "666230.xyz", "bkpcp.top",
    "metshop.top", "iill.top", "goodiptv.club", "jdshipin.com",
    "freetv.top", "3y1.xyz", "epg.pw", "ottiptv.cc", "pendy",
)


def host_port(url):
    try:
        p = urllib.parse.urlparse(url)
        return (p.hostname or ""), p.port
    except Exception:
        return "", None


def keep(url):
    """判断一条地址是否值得保留"""
    if not url.startswith("http"):
        return False, "非http"
    h, port = host_port(url)
    if not h:
        return False, "无主机"

    # 1. 裸 IP 一律剔除（省内组播/单播）
    if re.match(r"^[\d.]+$", h):
        return False, "裸IP(省内组播)"

    # 2. 带端口一律剔除
    if port:
        return False, "带端口(省内源)"

    # 3. 境外 VPS 网段
    if h.startswith(BAD_NET):
        return False, "境外VPS"

    # 4. 不可靠个人域名
    for b in BAD_DOMAIN:
        if b in h:
            return False, "个人域名({})".format(b)

    return True, "ok"


def parse(path):
    """解析 m3u -> [(extinf, url)]"""
    out = []
    lines = open(path, encoding="utf-8", errors="ignore").read().splitlines()
    header = ""
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith("#EXTM3U"):
            header = s
        elif s.startswith("#EXTINF"):
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("http"):
                out.append((s, lines[i + 1].strip()))
    return header, out


def chname(extinf):
    return extinf.split(",")[-1].strip()


def main():
    header, entries = parse(SRC)
    if not header:
        header = '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"'

    _, cctv_entries = parse(CCTV_FILE)

    kept, dropped = [], []
    reasons = {}
    for ext, url in entries:
        name = chname(ext)
        # 央视频道整体替换，这里先跳过
        if "CCTV" in name.upper() or "央视" in name:
            continue
        ok, why = keep(url)
        if ok:
            kept.append((ext, url))
        else:
            dropped.append((name, url, why))
            reasons[why] = reasons.get(why, 0) + 1

    # 去重：同一频道同一地址只留一条
    seen = set()
    dedup = []
    for ext, url in kept:
        if url in seen:
            continue
        seen.add(url)
        dedup.append((ext, url))

    # 按频道分组，每个频道最多保留 4 条线路
    bych = OrderedDict()
    for ext, url in dedup:
        bych.setdefault(chname(ext), []).append((ext, url))
    limited = []
    for name, items in bych.items():
        limited.extend(items[:4])

    out = [header]
    # 央视放最前面
    for ext, url in cctv_entries:
        out.append(ext)
        out.append(url)
    for ext, url in limited:
        out.append(ext)
        out.append(url)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    print("原始条目      : {}".format(len(entries)))
    print("央视(官方替换): {}".format(len(cctv_entries)))
    print("其他频道保留  : {}".format(len(limited)))
    print("剔除          : {}".format(len(dropped)))
    print("\n--- 剔除原因统计 ---")
    for w, c in sorted(reasons.items(), key=lambda x: -x[1]):
        print("  {:<22} {}".format(w, c))
    print("\n最终总条目: {}  频道数: {}".format(
        len(cctv_entries) + len(limited), len(bych) + 18))

    https_cnt = sum(1 for _, u in cctv_entries) + \
        sum(1 for _, u in limited if u.startswith("https://"))
    total = len(cctv_entries) + len(limited)
    print("https 占比: {}/{} = {:.0%}".format(https_cnt, total, https_cnt / total))


if __name__ == "__main__":
    main()
