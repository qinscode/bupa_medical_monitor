#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件通知模块
支持 Gmail SMTP 发送预约通知邮件
"""

import smtplib
import ssl
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self):
        """初始化邮件通知器"""
        self.gmail_user = os.getenv('GMAIL_USER')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        self.notification_email = os.getenv('NOTIFICATION_EMAIL')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # 验证配置
        self._validate_config()
    
    def _validate_config(self):
        """验证邮件配置"""
        required_vars = ['GMAIL_USER', 'GMAIL_APP_PASSWORD', 'NOTIFICATION_EMAIL']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")
        
        logger.info(f"邮件配置验证成功: {self.gmail_user} -> {self.notification_email}")
    
    def create_notification_email(self, available_slots, cutoff_date):
        """创建预约通知邮件"""
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['From'] = self.gmail_user
            msg['To'] = self.notification_email
            msg['Subject'] = f"🏥 Bupa 医疗预约通知 - 发现 {len(available_slots)} 个符合条件的预约"
            
            # 创建HTML邮件内容
            html_content = self._create_html_content(available_slots, cutoff_date)
            
            # 创建纯文本内容
            text_content = self._create_text_content(available_slots, cutoff_date)
            
            # 添加邮件内容
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            return msg
            
        except Exception as e:
            logger.error(f"创建邮件失败: {e}")
            return None
    
    def _create_html_content(self, available_slots, cutoff_date):
        """创建HTML格式邮件内容"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .appointment {{ background-color: #f8f9fa; border-left: 4px solid #28a745; padding: 15px; margin: 10px 0; }}
                .urgent {{ border-left-color: #dc3545; }}
                .details {{ margin-top: 10px; font-size: 14px; color: #666; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                .highlight {{ background-color: #fff3cd; padding: 2px 4px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 Bupa Medical Visa Services</h1>
                <h2>预约通知提醒</h2>
            </div>
            
            <div class="content">
                <p><strong>检测时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>筛选条件:</strong> {cutoff_date} 之前的 Perth/Booragoon/Fremantle 预约</p>
                <p><strong>发现结果:</strong> <span class="highlight">{len(available_slots)} 个符合条件的预约时段</span></p>
                
                <hr>
                
                <h3>📅 可用预约详情:</h3>
        """
        
        for slot in available_slots:
            urgency_class = "urgent" if slot['distance'] in ['4 km', '7 km'] else ""
            html += f"""
                <div class="appointment {urgency_class}">
                    <h4>🏥 {slot['location_name']} ({slot['distance']})</h4>
                    <p><strong>📅 预约时间:</strong> {slot['availability']}</p>
                    <p><strong>📍 地址:</strong> {slot['full_address'].replace(chr(10), '<br>')}</p>
                    <p><strong>🏢 类型:</strong> {slot['center_type']}</p>
                    <div class="details">
                        <p><strong>坐标:</strong> {slot['coordinates']}</p>
                        <p><strong>位置ID:</strong> {slot['location_id']}</p>
                    </div>
                </div>
            """
        
        html += f"""
                <hr>
                
                <h3>⚡ 下一步操作建议:</h3>
                <ol>
                    <li>立即访问 <a href="https://bmvs.onlineappointmentscheduling.net.au/oasis/Default.aspx">Bupa 预约网站</a></li>
                    <li>点击 "New Individual booking"</li>
                    <li>选择心仪的医疗中心</li>
                    <li>完成预约流程</li>
                </ol>
                
                <p><strong>⚠️ 提示:</strong> 预约时段可能很快被预订，建议尽快行动！</p>
            </div>
            
            <div class="footer">
                <p>此邮件由 Bupa Medical Visa Services 监控系统自动发送</p>
                <p>监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_text_content(self, available_slots, cutoff_date):
        """创建纯文本格式邮件内容"""
        text = f"""
Bupa Medical Visa Services 预约通知
=====================================

检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
筛选条件: {cutoff_date} 之前的 Perth/Booragoon/Fremantle 预约
发现结果: {len(available_slots)} 个符合条件的预约时段

可用预约详情:
"""
        
        for i, slot in enumerate(available_slots, 1):
            text += f"""
{i}. {slot['location_name']} ({slot['distance']})
   预约时间: {slot['availability']}
   地址: {slot['full_address']}
   类型: {slot['center_type']}
   坐标: {slot['coordinates']}
   位置ID: {slot['location_id']}
"""
        
        text += f"""
下一步操作建议:
1. 立即访问 Bupa 预约网站
2. 点击 "New Individual booking"  
3. 选择心仪的医疗中心
4. 完成预约流程

网址: https://bmvs.onlineappointmentscheduling.net.au/oasis/Default.aspx

⚠️ 提示: 预约时段可能很快被预订，建议尽快行动！

---
此邮件由 Bupa Medical Visa Services 监控系统自动发送
监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return text
    
    def send_notification(self, available_slots, cutoff_date):
        """发送预约通知邮件"""
        try:
            if not available_slots:
                logger.info("没有符合条件的预约，无需发送邮件")
                return False
            
            # 创建邮件
            msg = self.create_notification_email(available_slots, cutoff_date)
            if not msg:
                return False
            
            # 发送邮件
            logger.info(f"正在发送邮件通知到 {self.notification_email}...")
            
            # 创建SSL上下文
            context = ssl.create_default_context()
            
            # 连接SMTP服务器并发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.gmail_user, self.gmail_password)
                
                # 发送邮件
                text = msg.as_string()
                server.sendmail(self.gmail_user, self.notification_email, text)
            
            logger.info(f"✅ 邮件发送成功! 通知了 {len(available_slots)} 个可用预约")
            return True
            
        except Exception as e:
            logger.error(f"❌ 邮件发送失败: {e}")
            return False
    
    def test_email_config(self):
        """测试邮件配置"""
        try:
            logger.info("测试邮件配置...")
            
            # 创建测试邮件
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = self.notification_email
            msg['Subject'] = "🧪 Bupa 监控系统测试邮件"
            
            body = f"""
这是一封测试邮件，用于验证 Bupa Medical Visa Services 监控系统的邮件功能。

测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
发送方: {self.gmail_user}
接收方: {self.notification_email}

如果您收到这封邮件，说明邮件配置正确！

---
Bupa Medical Visa Services 监控系统
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送测试邮件
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.gmail_user, self.gmail_password)
                text = msg.as_string()
                server.sendmail(self.gmail_user, self.notification_email, text)
            
            logger.info("✅ 测试邮件发送成功!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 测试邮件发送失败: {e}")
            return False

def test_email_notifier():
    """测试邮件通知功能"""
    try:
        notifier = EmailNotifier()
        
        # 测试邮件配置
        if notifier.test_email_config():
            print("✅ 邮件配置测试成功!")
        else:
            print("❌ 邮件配置测试失败!")
            return
        
        # 创建测试数据
        test_slots = [
            {
                "location_id": "193",
                "location_name": "Perth",
                "full_address": "Perth - Bupa Centre\nLevel 3,\n2 Mill Street,\nPerth",
                "distance": "4 km",
                "availability": "Saturday 23/08/2025\n03:00 PM",
                "coordinates": "-31.9548200,115.8526330",
                "center_type": "Bupa Centre",
                "has_available_slots": True
            }
        ]
        
        # 发送测试通知
        if notifier.send_notification(test_slots, "2025-08-29"):
            print("✅ 测试通知发送成功!")
        else:
            print("❌ 测试通知发送失败!")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_email_notifier() 