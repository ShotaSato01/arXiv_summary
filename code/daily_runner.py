#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py と message.py を 1 日に 1 度順番に実行する常駐スクリプト。

起動時に次の実行時刻を計算し、指定時刻まで待機した後で
main.py → message.py の順に実行します。その後も 24 時間ごとに繰り返します。

実行時刻は環境変数 DAILY_RUN_AT（例: "07:30"）で指定できます。
指定がなければ 09:00 に実行します。
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, time as time_cls, timedelta
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent


def parse_run_time(value: str) -> time_cls:
    """ユーザー指定の実行時刻を HH:MM 形式で time オブジェクトに変換する。"""
    try:
        hour, minute = (int(part) for part in value.split(":", 1))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
        return time_cls(hour=hour, minute=minute)
    except (ValueError, TypeError):
        raise ValueError(f"DAILY_RUN_AT の値が不正です: {value!r}（例: '07:30'）")


def next_run_datetime(run_at: time_cls, reference: Optional[datetime] = None) -> datetime:
    """reference 以降で最初の実行時刻を返す。"""
    now = reference or datetime.now()
    candidate = datetime.combine(now.date(), run_at)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


def run_scripts() -> None:
    """main.py と message.py を順番に実行する。"""
    for script_name in ("main.py", "message.py"):
        script_path = BASE_DIR / script_name
        logging.info("▶ %s を実行します", script_name)
        subprocess.run([sys.executable, str(script_path)], check=True, cwd=str(BASE_DIR))
        logging.info("✅ %s の実行が完了しました", script_name)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    daily_run_at = os.getenv("DAILY_RUN_AT", "09:00")
    try:
        run_at = parse_run_time(daily_run_at)
    except ValueError as exc:
        logging.error(exc)
        raise SystemExit(1)

    logging.info("処理を開始します（実行時刻: %s）", run_at.strftime("%H:%M"))

    stop = False

    def handle_signal(signum, frame):
        nonlocal stop
        logging.info("🛑 シグナル(%s)を受信しました。次回の実行前に終了します。", signum)
        stop = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    next_run = next_run_datetime(run_at)
    while True:
        now = datetime.now()
        wait_seconds = (next_run - now).total_seconds()

        if wait_seconds > 0:
            logging.info("⏳ 次の実行まで %s 秒待機します（予定時刻: %s）", int(wait_seconds), next_run)
            time.sleep(wait_seconds)

        try:
            run_scripts()
        except subprocess.CalledProcessError as exc:
            logging.exception("❌ スクリプト実行中にエラーが発生しました: %s", exc)

        if stop:
            logging.info("👋 終了指示を受けたため停止します。")
            break

        next_run = next_run_datetime(run_at, reference=next_run)


if __name__ == "__main__":
    main()
