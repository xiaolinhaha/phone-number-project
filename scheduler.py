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
    def __init__(self, config_file: str = "config.json"):
        """
        初始化定时任务调度器
        
        Args:
            config_file (str): 配置文件路径（用于API调用）
        """
        self.api_caller = APIWorkflowCaller(config_file)
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
        """定时执行的API调用任务（获取号码）"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"⏰ 定时任务触发 - {current_time}")
            logging.info("=" * 60)
            
            # 调用API（获取号码列表，并保存到 files/numberList_YYYY-MM-DD.json）
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

    def run_python_script(self, script_name: str) -> bool:
        """在当前目录运行指定的 Python 脚本并记录日志
        
        Args:
            script_name: 脚本文件名，如 'get_captcha.py'
        Returns:
            bool: 运行是否成功
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(current_dir, script_name)
            if not os.path.exists(script_path):
                logging.error(f"❌ 脚本不存在: {script_path}")
                return False

            logging.info(f"🚀 开始执行脚本: {script_name}")
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, cwd=current_dir)
            if result.returncode == 0:
                logging.info(f"✅ 脚本执行成功: {script_name}")
                if result.stdout:
                    logging.info(f"📋 输出信息:\n{result.stdout}")
                return True
            else:
                logging.error(f"❌ 脚本执行失败: {script_name}，返回码: {result.returncode}")
                if result.stderr:
                    logging.error(f"💥 错误信息:\n{result.stderr}")
                return False
        except Exception as e:
            logging.error(f"💥 执行脚本时出错 ({script_name}): {str(e)}")
            return False

    def run_python_script_async(self, script_name: str) -> subprocess.Popen:
        """异步启动指定的 Python 脚本（并行执行）
        
        Args:
            script_name: 脚本文件名，如 'get_captcha.py'
        Returns:
            subprocess.Popen: 进程对象，可用于等待或收集输出
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(current_dir, script_name)
            if not os.path.exists(script_path):
                logging.error(f"❌ 脚本不存在: {script_path}")
                return None

            logging.info(f"🚀 异步启动脚本: {script_name}")
            proc = subprocess.Popen(
                [sys.executable, script_path],
                cwd=current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return proc
        except Exception as e:
            logging.error(f"💥 异步启动脚本出错 ({script_name}): {str(e)}")
            return None

    def scheduled_daily_workflow(self):
        """每天14:00执行：先获取号码，然后并行执行验证码与号码处理"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"⏰ 每日工作流触发 - {current_time}")
            logging.info("=" * 60)

            # 步骤1：获取号码（调用公共API工作流）
            logging.info("📞 步骤1/3：获取号码（调用API工作流）...")
            api_result = self.api_caller.call_api()
            if not api_result or not api_result.get("success", False):
                logging.error("❌ 获取号码失败，启用本地回退号码文件以继续流程")
                fallback_path = self.api_caller.create_fallback_number_file()
                if fallback_path:
                    logging.info(f"🧩 已生成本地示例号码文件: {fallback_path}")
                else:
                    logging.error("💥 无法生成本地示例号码文件，终止本次工作流")
                    logging.info("=" * 60)
                    return

            logging.info("✅ 获取号码完成")

            # 步骤2/3：并行执行 get_captcha.py 与 phone.py
            logging.info("🔧 步骤2/3：并行启动 get_captcha.py 与 phone.py ...")
            proc_captcha = self.run_python_script_async('get_captcha.py')
            proc_phone = self.run_python_script_async('phone.py')

            if proc_captcha is None or proc_phone is None:
                logging.error("❌ 启动并行脚本失败，终止本次工作流")
                logging.info("=" * 60)
                return

            # 等待两个脚本完成并收集输出
            out_captcha, err_captcha = proc_captcha.communicate()
            out_phone, err_phone = proc_phone.communicate()

            # 记录结果
            logging.info("📋 get_captcha.py 输出:\n%s", out_captcha or "<无输出>")
            if err_captcha:
                logging.error("💥 get_captcha.py 错误:\n%s", err_captcha)
            logging.info("📋 phone.py 输出:\n%s", out_phone or "<无输出>")
            if err_phone:
                logging.error("💥 phone.py 错误:\n%s", err_phone)

            success_captcha = (proc_captcha.returncode == 0)
            success_phone = (proc_phone.returncode == 0)
            if success_captcha and success_phone:
                logging.info("🎉 每日工作流并行步骤执行完成！两者均成功")
            else:
                logging.warning(
                    "⚠️ 并行步骤部分失败：get_captcha.py=%s, phone.py=%s",
                    "成功" if success_captcha else "失败",
                    "成功" if success_phone else "失败"
                )
            logging.info("=" * 60)
        except Exception as e:
            logging.error(f"💥 每日工作流执行出错: {str(e)}")
    
    def start_scheduler(self):
        """启动定时任务调度器"""
        try:
            logging.info("🚀 启动定时任务调度器...")
            logging.info(f"📅 任务计划:")
            logging.info(f"  - 每日工作流: 每天 14:00 执行（获取号码 → 验证码 → 号码处理）")
            logging.info("=" * 60)
            
            # 设置定时任务
            schedule.every().day.at("14:00").do(self.scheduled_daily_workflow)
            
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
    # 创建调度器实例
    scheduler = APIScheduler("config.json")
    
    # 显示帮助信息
    print("\n" + "=" * 60)
    print("🤖 API定时任务调度器")
    print("=" * 60)
    print("功能说明:")
    print("  • 每天14:00自动执行完整工作流：获取号码 → 验证码 → 号码处理")
    print("  • 支持日志记录和错误处理")
    print("  • 支持优雅退出 (Ctrl+C)")
    print("=" * 60)
    
    # 支持非交互模式：传入 --auto 或 --no-interactive 直接启动调度器
    auto_start = any(arg in ["--auto", "--no-interactive"] for arg in sys.argv[1:])

    if auto_start:
        logging.info("🤖 以非交互模式启动定时任务调度器 (--auto)")
        scheduler.start_scheduler()
        return

    # 交互模式
    try:
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