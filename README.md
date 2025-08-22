# Bupa Medical Visa Services 网站爬虫

这是一个使用 Selenium 自动化访问 [Bupa Medical Visa Services](https://bmvs.onlineappointmentscheduling.net.au/oasis/Default.aspx) 网站并点击 "New Individual booking" 按钮的爬虫脚本。

## 功能特性

- ✅ 自动访问 Bupa Medical Visa Services 网站
- ✅ 智能查找并点击 "New Individual booking" 按钮
- ✅ 多种元素定位策略确保高成功率
- ✅ 自动截图保存页面状态
- ✅ 详细的日志记录
- ✅ 支持有头/无头模式运行
- ✅ 错误处理和重试机制

## 系统要求

- Python 3.7+
- macOS/Linux/Windows
- Chrome 浏览器

## 安装步骤

### 1. 克隆或下载项目

```bash
cd /Users/fudong/Downloads/medical
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包包括：
- `selenium`: Web 自动化框架
- `webdriver-manager`: 自动管理 ChromeDriver
- `beautifulsoup4`: HTML 解析库
- `requests`: HTTP 请求库

### 3. 验证安装

```bash
python -c "import selenium; print('Selenium 安装成功')"
```

## 使用方法

### 基本用法

```bash
python bupa_scraper.py
```

运行时会询问是否使用无头模式：
- 输入 `y` 或 `yes`: 无头模式运行（后台运行，不显示浏览器窗口）
- 输入 `n` 或 `no`: 有头模式运行（显示浏览器窗口，可以看到操作过程）

### 代码中使用

```python
from bupa_scraper import BupaMedicalScraper

# 创建爬虫实例（有头模式）
scraper = BupaMedicalScraper(headless=False)

# 运行爬虫
success = scraper.run()

if success:
    print("爬虫运行成功！")
else:
    print("爬虫运行失败")
```

### 自定义使用

```python
from bupa_scraper import BupaMedicalScraper

# 创建爬虫实例
scraper = BupaMedicalScraper(headless=True)

# 手动控制流程
scraper.setup_driver()
scraper.load_page()
scraper.take_screenshot("before_click.png")
scraper.click_new_individual_booking()
scraper.wait_for_next_page()
scraper.take_screenshot("after_click.png")
scraper.close()
```

## 输出文件

运行完成后，会在项目目录下生成以下文件：

- `initial_page.png`: 初始页面截图
- `final_page.png`: 点击后的页面截图
- `error_page.png`: 如果出错时的页面截图（仅在出错时生成）

## 主要类和方法

### BupaMedicalScraper 类

#### 初始化参数
- `headless` (bool): 是否使用无头模式，默认 False

#### 主要方法
- `setup_driver()`: 设置 Chrome WebDriver
- `load_page()`: 加载目标网页
- `click_new_individual_booking()`: 点击 "New Individual booking" 按钮
- `wait_for_next_page()`: 等待页面跳转
- `take_screenshot(filename)`: 截图保存
- `get_page_info()`: 获取当前页面信息
- `run()`: 运行完整流程
- `close()`: 关闭浏览器

## 技术特性

### 智能元素定位

脚本使用多种策略来查找 "New Individual booking" 按钮：

1. **XPath 选择器**:
   - `//input[@value='New Individual booking']`
   - `//button[contains(text(), 'New Individual booking')]`
   - `//a[contains(text(), 'New Individual booking')]`

2. **CSS 选择器**:
   - `input[value*='New Individual booking']`
   - `button:contains('New Individual booking')`

3. **文本匹配**:
   - 查找包含 "Individual" 和 "booking" 的所有元素

### 点击策略

- 优先使用标准的 `click()` 方法
- 如果失败，自动切换到 JavaScript 点击
- 点击前自动滚动到元素位置

### 错误处理

- 网络超时处理
- 元素未找到处理
- 页面加载失败处理
- 详细的错误日志记录

## 配置选项

### Chrome 浏览器选项

脚本默认配置了以下 Chrome 选项：

```python
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
```

### 等待时间

- 隐式等待: 10秒
- 页面加载等待: 20秒
- 页面跳转等待: 30秒

## 故障排除

### 常见问题

1. **ChromeDriver 版本不匹配**
   - 脚本使用 `webdriver-manager` 自动下载匹配的 ChromeDriver
   - 如果仍有问题，尝试手动更新 Chrome 浏览器

2. **元素定位失败**
   - 检查网站是否有更新
   - 查看 `error_page.png` 截图
   - 检查网络连接

3. **页面加载超时**
   - 检查网络连接
   - 尝试增加等待时间
   - 使用有头模式查看页面状态

### 调试技巧

1. **使用有头模式**:
   ```python
   scraper = BupaMedicalScraper(headless=False)
   ```

2. **查看日志**:
   - 所有操作都有详细日志记录
   - 日志级别: INFO

3. **截图分析**:
   - 每个关键步骤都会自动截图
   - 可以通过截图分析问题

## 注意事项

1. **网站条款**: 请确保您的使用符合 Bupa Medical Visa Services 的服务条款
2. **请求频率**: 避免过于频繁的请求，以免被网站限制
3. **数据隐私**: 注意保护个人敏感信息
4. **合法使用**: 仅用于合法和授权的目的

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请创建 Issue 或联系开发者。 