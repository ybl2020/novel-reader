#!/usr/bin/env python3
"""生成简单的封面图片"""

from PIL import Image, ImageDraw, ImageFont
import sqlite3

# 颜色方案
COLORS = [
    '#4a90e2',  # 蓝色
    '#e74c3c',  # 红色
    '#2ecc71',  # 绿色
    '#9b59b6',  # 紫色
    '#34495e',  # 深灰
    '#f39c12',  # 橙色
    '#1abc9c',  # 青色
    '#e67e22',  # 深橙
]

def generate_cover(title, color, output_path):
    """生成简单的纯色封面"""
    # 创建图片
    img = Image.new('RGB', (300, 400), color)
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体
    try:
        font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 40)
    except:
        font = ImageFont.load_default()
    
    # 绘制标题（居中）
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (300 - text_width) // 2
    y = (400 - text_height) // 2
    
    # 添加阴影
    draw.text((x+2, y+2), title, font=font, fill='#000000')
    # 主文字
    draw.text((x, y), title, font=font, fill='#ffffff')
    
    img.save(output_path)
    print(f"生成封面: {output_path}")

# 连接数据库
conn = sqlite3.connect('novels.db')
cursor = conn.cursor()

# 获取所有小说
cursor.execute('SELECT id, title FROM novels')
novels = cursor.fetchall()

for i, (novel_id, title) in enumerate(novels):
    color = COLORS[i % len(COLORS)]
    output_path = f'static/covers/novel_{novel_id}.jpg'
    generate_cover(title, color, output_path)
    
    # 更新数据库中的封面路径
    cursor.execute(
        'UPDATE novels SET cover_url = ? WHERE id = ?',
        (f'/static/covers/novel_{novel_id}.jpg', novel_id)
    )

conn.commit()
conn.close()

print(f"\n✅ 已生成 {len(novels)} 个封面图片！")
