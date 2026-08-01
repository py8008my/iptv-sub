import re, os, collections
WS="/workspace"
SOURCES=[f"{WS}/aptv_fanmingming.m3u",f"{WS}/aptv_vbskycn.m3u",f"{WS}/aptv聚合国内源.m3u",
 f"{WS}/aptv国内源.m3u",f"{WS}/aptv_bestfan.m3u",f"{WS}/aptv全国CDN优选.m3u",
 f"{WS}/aptv_央视测试.m3u",f"{WS}/aptv_cctv移动.m3u"]
CH=[("CCTV-1 综合",1,False),("CCTV-2 财经",2,False),("CCTV-3 综艺",3,False),
 ("CCTV-4 中文国际",4,False),("CCTV-5 体育",5,False),("CCTV-5+ 体育赛事",5,True),
 ("CCTV-6 电影",6,False),("CCTV-7 国防军事",7,False),("CCTV-8 电视剧",8,False),
 ("CCTV-9 纪录",9,False),("CCTV-10 科教",10,False),("CCTV-11 戏曲",11,False),
 ("CCTV-12 社会与法",12,False),("CCTV-13 新闻",13,False),("CCTV-14 少儿",14,False),
 ("CCTV-15 音乐",15,False),("CCTV-16 奥林匹克",16,False),("CCTV-17 农业农村",17,False)]
def parse(p):
    o=[];n=None
    for l in open(p,encoding="utf-8",errors="ignore"):
        l=l.strip()
        if l.startswith("#EXTINF"):
            m=re.search(r',(.+)$',l);n=m.group(1).strip() if m else ""
        elif l.startswith("http"):o.append((n,l));n=None
    return o
def key(n):
    u=n.upper()
    if re.search(r'CCTV[-_ ]?5\s*\+',u) or "赛事" in n or "5PLUS" in u:return(5,True)
    m=re.search(r'CCTV[-_ ]?(\d{1,2})',u)
    return (int(m.group(1)),False) if m else None
FOREIGN={3,5,13,18,23,31,34,35,38,45,50,52,63,64,66,69,74,104,107,108,146,147,156,
 159,162,164,167,168,169,172,173,174,176,177,178,184,185,188,189,192,193,194,195,
 198,199,200,204,205,206,207,208,209,212,213,216,217}
BAD=("antik.sk","264788.xyz","bkpcp.top","imwork.net","xinketongxun.fun","163189.xyz",
 "livehwc4.com","gitv.tv")
BIG=("myqcloud.com","wscdns.com","bdydns.com","kcdnvip.com","myalicdn.com","myhwcdn.cn",
 "livehwc4.com","chinamobile.com","migu","cmvideo","aliyun","qcloud","hwcloud")
CN_SITE=("cztv.com","cztvcloud.com","iqilu.com","sctv.com","jlntv.cn","jilintv.cn",
 "xiancity.cn","cjyun.org","dxhmt.cn","cbg.cn","wuhubtv.com","chinashadt.com",
 "hebyun.com.cn","hnntv.cn","fjtv.net","gdbtv.com","gzstv.com","zjol.com.cn","btv.com.cn")
def host(u):
    m=re.match(r'https?://([^/]+)',u);return m.group(1).lower() if m else u
def classify(u):
    h=host(u)
    if ":" in h and (h[0]=="[" or re.match(r'^[0-9a-fA-F:]+$',h)):return(False,-1,"IPv6")
    if "cdrm" in u.lower():return(False,-1,"DRM加密-有声无画")
    if any(d in h for d in BAD):return(False,-1,"失效/海外")
    lo=h
    if "cztv.com" in lo:return(True,1,"浙江广电CDN(已验证)")
    if any(b in lo for b in BIG):return(True,2,"大厂CDN(腾讯/网宿/百度/金山/阿里)")
    if "ldncctvwbnd" in lo:return(True,2,"央视官方非DRM")
    if lo.endswith("cctv.cn") or lo.endswith("cctv.com"):return(True,3,"央视官方(可能403/DRM)")
    if any(d in lo for d in CN_SITE):return(True,4,"省级广电官网")
    is_ip=bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}',h))
    if is_ip:
        o=int(h.split(".")[0])
        if o in FOREIGN:return(False,-1,"海外VPS")
        return(True,6,"国内骨干IP")
    if lo.endswith((".cn",".com.cn",".org.cn")):return(True,4,"国内.cn域名")
    if lo.startswith("https"):return(True,5,"HTTPS源")
    if "github.io" in lo:return(True,9,"GitHub备")
    if lo.endswith((".xyz",".top",".fun")):return(False,-1,"个人域名")
    return(True,7,"其他")
raw=[]
for s in SOURCES:
    if os.path.exists(s):raw+=parse(s)
cand=collections.defaultdict(list)
for n,u in raw:
    k=key(n)
    if not k:continue
    ch=None
    for cn,d,p in CH:
        if d==k[0] and p==k[1]:ch=cn;break
    if not ch:continue
    keep,pri,reason=classify(u)
    if not keep:continue
    cand[ch].append((pri,u,reason))
out=["#EXTM3U x-tvg-url=\"https://epg.112114.xyz/pp.xml\"",
 "# 央视优选 v5 终版-全源类型覆盖(大厂CDN非DRM/移动/cztv/国内骨干IP)"]
total=0
for cn,d,p in CH:
    lst=sorted(set(cand.get(cn,[])),key=lambda x:x[0])[:4]
    if not lst:
        out.append(f'#EXTINF:-1 group-title="央视",{cn}');out.append('# 无候选');continue
    for pri,u,reason in lst:
        out.append(f'#EXTINF:-1 group-title="央视" tvg-name="{cn.replace(" ","")}",{cn}')
        out.append(u);total+=1
open(f"{WS}/cctv.m3u","w").write("\n".join(out)+"\n")
open(f"{WS}/aptv_cctv优选.m3u","w").write("\n".join(out)+"\n")
open(f"{WS}/aptv_cctv官方.m3u","w").write("\n".join(out)+"\n")
print("v5生成,总线路:",total)
for cn,d,p in CH:print(f"  {cn}: {min(4,len(cand.get(cn,[])))}")
