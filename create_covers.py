#!/usr/bin/env python3
"""
创建彩色封面图片（使用 HTML Canvas）
"""

import sqlite3
import os

def create_html_covers():
    """创建HTML封面生成页面"""
    
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, author, cover_url FROM novels ORDER BY id')
    novels = cursor.fetchall()
    conn.close()
    
    # 定义颜色方案
    colors = {
        '星辰变': '#4a90e2',
        '斗破苍穹': '#e74c3c',
        '凡人修仙传': '#2ecc71',
        '鬼吹灯': '#9b59b6',
        '盗墓笔记': '#34495e',
        '诡秘之主': '#1a1a2e',
        '全职高手': '#2c3e50',
        '庆余年': '#16a085',
        '琅琊榜': '#8e44ad',
        '雪中悍刀行': '#34495e',
        '择天记': '#2980b9',
        '斗罗大陆': '#8e44ad',
        '遮天': '#16a085'
    }
    
    # 更新数据库中的封面URL为本地路径
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    
    print("=== 更新封面路径 ===\n")
    
    for novel_id, title, author, current_url in novels:
        # 创建本地封面路径
        cover_path = f"covers/{title}.png"
        
        # 使用占位图URL（因为无法在服务器端生成图片）
        if title in colors:
            color = colors[title].replace('#', '')
            import urllib.parse
            text = urllib.parse.quote(title)
            placeholder_url = f"https://via.placeholder.com/300x400/{color}/ffffff.png?text={text}"
            
            # 更新数据库
            cursor.execute('UPDATE novels SET cover_url = ? WHERE id = ?', 
                          (placeholder_url, novel_id))
            print(f"✓ 已更新《{title}》的封面URL")
    
    conn.commit()
    conn.close()
    
    print("\n✓✓✓ 封面路径更新完成！")

if __name__ == '__main__':
    create_html_covers()
