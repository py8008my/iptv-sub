#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从本地/在线公开源中提取央视频道 URL，实测哪些 master+variant 都 200 可播，生成优选源。"""
import re, subprocess, json, os, sys
from urllib.parse import urljoin, urlparse

CANDIDATE_FILES = [
    "/workspace/aptv_vbskycn.m3u",
    "/workspace/aptv_bestfan.m3u",
    "/workspace/aptv_中文台源.m3u",
    "/workspace/aptv_国内源.m3u",
    "/workspace/aptv_全国CDN优选.m3u",
    "/workspace/aptv_聚合国内源.m3u",
    "/workspace/aptv_精选卫视.m3u",
]
ONLINE_SOURCES = [
    ("iptv-org cn", "https://iptv-org.github.io/iptv/countries/cn.m3u"),
    ("vbskycn iptv4", "https://live.zbds.top/tv/iptv4.m3u"),
    ("best-fan cn_all", "https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_all.m3u8"),
]

CANONICAL = {
    "1": ("cctv-1", "CCTV-1 综合"),
    "2": ("cctv-2", "CCTV-2 财经"),
    "3": ("cctv-3", "CCTV-3 综艺"),
    "4": ("cctv-4", "CCTV-4 中文国际"),
    "5": ("cctv-5", "CCTV-5 体育"),
    "5+": ("cctv-5+", "CCTV-5+ 体育赛事"),
    "6": ("cctv-6", "CCTV-6 电影"),
    "7": ("cctv-7", "CCTV-7 国防军事"),
    "8": ("cctv-8", "CCTV-8 电视剧"),
    "9": ("cctv-9", "CCTV-9 纪录"),
    "10": ("cctv-10", "CCTV-10 科教"),
    "11": ("cctv-11", "CCTV-11 戏曲"),
    "12": ("cctv-12", "CCTV-12 社会与法"),
    "13": ("cctv-13", "CCTV-13 新闻"),
    "14": ("cctv-14", "CCTV-14 少儿"),
    "15": ("cctv-15", "CCTV-15 音乐"),
    "16": ("cctv-16", "CCTV-16 奥林匹克"),
    "17": ("cctv-17", "CCTV-17 农业农村"),
}

def normalize_channel(text):
    t = text.upper()
    m = re.search(r"CCTV\s*-?\s*(\d+)\s*\+?|CCTV(\d+)\s*\+?|央视\s*(\d+)", t)
    if not m:
        return None
    n = next(g for g in m.groups() if g)
    plus = "+" if "+" in t or "PLUS" in t else ""
    if n == "5" and plus:
        return "5+"
    return n

def fetch_url(url, timeout=10):
    try:
        r = subprocess.run(
            ["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", str(timeout),
             "-w", "\\n__CURL_META__ %{http_code} %{size_download}", url],
            capture_output=True, text=True, timeout=timeout+3)
        out = r.stdout
        meta = re.search(r"__CURL_META__ (\d+) (\d+)\s*$", out)
        if not meta:
            return 0, ""
        code = int(meta.group(1))
        body = out[:meta.start()].strip()
        return code, body
    except Exception as e:
        return 0, ""

def parse_entries(text, source_name):
    entries = []
    lines = [l.strip() for l in text.splitlines()]
    extinf = None
    for line in lines:
        if line.startswith("#EXTINF"):
            extinf = line
        elif extinf and (line.startswith("http://") or line.startswith("https://")):
            ch = normalize_channel(extinf)
            if ch:
                entries.append((ch, line, source_name))
            extinf = None
        elif not line.startswith("#"):
            extinf = None
    return entries

def is_media_playlist(body):
    return "#EXTINF" in body and ".ts" in body

def get_variant_url(master_url, master_body):
    # 找第一个 variant 路径（通常在 #EXT-X-STREAM-INF 下一行）
    m = re.search(r"#EXT-X-STREAM-INF[^\r\n]*[\r\n]+([^\r\n ]+)", master_body)
    if not m:
        return None
    sub = m.group(1).strip()
    if sub.startswith("http://") or sub.startswith("https://"):
        return sub
    return urljoin(master_url, sub)

def main():
    all_entries = []
    # 本地文件
    for f in CANDIDATE_FILES:
        if not os.path.exists(f):
            continue
        with open(f, encoding="utf-8", errors="ignore") as fp:
            all_entries.extend(parse_entries(fp.read(), os.path.basename(f)))
    # 在线源
    for name, url in ONLINE_SOURCES:
        code, body = fetch_url(url, timeout=15)
        print(f"[在线] {name}: HTTP {code}, 大小 {len(body)}")
        if code == 200 and body:
            all_entries.extend(parse_entries(body, name))

    print(f"\n共收集到 {len(all_entries)} 个央视候选 URL\n")

    # 按频道聚合去重
    by_ch = {k: [] for k in CANONICAL}
    for ch, url, src in all_entries:
        if ch in by_ch and url not in [u for u, _, _ in by_ch[ch]]:
            by_ch[ch].append((url, src, None))

    # 实测
    results = {}
    for ch, items in by_ch.items():
        tested = []
        print(f"===== CCTV-{ch} ({CANONICAL[ch][1]}) 候选 {len(items)} 个 =====")
        for url, src, _ in items[:12]:  # 每个频道最多测 12 个，避免太久
            code, body = fetch_url(url, timeout=8)
            if code != 200 or not body or not body.startswith("#EXTM3U"):
                print(f"  skip {src}: master {code}")
                continue
            if is_media_playlist(body):
                ok = True
                vcode = 200
                vurl = url
                print(f"  OK {src}: media playlist (direct .ts) {url}")
            else:
                vurl = get_variant_url(url, body)
                if not vurl:
                    print(f"  skip {src}: no variant")
                    continue
                vcode, vbody = fetch_url(vurl, timeout=8)
                ok = vcode == 200 and vbody and ("#EXTINF" in vbody or ".ts" in vbody)
                print(f"  {'OK' if ok else 'FAIL'} {src}: master={code} variant={vcode} {url}")
            tested.append({"url": url, "src": src, "ok": ok, "vcode": vcode, "vurl": vurl})
            if ok:
                break  # 找到一个可播就停
        results[ch] = tested

    # 生成报告
    print("\n\n===== 每个频道最终可用 URL =====")
    selected = {}
    for ch, items in results.items():
        ok_items = [i for i in items if i["ok"]]
        if ok_items:
            selected[ch] = ok_items[0]
            print(f"CCTV-{ch}: {ok_items[0]['url']} ({ok_items[0]['src']})")
        else:
            print(f"CCTV-{ch}: 无可用 URL")

    # 写报告 JSON
    with open("/workspace/cctv_test_report.json", "w", encoding="utf-8") as f:
        json.dump({k: [{"url": i["url"], "src": i["src"], "ok": i["ok"], "vcode": i["vcode"]} for i in v]
                   for k, v in results.items()}, f, ensure_ascii=False, indent=2)

    # 生成 m3u（只包含有可用 URL 的频道）
    lines = ['#EXTM3U x-tvg-url="http://epg.51zmt.top:8000/e.xml"',
             "# 央视公开源优选（全国通用，master+variant 实测 200）"]
    for ch in sorted(selected.keys(), key=lambda x: (len(x), x)):
        tid, name = CANONICAL[ch]
        url = selected[ch]["url"]
        logo = f"https://tb.zbds.top/logo/{tid.upper()}.png" if ch != "5+" else "https://tb.zbds.top/logo/CCTV-5+.png"
        lines.append(f'#EXTINF:-1 tvg-name="{tid}" tvg-id="{tid}" tvg-logo="{logo}" group-title="央视频道",{name}')
        lines.append(url)
    with open("/workspace/aptv_cctv优选.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n已生成 /workspace/aptv_cctv优选.m3u（{len(selected)} 个频道）")

if __name__ == "__main__":
    main()
