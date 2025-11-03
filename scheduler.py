#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import schedule
import time
import logging
import json
import os
from datetime import datetime
import signal
import sys
import subprocess
from api_caller import APIWorkflowCaller

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

class APIScheduler:
    def __init__(self, api_key):
        """
        初始化定时任务调度器
        
        Args:
            api_key (str): API密钥
        """
        self.api_key = api_key
        self.api_caller = APIWorkflowCaller(api_key)
        self.is_running = True
        
        # 注册信号处理器，用于优雅退出
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理退出信号"""
        logging.info(f"🛑 接收到退出信号 {signum}，正在优雅退出...")
        self.is_running = False
    
    def scheduled_captcha_task(self):
        """定时执行的验证码查询任务"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"🔍 验证码查询任务触发 - {current_time}")
            logging.info("=" * 60)
            
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            get_captcha_path = os.path.join(current_dir, 'get_captcha.py')
            
            # 执行get_captcha.py
            logging.info("🚀 开始执行验证码查询任务...")
            result = subprocess.run([sys.executable, get_captcha_path], 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=current_dir)
            
            if result.returncode == 0:
                logging.info("✅ 验证码查询任务执行成功")
                if result.stdout:
                    logging.info(f"📋 输出信息:\n{result.stdout}")
            else:
                logging.error(f"❌ 验证码查询任务执行失败，返回码: {result.returncode}")
                if result.stderr:
                    logging.error(f"💥 错误信息:\n{result.stderr}")
            
            logging.info("=" * 60)
            
        except Exception as e:
            logging.error(f"💥 执行验证码查询任务时出错: {str(e)}")
    
    def scheduled_api_call(self):
        """定时执行的API调用任务"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"⏰ 定时任务触发 - {current_time}")
            logging.info("=" * 60)
            
            # 调用API
            result = self.api_caller.call_api()
            
            if result and result.get("success", True):
                logging.info("✅ 定时API调用成功完成!")
            else:
                logging.error("❌ 定时API调用失败!")
                
            logging.info("=" * 60)
            
        except Exception as e:
            logging.error(f"💥 定时任务执行出错: {str(e)}")
    
    def test_api_call(self):
        """测试API调用（用于调试）"""
        logging.info("🧪 执行测试API调用...")
        self.scheduled_api_call()
    
    def start_scheduler(self):
        """启动定时任务调度器"""
        try:
            logging.info("🚀 启动定时任务调度器...")
            logging.info(f"📅 任务计划:")
            logging.info(f"  - API调用: 每天 10:00 执行")
            logging.info(f"  - 验证码查询: 每天 10:30 执行")
            logging.info(f"🔑 API密钥: {self.api_key[:10]}...")
            logging.info("=" * 60)
            
            # 设置定时任务
            schedule.every().day.at("10:00").do(self.scheduled_api_call)
            schedule.every().day.at("10:30").do(self.scheduled_captcha_task)
            
            # 显示下次执行时间
            jobs = schedule.get_jobs()
            for i, job in enumerate(jobs, 1):
                next_run = job.next_run
                if next_run:
                    logging.info(f"⏰ 任务 {i} 下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 主循环
            while self.is_running:
                try:
                    # 检查并运行待执行的任务
                    schedule.run_pending()
                    
                    # 每分钟检查一次
                    time.sleep(60)
                    
                except KeyboardInterrupt:
                    logging.info("🛑 接收到键盘中断信号...")
                    break
                except Exception as e:
                    logging.error(f"💥 调度器运行出错: {str(e)}")
                    time.sleep(60)  # 出错后等待1分钟再继续
            
            logging.info("👋 定时任务调度器已停止")
            
        except Exception as e:
            logging.error(f"💥 启动调度器失败: {str(e)}")
    
    def show_schedule_info(self):
        """显示当前调度信息"""
        logging.info("📋 当前调度信息:")
        jobs = schedule.get_jobs()
        if jobs:
            for i, job in enumerate(jobs, 1):
                logging.info(f"  {i}. {job}")
                next_run = job.next_run
                if next_run:
                    logging.info(f"     下次执行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logging.info("  暂无调度任务")

def main():
    """主函数"""
    # 使用提供的API密钥
    api_key = "app-4djToLaTnYL1NYdlHv75knvx"
    
    # 创建调度器实例
    scheduler = APIScheduler(api_key)
    
    # 显示帮助信息
    print("\n" + "=" * 60)
    print("🤖 API定时任务调度器")
    print("=" * 60)
    print("功能说明:")
    print("  • 每天10:00自动调用指定的API接口")
    print("  • 支持日志记录和错误处理")
    print("  • 支持优雅退出 (Ctrl+C)")
    print("=" * 60)
    
    # 询问用户是否要先测试API调用
    try:
        test_choice = input("是否先测试API调用? (y/n): ").lower().strip()
        if test_choice in ['y', 'yes', '是']:
            scheduler.test_api_call()
            
        start_choice = input("是否启动定时任务调度器? (y/n): ").lower().strip()
        if start_choice in ['y', 'yes', '是']:
            scheduler.start_scheduler()
        else:
            print("👋 程序退出")
            
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        logging.error(f"💥 程序运行出错: {str(e)}")

if __name__ == "__main__":
    main()