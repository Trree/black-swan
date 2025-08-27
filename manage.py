#!/usr/bin/env python3
"""
系统管理脚本
"""

import argparse
from scheduler.task_scheduler import task_scheduler
from logging_config import logger


def show_status():
    """显示系统状态"""
    status = task_scheduler.get_job_status()
    print("系统任务状态:")
    for job_id, info in status.items():
        print(f"  {job_id}:")
        print(f"    下次运行: {info['next_run_time']}")
        print(f"    触发器: {info['trigger']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新闻监控系统管理工具")
    subparsers = parser.add_subparsers(dest='command')

    # 状态命令
    subparsers.add_parser('status', help='显示系统状态')

    # 立即运行命令
    run_parser = subparsers.add_parser('run-now', help='立即运行抓取任务')
    run_parser.add_argument('task', choices=['main', 'quick'], help='任务类型')

    args = parser.parse_args()

    if args.command == 'status':
        show_status()
    elif args.command == 'run-now':
        # 这里可以实现立即运行任务的逻辑
        print(f"立即运行 {args.task} 任务")


if __name__ == "__main__":
    main()