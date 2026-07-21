---
name: ray-dashboard
description: 在用户的本地知识库上安装、启动、升级或诊断"知识工作台"——一个零依赖的本地网页仪表盘（总览、审核队列、进展看板、搜索、灵感速记）。用于"给我的知识库装个工作台""启动/重启仪表盘""工作台打不开或数据不对""升级工作台"时；知识库结构可先用 ray-obsidian 搭建。只监听本机、不修改用户笔记、不覆盖用户配置、不擅自配置开机自启。
---

# Ray Dashboard

把一个随 vault 存放的本地工作台装进用户的知识库并保证它真的能用。仪表盘是入口层，不是第二套笔记系统：Markdown 仍是唯一真源。

> **孵化状态**：首个 lab 住户。安装/启动/停止/升级/诊断链路已实测；launchd 常驻自启只有文档还没有自动化；Windows/Linux 的 stop 依赖 lsof 回退，未充分验证。

## 固定原则

1. 仪表盘只监听 `127.0.0.1`，不改成对外监听，不做端口转发建议。
2. 不读取、不修改、不移动用户笔记；安装只写 `50-系统/40-自动化/知识仪表盘/` 一个目录。
3. `config.json` 是用户数据，任何命令任何情况下不覆盖。
4. 用户已改动的代码文件默认保留；只有用户明确要求升级时才用 `--upgrade` 替换，并逐项报告。
5. 启动的完成标准是 healthz 探测通过并交付可点击 URL，不以"命令没报错"为完成。
6. 开机自启是持久配置，只在用户明确要求时按 [autostart.md](references/autostart.md) 配置。

## 1. 确定知识库根目录

与 ray-obsidian 同一套定位顺序：用户明确给出的目录 → `.ray-obsidian.json` → 同时存在 `10-创作/`、`20-知识/`、`30-资料/`、`50-系统/` 的兼容库 → 只问一个问题。确定后先报告绝对路径。

vault 还没有结构时，先建议用 ray-obsidian 搭骨架；用户不想装 skill 也可以用仪表盘自带的 `bootstrap.py`（支持 `--demo` 演示数据）。

## 2. 先检查，后动手

```bash
python3 <skill-base>/scripts/dashboard_setup.py check --vault <知识库目录>
```

按 `status` 分流：`not-installed` 走安装；`incomplete` 补装；`outdated` 说明资产比已装版本新，问用户是否升级；`installed` 直接进入启动或诊断。`server.running` 为 true 时不要重复启动。

## 3. 安装与升级

先预演再执行；升级必须出示 `kept_local_changes` 与 `upgraded` 清单：

```bash
python3 <skill-base>/scripts/dashboard_setup.py install --vault <目录> --dry-run
python3 <skill-base>/scripts/dashboard_setup.py install --vault <目录>            # 只补缺失文件
python3 <skill-base>/scripts/dashboard_setup.py install --vault <目录> --upgrade  # 用户要求升级时
```

## 4. 启动、停止与验收

```bash
python3 <skill-base>/scripts/dashboard_setup.py start --vault <目录> [--port 8765] [--open]
python3 <skill-base>/scripts/dashboard_setup.py stop [--port 8765]
```

`start` 成功会返回 URL 与日志位置（它内部已完成 healthz 验收；手动复核时端点是 `/api/healthz`，不是 `/healthz`）。交付时告诉用户：浏览器"安装应用"（或 Safari"添加到程序坞"）可获得独立窗口；审核队列支持 `J/K` `1-4` 键盘流；顶栏 🔔 可开系统通知。

## 5. 诊断

用户说"打不开""空白""数据不对"时，先 `status` 再对照 [diagnose.md](references/diagnose.md) 逐项排查。诊断请求只诊断——交付根因与恢复命令，不代为启停服务，更不得借机升级或改配置；用户明确让你修，才动手。

## 完成标准

- check 的 status 与用户诉求一致（装完为 `installed`，升级后无 `differs`）。
- 服务 healthz 探测通过，用户拿到可点击的 URL。
- 升级/保留的文件清单已逐项呈现；`config.json` 从未被改写。
- 用户只要求其中一件事时，没有顺手做另外几件。

## 上游

资产副本来自 rays-brain-kit（工作台 + 采集管线的完整仓库）。更新资产时从上游整目录同步，不在本 skill 内单独修改仪表盘代码。
