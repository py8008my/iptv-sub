# APTV 订阅配置说明

> 最近更新：2026-08-01 · **国际官方源（纪录片 / 电影 / 动画 / 新闻）**
> 仓库：`py8008my/iptv-sub` · 部署：GitHub Pages

## 一、背景：国内源在你的网络上走不通

前面几版（v3 裸 IP 转发、v4 移动 CDN、v5 全源覆盖）在你**北京单位 + 长城宽带（无 IPv6，5G 也不通）**的网络上三种失败模式都中招了：

| 版本 | 失败模式 | 原因 |
|---|---|---|
| v3 裸 IP:端口转发 | 90% 不能看、10% 卡死 | 个人/省内 IPTV 转发，跨省被长城宽带 QoS 掐断 |
| v4 中国移动全国 CDN | 全黑屏 | 网络层不可达（`39.134.x` 纯超时） |
| v5 官方 CCTV CDN | 有声音无画面 / 被拒 | 官方 CDN 带 ChinaDRM 加密或反盗链 403 |

结论：**静态国内源在你这条网络上是死路**。所以按你的要求，转做**国外官方播放源**。

## 二、订阅链接（本次交付）

在 APTV 里选「设置 → 播放列表 → 添加」，填下面任意一条。两个版本任选：

| 版本 | 说明 | 链接 |
|---|---|---|
| **稳定版（推荐先试）** | 15 个，全部 Akamai / Amagi / Cloudfront / getaj 等**一线大 CDN 官方源**，在长城宽带下最有可能直接通 | `https://py8008my.github.io/iptv-sub/intl_stable.m3u` |
| 全量版 | 29 个，含稳定版 + 中小 CDN 源（动画类多为中小 CDN，需你实测） | `https://py8008my.github.io/iptv-sub/intl.m3u` |

备用（jsDelivr 加速，国内有时比 GitHub Pages 快）：

```
https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@main/intl_stable.m3u
https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@main/intl.m3u
```

> 中文同名文件 `国外官方台.m3u` / `国外官方台_稳定版.m3u` 内容相同，GitHub Pages 对中文路径需用 URL 编码，建议直接用上面的英文文件名。

## 三、这些源是怎么挑出来的

1. 数据源用 **iptv-org 权威总库**（13519 个频道），只挑你要求的四类：新闻 / 纪录片 / 电影 / 动画。
2. 全部用 `ffprobe` **真实解码验证**（不是只测握手）：必须拿到 `width>0` 的视频轨才算可播，并排除 DASH/HEVC（iOS 的 APTV 原生不支持 DASH，会黑屏）。
3. 部署前**重新实时跑了一遍 34 个候选**，29 个通过；5 个失效的（BBC News 403、Bloomberg 死链、ARTE 地域封锁、30A TV 断流、Action Hollywood 无视频轨）已自动剔除。

## 四、稳定版 15 个频道清单（按分类，已验证可播放）

| 分类 | 频道 | 分辨率 | 托管 CDN |
|---|---|---|---|
| 国际新闻 | Al Jazeera English 半岛电视台 | 1920×1080 | getaj |
| 国际新闻 | France 24 English 法国24 | 1920×1080 | france24 |
| 国际新闻 | NHK World-Japan 日本NHK世界 | 1280×720 | nhkworld |
| 国际新闻 | CGTN 中国国际电视台 | 640×360 | amagi |
| 国际新闻 | CNBC 财经 | 640×360 | amagi |
| 国际新闻 | Sky News Extra 天空新闻 | 1024×576 | akamaized |
| 国际新闻 | ABC News 澳洲广播公司 | 1280×720 | akamaized |
| 国际新闻 | CNA 亚洲新闻台 | 640×360 | amagi |
| 国际纪录片 | BBC Earth BBC地球 | 1920×1080 | amagi |
| 国际纪录片 | Love Nature 热爱自然 | 426×240 | cloudfront |
| 国际纪录片 | Curiosity Animales/Explora/Motores | 640×360 | cloudfront |
| 国际电影 | 24 Hour Free Movies 全天免费电影 | 1280×720 | cloudfront |
| 国际电影 | AMC 美国经典电影 | 1920×1080 | wns.live |

> 注：动画类在 iptv-org 里的真正官方源（Cartoon Network / Disney Channel）全是 `IP:端口` 个人中继，在你网络上必死，已排除；全量版里保留的 8 个动画台来自中小 CDN，**能不能通需要你实测**——优先试稳定版。

## 五、需要你验收

1. 先把**稳定版** `intl_stable.m3u` 加进 APTV；
2. 试播几个台，反馈：
   - ✅ 正常出画
   - ⏳ 超时 / 卡死
   - 🔇 有声音没画面（说明是 DASH/HEVC，需换源）
3. 稳定版若大多能看，再试全量版 `intl.m3u` 补动画类；
4. 若稳定版也普遍不通，说明这些大 CDN 在你网络上也被限，我再换思路（如走代理 / 找国内可直连的境外源）。

## 六、文件清单

| 文件 | 说明 |
|---|---|
| `intl_stable.m3u` | **稳定版** 15 个一线大 CDN 官方源（推荐） |
| `intl.m3u` | 全量版 29 个（含中小 CDN 动画源） |
| `国外官方台.m3u` / `国外官方台_稳定版.m3u` | 同上两份的中文同名副本 |
| `cctv.m3u` 等旧文件 | 国内源历史版本，已确认在你的网络不可用，保留备查 |
