# Bupa Medical Visa Services 监控系统使用指南

## 🎯 系统更新说明

根据您的要求，我已经修改了系统架构：

**新的工作流程：**
1. ✅ 运行爬虫获取数据
2. ✅ 检查是否符合条件（Perth/Booragoon/Fremantle 在 2025-08-29 之前）
3. ✅ 如果符合条件，立即发送邮件通知

## 📁 文件说明

### 主要脚本
- **`bupa_monitor.py`** - 主监控程序（修改后的版本）
- **`schedule_monitor.py`** - 定时调度器（可选）
- **`bupa_scraper_v2.py`** - 数据爬虫
- **`email_notifier.py`** - 邮件通知服务

### 配置文件
- **`.env`** - 环境配置（邮箱设置）
- **`env_template.txt`** - 配置模板
- **`requirements.txt`** - 依赖包

### 文档
- **`MONITOR_SETUP.md`** - 详细设置指南
- **`USAGE_GUIDE.md`** - 本使用指南

## 🚀 使用方法

### 方式1：单次运行（推荐）

```bash
python bupa_monitor.py
```

**工作流程：**
1. 程序询问是否使用无头模式
2. 运行爬虫获取最新预约数据
3. 自动检查 Perth、Booragoon、Fremantle 的预约
4. 筛选 2025-08-29 之前的可用时段
5. 如果发现符合条件的预约，立即发送邮件通知

**示例输出：**
```
🏥 Bupa Medical Visa Services 爬虫 + 邮件通知
============================================================
此程序将:
1. 运行爬虫获取最新预约数据
2. 检查是否有符合条件的预约 (Perth/Booragoon/Fremantle 在 2025-08-29 之前)
3. 如果符合条件，立即发送邮件通知

🤖 步骤1: 运行爬虫获取数据...
是否使用无头模式？(y/n，默认y): y
✅ 爬虫运行成功，获取到 6 个位置的数据

📧 步骤2: 检查条件并发送通知...
🎯 发现 2 个符合条件的预约时段:
  📍 Perth (4 km) - Friday 23/08/2025 09:00 AM
  📍 Fremantle (12 km) - Monday 26/08/2025 14:30 PM
✅ 邮件通知发送成功！

============================================================
📊 运行总结:
  数据获取: ✅ 成功 (6 个位置)
  邮件通知: ✅ 已发送
  🎉 发现符合条件的预约，请查收邮件！
  检查时间: 2025-08-22 14:30:00
```

### 方式2：定时自动运行

```bash
python schedule_monitor.py
```

**功能：**
- 每30分钟自动运行一次 `bupa_monitor.py`
- 在后台持续监控
- 生成 `schedule_monitor.log` 日志文件

### 方式3：只运行爬虫（不检查通知）

```bash
python bupa_scraper_v2.py
```

**功能：**
- 只获取预约数据
- 保存到 CSV 和 JSON 文件
- 不发送邮件通知

## 📧 邮件通知详情

### 触发条件
- **地点**: Perth、Booragoon、Fremantle
- **时间**: 2025年8月29日之前
- **状态**: 有可用预约时段

### 邮件内容
- 🏥 医疗中心名称和距离
- 📅 具体预约时间
- 📍 完整地址信息
- 🏢 中心类型（Bupa Centre / Regional Medical Centre）
- 🔗 直接预约链接

### 通知特点
- ✅ 发现新的符合条件预约立即通知
- ✅ HTML格式美观邮件
- ✅ 包含所有必要信息
- ✅ 提供操作建议

## ⚙️ 配置说明

### 环境变量 (.env 文件)

```bash
# Gmail 配置
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_digit_password
NOTIFICATION_EMAIL=recipient@gmail.com

# 监控设置
MONITOR_LOCATIONS=Perth,Booragoon,Fremantle
CUTOFF_DATE=2025-08-29
CHECK_INTERVAL=30
```

### 自定义选项

**修改监控地点：**
```bash
MONITOR_LOCATIONS=Perth,Booragoon  # 只监控这两个
```

**修改截止日期：**
```bash
CUTOFF_DATE=2025-09-15  # 改为9月15日
```

**修改检查间隔：**
```bash
CHECK_INTERVAL=15  # 15分钟检查一次
```

## 🔧 技术特点

### 改进的架构
- **分离关注点**: 爬虫、检查、通知各自独立
- **即时响应**: 每次运行都检查并通知
- **灵活使用**: 可单次运行或定时调度
- **详细日志**: 完整的执行过程记录

### 智能筛选
- **地点匹配**: 精确匹配监控地点
- **日期解析**: 自动解析预约日期
- **条件判断**: 严格按照设定条件筛选
- **结果展示**: 清晰显示筛选结果

### 邮件系统
- **HTML邮件**: 美观的格式化邮件
- **Gmail支持**: 完整的Gmail SMTP配置
- **错误处理**: 完善的邮件发送错误处理
- **测试功能**: 内置邮件配置测试

## 🐛 故障排除

### 常见问题

**1. 爬虫运行失败**
```bash
# 检查网络连接
ping bmvs.onlineappointmentscheduling.net.au

# 检查ChromeDriver
which chromedriver
```

**2. 邮件发送失败**
```bash
# 测试邮件配置
python email_notifier.py

# 检查.env文件
cat .env
```

**3. 没有检测到符合条件的预约**
- 检查当前预约数据：查看生成的 `bupa_locations.csv`
- 确认监控地点配置正确
- 确认截止日期设置合理

### 调试技巧

**查看详细日志：**
- 运行时会显示详细的筛选过程
- 包含每个地点的检查结果
- 显示日期解析和条件匹配情况

**手动验证数据：**
```bash
# 只运行爬虫查看数据
python bupa_scraper_v2.py

# 查看CSV数据
cat bupa_locations.csv
```

## 📱 使用建议

### 最佳实践
1. **定期检查**: 建议每30分钟运行一次
2. **手机通知**: 设置邮箱手机推送
3. **快速响应**: 收到通知后尽快预约
4. **备用方案**: 同时关注官方网站

### 运行策略
- **工作日**: 使用定时监控 `schedule_monitor.py`
- **急需时**: 手动频繁运行 `bupa_monitor.py`
- **测试时**: 先运行 `bupa_scraper_v2.py` 查看数据

## 🎉 使用总结

现在您有了一个完全按照要求设计的监控系统：

✅ **每次运行都检查**: 运行爬虫后立即检查条件  
✅ **精确筛选**: Perth/Booragoon/Fremantle 在 2025-08-29 之前  
✅ **即时通知**: 符合条件立即发送邮件  
✅ **灵活使用**: 可单次运行或定时调度  
✅ **完整信息**: 邮件包含所有必要的预约信息  

祝您早日预约成功！🚀 