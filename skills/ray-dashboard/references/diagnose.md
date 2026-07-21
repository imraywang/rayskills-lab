# 工作台诊断手册

按症状排查，动作从便宜到贵。任何一步修好就停。

## 页面打不开

1. `status` 探测：`running: false` → 直接 `start`；`true` 则是浏览器侧问题（换无痕窗口排除扩展）。
2. `start` 报端口占用 → `lsof -i :8765` 看占用者；是旧仪表盘就 `stop`，是别的服务就换 `--port`。
3. `start` 报"没有在预期时间内就绪" → 读返回的日志路径，常见原因是配置文件非法（`config.json` 未知键或越界路径会直接拒绝启动，错误信息里写了原因）。

## 页面能开但数据不对 / 很慢

- **计数为 0 或明显偏少**：确认服务的 `RAYS_BRAIN` 指向正确 vault（healthz 返回里有 vault 名）；再确认 vault 结构存在（缺目录先跑 bootstrap 或 ray-obsidian）。
- **iCloud vault 首次很慢**：文件可能未下载到本机。Finder 里对 vault 目录"立即下载"，或 `brctl download <目录>`。单个文件读不出不会拖垮整页（会被跳过），但内容会缺。
- **改了笔记页面没反应**：页面有 SSE 自动刷新，3–4 秒内应更新；没更新先手动刷新，再看服务日志里有无异常。

## 审核操作报错

- "这张卡已经处理，刷新后再试"：卡片状态已不是待审核（可能自动管线刚处理过），刷新即可，不是故障。
- "这张审核卡格式不完整"：卡片缺人工审核四选项，去 Obsidian 里检查该文件，通常是手工编辑破坏了格式。

## 升级后异常

- 浏览器强刷（Cmd+Shift+R）排除旧静态文件缓存。
- `check` 看 `differs`：非空说明本地代码与资产不一致，和用户确认是保留本地改动还是 `--upgrade` 对齐。

## 自启没生效

`launchctl list | grep rays-brain` 无输出说明 plist 没装载；对照 [autostart.md](autostart.md) 检查路径替换与 `launchctl load`。日志看 `~/.local/state/rays-brain/logs/dashboard.log`。
