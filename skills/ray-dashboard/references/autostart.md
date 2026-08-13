# 开机自启（launchd 常驻）

仪表盘是常驻服务，用 `KeepAlive` 让它随登录启动、崩溃自拉起。**这是持久配置，只在用户明确要求时安装。**

## plist 模板

存为 `~/Library/LaunchAgents/com.rays-brain.dashboard.plist`，把 `__VAULT__` 换成 vault 绝对路径、`__HOME__` 换成家目录：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>com.rays-brain.dashboard</string>
	<key>ProgramArguments</key>
	<array>
		<string>/usr/bin/env</string>
		<string>python3</string>
		<string>__VAULT__/50-系统/40-自动化/知识仪表盘/server.py</string>
		<string>--no-open</string>
		<string>--quiet</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
	<key>KeepAlive</key>
	<true/>
	<key>EnvironmentVariables</key>
	<dict>
		<key>PATH</key>
		<string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
		<key>RAYS_BRAIN</key>
		<string>__VAULT__</string>
	</dict>
	<key>StandardOutPath</key>
	<string>__HOME__/Library/Logs/rays-brain/dashboard.launchd.log</string>
	<key>StandardErrorPath</key>
	<string>__HOME__/Library/Logs/rays-brain/dashboard.launchd.log</string>
	<key>ProcessType</key>
	<string>Background</string>
</dict>
</plist>
```

## 装载与验证

```bash
launchctl load ~/Library/LaunchAgents/com.rays-brain.dashboard.plist
launchctl list | grep rays-brain          # 应出现 com.rays-brain.dashboard
curl -s http://127.0.0.1:8765/api/healthz # 应返回 {"ok": true, ...}
```

## 注意

- 装载前先把手动启动的实例 `stop` 掉，否则端口冲突导致 launchd 反复重启。
- 卸载：`launchctl unload ~/Library/LaunchAgents/com.rays-brain.dashboard.plist`。
- 采集管线的三个定时任务是另一套 plist（见 rays-brain-kit 的 `定时任务/`），与本服务互相独立。
