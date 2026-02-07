#!/usr/bin/env python3
"""
网络小说阅读器
支持获取小说封面、作者、简介、章节、内容、评分等功能
"""

import os
import json
import requests
from flask import Flask, render_template, jsonify, request, send_from_directory
import sqlite3
from datetime import datetime
import threading
import time
from urllib.parse import urlparse
import re

app = Flask(__name__)

# 数据库初始化
def init_db():
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    
    # 创建小说表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS novels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            cover_url TEXT,
            description TEXT,
            rating REAL,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建章节表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            novel_id INTEGER,
            chapter_number INTEGER,
            title TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (novel_id) REFERENCES novels (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# 小说数据类
class NovelManager:
    def __init__(self):
        self.novels = {}
        
    def add_novel(self, title, author, cover_url, description, rating, source_url):
        """添加小说到数据库"""
        conn = sqlite3.connect('novels.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO novels (title, author, cover_url, description, rating, source_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, author, cover_url, description, rating, source_url))
        
        novel_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return novel_id
    
    def get_novel_by_id(self, novel_id):
        """获取小说详情"""
        conn = sqlite3.connect('novels.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM novels WHERE id = ?', (novel_id,))
        novel = cursor.fetchone()
        
        if novel:
            novel_dict = {
                'id': novel[0],
                'title': novel[1],
                'author': novel[2],
                'cover_url': novel[3],
                'description': novel[4],
                'rating': novel[5],
                'source_url': novel[6],
                'created_at': novel[7]
            }
        else:
            novel_dict = None
            
        conn.close()
        return novel_dict
    
    def get_all_novels(self):
        """获取所有小说列表"""
        conn = sqlite3.connect('novels.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, title, author, cover_url, rating FROM novels ORDER BY created_at DESC')
        novels = cursor.fetchall()
        
        novel_list = []
        for novel in novels:
            novel_list.append({
                'id': novel[0],
                'title': novel[1],
                'author': novel[2],
                'cover_url': novel[3],
                'rating': novel[4]
            })
        
        conn.close()
        return novel_list
    
    def add_chapter(self, novel_id, chapter_number, title, content):
        """添加章节"""
        conn = sqlite3.connect('novels.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chapters (novel_id, chapter_number, title, content)
            VALUES (?, ?, ?, ?)
        ''', (novel_id, chapter_number, title, content))
        
        conn.commit()
        conn.close()
    
    def get_chapters(self, novel_id):
        """获取小说所有章节"""
        conn = sqlite3.connect('novels.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, chapter_number, title FROM chapters 
            WHERE novel_id = ? ORDER BY chapter_number
        ''', (novel_id,))
        chapters = cursor.fetchall()
        
        chapter_list = []
        for chapter in chapters:
            chapter_list.append({
                'id': chapter[0],
                'chapter_number': chapter[1],
                'title': chapter[2]
            })
        
        conn.close()
        return chapter_list
    
    def get_chapter_content(self, chapter_id):
        """获取章节内容"""
        conn = sqlite3.connect('novels.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT content FROM chapters WHERE id = ?', (chapter_id,))
        result = cursor.fetchone()
        
        content = result[0] if result else None
        conn.close()
        return content

# 创建全局小说管理器
novel_manager = NovelManager()

@app.route('/')
def index():
    """主页 - 显示所有小说"""
    novels = novel_manager.get_all_novels()
    return render_template('index.html', novels=novels)

@app.route('/novel/<int:novel_id>')
def novel_detail(novel_id):
    """小说详情页"""
    novel = novel_manager.get_novel_by_id(novel_id)
    if not novel:
        return "小说不存在", 404
    
    chapters = novel_manager.get_chapters(novel_id)
    return render_template('novel_detail.html', novel=novel, chapters=chapters)

@app.route('/chapter/<int:chapter_id>')
def read_chapter(chapter_id):
    """阅读章节"""
    content = novel_manager.get_chapter_content(chapter_id)
    if not content:
        return "章节不存在", 404
    
    # 获取章节信息
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.title, c.chapter_number, n.title as novel_title, n.id as novel_id
        FROM chapters c
        JOIN novels n ON c.novel_id = n.id
        WHERE c.id = ?
    ''', (chapter_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return "章节信息不存在", 404
    
    chapter_info = {
        'id': chapter_id,
        'title': result[0],
        'chapter_number': result[1],
        'novel_title': result[2],
        'novel_id': result[3]
    }
    
    # 获取上一章和下一章
    cursor.execute('''
        SELECT id FROM chapters 
        WHERE novel_id = ? AND chapter_number < ?
        ORDER BY chapter_number DESC LIMIT 1
    ''', (chapter_info['novel_id'], chapter_info['chapter_number']))
    prev_result = cursor.fetchone()
    chapter_info['prev_id'] = prev_result[0] if prev_result else None
    
    cursor.execute('''
        SELECT id FROM chapters 
        WHERE novel_id = ? AND chapter_number > ?
        ORDER BY chapter_number ASC LIMIT 1
    ''', (chapter_info['novel_id'], chapter_info['chapter_number']))
    next_result = cursor.fetchone()
    chapter_info['next_id'] = next_result[0] if next_result else None
    
    conn.close()
    
    return render_template('chapter.html', content=content, chapter=chapter_info)

@app.route('/api/novels')
def api_novels():
    """API: 获取所有小说"""
    novels = novel_manager.get_all_novels()
    return jsonify(novels)

@app.route('/api/novel/<int:novel_id>')
def api_novel(novel_id):
    """API: 获取小说详情"""
    novel = novel_manager.get_novel_by_id(novel_id)
    if not novel:
        return jsonify({'error': 'Novel not found'}), 404
    
    chapters = novel_manager.get_chapters(novel_id)
    novel['chapters'] = chapters
    return jsonify(novel)

@app.route('/api/chapter/<int:chapter_id>')
def api_chapter(chapter_id):
    """API: 获取章节内容"""
    content = novel_manager.get_chapter_content(chapter_id)
    if not content:
        return jsonify({'error': 'Chapter not found'}), 404
    
    return jsonify({'content': content})

@app.route('/static/covers/<path:filename>')
def covers(filename):
    """提供封面图片"""
    return send_from_directory('covers', filename)

def create_templates():
    """创建HTML模板"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # 主页模板
    index_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网络小说阅读器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
        }
        h1 {
            color: white;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            color: rgba(255,255,255,0.8);
            font-size: 1.1em;
        }
        .novel-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .novel-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            text-align: center;
        }
        .novel-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .cover-img {
            width: 120px;
            height: 160px;
            object-fit: cover;
            border-radius: 10px;
            margin: 0 auto 15px;
            display: block;
            border: 3px solid #ddd;
        }
        .novel-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .novel-author {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .novel-rating {
            color: #ff6b35;
            font-weight: bold;
            font-size: 1.1em;
        }
        .add-novel-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            font-size: 2em;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .add-novel-btn:hover {
            transform: scale(1.1);
        }
        .search-box {
            margin: 20px 0;
            text-align: center;
        }
        .search-input {
            padding: 12px 20px;
            border: none;
            border-radius: 25px;
            width: 300px;
            font-size: 16px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        @media (max-width: 768px) {
            .novel-grid {
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            }
            .search-input {
                width: 250px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 网络小说阅读器</h1>
            <p class="subtitle">享受您的私人阅读时光</p>
        </header>
        
        <div class="search-box">
            <input type="text" class="search-input" id="searchInput" placeholder="🔍 搜索小说...">
        </div>
        
        <div class="novel-grid" id="novelGrid">
            {% for novel in novels %}
            <div class="novel-card" onclick="window.location.href='/novel/{{ novel.id }}'">
                {% if novel.cover_url %}
                <img src="{{ novel.cover_url }}" alt="{{ novel.title }}" class="cover-img" onerror="this.style.display='none'">
                {% endif %}
                <div class="novel-title">{{ novel.title }}</div>
                <div class="novel-author">作者: {{ novel.author }}</div>
                <div class="novel-rating">⭐ {{ "%.1f"|format(novel.rating or 0) }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <button class="add-novel-btn" onclick="location.href='/add'">+</button>
    
    <script>
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.novel-card');
            
            cards.forEach(card => {
                const title = card.querySelector('.novel-title').textContent.toLowerCase();
                const author = card.querySelector('.novel-author').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || author.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>
'''
    
    novel_detail_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ novel.title }} - 详情</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        .novel-header {
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        .cover-container {
            flex-shrink: 0;
        }
        .cover-img {
            width: 200px;
            height: 280px;
            object-fit: cover;
            border-radius: 10px;
            border: 3px solid #ddd;
        }
        .novel-info {
            flex: 1;
        }
        .novel-title {
            font-size: 2em;
            color: #333;
            margin-bottom: 10px;
        }
        .novel-author {
            font-size: 1.2em;
            color: #666;
            margin-bottom: 15px;
        }
        .novel-rating {
            font-size: 1.3em;
            color: #ff6b35;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .novel-description {
            line-height: 1.6;
            color: #555;
            margin-bottom: 20px;
        }
        .chapters-list {
            margin-top: 30px;
        }
        .chapters-title {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .chapter-item {
            padding: 12px 15px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s ease;
            border-left: 4px solid #667eea;
        }
        .chapter-item:hover {
            background: #e9ecef;
        }
        .chapter-title {
            font-weight: bold;
            color: #333;
        }
        .back-btn {
            display: inline-block;
            margin-bottom: 20px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        }
        @media (max-width: 768px) {
            .novel-header {
                flex-direction: column;
                text-align: center;
            }
            .cover-img {
                margin: 0 auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-btn">← 返回书架</a>
        
        <div class="novel-header">
            <div class="cover-container">
                {% if novel.cover_url %}
                <img src="{{ novel.cover_url }}" alt="{{ novel.title }}" class="cover-img">
                {% endif %}
            </div>
            <div class="novel-info">
                <h1 class="novel-title">{{ novel.title }}</h1>
                <div class="novel-author">作者: {{ novel.author }}</div>
                <div class="novel-rating">⭐ 评分: {{ "%.1f"|format(novel.rating or 0) }}</div>
                <div class="novel-description">{{ novel.description }}</div>
            </div>
        </div>
        
        <div class="chapters-list">
            <h2 class="chapters-title">📖 章节目录</h2>
            {% for chapter in chapters %}
            <div class="chapter-item" onclick="window.location.href='/chapter/{{ chapter.id }}'">
                <div class="chapter-title">{{ chapter.title }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''
    
    chapter_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ chapter.title }} - {{ chapter.novel_title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            background: #f5f5dc;
            color: #333;
            line-height: 1.8;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .chapter-header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #ddd;
        }
        .chapter-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .novel-title {
            font-size: 1.2em;
            color: #666;
            margin-bottom: 15px;
        }
        .chapter-number {
            font-size: 1em;
            color: #999;
        }
        .chapter-content {
            font-size: 1.2em;
            text-indent: 2em;
            margin-bottom: 30px;
            line-height: 2;
        }
        .navigation {
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        .nav-btn {
            padding: 12px 25px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        }
        .nav-btn:hover {
            opacity: 0.9;
        }
        .back-btn {
            display: inline-block;
            margin-bottom: 20px;
            padding: 10px 20px;
            background: #6c757d;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        }
        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }
            .chapter-content {
                font-size: 1.1em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/novel/{{ chapter.novel_id }}" class="back-btn">← 返回目录</a>
        
        <div class="chapter-header">
            <h1 class="chapter-title">{{ chapter.title }}</h1>
            <div class="novel-title">{{ chapter.novel_title }}</div>
            <div class="chapter-number">第 {{ chapter.chapter_number }} 章</div>
        </div>
        
        <div class="chapter-content">
            {{ content|replace('\\n', '<br>')|safe }}
        </div>
        
        <div class="navigation">
            <a href="/novel/{{ chapter.novel_id }}" class="nav-btn">📚 返回目录</a>
            <a href="/" class="nav-btn">🏠 返回书架</a>
        </div>
    </div>
</body>
</html>
'''
    
    # 写入模板文件
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    with open(os.path.join(templates_dir, 'novel_detail.html'), 'w', encoding='utf-8') as f:
        f.write(novel_detail_html)
    
    with open(os.path.join(templates_dir, 'chapter.html'), 'w', encoding='utf-8') as f:
        f.write(chapter_html)

def sample_data():
    """添加一些示例数据用于演示"""
    # 检查是否已有数据
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM novels')
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        # 添加示例小说
        novel_id = novel_manager.add_novel(
            title="星辰变",
            author="我吃西红柿",
            cover_url="https://via.placeholder.com/200x280/4a90e2/ffffff?text=星辰变",
            description="一个平凡少年秦羽，为了追寻心中的梦想，踏上修真之路的传奇故事。",
            rating=9.2,
            source_url="https://example.com/xingchenbian"
        )
        
        # 添加示例章节
        novel_manager.add_chapter(novel_id, 1, "第一章 初入修真", "秦羽站在山峰之上，望着远方的云海，心中涌起了无限的向往。从小体弱多病的他，一直梦想着能够像传说中的仙人一样，御剑飞行，遨游天地之间...")
        novel_manager.add_chapter(novel_id, 2, "第二章 修炼开始", "经过一番努力，秦羽终于找到了修炼的方法。他开始按照古籍上的记载，尝试吸收天地灵气...")
        novel_manager.add_chapter(novel_id, 3, "第三章 初露锋芒", "经过数月的修炼，秦羽的实力有了显著提升。这一天，他在村外遇到了几个强盗，终于有机会展现自己的修炼成果...")

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 创建模板
    create_templates()
    
    # 创建封面目录
    os.makedirs('covers', exist_ok=True)
    
    # 添加示例数据
    sample_data()
    
    print("网络小说阅读器已启动!")
    print("访问地址: http://localhost:5000")
    print("支持远程访问: http://YOUR_IP:5000")
    print("按 Ctrl+C 停止服务")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=8080, debug=False)