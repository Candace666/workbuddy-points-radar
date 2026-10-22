#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""workbuddy-points-radar 连签追踪工具。

只记录用户手动领取积分的流水并计算连签状态；不访问网络、不调用任何
WorkBuddy 接口、不读取登录态。数据为本地 CSV：date,channel,note。

用法:
    streak.py status
    streak.py claim <channel> [--note 备注] [--date YYYY-MM-DD]
    streak.py week [--date YYYY-MM-DD]
    streak.py channels
"""

import argparse
import csv
import os
import sys
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG = os.path.join(BASE_DIR, "data", "streak.log")

CHANNELS = {
    "buddy-station": "Buddy加油站(每日100,连签7天+1000)",
    "cat-travel": "派猫猫旅行(积分+能量盲盒)",
    "growth-task": "成长计划/任务中心(一次性100-300)",
    "community-post": "社区发文(心得+500/教程+1000/精选+2000)",
    "invite": "邀请好友(双方+500,好友付费再+1000)",
    "monthly-quota": "每月免费额度(每月1号自动刷新)",
    "other": "其他",
}


def log_path():
    return os.environ.get("WB_POINTS_LOG", DEFAULT_LOG)


def load_rows():
    path = log_path()
    rows = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) >= 2 and row[0].strip():
                    rows.append((row[0].strip(), row[1].strip(),
                                 row[2].strip() if len(row) > 2 else ""))
    return rows


def append_row(day, channel, note):
    path = log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([day.isoformat(), channel, note])


def claimed_dates(rows, channel):
    return {date.fromisoformat(d) for d, c, _ in rows if c == channel}


def current_streak(dates, today):
    """从今天(未领则从昨天)往回数连续领取天数。"""
    cursor = today if today in dates else today - timedelta(days=1)
    streak = 0
    while cursor in dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def cmd_channels(_args):
    for key, desc in CHANNELS.items():
        print("%-16s %s" % (key, desc))
    return 0


def cmd_claim(args):
    if args.channel not in CHANNELS:
        print("未知渠道: %s" % args.channel)
        print("可用渠道: %s" % ", ".join(CHANNELS))
        return 2
    day = date.fromisoformat(args.date) if args.date else date.today()
    rows = load_rows()
    if day in claimed_dates(rows, args.channel):
        print("%s 的 %s 已记录过，跳过重复。" % (day.isoformat(), args.channel))
        return 0
    append_row(day, args.channel, args.note or "")
    streak = current_streak(claimed_dates(load_rows(), args.channel), date.today())
    print("已记录: %s %s%s  当前连签 %d 天" % (
        day.isoformat(), args.channel,
        " (%s)" % args.note if args.note else "", streak))
    return 0


def cmd_status(_args):
    today = date.today()
    rows = load_rows()
    print("===== 积分领取状态 %s =====" % today.isoformat())
    if not rows:
        print("(还没有任何领取记录。用户手动领取后，用 claim 命令记录。)")
    for key, desc in CHANNELS.items():
        dates = claimed_dates(rows, key)
        if not dates:
            continue
        streak = current_streak(dates, today)
        last = max(dates)
        today_done = today in dates
        line = "- %s: %s | 连签 %d 天 | 上次 %s" % (
            key, "今日已领" if today_done else "今日未领", streak, last.isoformat())
        if key == "buddy-station" and not today_done:
            need = 7 - (streak % 7) if streak % 7 else 7
            if streak % 7 == 0 and streak > 0:
                line += " | 连签满 %d 天，本期大奖应已到手" % streak
            else:
                line += " | 再领 %d 天拿 1000 连签大奖(断签清零!)" % need
        print(line)
    week_rows = [r for r in rows
                 if today - timedelta(days=today.weekday()) <= date.fromisoformat(r[0]) <= today]
    print("本周已记录 %d 次领取。" % len(week_rows))
    print("提示: 领取动作请在桌面客户端手动完成(左下角头像 -> Buddy加油站)。")
    return 0


def cmd_week(args):
    ref = date.fromisoformat(args.date) if args.date else date.today()
    monday = ref - timedelta(days=ref.weekday())
    sunday = monday + timedelta(days=6)
    rows = [r for r in load_rows() if monday <= date.fromisoformat(r[0]) <= sunday]
    print("===== 本周领取记录 %s ~ %s =====" % (monday.isoformat(), sunday.isoformat()))
    if not rows:
        print("(本周无记录)")
        return 0
    by_day = {}
    for d, c, note in sorted(rows):
        by_day.setdefault(d, []).append(c + ("(%s)" % note if note else ""))
    for d in sorted(by_day):
        print("%s  %s" % (d, ", ".join(by_day[d])))
    missed = [ (monday + timedelta(days=i)).isoformat()
               for i in range(7)
               if (monday + timedelta(days=i)) <= ref
               and (monday + timedelta(days=i)).isoformat() not in by_day ]
    if missed:
        print("截至今天漏领日期: %s" % ", ".join(missed))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="WorkBuddy 积分连签追踪(仅记录,不自动领取)")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="今日状态 + 各渠道连签")
    p_claim = sub.add_parser("claim", help="记录今日已手动领取")
    p_claim.add_argument("channel")
    p_claim.add_argument("--note", default="")
    p_claim.add_argument("--date", default="", help="补记日期 YYYY-MM-DD")
    p_week = sub.add_parser("week", help="本周领取记录")
    p_week.add_argument("--date", default="")
    sub.add_parser("channels", help="列出已知渠道标识")

    args = parser.parse_args(argv)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "claim":
        return cmd_claim(args)
    if args.cmd == "week":
        return cmd_week(args)
    if args.cmd == "channels":
        return cmd_channels(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
