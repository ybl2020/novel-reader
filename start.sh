#!/bin/bash

# 网络小说阅读器 - 快速启动脚本

echo "🚀 正在启动网络小说阅读器..."
echo ""
echo "📱 移动端优化版本"
echo "✨ 新功能：上一章/下一章导航"
echo ""

# 获取本机IP地址
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

echo "📍 访问地址："
echo "   本地: http://localhost:8080"
if [ ! -z "$LOCAL_IP" ]; then
    echo "   局域网: http://$LOCAL_IP:8080"
    echo ""
    echo "💡 用手机扫描下方二维码访问："
    echo "   http://$LOCAL_IP:8080"
fi
echo ""
echo "按 Ctrl+C 停止服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 启动服务器
python3 server.py
