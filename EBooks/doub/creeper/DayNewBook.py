"""
豆瓣 > 新书速递
爬虫
"""

import json
import os
import re

import requests
from bs4 import BeautifulSoup

main_url = 'https://book.douban.com/latest?icn=index-latestbook-all'

tmp_book_info_json = ''



def book_info_json_joint(key, value):
    """ 拼接书本的信息
    key 对应的  id
    书名:bookName
    封面:cover
    作者:author
    作者id:authorId
    出版社:publisher
    出品方:exporter
    原作名:originalName
    译者:translator
    出版年:pubTime
    页数:totalPage
    定价:price
    装帧:bindingLayout
    丛书:seriesOfBooks
    国际标准书号:isbn
    内容简介:introduction
    作者简介:authorIntroduction
    评分:score
    标签:tag
    """
    global tmp_book_info_json

    _key = key.replace(':', '')
    _id = ''
    if _key == '书名':
        _id = 'bookName'
    elif _key == '封面':
        _id = 'cover'
    elif _key == '作者':
        _id = 'author'
    elif _key == '作者id':
        _id = 'authorId'
    elif _key == '出版社':
        _id = 'publisher'
    elif _key == '出品方':
        _id = 'exporter'
    elif _key == '原作名':
        _id = 'originalName'
    elif _key == '译者':
        _id = 'translator'
    elif _key == '出版年':
        _id = 'pubTime'
    elif _key == '页数':
        _id = 'totalPage'
    elif _key == '定价':
        _id = 'price'
    elif _key == '装帧':
        _id = 'bindingLayout'
    elif _key == '丛书':
        _id = 'seriesOfBooks'
    elif _key == 'ISBN':
        _id = 'isbn'
    elif _key == '内容简介':
        _id = 'introduction'
    elif _key == '作者简介':
        _id = 'authorIntroduction'
    elif _key == '评分':
        _id = 'score'
    elif _key == '标签':
        _id = 'tag'

    if not _id == '':
        tmp_book_info_json = tmp_book_info_json + ',\"' + _id + '\":\"' + str(value) + '\"'


def deal_author_intro(soup):
    """ 解析作者简介 """
    try:
        author_info = soup.select('#content > div > div.article > div.related_info > div.indent')[1]
        author_text = author_info.select('.intro')[0].text.strip()
        author_text = str(author_text).replace('\\', '\\\\')
        author_text = re.sub('[\x00-\x1f]', ' ', str(author_text).replace('"', '\\"'))
        print('作者简介:' + author_text)
        book_info_json_joint('作者简介', author_text)
        return
    except IndexError:
        """ 作者简介错误 """
    try:
        author_info = soup.select('#content > div > div.article > div.related_info > div.indent')
        author_text = author_info[0].select('span')[1].select('.intro')[0].text.strip()
        author_text = str(author_text).replace('\\', '\\\\')
        author_text = re.sub('[\x00-\x1f]', ' ', str(author_text).replace('"', '\\"'))
        print('作者简介:' + author_text)
        book_info_json_joint('作者简介', author_text)
        return
    except IndexError:
        """ 作者简介错误 """

    print('作者简介错误')


def deal_content_intro(soup):
    """ 解析内容简介 """
    pos = -1
    link_list = soup.select("#link-report > div")
    pos = len(link_list)
    if pos > 0:
        intro = link_list[0].select(".intro")[0].text.strip()

        # print('内容简介:' + str(intro))
        # book_info_json_joint('内容简介', str(intro))
        value_str = intro.replace('\\', '\\\\')
        value_str = value_str.replace('"', '\\"')
        tmp_intro = re.sub('[\x00-\x1f]', ' ', value_str)
        print('内容简介:' + tmp_intro)
        book_info_json_joint('内容简介', tmp_intro)
        return

    link_list = soup.select('#link-report > span.all.hidden > div > div')
    pos = len(link_list)
    if pos > 0:
        intro = link_list[0].text.strip()
        value_str = intro.replace('\\', '\\\\')
        value_str = value_str.replace('"', '\\"')
        tmp_intro = re.sub('[\x00-\x1f]', ' ', value_str)
        # tmp_intro = re.sub('[\x00-\x1f]', ' ', intro.replace('"', '\\"').replace('\\', '\\\\'))
        print('内容简介:' + tmp_intro)
        book_info_json_joint('内容简介', tmp_intro)
        # book_info_json_joint('内容简介', str(intro))
        return


def deal_book_name(soup):
    book_name = soup.select('#wrapper > h1 > span')
    if len(book_name) > 0:
        name_str = book_name[0].text.strip()
        name_str = str(name_str).replace('"', '\\"')
        print('书名:' + str(name_str))
        book_info_json_joint('书名', name_str)


def deal_rating_num(soup):
    """  豆瓣评分 """
    strong = soup.select('#interest_sectl > div > div.rating_self.clearfix > strong')
    if len(strong) > 0:
        print('评分:' + strong[0].text.strip())
        book_info_json_joint('评分', strong[0].text.strip())


def deal_with_key_map(key, pl, json):
    """  解析一些数据 """
    for item_str in json.split('<br'):
        if key not in item_str:
            continue
        tmp_key = key.strip()
        if ':' not in tmp_key:
            tmp_key = tmp_key + ':'
        _name = tmp_key
        content = ''
        if 'href=' in item_str:
            text_list = item_str.split('href=')
            text = text_list[len(text_list) - 1]
            first_pos = text.find('>') + 1
            last_pos = text.find('</a>')
            name = text[first_pos:last_pos].replace(' ', '').strip()
            name_value = re.sub('[\x00-\x1f]', '', name)
            name_value = name_value.replace('\\', '\\\\')
            name_value = name_value.replace('"', '\\"')
            content = name_value
            _name = _name + name_value
        else:
            span_list = item_str.split('</span>')
            span = span_list[len(span_list) - 1].strip()
            span = re.sub('[\x00-\x1f]', '', span)
            span = str(span).replace('\\', '\\\\')
            span = span.replace('"', '\\"')
            content = span
            _name = _name + span
        print(_name)
        book_info_json_joint(tmp_key, content)
        return


def get_book_detail(url):
    """ 获取书本信息 """

    try:
        # req_result = requests.get(url)
        req_result = get_url(url)

    except requests.exceptions.ConnectionError:
        print('错误url: ' + url)
        return

    if req_result.status_code == 200:
        html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        # 图书URL
        main_pic = soup.select('#mainpic')[0].a.attrs['href']
        print('封面:' + main_pic)
        book_info_json_joint('封面', main_pic)

        # 作者ID ??
        articles = soup.select('#content > div > div.article > div')
        for article_item in articles:
            pos = str(article_item).find('collect_form_')
            if pos > -1:
                start_pos = str(article_item).rfind('_') + 1
                end_pos = str(article_item).rfind('"')
                author_id = str(article_item)[start_pos:end_pos]
                print('作者id:' + author_id.strip())
                book_info_json_joint('作者id', author_id.strip())
                break

        # 书名
        deal_book_name(soup)

        # 豆瓣评分
        deal_rating_num(soup)

        # 内容简介
        deal_content_intro(soup)

        # 作者简介
        deal_author_intro(soup)

        # 图书信息
        book_detail = soup.select('#info')[0]
        pl_list = book_detail.select('.pl')
        for pl in pl_list:
            deal_with_key_map(pl.text, str(pl), str(book_detail))

        # 常用标签
        tags_section_span = soup.select("#db-tags-section > div.indent > span")
        tag_value = ''
        for span in tags_section_span:
            # print(span.a.text.strip())
            span_text = str(span.a.text.strip()).replace('\\', '\\\\')
            span_text = span_text.replace('"', '\\"')
            tag_value = tag_value + span_text + ' '
        print('常用标签:' + tag_value)
        book_info_json_joint('标签', str(tag_value))

        # 图书信息的最后处理
        # print(tmp_book_info_json)
        write_book_info(tmp_book_info_json)


is_remove = False
write_file_path = 'NewBookInfo.txt'


def write_book_info(book_info):
    content = '{' + str(book_info)[1:] + '}'
    print(content)
    json_str = json.loads(content)
    print('test:' + str(json_str))

    print('检查json成功\n')
    global is_remove
    if not os.path.exists(write_file_path):
        is_remove = True
        file = open(write_file_path, 'w+', encoding='utf-8')
        file.write('[]')
        file.close()

    file_r = open(write_file_path, 'rb+')
    file_r.seek(-1, os.SEEK_END)
    file_r.truncate()
    file_r.close()

    file_w = open(write_file_path, 'a+', encoding='utf-8')
    if not is_remove:
        file_w.write(',' + content + ']')
    else:
        file_w.write(content + ']')
        is_remove = False
    file_w.close()


def get_url(url):
    return requests.get(url)


def get_book_list(url):
    req_result = get_url(url)
    if req_result.status_code == 200:
        print()
        html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        # 虚构类
        book_article_list = soup.select('#content > div > div.article > ul > li')
        handle_article_list(book_article_list)
        # 非虚构类
        book_aside_list = soup.select('#content > div > div.aside > ul > li')
        handle_aside_list(book_aside_list)


def handle_article_list(book_list):
    for book_li in book_list:
        book_href = book_li.a.attrs['href']
        get_book_detail(book_href)


def handle_aside_list(book_list):
    for book_li in book_list:
        book_href = book_li.a.attrs['href']
        get_book_detail(book_href)


get_book_list(main_url)
