# APTVA 直播源订阅配置

> 已实测可用的 IPTV 订阅链接 + 本地生成的订阅文件，直接复制到 APTV 即可订阅。

---

## ? 你的专属公网订阅链接（已部署完成）

仓库 `py8008my/iptv-sub` 已创建并设为公开，`main` 分支根目录的 `index.m3u`（599 条目）已上线，**均已实测 HTTP 200**：

| 优先级 | 链接 | 说明 |
|--------|------|------|
| **★ 立刻生效** | `https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@c179dc8/index.m3u` | **jsDelivr 国内 CDN，指向最新 commit，立即生效** |
| 稳定版 | `https://py8008my.github.io/iptv-sub/index.m3u` | **GitHub Pages**，自动随仓库更新，链接永远不变（约 1 分钟重建） |
| 直链 | `https://raw.githubusercontent.com/py8008my/iptv-sub/main/index.m3u` | GitHub 官方 raw 直链，全球可达 |

---

## 二、当前源构成（第五版 · 央视公开源优选）

- **央视频道（CCTV-1 ~ CCTV-17 + CCTV-5+，共 18 台）**：已换成**实测可播的公开源**。此前从央视官网播放器扒出的 `cntv` 六大 CDN 直链在 APTV 里能连但无法播放（子切片返回 404，疑似官方播放器内部做了额外校验），因此改为从 **vbskycn / best-fan / iptv-org** 等公开聚合源中逐台测试，筛选出 **master + .ts 切片均返回 200** 的 URL。
  - 来源包括各省运营商 IPTV 直链、个人 relay、海外公开节点等，共 18 条全部实测可播。
  - 画质以 720p/540p 为主，个别台为海外源；**央视 1/2/3/5/6/7/8/9/10/11/12/13/14/15/16/17/5+ 全覆盖**。
  - **全国通用说明**：免费公开源里不存在"100% 全国任意运营商任意省份都稳"的央视源（各省 IPTV 源本身有运营商/地域限制）。本版策略是**分散来源**（不同省份/不同 hosting），相比单一跨省移动 IPTV 或单一地区联通源，全国可播概率最高。
- **卫视 / 地方台 / 其他**：保留 vbskycn + best-fan + iptv-org 全国 CDN 聚合源（每个频道多个备选），个别卫视若超时，试同名带「[备选]」的条目。

> 历版演进：
> - iptv-org 全球源 → CCTV 流在海外节点，延迟 2s+
> - fanmingming → 广东联通内网源，非联通访问全超时
> - vbskycn/best-fan 聚合 → 源混杂，部分稳定部分超时
> - 中国移动 IPTV（黑龙江移动 `ottrrs.hl.chinamobile.com`）→ 跨省访问全超时
> - 央视官网 cntv 直链 → master 能取但切片 404，APTV 无法播放
>
> **本次改为实测可播的公开源**，至少保证当前 18 个央视 URL 在测试环境中 master + 切片均正常。

---

## 三、如何更新你的专属源

```bash
cd /workspace
git add index.m3u aptv_cctv官方.m3u
git commit -m "update channels"
git push
# Pages 约 1 分钟重建；jsDelivr @main 几分钟内刷新
```

> 每次 push 后 commit SHA 会变，带 `@c179dc8` 的 jsDelivr 链接需跟着变；**长期用建议直接用 Pages 链接**（自动更新，链接不变）。

---

## 四、央视公开源（可单独订阅）

如果只想看央视，直接用这个独立文件即可（18 个央视频道，实测可播公开源）：
- 文件：`aptv_cctv官方.m3u`
- 订阅：`https://cdn.jsdelivr.net/gh/py8008my/iptv-sub@c179dc8/aptv_cctv官方.m3u`
- 或 Pages：`https://py8008my.github.io/iptv-sub/aptv_cctv官方.m3u`

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
| `aptv_cctv官方.m3u` | **央视公开源优选**：CCTV-1~17 + 5+ 实测可播公开源 | 18 |
| `aptv_cctv优选.m3u` | 同上，生成过程中的中间文件 | 18 |
| `aptv_聚合国内源.m3u` | vbskycn + best-fan + 全国 CDN 聚合（卫视/地方台） | 650 |
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
- **卫视源**：央视频道已换实测可播公开源；卫视/地方台仍用第三方聚合源，个别不稳定属正常。
- **版权**：以上均为公开免费流聚合，请勿用于商业转播。
