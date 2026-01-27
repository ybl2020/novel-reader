#!/usr/bin/env python3
"""
网络小说阅读器 - 服务器启动脚本
"""

import subprocess
import sys
import os
from novel_reader import app

def start_server():
    """启动服务器"""
    print("正在启动网络小说阅读器...")
    print("服务器将监听所有网络接口")
    print("访问地址: http://localhost:8080")
    print("局域网访问: http://YOUR_LOCAL_IP:8080")
    print("按 Ctrl+C 停止服务")
    
    try:
        # 使用0.0.0.0确保可以从外部访问
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器时出错: {e}")

if __name__ == '__main__':
    start_server()