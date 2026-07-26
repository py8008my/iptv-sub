# APTVA 直播源订阅配�?

> 已实测可用的 IPTV 订阅链接 + 本地生成的订阅文件，直接复制�? APTV 即可订阅�?

---

## �? 你的专属公网订阅链接（已部署完成�?

仓库 `py8008my/iptv-sub` 已创建并设为公开，`main` 分支根目录的 `index.m3u`�?599 条目）已上线�?**均已实测 HTTP 200**�?

| 优先�? | 链接 | 说明 |
|--------|------|------|
| **�? 立刻生效** | `https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@aa64ce523874727fad7e7de7b1f710899bfc3f13/index.m3u` | **jsDelivr 国内 CDN，指向最�? commit，立即生�?** |
| 稳定�? | `https://py8008my.github.io/iptv-sub/index.m3u` | **GitHub Pages**，自动随仓库更新，链接永远不变（�? 1 分钟重建�? |
| 直链 | `https://raw.githubusercontent.com/py8008my/iptv-sub/main/index.m3u` | GitHub 官方 raw 直链，全球可�? |

---

## 二、当前源构成（第五版 · 央视官方直链�?

针对�?**深圳**的网络环境做了优化，央视频道已换�?**央视官网同款、全国可�?**的官方直播源�?

- **央视频道（CCTV-1 ~ CCTV-17 + CCTV-5+，共 18 台）**：已换成 **央视官网（cntv）官方直�? CDN 直链**，取自央�? HTML5 播放�? `js.player.cntv.cn` 内硬编码的六�? CDN 地址。本次选用**腾讯�? CDN**（`liveplay.myqcloud.com`）——它是央视全量频道的镜像源（1~17 �? 5+ 全部 200），且腾讯云在广�?/深圳为本地节点，**延迟最低、最�?**�?
  - 格式：`http://ldncctvwbcdtxy.liveplay.myqcloud.com/ldncctvwbcd/cdrmldcctv<N>_1/index.m3u8`
  - **无需签名、无需 Referer、无地域限制**，浏览器/播放器可直接拉流；切片为当天实时值，确为真实直播流�?
  - 画质：CCTV-1 主列表自�? **1080P / 720P** 两档；其余频道为 **960×540** 流畅档（电视观看足够清晰）�?
- **卫视 / 地方�? / 其他**：保�? vbskycn + best-fan + iptv-org 全国 CDN 聚合源（每个频道多个备选），个别卫视若超时，试同名带「[备选]」的条目�?

> 历版演进（为什么前面几版都卡）�?
> - iptv-org 全球�? �? CCTV 流在海外节点，延�? 2s+
> - fanmingming �? 广东联通内网源，深圳非联通访问全超时
> - vbskycn/best-fan 聚合 �? 源混杂，部分稳定部分超时
> - 中国移动 IPTV（黑龙江移动 `ottrrs.hl.chinamobile.com`）→ 跨省访问全超�?
>
> **本次直接从央视官网播放器扒出官方 CDN 直链**，绕开一切第三方中转与运营商限制——只要在国内（任意运营商/地域）能开腾讯云，就能稳定看央视直播。这是目前最稳、最"根正苗红"的方案�?

---

## 三、如何更新你的专属源

```bash
cd /workspace
git add index.m3u aptv_cctv�ٷ�.m3u
git commit -m "update channels"
git push
# Pages �? 1 分钟重建；jsDelivr @main 几分钟内刷新
```

> 每次 push �? commit SHA 会变，带 `@aa64ce5` �? jsDelivr 链接需跟着变；**长期用建议直接用 Pages 链接**（自动更新，链接不变）�?

---

## 四、央视官方源（可单独订阅�?

如果只想看央视，直接用这个独立文件即可（18 个央视频道，央视官网官方 CDN 直链，全国可播）�?
- 文件：`aptv_cctv官方.m3u`
- 订阅：`https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@aa64ce523874727fad7e7de7b1f710899bfc3f13/aptv_cctv官方.m3u`
- �? Pages：`https://py8008my.github.io/iptv-sub/aptv_cctv官方.m3u`

---

## 五、立即可用的公开订阅链接（无需部署�?

| 名称 | 订阅链接 | 频道�? |
|------|----------|--------|
| **vbskycn iptv4（每日更新）** | `https://live.zbds.top/tv/iptv4.m3u` | 526 |
| **best-fan 国内合集（每日检测）** | `https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_all.m3u8` | 133 |
| **iptv-org 国内频道** | `https://iptv-org.github.io/iptv/countries/cn.m3u` | 151 |

---

## 六、本地生成的订阅文件（`/workspace`�?

| 文件 | 内容 | 频道�? |
|------|------|--------|
| `aptv_cctv官方.m3u` | **央视官方�?**：CCTV-1~17 + 5+ 官网腾讯�? CDN 直链（全国可播） | 18 |
| `aptv聚合国内�?.m3u` | vbskycn + best-fan + 全国 CDN 聚合（卫�?/地方台） | 650 |
| `aptv_vbskycn.m3u` | vbskycn iptv4 原始�? | 526 |
| `aptv_bestfan.m3u` | best-fan cn_all 原始�? | 133 |

> 本地导入：把 `.m3u` 传到 iPhone/电脑，在 APTVA 选「本地文件」导入，无需联网�?

---

## 七、电子节目单（EPG�?

当前线上 `index.m3u` 已内�? EPG 地址�?
```
http://epg.51zmt.top:8000/e.xml
```
�? APTVA 未自动加载，在「EPG 地址」里手动粘贴即可�?

---

## 八、安全与注意事项

- **撤销部署用的 Token**：本次部署用�? GitHub Personal Access Token 仅具 `repo` 权限且已完成任务，建议去 GitHub �? **Settings �? Developer settings �? Personal access tokens** 把它删掉，零残留�?
- **卫视�?**：央视频道已换官方源；卫�?/地方台仍用第三方聚合源，深圳移动下多数可用，个别不稳定属正常�?
- **版权**：以上均为公开免费流聚合，请勿用于商业转播�?
