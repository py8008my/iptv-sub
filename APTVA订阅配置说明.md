# APTVA 直播源订阅配置

> 已实测可用的 IPTV 订阅链接 + 本地生成的订阅文件，直接复制到 APTV 即可订阅。

---

## ✅ 你的专属公网订阅链接（已部署完成）

仓库 `py8008my/iptv-sub` 已创建并设为公开，`main` 分支根目录的 `index.m3u`（617 条目）已上线，**均已实测 HTTP 200**：

| 优先级 | 链接 | 说明 |
|--------|------|------|
| **★ 立刻生效** | `https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@7b8d051/index.m3u` | **jsDelivr 国内 CDN，指向最新 commit，立即生效** |
| 稳定版 | `https://py8008my.github.io/iptv-sub/index.m3u` | **GitHub Pages**，自动随仓库更新，链接永远不变 |
| 直链 | `https://raw.githubusercontent.com/py8008my/iptv-sub/main/index.m3u` | GitHub 官方 raw 直链，全球可达 |

---

## 二、当前源构成（第四版）

针对你**深圳 + 中国移动**的网络环境做了优化：

- **央视频道（CCTV-1 ~ CCTV-17，共 18 台）**：已换成 **中国移动 IPTV 官方源**（黑龙江移动 PLTV 服务 `ottrrs.hl.chinamobile.com`）。这是运营商级官方源，清晰度稳、延迟低，在移动网络下应可流畅播放。
- **卫视 / 地方台 / 其他**：保留 vbskycn + best-fan + iptv-org 全国 CDN 聚合源（每个频道多个备选），个别卫视若超时，试同名带「[备选]」的条目。

> 之前几版为什么卡：
> - iptv-org 全球源 → CCTV 流在海外节点，延迟 2s+
> - fanmingming → 广东联通内网源，深圳移动访问全超时
> - vbskycn/best-fan 聚合 → 源混杂，部分稳定部分超时
>
> 这次央视频道切到**你所在运营商（移动）的官方直播源**，是公开方案里最稳的选择。

---

## 三、如何更新你的专属源

```bash
cd /workspace
git add index.m3u
git commit -m "update channels"
git push
# Pages 约 1 分钟重建；jsDelivr @main 几分钟内刷新
```

> 每次 push 后 commit SHA 会变，带 `@7b8d051` 的 jsDelivr 链接需跟着变；**长期用建议直接用 Pages 链接**（自动更新，链接不变）。

---

## 四、央视官方源（可单独订阅）

如果只想看央视，直接用这个独立文件即可：
- 文件：`aptv_cctv移动.m3u`（18 个央视频道，移动 IPTV 官方源）
- 订阅：`https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@7b8d051/aptv_cctv移动.m3u`

---

## 五、立即可用的公开订阅链接（无需部署）

| 名称 | 订阅链接 | 频道数 |
|------|----------|--------|
| **vbskycn iptv4（每日更新）** | `https://live.zbds.top/tv/iptv4.m3u` | 526 |
| **best-fan 国内合集（每日检测）** | `https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_all.m3u8` | 133 |
| **iptv-org 国内频道** | `https://iptv-org.github.io/iptv/countries/cn.m3u` | 151 |

---

## 六、本地生成的订阅文件（`/workspace`）

| 文件 | 内容 | 频道数 |
|------|------|--------|
| `aptv_cctv移动.m3u` | **央视官方源**：CCTV-1~17 移动 IPTV（深圳移动可用） | 18 |
| `aptv聚合国内源.m3u` | vbskycn + best-fan + 全国 CDN 聚合（卫视/地方台） | 650 |
| `aptv_vbskycn.m3u` | vbskycn iptv4 原始源 | 526 |
| `aptv_bestfan.m3u` | best-fan cn_all 原始源 | 133 |

> 本地导入：把 `.m3u` 传到 iPhone/电脑，在 APTVA 选「本地文件」导入，无需联网。

---

## 七、电子节目单（EPG）

当前线上 `index.m3u` 已内置 EPG 地址：
```
http://epg.51zmt.top:8000/e.xml
```
若 APTVA 未自动加载，在「EPG 地址」里手动粘贴即可。

---

## 八、安全与注意事项

- **撤销部署用的 Token**：本次部署用的 GitHub Personal Access Token 仅具 `repo` 权限且已完成任务，建议去 GitHub → **Settings → Developer settings → Personal access tokens** 把它删掉，零残留。
- **卫视源**：央视频道已换官方源；卫视/地方台仍用第三方聚合源，深圳移动下多数可用，个别不稳定属正常。
- **版权**：以上均为公开免费流聚合，请勿用于商业转播。
