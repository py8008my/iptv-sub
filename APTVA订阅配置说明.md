# APTV 订阅配置说明

> 最近更新：2026-08-01 · **国际主流官方源 v2（全主流品牌，已剔除中东/小地区/宗教源）**
> 仓库：`py8008my/iptv-sub` · 部署：GitHub Pages

## 一、订阅链接

在 APTV 里「设置 → 播放列表 → 添加」，填下面任意一条：

| 版本 | 说明 | 链接 |
|---|---|---|
| **稳定版（推荐先试）** | 19 个，全主流大厂 + Akamai/Amagi/Cloudfront 大 CDN | `https://py8008my.github.io/iptv-sub/intl_stable.m3u` |
| 全量版 | 22 个，稳定版 + 3 个动画（主流品牌但小 CDN，需实测） | `https://py8008my.github.io/iptv-sub/intl.m3u` |

jsDelivr 加速备用：

```
https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@main/intl_stable.m3u
https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@main/intl.m3u
```

## 二、这版改了什么（v2 vs v1）

上一版混进了中东/小地区/宗教野鸡源（Asharq Discovery、God Stands 儿童、Akili 肯尼亚、ERT 希腊、TV Artequatre 比利时、Cowboy Movie、ABN 圣经电影等），已**全部剔除**。本版只留全球主流品牌：

- **新闻 9 个**：France 24、Al Jazeera、NHK World、CGTN、CNBC、Sky News、CNA、Euronews、ABC News
- **纪录片 6 个**：BBC Earth、Love Nature、Curiosity×3、CGTN Documentary
- **电影 4 个**：AMC、MovieSphere(Lionsgate)、Hallmark、Gravitas
- **动画 3 个**：Nickelodeon、Disney XD、Nick Jr（主流品牌，但小 CDN 托管）

所有源均用 `ffprobe` 真实解码验证（拿到 `width>0` 视频轨），并排除 DASH/HEVC。

## 三、为什么动画类只有 3 个、且不是 Cartoon Network / Disney Channel

这是**免费公开源的硬限制**，不是我偷懒：

- iptv-org 总库里 Cartoon Network / Disney Channel / Nickelodeon 的真·官方源，**全是 `IP:端口` 个人中继**（如 `45.171.x:8888`、`206.212.x`），在你北京长城宽带 + 无 IPv6 的网络上必然卡死/不通，已排除。
- 聚合站 jmp2.uk 的 Nickelodeon/Disney 实测返回 400（需鉴权），也死了。
- 剩下能播的动画源只有 Nickelodeon(anixa)、Disney XD(aynascope)、Nick Jr(cinerama) 这几个**主流品牌 + 中小 CDN**——品牌是官方的，但 CDN 不够大，在长城宽带下能否通**需要你实测**。
- Discovery / National Geographic / History 同样没有大 CDN 免费版，故纪录片类未放。

> 想要 Cartoon Network / Disney Channel 这种级别的主流动画大厂源，免费公开源基本无解，得走付费 IPTV 或代理。如果你能接受，先把这 3 个动画台测了；如果不行，告诉我，我找别的途径。

## 四、稳定版 19 个频道清单（全大厂 + 大 CDN）

| 分类 | 频道 | 托管 |
|---|---|---|
| 国际新闻 | France 24 English | france24 |
| 国际新闻 | Al Jazeera English | getaj |
| 国际新闻 | NHK World-Japan | nhkworld |
| 国际新闻 | CGTN | amagi |
| 国际新闻 | CNBC | amagi |
| 国际新闻 | Sky News Extra | akamaized |
| 国际新闻 | CNA Originals | amagi |
| 国际新闻 | Euronews | akamaized |
| 国际新闻 | ABC News | akamaized |
| 国际纪录片 | BBC Earth | amagi |
| 国际纪录片 | Love Nature | cloudfront |
| 国际纪录片 | Curiosity Animales / Explora / Motores | cloudfront |
| 国际纪录片 | CGTN Documentary | amagi |
| 国际电影 | AMC | wns.live |
| 国际电影 | MovieSphere (Lionsgate) | amagi |
| 国际电影 | Hallmark Movies | cloudfront |
| 国际电影 | Gravitas Movies | cloudfront |

> 全量版 `intl.m3u` 另含动画：Nickelodeon、Disney XD、Nick Jr（主流品牌小 CDN）。

## 五、需要你验收

1. 先加**稳定版** `intl_stable.m3u`（19 个全大厂），试播几个；
2. 反馈：✅出画 / ⏳卡死 / 🔇有声音无画面（DASH/HEVC，需换源）；
3. 稳定版若大多能看，再试全量版 `intl.m3u` 补动画类；
4. 若稳定版也普遍不通，说明这些大 CDN 在你网络也被限，我再换思路（代理 / 国内可直连境外源）。

## 六、文件清单

| 文件 | 说明 |
|---|---|
| `intl_stable.m3u` | **稳定版** 19 个主流大厂源（推荐） |
| `intl.m3u` | 全量版 22 个（含动画小 CDN 源） |
| `国外官方台.m3u` / `国外官方台_稳定版.m3u` | 中文同名副本 |
| 旧 `cctv.m3u` 等 | 国内源历史版本，已确认在你的网络不可用 |
