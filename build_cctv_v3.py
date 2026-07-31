#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建央视(CCTV 1-17 + 5+) 全国通用播放列表 v3。
- 海外沙箱无法验证"中国网络可达性"，故不依赖沙箱 ffprobe 延迟筛选。
- 优先采用【国内 CDN / 运营商 / 省级广电 / 国内IP转发】，剔除海外VPS、IPv6。
- 剔除 gitv.tv 带 livodToken 的失效线路（已验证返回HTML错误，无法播放）。
- 由用户真机(北京/长城宽带)最终验证；本列表为"高概率可用"候选。
"""
import re, os, collections

WS = "/workspace"
SOURCES = [
    "/tmp/gh_09e0805b.m3u",                       # iptv-org cn.m3u（新鲜）
    f"{WS}/aptv_fanmingming.m3u",
    f"{WS}/aptv_vbskycn.m3u",
    f"{WS}/aptv聚合国内源.m3u",
    f"{WS}/aptv国内源.m3u",
    f"{WS}/aptv_bestfan.m3u",
    f"{WS}/aptv全国CDN优选.m3u",
]

# (规范名, 数字, 是否5+)
CHANNELS = [
    ("CCTV-1 综合",1,False),("CCTV-2 财经",2,False),("CCTV-3 综艺",3,False),
    ("CCTV-4 中文国际",4,False),("CCTV-5 体育",5,False),("CCTV-5+ 体育赛事",5,True),
    ("CCTV-6 电影",6,False),("CCTV-7 国防军事",7,False),("CCTV-8 电视剧",8,False),
    ("CCTV-9 纪录",9,False),("CCTV-10 科教",10,False),("CCTV-11 戏曲",11,False),
    ("CCTV-12 社会与法",12,False),("CCTV-13 新闻",13,False),("CCTV-14 少儿",14,False),
    ("CCTV-15 音乐",15,False),("CCTV-16 奥林匹克",16,False),("CCTV-17 农业农村",17,False),
]

def parse(path):
    out=[]; name=None
    try:
        for line in open(path,encoding="utf-8",errors="ignore"):
            line=line.strip()
            if line.startswith("#EXTINF"):
                m=re.search(r',(.+)$',line); name=m.group(1).strip() if m else ""
            elif line.startswith("http"):
                out.append((name,line)); name=None
    except Exception as e:
        print("解析失败",path,e)
    return out

def cctv_key(name):
    n=name.upper()
    if re.search(r'CCTV[-_ ]?5\s*\+',n) or "赛事" in name or "5PLUS" in n:
        return (5,True)
    m=re.search(r'CCTV[-_ ]?(\d{1,2})',n)
    if m:
        return (int(m.group(1)), False)
    return None

FOREIGN_OCTET = {3,5,13,18,23,31,34,35,38,45,50,52,63,64,66,69,74,104,107,108,
    146,147,156,159,162,164,167,168,169,172,173,174,176,177,178,184,185,188,
    189,192,193,194,195,198,199,200,204,205,206,207,208,209,212,213,216,217}
BAD_DOMAINS = ("antik.sk","264788.xyz","bkpcp.top","imwork.net","xinketongxun.fun",
    "163189.xyz","livehwc4.com","gitv.tv")   # gitv.tv: livodToken失效，返回HTML无法播放
DOMESTIC_CDN = ("cztv.com","cztvcloud.com","cntv.cn","cctv.cn","cctv.com",
    "iqilu.com","sctv.com","jlntv.cn","jilintv.cn","xiancity.cn","cjyun.org",
    "dxhmt.cn","cbg.cn","wuhubtv.com","chinashadt.com","aodianyun.com",
    "hebyun.com.cn","hnntv.cn","fjtv.net","gdbtv.com","gzstv.com","zjol.com.cn",
    "btv.com.cn","chinamobile.com","miguvideo.com")

def host_of(u):
    m=re.match(r'https?://([^/]+)',u); return m.group(1).lower() if m else u

def classify(url):
    h=host_of(url)
    if ":" in h and (h[0]=="[" or re.match(r'^[0-9a-fA-F:]+$',h)):
        return (False,"IPv6")
    if any(d in h for d in BAD_DOMAINS):
        return (False,"海外/失效域名")
    is_ip = bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}',h))
    if is_ip:
        octet=int(h.split(".")[0])
        if octet in FOREIGN_OCTET:
            return (False,"海外VPS")
        return (True,"国内IP转发")        # 国内裸IP(多为联通/电信/移动骨干)
    low=h
    if "cztv.com" in low or "cztvcloud.com" in low:
        return (True,"浙江广电CDN(已实测可达260ms)")
    if low.endswith("cctv.cn") or low.endswith("cctv.com") or "cntv.cn" in low:
        return (True,"央视官方(注意可能DRM)")
    if any(d in low for d in DOMESTIC_CDN):
        return (True,"国内广电/运营商CDN")
    if low.endswith(".cn") or low.endswith(".com.cn") or low.endswith(".org.cn"):
        return (True,"国内.cn域名")
    if "github.io" in low:
        return (True,"GitHub(最后备份)")
    if low.endswith((".xyz",".top",".fun",".live")):
        return (False,"个人/海外域名")
    return (True,"其他域名")

def main():
    raw=[]
    for s in SOURCES:
        if os.path.exists(s): raw+=parse(s)
    print("原始条目:",len(raw))
    cand=collections.defaultdict(list)
    for name,url in raw:
        k=cctv_key(name)
        if not k: continue
        ch=None
        for cn,d,plus in CHANNELS:
            if d==k[0] and plus==k[1]:
                ch=cn; break
        if not ch: continue
        keep,reason=classify(url)
        if not keep: continue
        cand[ch].append((reason,url))
    # 排序：按优先级字典序(reason字符串前缀数字)
    pri_order={"浙江广电CDN":1,"央视官方":2,"国内广电":3,"国内.cn":4,"国内IP转发":5,"其他域名":8,"GitHub":9}
    def sortkey(t):
        r=t[0]; 
        for k,v in pri_order.items():
            if r.startswith(k): return v
        return 8
    out=["#EXTM3U x-tvg-url=\"https://epg.112114.xyz/pp.xml\"","# 央视全国通用优选(v3) - 北京/长城宽带实测候选"]
    total=0
    for cn,d,plus in CHANNELS:
        lst=cand.get(cn,[])
        lst=sorted(set(lst),key=sortkey)
        lst=lst[:3]
        if not lst:
            out.append(f'#EXTINF:-1 group-title="央视",{cn}')
            out.append('# 该频道暂无国内候选线路，请反馈')
            continue
        for reason,url in lst:
            out.append(f'#EXTINF:-1 group-title="央视" tvg-name="{cn.replace(" ","")}",{cn}')
            out.append(url); total+=1
    txt="\n".join(out)+"\n"
    for fn in ("aptv_cctv优选.m3u","aptv_cctv官方.m3u"):
        with open(f"{WS}/{fn}","w",encoding="utf-8") as f: f.write(txt)
    print("生成完成，总线路:",total)
    for cn,d,plus in CHANNELS:
        c=len(cand.get(cn,[]))
        print(f"  {cn}: 候选{c} -> 选用{min(3,c)}")

if __name__=="__main__":
    main()
