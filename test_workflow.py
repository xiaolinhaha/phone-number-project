#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：直接调用 scheduler.py 中的“每日工作流”定时任务逻辑一次。

运行：
  python3 test_workflow.py
"""

import logging
from scheduler import APIScheduler


def main():
    logging.info('🧪 测试：直接触发 scheduler 的每日工作流一次')
    sched = APIScheduler('config.json')
    sched.scheduled_daily_workflow()
    logging.info('✅ 测试执行完毕（详见控制台与 scheduler.log）')


if __name__ == '__main__':
    main()