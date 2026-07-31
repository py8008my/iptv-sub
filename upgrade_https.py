#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把播放列表里的 http:// 地址逐个探测，能走 https 的一律升级。
原因：iOS 的 App Transport Security 默认拦截明文 http 流，
      APTV 里表现就是"转圈 / 动也不动"。
"""
import urllib.request
import urllib.parse
import concurrent.futures as cf
from collections import OrderedDict

PATH = "/workspace/index.m3u"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")


def try_https(host):
    """按域名探测一次，能通就整域升级"""
    url = "https://{}/".format(host)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except urllib.error.HTTPError:
        # 有响应码就说明 TLS 通了（404/403 都算通）
        return True
    except Exception:
        return False


def main():
    lines = open(PATH, encoding="utf-8", errors="ignore").read().splitlines()

    hosts = OrderedDict()
    for l in lines:
        s = l.strip()
        if s.startswith("http://"):
            h = urllib.parse.urlparse(s).hostname
            if h:
                hosts[h] = None

    print("待探测域名: {}".format(len(hosts)))
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        futs = {h: ex.submit(try_https, h) for h in hosts}
        for h, f in futs.items():
            hosts[h] = f.result()

    okhosts = [h for h, v in hosts.items() if v]
    print("支持 https: {}/{}".format(len(okhosts), len(hosts)))
    for h in okhosts:
        print("  ↑ {}".format(h))
    for h, v in hosts.items():
        if not v:
            print("  × {} (保持http)".format(h))

    out = []
    up = 0
    for l in lines:
        s = l.strip()
        if s.startswith("http://"):
            h = urllib.parse.urlparse(s).hostname
            if h and hosts.get(h):
                s = "https://" + s[len("http://"):]
                up += 1
        out.append(s)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    total = sum(1 for l in out if l.startswith("http"))
    https = sum(1 for l in out if l.startswith("https://"))
    print("\n升级 {} 条".format(up))
    print("https 占比: {}/{} = {:.0%}".format(https, total, https / total))


if __name__ == "__main__":
    main()
