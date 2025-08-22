#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bupa Medical Visa Services Web Scraper V2
改进版数据提取爬虫
"""

import time
import logging
import csv
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BupaMedicalScraperV2:
    def __init__(self, headless=False):
        """
        初始化爬虫
        
        Args:
            headless (bool): 是否使用无头模式
        """
        self.url = "https://bmvs.onlineappointmentscheduling.net.au/oasis/Default.aspx"
        self.driver = None
        self.headless = headless
        
    def setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            chrome_options = Options()
            
            # 基本选项
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # 用户代理
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 如果需要无头模式
            if self.headless:
                chrome_options.add_argument('--headless=new')
            
            # 使用系统ChromeDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome WebDriver 初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"WebDriver 初始化失败: {e}")
            return False
    
    def load_page(self):
        """加载目标页面"""
        try:
            logger.info(f"正在访问: {self.url}")
            self.driver.get(self.url)
            
            # 等待页面加载完成
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("页面加载成功")
            return True
            
        except TimeoutException:
            logger.error("页面加载超时")
            return False
        except Exception as e:
            logger.error(f"页面加载失败: {e}")
            return False
    
    def click_new_individual_booking(self):
        """点击 'New Individual booking' 按钮"""
        try:
            # 使用精确的ID选择器
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_btnInd"))
            )
            
            # 滚动到元素位置
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            # 点击按钮
            button.click()
            logger.info("成功点击 'New Individual booking' 按钮")
            return True
                
        except TimeoutException:
            logger.error("等待 'New Individual booking' 按钮超时")
            return False
        except Exception as e:
            logger.error(f"点击 'New Individual booking' 按钮失败: {e}")
            return False
    
    def wait_for_location_page(self, timeout=30):
        """等待位置选择页面加载"""
        try:
            logger.info("等待页面跳转到位置选择...")
            
            # 等待URL包含Location.aspx
            WebDriverWait(self.driver, timeout).until(
                lambda driver: "Location.aspx" in driver.current_url
            )
            
            logger.info(f"页面已跳转到: {self.driver.current_url}")
            return True
            
        except TimeoutException:
            logger.warning("页面跳转等待超时")
            return False
        except Exception as e:
            logger.error(f"等待页面跳转失败: {e}")
            return False
    
    def extract_location_data(self):
        """提取医疗中心位置和预约数据"""
        try:
            logger.info("开始提取位置数据...")
            
            # 等待表格加载
            table = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.tbl-location"))
            )
            
            # 提取所有行数据
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr.trlocation")
            logger.info(f"找到 {len(rows)} 行数据")
            
            locations_data = []
            
            for i, row in enumerate(rows):
                try:
                    logger.info(f"提取第 {i+1} 行数据...")
                    
                    # 提取基本信息
                    radio_input = row.find_element(By.CSS_SELECTOR, "input.rbLocation")
                    location_id = radio_input.get_attribute("value")
                    
                    # 提取位置名称
                    name_cell = row.find_element(By.CSS_SELECTOR, ".tdloc_name")
                    location_name = name_cell.find_element(By.CSS_SELECTOR, ".tdlocNameTitle").text.strip()
                    
                    # 提取完整地址
                    address_span = name_cell.find_element(By.TAG_NAME, "span")
                    full_address = address_span.text.strip()
                    
                    # 提取距离
                    distance_cell = row.find_element(By.CSS_SELECTOR, ".td-distance span")
                    distance = distance_cell.text.strip()
                    
                    # 提取可用日期
                    availability_cell = row.find_element(By.CSS_SELECTOR, ".tdloc_availability span")
                    availability = availability_cell.text.strip()
                    
                    # 提取坐标
                    try:
                        coords_input = row.find_element(By.ID, f"{location_id}hidCoords")
                        coordinates = coords_input.get_attribute("value")
                    except:
                        coordinates = ""
                    
                    # 确定中心类型
                    center_type = "Bupa Centre" if "blue-dot.png" in row.get_attribute("innerHTML") else "Regional Medical Centre"
                    
                    location_data = {
                        "location_id": location_id,
                        "location_name": location_name,
                        "full_address": full_address,
                        "distance": distance,
                        "availability": availability,
                        "coordinates": coordinates,
                        "center_type": center_type,
                        "has_available_slots": "No available slot" not in availability,
                        "extracted_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    locations_data.append(location_data)
                    logger.info(f"✅ 提取数据: {location_name} - {availability}")
                    
                except Exception as row_error:
                    logger.warning(f"❌ 提取第 {i+1} 行数据失败: {row_error}")
                    continue
            
            logger.info(f"成功提取 {len(locations_data)} 个位置的数据")
            return locations_data
            
        except TimeoutException:
            logger.error("等待位置表格加载超时")
            return []
        except Exception as e:
            logger.error(f"提取位置数据失败: {e}")
            return []
    
    def save_data_to_csv(self, data, filename="bupa_locations.csv"):
        """保存数据到CSV文件"""
        try:
            if not data:
                logger.warning("没有数据需要保存")
                return False
            
            fieldnames = [
                "location_id", "location_name", "full_address", "distance", 
                "availability", "coordinates", "center_type", "has_available_slots", "extracted_time"
            ]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"数据已保存到CSV文件: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"保存CSV文件失败: {e}")
            return False
    
    def save_data_to_json(self, data, filename="bupa_locations.json"):
        """保存数据到JSON文件"""
        try:
            if not data:
                logger.warning("没有数据需要保存")
                return False
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到JSON文件: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            return False
    
    def analyze_data(self, data):
        """分析提取的数据"""
        try:
            if not data:
                logger.warning("没有数据可分析")
                return
            
            logger.info("数据分析结果:")
            logger.info("=" * 50)
            
            # 统计信息
            total_locations = len(data)
            available_locations = len([loc for loc in data if loc["has_available_slots"]])
            bupa_centers = len([loc for loc in data if loc["center_type"] == "Bupa Centre"])
            regional_centers = len([loc for loc in data if loc["center_type"] == "Regional Medical Centre"])
            
            logger.info(f"总位置数量: {total_locations}")
            logger.info(f"有可用时段的位置: {available_locations}")
            logger.info(f"Bupa 中心: {bupa_centers}")
            logger.info(f"区域医疗中心: {regional_centers}")
            
            # 显示有可用时段的位置
            logger.info("\n有可用预约时段的位置:")
            logger.info("-" * 30)
            for loc in data:
                if loc["has_available_slots"]:
                    logger.info(f"📍 {loc['location_name']} ({loc['distance']}) - {loc['availability']}")
            
            # 显示无可用时段的位置
            unavailable_locations = [loc for loc in data if not loc["has_available_slots"]]
            if unavailable_locations:
                logger.info("\n无可用预约时段的位置:")
                logger.info("-" * 30)
                for loc in unavailable_locations:
                    logger.info(f"❌ {loc['location_name']} ({loc['distance']}) - 无可用时段")
            
        except Exception as e:
            logger.error(f"数据分析失败: {e}")
    
    def take_screenshot(self, filename="screenshot.png"):
        """截图保存"""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"截图已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")
    
    def run(self):
        """运行完整的爬虫流程"""
        try:
            logger.info("开始运行Bupa Medical Visa Services爬虫 V2")
            
            # 1. 设置WebDriver
            if not self.setup_driver():
                return False, []
            
            # 2. 加载页面
            if not self.load_page():
                return False, []
            
            # 3. 截图保存初始页面
            self.take_screenshot("initial_page.png")
            
            # 4. 点击 "New Individual booking"
            if not self.click_new_individual_booking():
                self.take_screenshot("error_page.png")
                return False, []
            
            # 5. 等待页面跳转到位置选择
            if not self.wait_for_location_page():
                return False, []
            
            # 6. 截图保存位置选择页面
            self.take_screenshot("location_page.png")
            
            # 7. 提取位置数据
            logger.info("开始提取医疗中心数据...")
            locations_data = self.extract_location_data()
            
            if locations_data:
                # 8. 分析数据
                self.analyze_data(locations_data)
                
                # 9. 保存数据到文件
                self.save_data_to_csv(locations_data, "bupa_locations.csv")
                self.save_data_to_json(locations_data, "bupa_locations.json")
                
                logger.info("数据提取和保存完成！")
            else:
                logger.warning("未能提取到位置数据")
            
            # 10. 截图保存最终页面
            self.take_screenshot("final_page.png")
            
            logger.info("爬虫运行完成！")
            return True, locations_data
            
        except Exception as e:
            logger.error(f"爬虫运行失败: {e}")
            return False, []
        finally:
            # 保持浏览器打开一段时间以便查看结果
            if not self.headless:
                logger.info("等待5秒后关闭浏览器...")
                time.sleep(5)
            self.close()

def main():
    """主函数"""
    print("Bupa Medical Visa Services 爬虫 V2")
    print("=" * 50)
    print("此爬虫将自动:")
    print("1. 访问 Bupa Medical Visa Services 网站")
    print("2. 点击 'New Individual booking'")
    print("3. 提取所有医疗中心的位置和预约信息")
    print("4. 保存数据到 CSV 和 JSON 文件")
    print("5. 提供数据分析报告")
    print("-" * 50)
    
    # 询问用户是否使用无头模式
    while True:
        choice = input("是否使用无头模式？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            headless = True
            break
        elif choice in ['n', 'no', '否']:
            headless = False
            break
        else:
            print("请输入 y/n")
    
    # 创建并运行爬虫
    scraper = BupaMedicalScraperV2(headless=headless)
    success, data = scraper.run()
    
    if success and data:
        print("\n✅ 爬虫运行成功！")
        print(f"📊 成功提取了 {len(data)} 个医疗中心的数据")
        
        # 统计可用预约
        available_count = len([loc for loc in data if loc["has_available_slots"]])
        print(f"🕐 其中 {available_count} 个中心有可用预约时段")
        
        print("\n📁 生成的文件:")
        print("- bupa_locations.csv (Excel可打开的表格文件)")
        print("- bupa_locations.json (程序可读的数据文件)")
        print("- initial_page.png (首页截图)")
        print("- location_page.png (位置选择页截图)")
        print("- final_page.png (最终页面截图)")
        
        # 显示最早可用的预约
        available_locations = [loc for loc in data if loc["has_available_slots"]]
        if available_locations:
            print(f"\n🏥 有可用预约的医疗中心:")
            for loc in available_locations[:3]:  # 显示前3个
                print(f"   • {loc['location_name']} ({loc['distance']}) - {loc['availability']}")
            if len(available_locations) > 3:
                print(f"   ... 还有 {len(available_locations) - 3} 个中心有可用预约")
    
    elif success:
        print("\n⚠️ 爬虫运行成功，但未提取到数据")
    else:
        print("\n❌ 爬虫运行失败，请检查日志")

if __name__ == "__main__":
    main() 