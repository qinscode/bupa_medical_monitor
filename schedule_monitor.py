#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时调度脚本 - 定期运行 Bupa 监控
"""

import schedule
import time
import subprocess
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('schedule_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_bupa_monitor():
    """运行 Bupa 监控程序"""
    try:
        logger.info("=" * 60)
        logger.info(f"开始定时监控任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 运行监控脚本
        result = subprocess.run([
            'python', 'bupa_monitor.py'
        ], 
        capture_output=True, 
        text=True, 
        input='y\n'  # 自动选择无头模式
        )
        
        if result.returncode == 0:
            logger.info("✅ 监控任务执行成功")
            if result.stdout:
                logger.info("程序输出:")
                for line in result.stdout.strip().split('\n'):
                    logger.info(f"  {line}")
        else:
            logger.error("❌ 监控任务执行失败")
            if result.stderr:
                logger.error("错误信息:")
                for line in result.stderr.strip().split('\n'):
                    logger.error(f"  {line}")
        
        logger.info(f"定时监控任务完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"执行定时任务时发生错误: {e}")

def main():
    """主函数"""
    check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
    
    print("🕐 Bupa Medical Visa Services 定时监控调度器")
    print("=" * 60)
    print(f"监控间隔: 每 {check_interval} 分钟运行一次")
    print("监控内容: Perth/Booragoon/Fremantle 在 2025-08-29 之前的预约")
    print("日志文件: schedule_monitor.log")
    print("-" * 60)
    
    # 检查依赖文件
    required_files = ['.env', 'bupa_monitor.py', 'bupa_scraper_v2.py', 'email_notifier.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return
    
    # 设置定时任务
    schedule.every(check_interval).minutes.do(run_bupa_monitor)
    
    logger.info(f"🚀 定时监控调度器启动，每 {check_interval} 分钟检查一次")
    logger.info("按 Ctrl+C 停止调度器")
    
    # 立即执行一次
    print("🤖 执行初始检查...")
    run_bupa_monitor()
    
    # 开始定时循环
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次调度
    except KeyboardInterrupt:
        logger.info("🛑 定时监控调度器已停止")
        print("\n🛑 定时监控调度器已停止")

if __name__ == "__main__":
    main() 