#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bupa Medical Visa Services 预约监控系统
每次运行爬虫后检查条件并发送邮件通知
"""

import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from bupa_scraper_v2 import BupaMedicalScraperV2
from email_notifier import EmailNotifier

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BupaMonitor:
    def __init__(self):
        """初始化监控系统"""
        self.monitor_locations = os.getenv('MONITOR_LOCATIONS', 'Perth,Booragoon,Fremantle').split(',')
        self.cutoff_date = os.getenv('CUTOFF_DATE', '2025-08-29')
        
        # 清理空格
        self.monitor_locations = [loc.strip() for loc in self.monitor_locations]
        
        logger.info(f"监控配置:")
        logger.info(f"  监控地点: {', '.join(self.monitor_locations)}")
        logger.info(f"  截止日期: {self.cutoff_date}")
    
    def parse_availability_date(self, availability_text):
        """解析预约时间文本，返回日期对象"""
        try:
            if "No available slot" in availability_text:
                return None
            
            # 提取日期部分 (例如: "Friday 29/08/2025\n10:15 AM" -> "29/08/2025")
            lines = availability_text.strip().split('\n')
            if len(lines) >= 1:
                # 查找日期模式 DD/MM/YYYY
                import re
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', lines[0])
                if date_match:
                    date_str = date_match.group(1)
                    # 解析日期
                    return datetime.strptime(date_str, '%d/%m/%Y').date()
            
            return None
            
        except Exception as e:
            logger.warning(f"解析日期失败: {availability_text} -> {e}")
            return None
    
    def filter_matching_slots(self, locations_data):
        """筛选符合条件的预约时段"""
        matching_slots = []
        cutoff_date = datetime.strptime(self.cutoff_date, '%Y-%m-%d').date()
        
        logger.info(f"开始筛选条件：监控地点 {self.monitor_locations}，截止日期 {self.cutoff_date}")
        
        for location in locations_data:
            location_name = location['location_name'].strip()
            
            # 检查是否是监控的地点
            if location_name not in self.monitor_locations:
                logger.debug(f"跳过非监控地点: {location_name}")
                continue
            
            # 检查是否有可用时段
            if not location['has_available_slots']:
                logger.info(f"{location_name}: 无可用时段")
                continue
            
            # 解析预约日期
            availability_date = self.parse_availability_date(location['availability'])
            if not availability_date:
                logger.warning(f"{location_name}: 无法解析预约日期 - {location['availability']}")
                continue
            
            # 检查是否在截止日期之前
            if availability_date <= cutoff_date:
                matching_slots.append(location)
                logger.info(f"✅ 符合条件: {location_name} - {location['availability']} (日期: {availability_date})")
            else:
                logger.info(f"❌ 超出截止日期: {location_name} - {location['availability']} (日期: {availability_date})")
        
        return matching_slots
    
    def check_and_notify(self, locations_data):
        """检查条件并发送通知"""
        try:
            logger.info("=" * 60)
            logger.info(f"开始检查预约条件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if not locations_data:
                logger.warning("没有位置数据可检查")
                return False
            
            # 筛选符合条件的预约
            matching_slots = self.filter_matching_slots(locations_data)
            
            if matching_slots:
                logger.info(f"🎯 发现 {len(matching_slots)} 个符合条件的预约时段:")
                for slot in matching_slots:
                    logger.info(f"  📍 {slot['location_name']} ({slot['distance']}) - {slot['availability']}")
                
                # 发送邮件通知
                try:
                    email_notifier = EmailNotifier()
                    if email_notifier.send_notification(matching_slots, self.cutoff_date):
                        logger.info("✅ 邮件通知发送成功！")
                        return True
                    else:
                        logger.error("❌ 邮件通知发送失败")
                        return False
                        
                except Exception as email_error:
                    logger.error(f"❌ 邮件通知失败: {email_error}")
                    logger.info("💡 提示: 请检查 .env 文件中的邮箱配置")
                    return False
            else:
                logger.info("ℹ️  未找到符合条件的预约时段")
                logger.info(f"  条件: {', '.join(self.monitor_locations)} 在 {self.cutoff_date} 之前")
                return False
                
        except Exception as e:
            logger.error(f"检查过程中发生错误: {e}")
            return False

def main():
    """主函数：运行爬虫并检查通知"""
    print("🏥 Bupa Medical Visa Services 爬虫 + 邮件通知")
    print("=" * 60)
    print("此程序将:")
    print("1. 运行爬虫获取最新预约数据")
    print("2. 检查是否有符合条件的预约 (Perth/Booragoon/Fremantle 在 2025-08-29 之前)")
    print("3. 如果符合条件，立即发送邮件通知")
    print("-" * 60)
    
    # 检查 .env 文件
    if not os.path.exists('.env'):
        print("❌ 未找到 .env 文件")
        print("请参考 env_template.txt 创建 .env 文件并配置邮箱信息")
        return
    
    try:
        # 1. 运行爬虫
        print("\n🤖 步骤1: 运行爬虫获取数据...")
        headless = input("是否使用无头模式？(y/n，默认y): ").lower().strip()
        if headless == '' or headless in ['y', 'yes', '是']:
            headless = True
        else:
            headless = False
            
        scraper = BupaMedicalScraperV2(headless=headless)
        success, locations_data = scraper.run()
        
        if not success:
            print("❌ 爬虫运行失败")
            return
            
        if not locations_data:
            print("❌ 未获取到数据")
            return
            
        print(f"✅ 爬虫运行成功，获取到 {len(locations_data)} 个位置的数据")
        
        # 2. 检查条件并发送通知
        print("\n📧 步骤2: 检查条件并发送通知...")
        monitor = BupaMonitor()
        notification_sent = monitor.check_and_notify(locations_data)
        
        # 3. 总结
        print("\n" + "=" * 60)
        print("📊 运行总结:")
        print(f"  数据获取: ✅ 成功 ({len(locations_data)} 个位置)")
        
        if notification_sent:
            print("  邮件通知: ✅ 已发送")
            print("  🎉 发现符合条件的预约，请查收邮件！")
        else:
            print("  邮件通知: ⏸️  无需发送")
            print("  💡 当前没有符合条件的预约时段")
        
        print(f"  检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示生成的文件
        print("\n📁 生成的文件:")
        print("  - bupa_locations.csv (最新预约数据)")
        print("  - bupa_locations.json (JSON格式数据)")
        print("  - *.png (页面截图)")
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断操作")
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        print(f"\n❌ 程序运行失败: {e}")
        print("请检查网络连接和配置")

if __name__ == "__main__":
    main() 