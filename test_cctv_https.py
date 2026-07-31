#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新筛选央视源：优先 HTTPS，每频道给多个不同网络类型的备选，确保跨网可达。"""
import re, subprocess
from urllib.parse import urljoin
from pathlib import Path

ONLINE = [
    ("vbskycn", "https://live.zbds.top/tv/iptv4.m3u"),
    ("best-fan", "https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_all.m3u8"),
    ("iptv-org", "https://iptv-org.github.io/iptv/countries/cn.m3u"),
]
CANONICAL = {
    "1": ("cctv-1", "CCTV-1 综合"), "2": ("cctv-2", "CCTV-2 财经"),
    "3": ("cctv-3", "CCTV-3 综艺"), "4": ("cctv-4", "CCTV-4 中文国际"),
    "5": ("cctv-5", "CCTV-5 体育"), "5+": ("cctv-5+", "CCTV-5+ 体育赛事"),
    "6": ("cctv-6", "CCTV-6 电影"), "7": ("cctv-7", "CCTV-7 国防军事"),
    "8": ("cctv-8", "CCTV-8 电视剧"), "9": ("cctv-9", "CCTV-9 纪录"),
    "10": ("cctv-10", "CCTV-10 科教"), "11": ("cctv-11", "CCTV-11 戏曲"),
    "12": ("cctv-12", "CCTV-12 社会与法"), "13": ("cctv-13", "CCTV-13 新闻"),
    "14": ("cctv-14", "CCTV-14 少儿"), "15": ("cctv-15", "CCTV-15 音乐"),
    "16": ("cctv-16", "CCTV-16 奥林匹克"), "17": ("cctv-17", "CCTV-17 农业农村"),
}
GLOBAL_HOSTS = ("antik.sk", "github.io", "264788.xyz", "iptv-org", "abnvideos",
                "akamaized", "imgg", "cdn", "0472.org")

def norm_ch(text):
    t = text.upper()
    m = re.search(r"CCTV\s*-?\s*(\d+)\s*\+?|CCTV(\d+)\s*\+?|央视\s*(\d+)", t)
    if not m:
        return None
    n = next(g for g in m.groups() if g)
    plus = "+" if "+" in t or "PLUS" in t else ""
    return "5+" if (n == "5" and plus) else n

def fetch(url, timeout=10):
    try:
        r = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0",
                            "--max-time", str(timeout), "-w",
                            "\\n__M__ %{http_code} %{size_download}", url],
                           capture_output=True, text=True, timeout=timeout+3)
        out = r.stdout
        m = re.search(r"__M__ (\d+) (\d+)\s*$", out)
        if not m:
            return 0, ""
        return int(m.group(1)), out[:m.start()].strip()
    except Exception:
        return 0, ""

def parse(text, src):
    res = []
    lines = [l.strip() for l in text.splitlines()]
    inf = None
    for l in lines:
        if l.startswith("#EXTINF"):
            inf = l
        elif inf and (l.startswith("http://") or l.startswith("https://")):
            ch = norm_ch(inf)
            if ch:
                res.append((ch, l, src, l.startswith("https://")))
            inf = None
        else:
            inf = None
    return res

def playable(url):
    code, body = fetch(url, 8)
    if code != 200 or not body.startswith("#EXTM3U"):
        return False
    if "#EXTINF" in body and ".ts" in body:
        return True
    m = re.search(r"#EXT-X-STREAM-INF[^\r\n]*[\r\n]+([^\r\n ]+)", body)
    if not m:
        return False
    sub = m.group(1).strip()
    if not (sub.startswith("http://") or sub.startswith("https://")):
        sub = urljoin(url, sub)
    vcode, vbody = fetch(sub, 8)
    return vcode == 200 and vbody and (".ts" in vbody or "#EXTINF" in vbody)

def classify(url):
    if url.startswith("https://"):
        if any(h in url for h in GLOBAL_HOSTS):
            return "g_https"
        return "d_https"
    return "http"

def main():
    entries = []
    for name, url in ONLINE:
        code, body = fetch(url, 15)
        print(f"[在线] {name}: {code} bytes={len(body)}")
        if code == 200 and body:
            entries.extend(parse(body, name))

    by_ch = {k: [] for k in CANONICAL}
    seen = {k: set() for k in CANONICAL}
    for ch, url, src, _ in entries:
        if ch in by_ch and url not in seen[ch]:
            seen[ch].add(url)
            by_ch[ch].append(url)

    # 测试并分类
    selected = {}
    for ch, urls in by_ch.items():
        pools = {"d_https": [], "g_https": [], "http": []}
        print(f"\n=== CCTV-{ch} 候选 {len(urls)} ===")
        for url in urls[:25]:
            cls = classify(url)
            ok = playable(url)
            print(f"  {'OK ' if ok else 'FAIL'} {cls:8} {url[:70]}")
            if ok:
                pools[cls].append(url)
        # 选优：国内HTTPS > 全球HTTPS > HTTP(iptv-org优先) > 其它HTTP
        chosen = []
        chosen += pools["d_https"][:1]
        chosen += pools["g_https"][:1]
        # http: 优先 iptv-org
        http_sorted = sorted(pools["http"], key=lambda u: 0 if "iptv-org" in u else 1)
        chosen += http_sorted[:1]
        if not chosen:
            chosen = pools["http"][:1]
        selected[ch] = chosen[:3]
        print(f"  >> 选用 {len(chosen)} 条: " + " | ".join(chosen))

    # 生成 m3u（每频道主源 + 备选，用不同显示名区分）
    out = ['#EXTM3U x-tvg-url="http://epg.51zmt.top:8000/e.xml"',
           "# 央视多线路优选（HTTPS优先+海外+iptv-org 备选，跨网可达）"]
    for ch in sorted(selected, key=lambda x: (len(x), x)):
        tid, name = CANONICAL[ch]
        urls = selected[ch]
        if not urls:
            continue
        labels = [name] + [f"{name} [备选{i}]" for i in range(1, len(urls))]
        for u, lab in zip(urls, labels):
            logo = f"https://tb.zbds.top/logo/{tid.upper()}.png" if ch != "5+" else "https://tb.zbds.top/logo/CCTV-5+.png"
            out.append(f'#EXTINF:-1 tvg-name="{tid}" tvg-id="{tid}" tvg-logo="{logo}" group-title="央视频道",{lab}')
            out.append(u)
    Path("/workspace/aptv_cctv优选.m3u").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\n已生成 aptv_cctv优选.m3u：{sum(len(v) for v in selected.values())} 个央视条目")

if __name__ == "__main__":
    main()
