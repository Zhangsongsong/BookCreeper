import re
import time

import requests
from bs4 import BeautifulSoup

tag_head_url = 'https://book.douban.com'
main_url = 'https://book.douban.com/tag/?view=type&icn=index-sorttags-hot'

isDebug = False
start_index = 127  # 127

is_test_url = False
debug_url = 'https://book.douban.com/subject/1059419/'
debug_name = '海边的卡夫卡'


def get_book_tags():
    req_result = requests.get(main_url)
    if req_result.status_code == 200:
        html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        tags = soup.select('#content > div > div.article > div:nth-child(2) > div')
        for div in tags:
            trs = div.select('.tagCol > tbody > tr')
            for tr in trs:
                print(tr.a.attrs['href'] + '  ' + tr.a.text.strip())
                get_book_list(tag_head_url + tr.a.attrs['href'])
                if isDebug:
                    return


def get_book_list(url):
    print('get_book_list: ' + url)
    req_result = requests.get(url)
    # print('get_book_list: ' + str(req_result.status_code))

    if req_result.status_code == 200:
        html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        book_list = soup.select('#subject_list > ul > li')
        for book in book_list:
            book_detail_url = book.select('.info > h2')[0].a.attrs['href']
            book_detail_name = book.select('.info > h2')[0].a.attrs['title']
            get_book_detail(book_detail_url, book_detail_name)
            if isDebug:
                return
                # 下一页标签
        next_tags = soup.select('#subject_list > div.paginator > span.next')[0].a.attrs['href']
        time.sleep(1)
        get_book_list(tag_head_url + next_tags)


def get_book_detail(url, name):
    global book_count
    book_count = book_count + 1
    print('第' + str(book_count) + '本书 ：' + name + ' url: ' + url)
    if is_test_url is False:
        if start_index >= book_count:
            return

    try:
        req_result = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('错误url: ' + url)
        return
    if req_result.status_code == 200:
        html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        # 图书URL
        main_pic = soup.select('#mainpic')[0].a.attrs['href']
        print('封面:' + main_pic)

        # 作者ID ??
        articles = soup.select('#content > div > div.article > div')
        for article_item in articles:
            pos = str(article_item).find('collect_form_')
            if pos > -1:
                start_pos = str(article_item).rfind('_') + 1
                end_pos = str(article_item).rfind('"')
                author_id = str(article_item)[start_pos:end_pos]
                print('作者Id: ' + author_id)
                break

        # 内容简介
        # intro = ''
        # link_report_list = soup.select("#link-report > div")
        # link_len = len(link_report_list)
        # if link_len > 0:
        #     link_report = link_report_list[0]
        #     intro = link_report.select(".intro")[0].text.strip()
        # else:
        #     intro_div = soup.select('#link-report > span.all.hidden > div > div')[0]
        #     intro = intro_div.text.strip()
        # print('内容简介:' + str(intro))
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
            tag_value = tag_value + span.a.text.strip() + ' '
        print('常用标签:' + tag_value)
        time.sleep(1)


def deal_author_intro(soup):
    """ 解析作者简介 """
    try:
        author_info = soup.select('#content > div > div.article > div.related_info > div.indent')[1]
        author_text = author_info.select('.intro')[0].text.strip()
        print('作者简介:' + author_text)
        return
    except IndexError:
        """ 作者简介错误 """
    try:
        author_info = soup.select('#content > div > div.article > div.related_info > div.indent')
        author_text = author_info[0].select('span')[1].select('.intro')[0].text.strip()
        print('作者简介:' + author_text)
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
        print('内容简介:' + str(intro))
        return

    link_list = soup.select('#link-report > span.all.hidden > div > div')
    pos = len(link_list)
    if pos > 0:
        intro = link_list[0].text.strip()
        print('内容简介:' + str(intro))
        return


def deal_with_key_map(key, pl, json):
    for item_str in json.split('<br'):
        if key not in item_str:
            continue
        tmp_key = key.strip()
        if ':' not in tmp_key:
            tmp_key = tmp_key + ':'
        _name = tmp_key
        if 'href=' in item_str:
            text_list = item_str.split('href=')
            text = text_list[len(text_list) - 1]
            first_pos = text.find('>') + 1
            last_pos = text.find('</a>')
            name = text[first_pos:last_pos].replace(' ', '').strip()
            name_value = re.sub('[\x00-\x1f]', '', name)
            _name = _name + name_value
        else:
            span_list = item_str.split('</span>')
            span = span_list[len(span_list) - 1].strip()
            _name = _name + span
        print(_name)
        return


if is_test_url:
    book_count = 0
    get_book_detail(debug_url, debug_name)
else:
    book_count = 0
    get_book_tags()
