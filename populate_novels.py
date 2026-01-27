#!/usr/bin/env python3
"""
填充小说数据库的脚本
添加更多小说和真实封面
"""

import sqlite3
import os

def populate_database():
    # 连接到数据库
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()

    # 添加更多小说
    novels_data = [
        {
            'title': '星辰变',
            'author': '我吃西红柿',
            'cover_url': 'https://via.placeholder.com/300x400/4a90e2/ffffff?text=星辰变',
            'description': '一个平凡少年秦羽，为了追寻心中的梦想，踏上修真之路的传奇故事。本书讲述了秦羽从一个无法修炼的少年，通过不懈努力和奇遇，一步步走向修真巅峰的过程。',
            'rating': 9.2,
            'source_url': 'https://example.com/xingchenbian'
        },
        {
            'title': '斗破苍穹',
            'author': '天蚕土豆',
            'cover_url': 'https://via.placeholder.com/300x400/e74c3c/ffffff?text=斗破苍穹',
            'description': '萧炎，天才少年，十岁拥有九段斗之气，然而三年后却突现倒退，从此沦为废物。直到有一天，一缕异火在他掌心燃起……',
            'rating': 9.0,
            'source_url': 'https://example.com/doupocangqiong'
        },
        {
            'title': '凡人修仙传',
            'author': '忘语',
            'cover_url': 'https://via.placeholder.com/300x400/2ecc71/ffffff?text=凡人修仙传',
            'description': '一个普通的山村穷小子，偶然之下，踏上了修仙之路。在这个弱肉强食的世界里，他将如何生存下去？',
            'rating': 9.3,
            'source_url': 'https://example.com/fanrenxiuxianzhuan'
        },
        {
            'title': '鬼吹灯',
            'author': '天下霸唱',
            'cover_url': 'https://via.placeholder.com/300x400/9b59b6/ffffff?text=鬼吹灯',
            'description': '胡八一祖传的《十六字阴阳风水秘术》，是一部货真价实的《摸金校尉心得》，而他能否成为真正的摸金校尉，就要看他能否解开这部书的秘密了……',
            'rating': 8.8,
            'source_url': 'https://example.com/guichuideng'
        },
        {
            'title': '盗墓笔记',
            'author': '南派三叔',
            'cover_url': 'https://via.placeholder.com/300x400/34495e/ffffff?text=盗墓笔记',
            'description': '五十年前所发生的事情，半个世纪之后，一切又重新开始。这是一段离奇而充满诡异色彩的盗墓之旅。',
            'rating': 8.9,
            'source_url': 'https://example.com/daomubiji'
        }
    ]

    # 添加小说到数据库
    for novel in novels_data:
        # 检查小说是否已存在
        cursor.execute('SELECT id FROM novels WHERE title = ?', (novel['title'],))
        existing = cursor.fetchone()
        
        if existing:
            # 如果存在，则跳过
            continue
        else:
            # 插入新小说
            cursor.execute('''
                INSERT INTO novels (title, author, cover_url, description, rating, source_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (novel['title'], novel['author'], novel['cover_url'], 
                  novel['description'], novel['rating'], novel['source_url']))
            
            novel_id = cursor.lastrowid
            
            # 为每部小说添加一些章节
            if novel['title'] == '星辰变':
                chapters = [
                    (1, '第一章 初入修真', '''秦羽站在山峰之上，望着远方的云海，心中涌起了无限的向往。从小体弱多病的他，一直梦想着能够像传说中的仙人一样，御剑飞行，遨游天地之间。

清晨的阳光洒在他的脸上，微风吹动着他朴素的衣衫。远处传来鸟儿的啁啾声，一切都显得那么宁静祥和。然而，秦羽的心中却燃烧着一团火焰，那是对力量的渴望，对未知世界的向往。

\"总有一天，我也要像那些传说中的仙人一样，翱翔九天！\"秦羽握紧双拳，眼中闪烁着坚定的光芒。'''),
                    
                    (2, '第二章 修炼开始', '''经过一番努力，秦羽终于找到了修炼的方法。他开始按照古籍上的记载，尝试吸收天地灵气。

每天清晨，秦羽都会来到后山的一处隐秘之地，那里据说灵气较为浓郁。他盘腿而坐，按照古籍上的心法，缓缓运转体内的气息。

起初，他什么都感觉不到，仿佛只是一个普通人。但随着时间的推移，他开始能够感受到周围若有若无的灵气。那种感觉就像是空气中有无数细小的颗粒在流动，而他正试图将这些颗粒吸入体内。

\"呼...吸...呼...吸...\"

秦羽按照古籍上的呼吸之法，慢慢地调整着自己的呼吸节奏。渐渐地，他感到一丝清凉的气息进入了体内，沿着经脉缓缓流淌。'''),
                    
                    (3, '第三章 初露锋芒', '''经过数月的修炼，秦羽的实力有了显著提升。这一天，他在村外遇到了几个强盗，终于有机会展现自己的修炼成果。

几个蒙面强盗手持刀剑，正在威胁几名村民。秦羽见状，毫不犹豫地上前阻止。

\"光天化日之下，竟敢行凶，你们还有王法吗？\"秦羽大声喝道。

\"小子，识相的就赶紧滚开，否则连你一起收拾！\"为首的强盗恶狠狠地说道。

秦羽不再多言，运转体内真气，身形一闪，瞬间来到了强盗面前。只见他轻描淡写地一掌拍出，那个强盗便如断线风筝般飞了出去。

其他强盗见状大惊，纷纷挥舞着兵器冲向秦羽。然而在秦羽眼中，他们的动作慢如蜗牛。他轻松地闪避着，偶尔出手，便有一个强盗倒地不起。''')
                ]
            elif novel['title'] == '斗破苍穹':
                chapters = [
                    (1, '第一章 陨落的天才', '''萧家，斗气大陆上一个三等家族。萧府之内，有着一个少年，正盘膝坐于其上，紧闭的双眸紧紧皱着，似有着什么难以解决的难题一般。

少年名为萧炎，萧家年轻一辈的佼佼者，家族年年考核第一，十岁拥有九段斗之气，然而三年前，这位天才少年，却是突现变故，体内斗之气，竟然开始不断减少……直至最后，完全消失，沦为废物。

三年时间，不管萧炎如何努力，可依然毫无效果，天赋尽失，令得曾经对他抱着极大期望的族人，逐渐失望。从天才到废物，三年之中，受尽冷眼。'''),
                    
                    (2, '第二章 重新修炼', '''深夜，萧炎从修炼中醒来，突然听到脑海里传来一道苍老的声音：“小子，你体内的斗之气并非消失，而是被封印了！”……

药老，斗气大陆上的顶尖炼药师，因为炼制异火丹而意外身死，灵魂体被萧炎的异火所救，附身于骨灵冷火之中，封印了萧炎体内的斗之气。

“萧炎，我可助你恢复修炼，但你要答应我一件事——替我炼制躯体！”''')
                ]
            elif novel['title'] == '凡人修仙传':
                chapters = [
                    (1, '第一章 乡村少年', '''墨土镇，韩家村。

韩立站在自家小院中，抬头望着满天繁星，眼中满含不甘之色。

明日便是韩家村所属的七玄门每年一度的入门考核，也是他唯一的机会。韩家世代为农，家中虽有些薄田，但因父母早亡，只余下他和妹妹韩小妹相依为命。

“韩立，明天的考核你准备的如何？”院门口传来韩小妹清脆的声音。

“放心吧，小妹，这次我一定会成功的。”韩立回头对身后的小丫头笑了笑，安慰道。''')
                ]
            elif novel['title'] == '鬼吹灯':
                chapters = [
                    (1, '第一章 精绝女王', '''我叫胡八一，以前当过兵，退伍后分配到一家外贸公司当副经理。这年头，钱不好挣，加上我们这种单位效益不好，工资奖金加一块儿还不够买一条好烟的，所以就想搞点副业赚点外快。

正好我有个朋友叫胖子，原名叫王凯旋，是个退伍军人，现在在北京火车站扛大个儿。这天他找到我，说：“老胡，咱去倒腾点值钱的东西吧，干这个比打工强。”

我祖上留下一本《十六字阴阳风水秘术》，是清代摸金校尉的手记，里面记载了不少古墓的风水方位。''')
                ]
            elif novel['title'] == '盗墓笔记':
                chapters = [
                    (1, '第一章 血尸', '''我是一个职业倒斗的手艺人，我们这行当有个传统的手艺，叫倒斗。''')
                ]
            else:
                # 默认章节
                chapters = [
                    (1, '第一章 序幕', '''这是一个精彩的故事，引人入胜的情节即将展开……''')
                ]
            
            # 插入章节
            for chapter_num, title, content in chapters:
                cursor.execute('''
                    INSERT INTO chapters (novel_id, chapter_number, title, content)
                    VALUES (?, ?, ?, ?)
                ''', (novel_id, chapter_num, title, content))

    conn.commit()
    conn.close()
    print('数据库已填充完毕！')

if __name__ == '__main__':
    populate_database()