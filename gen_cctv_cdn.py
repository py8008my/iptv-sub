#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
央视官方多CDN直连生成器
验证 master -> 变体 -> .ts 三层链路，为每个频道生成多条不同CDN的备用线路。
所有地址均为 https，且为央视自建商用CDN（阿里云/网宿/百度/金山/腾讯），全国通用。
"""
import json
import urllib.request
import urllib.parse
import concurrent.futures as cf

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
REF = "https://tv.cctv.com/live/"

# 央视官方六套CDN（按国内通用性排序：阿里云 > 网宿 > 百度 > 金山 > 腾讯）
CDNS = [
    ("阿里云", "ldncctvwbcdali.v.myalicdn.com"),
    ("网宿",   "ldncctvwbcdcnc.v.wscdns.com"),
    ("百度",   "ldncctvwbcdbd.a.bdydns.com"),
    ("金山",   "ldncctvwbcdks.v.kcdnvip.com"),
    ("腾讯",   "ldncctvwbcdtxy.liveplay.myqcloud.com"),
]

# 频道: (显示名, cctv编号, tvg-id, logo编号)
CHANNELS = [
    ("CCTV-1 综合",     "cctv1_1",   "CCTV1",     "CCTV1"),
    ("CCTV-2 财经",     "cctv2_1",   "CCTV2",     "CCTV2"),
    ("CCTV-3 综艺",     "cctv3_1",   "CCTV3",     "CCTV3"),
    ("CCTV-4 中文国际", "cctv4_1",   "CCTV4",     "CCTV4"),
    ("CCTV-5 体育",     "cctv5_1",   "CCTV5",     "CCTV5"),
    ("CCTV-5+ 体育赛事","cctv5plus_1","CCTV5PLUS","CCTV5+"),
    ("CCTV-6 电影",     "cctv6_1",   "CCTV6",     "CCTV6"),
    ("CCTV-7 国防军事", "cctv7_1",   "CCTV7",     "CCTV7"),
    ("CCTV-8 电视剧",   "cctv8_1",   "CCTV8",     "CCTV8"),
    ("CCTV-9 纪录",     "cctv9_1",   "CCTV9",     "CCTV9"),
    ("CCTV-10 科教",    "cctv10_1",  "CCTV10",    "CCTV10"),
    ("CCTV-11 戏曲",    "cctv11_1",  "CCTV11",    "CCTV11"),
    ("CCTV-12 社会与法","cctv12_1",  "CCTV12",    "CCTV12"),
    ("CCTV-13 新闻",    "cctv13_1",  "CCTV13",    "CCTV13"),
    ("CCTV-14 少儿",    "cctv14_1",  "CCTV14",    "CCTV14"),
    ("CCTV-15 音乐",    "cctv15_1",  "CCTV15",    "CCTV15"),
    ("CCTV-16 奥林匹克","cctv16_1",  "CCTV16",    "CCTV16"),
    ("CCTV-17 农业农村","cctv17_1",  "CCTV17",    "CCTV17"),
]

LOGO = "https://live.fanmingming.com/tv/{}.png"


def fetch(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": REF})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read().decode("utf-8", "ignore")
    except Exception as e:
        return 0, str(e)


def check(host, cid):
    """检查 master -> 变体 -> .ts 三层链路是否完整"""
    base = "https://{}".format(host)
    master = "{}/ldncctvwbcd/cdrm{}/index.m3u8".format(base, "ld" + cid)
    code, body = fetch(master)
    if code != 200 or "#EXTM3U" not in body:
        return None, "master {}".format(code)

    # 找一条变体（优先中等码率，稳定性好）
    lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#")]
    if not lines:
        # master 本身就是媒体列表
        if ".ts" in body:
            return master, "direct"
        return None, "no variant"

    # 优先挑 hd/480P/BR=hd 这类中码率
    pick = None
    for kw in ("hd", "480P", "576P", "ud"):
        for l in lines:
            if kw in l:
                pick = l
                break
        if pick:
            break
    if not pick:
        pick = lines[0]

    vurl = urllib.parse.urljoin(master, pick)
    vcode, vbody = fetch(vurl)
    if vcode != 200 or ".ts" not in vbody:
        return None, "variant {}".format(vcode)

    # 验证 .ts 真能下
    seg = None
    for l in vbody.splitlines():
        l = l.strip()
        if l and not l.startswith("#") and ".ts" in l:
            seg = urllib.parse.urljoin(vurl, l)
            break
    if seg:
        req = urllib.request.Request(seg, headers={"User-Agent": UA, "Referer": REF})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read(8192)
                if len(data) < 1000:
                    return None, "ts too small"
        except Exception as e:
            return None, "ts {}".format(str(e)[:30])

    # 返回 master（播放器会自己选码率）
    return master, "ok"


def main():
    results = {}
    tasks = []
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        for disp, cid, tvg, logo in CHANNELS:
            for cdnname, host in CDNS:
                tasks.append((disp, cid, tvg, logo, cdnname, host,
                              ex.submit(check, host, cid)))
        for disp, cid, tvg, logo, cdnname, host, fut in tasks:
            url, msg = fut.result()
            results.setdefault(disp, {"cid": cid, "tvg": tvg, "logo": logo, "ok": [], "fail": []})
            if url:
                results[disp]["ok"].append((cdnname, url))
            else:
                results[disp]["fail"].append((cdnname, msg))

    out = ["#EXTM3U x-tvg-url=\"https://live.fanmingming.com/e.xml\""]
    report = {}
    total_ok = 0
    for disp, cid, tvg, logo in CHANNELS:
        r = results[disp]
        oks = r["ok"]
        # 按 CDNS 顺序排序
        order = {n: i for i, (n, _) in enumerate(CDNS)}
        oks.sort(key=lambda x: order.get(x[0], 99))
        print("=== {}  可用 {}/{}".format(disp, len(oks), len(CDNS)))
        for n, u in oks:
            print("   OK   [{}] {}".format(n, u))
        for n, m in r["fail"]:
            print("   FAIL [{}] {}".format(n, m))
        report[disp] = {"ok": [{"cdn": n, "url": u} for n, u in oks],
                        "fail": [{"cdn": n, "msg": m} for n, m in r["fail"]]}
        total_ok += len(oks)
        for idx, (n, u) in enumerate(oks):
            label = disp if idx == 0 else "{} [{}]".format(disp, n)
            out.append(
                '#EXTINF:-1 tvg-id="{}" tvg-name="{}" tvg-logo="{}" group-title="央视频道",{}'.format(
                    tvg, disp, LOGO.format(logo), label))
            out.append(u)

    with open("/workspace/aptv_cctv优选.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    with open("/workspace/cctv_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n生成完成：{} 个频道，{} 条线路".format(len(CHANNELS), total_ok))


if __name__ == "__main__":
    main()
