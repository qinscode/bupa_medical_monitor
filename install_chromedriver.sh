#!/bin/bash

echo "开始安装 ChromeDriver for Mac ARM64..."

# 检查是否安装了 Chrome
if [ ! -d "/Applications/Google Chrome.app" ]; then
    echo "错误: 未找到 Google Chrome，请先安装 Chrome 浏览器"
    exit 1
fi

# 获取 Chrome 版本
CHROME_VERSION=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version | sed 's/Google Chrome //' | cut -d. -f1-3)
echo "检测到 Chrome 版本: $CHROME_VERSION"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "使用临时目录: $TEMP_DIR"

# 下载对应版本的 ChromeDriver
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
echo "下载 ChromeDriver 版本: $CHROMEDRIVER_VERSION"

# 下载 ChromeDriver
DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_mac64.zip"
echo "下载地址: $DOWNLOAD_URL"

curl -L -o "$TEMP_DIR/chromedriver.zip" "$DOWNLOAD_URL"

if [ $? -ne 0 ]; then
    echo "下载失败，尝试新的下载地址..."
    # 尝试新的 Chrome for Testing API
    DOWNLOAD_URL="https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/mac-arm64/chromedriver-mac-arm64.zip"
    echo "新下载地址: $DOWNLOAD_URL"
    curl -L -o "$TEMP_DIR/chromedriver.zip" "$DOWNLOAD_URL"
fi

if [ $? -ne 0 ]; then
    echo "下载失败，请检查网络连接"
    exit 1
fi

# 解压文件
cd "$TEMP_DIR"
unzip -q chromedriver.zip

# 查找 chromedriver 可执行文件
CHROMEDRIVER_PATH=""
if [ -f "chromedriver" ]; then
    CHROMEDRIVER_PATH="chromedriver"
elif [ -f "chromedriver-mac-arm64/chromedriver" ]; then
    CHROMEDRIVER_PATH="chromedriver-mac-arm64/chromedriver"
else
    echo "未找到 chromedriver 可执行文件"
    ls -la
    exit 1
fi

echo "找到 chromedriver: $CHROMEDRIVER_PATH"

# 添加执行权限
chmod +x "$CHROMEDRIVER_PATH"

# 移动到 /usr/local/bin
sudo mv "$CHROMEDRIVER_PATH" /usr/local/bin/chromedriver

if [ $? -eq 0 ]; then
    echo "✅ ChromeDriver 安装成功!"
    echo "版本信息:"
    /usr/local/bin/chromedriver --version
else
    echo "❌ 安装失败"
    exit 1
fi

# 清理临时文件
rm -rf "$TEMP_DIR"

echo "安装完成，您现在可以运行爬虫了" 