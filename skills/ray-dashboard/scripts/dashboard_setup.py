#!/usr/bin/env python3
"""知识工作台（本地知识仪表盘）的安装、启动与诊断。

命令都输出 JSON，便于上层判断；除 install 外全部只读或可逆。
安装目标固定为 <vault>/50-系统/40-自动化/知识仪表盘/，与 ray-content-v1 布局一致。
server.py 依赖上一级目录的 review_protocol.json / board_protocol.json（管线协议），
install 会在缺失时从资产补默认副本；已存在的协议是管线数据，任何情况下不覆盖。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSET_ROOT = HERE.parent / "assets" / "dashboard"
PROTOCOL_ROOT = HERE.parent / "assets"  # 镜像 40-自动化 布局：协议在仪表盘上一级
PROTOCOL_FILES = ("review_protocol.json", "board_protocol.json")
DASHBOARD_REL = "50-系统/40-自动化/知识仪表盘"
STATE_HOME = Path(os.environ.get("RAYS_BRAIN_STATE", str(Path.home() / ".local/state/rays-brain")))
LOG_FILE = STATE_HOME / "logs" / "dashboard.log"
USER_CONFIG = "config.json"  # 用户数据，任何情况下不覆盖
IGNORED_DIR_PARTS = {"__pycache__"}
IGNORED_NAMES = {".DS_Store"}


def pid_file(port: int) -> Path:
    """按端口区分 pid 文件：多个 vault 各跑一个实例时互不接管。"""
    return STATE_HOME / f"dashboard-{port}.pid"


def asset_files() -> list[Path]:
    result: list[Path] = []
    for path in ASSET_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ASSET_ROOT)
        if any(part in IGNORED_DIR_PARTS for part in rel.parts):
            continue
        if rel.name in IGNORED_NAMES or rel.suffix == ".pyc":
            continue
        result.append(rel)
    return sorted(result)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def healthz(port: int) -> dict | None:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/healthz", timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return None


def port_pids(port: int) -> list[int]:
    try:
        proc = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [int(line) for line in proc.stdout.split() if line.strip().isdigit()]


def check(vault: Path, port: int) -> dict:
    target = vault / DASHBOARD_REL
    missing: list[str] = []
    differs: list[str] = []
    for rel in asset_files():
        installed = target / rel
        if not installed.exists():
            missing.append(str(rel))
        elif digest(installed) != digest(ASSET_ROOT / rel):
            differs.append(str(rel))
    missing_protocols = [
        name for name in PROTOCOL_FILES if not (target.parent / name).exists()
    ]
    if not target.exists():
        status = "not-installed"
    elif missing or missing_protocols:
        status = "incomplete"
    elif differs:
        status = "outdated"
    else:
        status = "installed"
    health = healthz(port)
    return {
        "status": status,
        "dashboard_dir": str(target),
        "missing": missing,
        "missing_protocols": missing_protocols,
        "differs": differs,
        "has_user_config": (target / USER_CONFIG).exists(),
        "inbox_exists": (vault / "10-创作/10-灵感/inbox.md").exists(),
        "server": {"port": port, "running": health is not None, "healthz": health},
    }


def install(vault: Path, upgrade: bool, dry_run: bool) -> dict:
    target = vault / DASHBOARD_REL
    copied: list[str] = []
    upgraded: list[str] = []
    kept: list[str] = []
    for rel in asset_files():
        source = ASSET_ROOT / rel
        installed = target / rel
        if not installed.exists():
            if not dry_run:
                installed.parent.mkdir(parents=True, exist_ok=True)
                installed.write_bytes(source.read_bytes())
                if os.access(source, os.X_OK):
                    installed.chmod(0o755)
            copied.append(str(rel))
        elif digest(installed) != digest(source):
            if rel.name == USER_CONFIG or not upgrade:
                kept.append(str(rel))
            else:
                if not dry_run:
                    installed.write_bytes(source.read_bytes())
                upgraded.append(str(rel))
    seeded: list[str] = []
    for name in PROTOCOL_FILES:
        # server.py 硬依赖审核协议；缺失时补默认副本。已有协议是管线数据，
        # 用户可能已自定义动作或流转，--upgrade 也不覆盖。
        dest = target.parent / name
        if dest.exists():
            continue
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((PROTOCOL_ROOT / name).read_bytes())
        seeded.append(name)
    return {
        "ok": True,
        "dry_run": dry_run,
        "dashboard_dir": str(target),
        "copied": copied,
        "upgraded": upgraded,
        "kept_local_changes": kept,
        "seeded_protocols": seeded,
    }


def start(vault: Path, port: int, open_browser: bool) -> dict:
    if healthz(port) is not None:
        return {"ok": True, "already_running": True, "url": f"http://127.0.0.1:{port}"}
    if port_pids(port):
        return {"ok": False, "error": f"端口 {port} 被其他进程占用，换 --port 或先停掉对方"}
    server = vault / DASHBOARD_REL / "server.py"
    if not server.exists():
        return {"ok": False, "error": "仪表盘还没安装，先运行 install"}
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "RAYS_BRAIN": str(vault)}
    args = [sys.executable, str(server), "--port", str(port), "--quiet"]
    if not open_browser:
        args.append("--no-open")
    with LOG_FILE.open("a", encoding="utf-8") as log:
        proc = subprocess.Popen(args, stdout=log, stderr=log, start_new_session=True, env=env)
    for _ in range(20):
        time.sleep(0.4)
        if healthz(port) is not None:
            pid_file(port).parent.mkdir(parents=True, exist_ok=True)
            pid_file(port).write_text(str(proc.pid), encoding="utf-8")
            return {"ok": True, "pid": proc.pid, "url": f"http://127.0.0.1:{port}", "log": str(LOG_FILE)}
    proc.terminate()
    return {"ok": False, "error": f"服务没有在预期时间内就绪，查看日志：{LOG_FILE}"}


def stop(port: int) -> dict:
    pids: list[int] = []
    marker = pid_file(port)
    if marker.exists():
        raw = marker.read_text(encoding="utf-8").strip()
        if raw.isdigit():
            pids.append(int(raw))
    pids.extend(pid for pid in port_pids(port) if pid not in pids)
    stopped: list[int] = []
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            stopped.append(pid)
        except (ProcessLookupError, PermissionError):
            continue
    marker.unlink(missing_ok=True)
    return {"ok": True, "stopped": stopped, "was_running": bool(stopped)}


def main() -> None:
    parser = argparse.ArgumentParser(description="知识工作台安装与诊断")
    parser.add_argument("command", choices=["check", "install", "start", "stop", "status"])
    parser.add_argument("--vault", help="check/install/start 需要；stop/status 不需要")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--upgrade", action="store_true", help="install 时用资产替换已改动的代码文件（config.json 永不覆盖）")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--open", action="store_true", help="start 后自动打开浏览器")
    args = parser.parse_args()
    vault = Path(args.vault).expanduser().resolve() if args.vault else None
    if args.command in {"check", "install", "start"}:
        if vault is None or not vault.is_dir():
            print(json.dumps({"ok": False, "error": f"需要 --vault 指向已存在的知识库目录，当前：{vault}"}, ensure_ascii=False))
            raise SystemExit(1)
    if args.command == "check":
        result = check(vault, args.port)
    elif args.command == "install":
        result = install(vault, args.upgrade, args.dry_run)
    elif args.command == "start":
        result = start(vault, args.port, args.open)
    elif args.command == "stop":
        result = stop(args.port)
    else:
        health = healthz(args.port)
        result = {"port": args.port, "running": health is not None, "healthz": health}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
