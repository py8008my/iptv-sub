#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
央视频道源生成器（全国通用版）

核心原则：
1. 本沙箱位于境外，测试结论会反向失真——
   境外 VPS（38.x/63.x/69.x/74.x/104.x/173.x/198.x/204.x 等）在这里测得飞快，
   但国内用户访问必然超时卡死（就是"动也不动"的真凶）；
   而国内 CDN 常拒绝境外 IP，在这里显示失败，国内其实好用。
   => 因此按【域名归属】白名单筛选，不迷信连通性测试结果。
2. 一律 https（iOS ATS 会拦 http 流）。
3. 排除一切 IP:端口 形式的省内组播/单播（跨省跨运营商必死）。
4. 每个频道给多条不同 CDN 的备用线路，APTV 可手动切换。
"""
import re
import json
import urllib.request
import urllib.parse

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

# ---------- 1. 央视官方 CDN（已实测 master->变体->.ts 三层全通）----------
OFFICIAL_CDNS = [
    ("阿里云", "ldncctvwbcdali.v.myalicdn.com"),
    ("网宿",   "ldncctvwbcdcnc.v.wscdns.com"),
    ("百度",   "ldncctvwbcdbd.a.bdydns.com"),
    ("金山",   "ldncctvwbcdks.v.kcdnvip.com"),
    ("腾讯",   "ldncctvwbcdtxy.liveplay.myqcloud.com"),
]
# 官方宽带专线只免费开放 CCTV-1 / CCTV-13
OFFICIAL_IDS = {"CCTV-1 综合": "cdrmldcctv1_1", "CCTV-13 新闻": "cdrmldcctv13_1"}

# ---------- 2. 国内域名白名单（域名型 CDN，全国可达）----------
CN_DOMAIN_WHITELIST = [
    "myalicdn.com", "wscdns.com", "bdydns.com", "kcdnvip.com",
    "liveplay.myqcloud.com", "myhwcdn.cn",           # 央视六套CDN
    "miguvideo.com", "cmvideo.cn",                    # 咪咕
    "chinamobile.com", "dxhmt.cn",                    # 移动/电信虹魔方
    "cztvcloud.com", "cztv.com", "cztv.cc",           # 浙江广电云
    "hebyun.com.cn", "hebtv.com",                     # 河北云
    "cnr.cn",                                         # 央广
    "freetv.fun",                                     # 国内反代
    "jlntv.cn", "thmz.com", "hrbtv.net", "xntv.tv",   # 地方台
    "gztv.com", "zohi.tv", "habctv.com", "51kandianshi.com",
    "kankanlive.com", "qingting.fm", "kwimgs.com",
    "yangshipin.cn", "cctv.com", "cntv.cn",
]
# 明确排除：境外 VPS 段 + 一切裸 IP
BAD_IP_PREFIX = ("38.", "63.", "69.", "74.", "104.", "107.", "141.", "154.",
                 "156.", "172.", "173.", "185.", "192.151.", "198.", "204.",
                 "207.", "209.", "23.", "45.", "66.", "8.210.")

CHANNELS = [
    ("CCTV-1 综合",     "CCTV1",     "CCTV1"),
    ("CCTV-2 财经",     "CCTV2",     "CCTV2"),
    ("CCTV-3 综艺",     "CCTV3",     "CCTV3"),
    ("CCTV-4 中文国际", "CCTV4",     "CCTV4"),
    ("CCTV-5 体育",     "CCTV5",     "CCTV5"),
    ("CCTV-5+ 体育赛事","CCTV5PLUS", "CCTV5+"),
    ("CCTV-6 电影",     "CCTV6",     "CCTV6"),
    ("CCTV-7 国防军事", "CCTV7",     "CCTV7"),
    ("CCTV-8 电视剧",   "CCTV8",     "CCTV8"),
    ("CCTV-9 纪录",     "CCTV9",     "CCTV9"),
    ("CCTV-10 科教",    "CCTV10",    "CCTV10"),
    ("CCTV-11 戏曲",    "CCTV11",    "CCTV11"),
    ("CCTV-12 社会与法","CCTV12",    "CCTV12"),
    ("CCTV-13 新闻",    "CCTV13",    "CCTV13"),
    ("CCTV-14 少儿",    "CCTV14",    "CCTV14"),
    ("CCTV-15 音乐",    "CCTV15",    "CCTV15"),
    ("CCTV-16 奥林匹克","CCTV16",    "CCTV16"),
    ("CCTV-17 农业农村","CCTV17",    "CCTV17"),
]

SOURCES = [
    "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
    "https://live.zbds.top/tv/iptv4.m3u",
    "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u",
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
]

LOGO = "https://live.fanmingming.com/tv/{}.png"


def fetch(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception as e:
        print("  拉取失败 {}: {}".format(url[:60], e))
        return ""


def norm(name):
    """频道名归一化 -> CCTV1 / CCTV5PLUS 形式"""
    s = name.upper().replace(" ", "").replace("-", "").replace("_", "")
    s = s.replace("高清", "").replace("HD", "").replace("超清", "")
    s = s.replace("4K", "").replace("综合", "").replace("财经", "")
    if "5+" in s or "5PLUS" in s or "5＋" in s:
        return "CCTV5PLUS"
    m = re.match(r"^CCTV(\d{1,2})", s)
    if m:
        return "CCTV" + m.group(1)
    return None


def host_of(url):
    try:
        return urllib.parse.urlparse(url).hostname or ""
    except Exception:
        return ""


def is_good(url):
    """只保留 https + 国内白名单域名 + 非裸IP"""
    if not url.startswith("https://"):
        return False
    h = host_of(url)
    if not h:
        return False
    # 裸 IP 一律排除
    if re.match(r"^[\d.]+$", h) or ":" in h:
        return False
    if h.startswith(BAD_IP_PREFIX):
        return False
    return any(d in h for d in CN_DOMAIN_WHITELIST)


def main():
    pool = {}
    for src in SOURCES:
        print("拉取 {}".format(src[:70]))
        txt = fetch(src)
        if not txt:
            continue
        lines = txt.splitlines()
        cnt = 0
        for i, l in enumerate(lines):
            if not l.startswith("#EXTINF"):
                continue
            name = l.split(",")[-1].strip()
            key = norm(name)
            if not key:
                continue
            if i + 1 >= len(lines):
                continue
            url = lines[i + 1].strip()
            if not url.startswith("http"):
                continue
            if is_good(url):
                pool.setdefault(key, [])
                if url not in pool[key]:
                    pool[key].append(url)
                    cnt += 1
        print("  采纳 {} 条".format(cnt))

    out = ['#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"']
    report = {}
    total = 0

    for disp, tvg, logo in CHANNELS:
        key = norm(disp)
        lines_for_ch = []

        # 官方 CDN 优先（仅 CCTV-1 / CCTV-13）
        if disp in OFFICIAL_IDS:
            cid = OFFICIAL_IDS[disp]
            for cdnname, host in OFFICIAL_CDNS:
                lines_for_ch.append(
                    ("央视官方·" + cdnname,
                     "https://{}/ldncctvwbcd/{}/index.m3u8".format(host, cid)))

        # 国内白名单源补充（每个域名最多取1条，保证线路分散）
        seen_host = set()
        for u in pool.get(key, []):
            h = host_of(u)
            if h in seen_host:
                continue
            seen_host.add(h)
            lines_for_ch.append((h.split(".")[0], u))
            if len(lines_for_ch) >= 6:
                break

        report[disp] = [{"标签": n, "地址": u} for n, u in lines_for_ch]
        total += len(lines_for_ch)
        print("{}  -> {} 条线路".format(disp, len(lines_for_ch)))

        for idx, (label, u) in enumerate(lines_for_ch):
            title = disp if idx == 0 else "{} [{}]".format(disp, label)
            out.append(
                '#EXTINF:-1 tvg-id="{}" tvg-name="{}" tvg-logo="{}" '
                'group-title="央视频道",{}'.format(tvg, disp, LOGO.format(logo), title))
            out.append(u)

    with open("/workspace/aptv_cctv优选.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    with open("/workspace/cctv_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n完成：{} 个频道，共 {} 条线路".format(len(CHANNELS), total))


if __name__ == "__main__":
    main()
