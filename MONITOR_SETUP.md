# Bupa Medical Visa Services 预约监控系统设置指南

## 🎯 系统功能

这个监控系统会自动：
- 每30分钟检查一次 Perth、Booragoon、Fremantle 的预约时段
- 筛选出 **2025年8月29日之前** 的可用预约
- 发现符合条件的预约时立即发送邮件通知
- 避免重复通知相同的预约时段

## 📋 设置步骤

### 1. 安装依赖包

```bash
pip install -r requirements.txt
```

### 2. 配置 Gmail 邮箱

#### 2.1 启用两步验证
1. 打开 [Google 账户设置](https://myaccount.google.com/)
2. 选择 "安全性"
3. 启用 "两步验证"

#### 2.2 生成应用专用密码
1. 在 "两步验证" 下方，找到 "应用专用密码"
2. 选择 "邮件" 和设备类型
3. 生成16位应用专用密码（**重要**: 复制并保存这个密码）

### 3. 创建环境配置文件

```bash
# 复制模板文件
cp env_template.txt .env
```

编辑 `.env` 文件，填写真实信息：

```bash
# Gmail 发送方配置
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_digit_app_password

# 接收方邮箱（可以是同一个邮箱）
NOTIFICATION_EMAIL=recipient@gmail.com

# 监控设置（可选修改）
MONITOR_LOCATIONS=Perth,Booragoon,Fremantle
CUTOFF_DATE=2025-08-29
CHECK_INTERVAL=30
```

### 4. 测试邮件配置

```bash
python email_notifier.py
```

如果配置正确，您会收到一封测试邮件。

## 🚀 使用方式

### 方式1：单次运行（推荐）

每次运行时自动检查并发送通知：

```bash
python bupa_monitor.py
```

这个脚本会：
1. 运行爬虫获取最新数据
2. 检查是否有符合条件的预约
3. 如果有，立即发送邮件通知

### 方式2：定时自动运行

如果想要定期自动检查：

```bash
python schedule_monitor.py
```

这个脚本会：
- 每30分钟自动运行一次 `bupa_monitor.py`
- 生成 `schedule_monitor.log` 日志文件
- 可通过 `.env` 中的 `CHECK_INTERVAL` 调整间隔

### 方式3：手动调用爬虫

如果只想获取数据不发送通知：

```bash
python bupa_scraper_v2.py
```

## 📧 邮件通知示例

当发现符合条件的预约时，您会收到类似这样的邮件：

**主题**: 🏥 Bupa 医疗预约通知 - 发现 2 个符合条件的预约

**内容**:
```
检测时间: 2025-08-22 14:30:00
筛选条件: 2025-08-29 之前的 Perth/Booragoon/Fremantle 预约
发现结果: 2 个符合条件的预约时段

可用预约详情:

🏥 Perth (4 km)
📅 预约时间: Friday 23/08/2025 09:00 AM
📍 地址: Perth - Bupa Centre, Level 3, 2 Mill Street, Perth
🏢 类型: Bupa Centre

🏥 Fremantle (12 km)  
📅 预约时间: Monday 26/08/2025 14:30 PM
📍 地址: Ellen Health, 7/195 Hampton Road, Fremantle WA 6160
🏢 类型: Regional Medical Centre
```

## 📊 监控规则详解

### 筛选条件
- **地点**: Perth、Booragoon、Fremantle
- **时间**: 2025年8月29日之前的预约
- **状态**: 必须有可用时段

### 通知逻辑
- **新预约**: 发现新的符合条件预约时立即通知
- **避免重复**: 相同预约时段不会重复通知
- **冷却时间**: 距离上次通知至少4小时才会再次通知

### 检查频率
- 默认每30分钟检查一次
- 可在 `.env` 文件中修改 `CHECK_INTERVAL`

## 📁 生成的文件

运行期间会生成以下文件：
- `bupa_monitor.log` - 监控系统日志
- `bupa_locations.csv` - 最新一次的预约数据
- `bupa_locations.json` - JSON格式的预约数据
- `*.png` - 网页截图

## 🔧 自定义配置

### 修改监控地点
```bash
# 在 .env 文件中修改
MONITOR_LOCATIONS=Perth,Booragoon  # 只监控这两个地点
```

### 修改截止日期
```bash
# 在 .env 文件中修改
CUTOFF_DATE=2025-09-15  # 改为9月15日之前
```

### 修改检查频率
```bash
# 在 .env 文件中修改
CHECK_INTERVAL=15  # 每15分钟检查一次
```

## 🐛 故障排除

### 邮件发送失败
1. **检查应用专用密码**: 确保使用的是16位应用专用密码，不是普通密码
2. **检查两步验证**: 确保已启用两步验证
3. **检查网络**: 确保能访问 smtp.gmail.com:587

### 爬虫执行失败
1. **检查ChromeDriver**: 确保已安装最新版本的 Chrome 和 ChromeDriver
2. **检查网络**: 确保能访问 bmvs.onlineappointmentscheduling.net.au
3. **查看日志**: 检查 `bupa_monitor.log` 中的错误信息

### 测试单次运行
```bash
# 只运行一次检查，不启动定时监控
python -c "from bupa_monitor import BupaMonitor; BupaMonitor().run_check()"
```

## 📱 接收移动端通知

建议设置邮箱在手机上的推送通知：
1. 在手机上添加邮箱账户
2. 开启邮件推送通知
3. 这样就能第一时间收到预约通知

## ⚠️ 重要提醒

1. **及时响应**: 预约时段可能很快被他人预订，收到通知后请尽快行动
2. **保护隐私**: `.env` 文件包含敏感信息，不要分享给他人
3. **合理使用**: 避免过于频繁的检查，以免对网站造成压力
4. **备用方案**: 建议同时手动关注官方网站的更新

## 📞 技术支持

如遇到问题，请检查：
1. `bupa_monitor.log` 文件中的错误日志
2. 确保所有依赖包正确安装
3. 验证 `.env` 文件配置正确

祝您早日预约成功！ 🎉 