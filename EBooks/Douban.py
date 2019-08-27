import json
import os
import random
import re
import time
import fake_useragent

import requests
import urllib3
from bs4 import BeautifulSoup

tag_head_url = 'https://book.douban.com'
main_url = 'https://book.douban.com/tag/?view=type&icn=index-sorttags-hot'

# 如果开启的话，默认解析第一条
isDebug = False
start_index = 1272  # 487
end_index = -1
tag_index = 30  # 两性

# 文件写入
is_write = False
tmp_book_info_json = ''
write_file_path = 'BookInfo.txt'

# 仅供调试使用
is_test_url = False
debug_url = 'https://book.douban.com/subject/2067064/'
debug_name = 'I”S(01)'

# http://117.103.5.186:44825
# http://109.72.227.56:53281

cookies = [
    'bid=KDr0ry3Xn5o; ll="118281"; gr_user_id=6ea35de4-ad7b-415b-8a95-0781ec525004; _vwo_uuid_v2=DA62BB396B3E7249F974E2CDACD9D7C59|0583b5f97761053db60af2ed2775a954; ct=y; __gads=ID=63be7534ee366445:T=1566351934:S=ALNI_MYMa8QdtIz4ESy_82PzftVAxJncgw; viewed="3921921_1014278_26742663_1770782_26389895_1019568_30472543_25862578_30230061_1083435"; __utmc=30149280; push_noty_num=0; push_doumail_num=0; __yadk_uid=e1BC844JNKOA61MigB6hMIEQEe47uI55; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1566890758%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.1818568439.1565949828.1566886384.1566890759.33; __utmz=30149280.1566890759.33.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; __utmv=30149280.20284; __utmt_douban=1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=4f0364c0-b303-4f05-a735-d8d48a317e71; gr_cs1_4f0364c0-b303-4f05-a735-d8d48a317e71=user_id%3A1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_4f0364c0-b303-4f05-a735-d8d48a317e71=true; dbcl2="202845392:7W+CLptWvr0"; ck=Skt7; _pk_id.100001.8cb4=101f7da4deb38711.1565949834.10.1566891183.1566886385.; __utmb=30149280.8.10.1566890759'
    ,
    'bid=KDr0ry3Xn5o; ll="118281"; gr_user_id=6ea35de4-ad7b-415b-8a95-0781ec525004; _vwo_uuid_v2=DA62BB396B3E7249F974E2CDACD9D7C59|0583b5f97761053db60af2ed2775a954; ct=y; __gads=ID=63be7534ee366445:T=1566351934:S=ALNI_MYMa8QdtIz4ESy_82PzftVAxJncgw; viewed="3921921_1014278_26742663_1770782_26389895_1019568_30472543_25862578_30230061_1083435"; push_noty_num=0; push_doumail_num=0; __yadk_uid=e1BC844JNKOA61MigB6hMIEQEe47uI55; __utmv=30149280.20285; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1566900542%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DqDe1S1tuxXwodtzAesgJXSPVaZK9b4QlzkG_vbm9azRsCs9_UsIklqlJexPoCFpT%26wd%3D%26eqid%3Df2afd0df00183faa000000065d650138%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.1818568439.1565949828.1566896459.1566900543.35; __utmc=30149280; __utmz=30149280.1566900543.35.6.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmt=1; dbcl2="202855021:4ypJW6mjbdk"; ck=YVu2; _pk_id.100001.8cb4=101f7da4deb38711.1565949834.12.1566900607.1566896654.; __utmb=30149280.5.10.1566900543',
    'bid=KDr0ry3Xn5o; ll="118281"; gr_user_id=6ea35de4-ad7b-415b-8a95-0781ec525004; _vwo_uuid_v2=DA62BB396B3E7249F974E2CDACD9D7C59|0583b5f97761053db60af2ed2775a954; ct=y; __gads=ID=63be7534ee366445:T=1566351934:S=ALNI_MYMa8QdtIz4ESy_82PzftVAxJncgw; viewed="3921921_1014278_26742663_1770782_26389895_1019568_30472543_25862578_30230061_1083435"; __utmc=30149280; push_noty_num=0; push_doumail_num=0; __yadk_uid=e1BC844JNKOA61MigB6hMIEQEe47uI55; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1566890758%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.1818568439.1565949828.1566886384.1566890759.33; __utmz=30149280.1566890759.33.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); ap_v=0,6.0; dbcl2="202276626:MPkGuRSCBPg"; ck=Iz26; __utmt=1; __utmv=30149280.20227; _pk_id.100001.8cb4=101f7da4deb38711.1565949834.10.1566893803.1566886385.; __utmb=30149280.51.10.1566890759',
    'bid=KDr0ry3Xn5o; ll="118281"; gr_user_id=6ea35de4-ad7b-415b-8a95-0781ec525004; _vwo_uuid_v2=DA62BB396B3E7249F974E2CDACD9D7C59|0583b5f97761053db60af2ed2775a954; ct=y; __gads=ID=63be7534ee366445:T=1566351934:S=ALNI_MYMa8QdtIz4ESy_82PzftVAxJncgw; viewed="3921921_1014278_26742663_1770782_26389895_1019568_30472543_25862578_30230061_1083435"; __utmc=30149280; push_noty_num=0; push_doumail_num=0; __yadk_uid=e1BC844JNKOA61MigB6hMIEQEe47uI55; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1566890758%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.1818568439.1565949828.1566886384.1566890759.33; __utmz=30149280.1566890759.33.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=4f0364c0-b303-4f05-a735-d8d48a317e71; gr_cs1_4f0364c0-b303-4f05-a735-d8d48a317e71=user_id%3A1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_4f0364c0-b303-4f05-a735-d8d48a317e71=true; ap_v=0,6.0; __utmv=30149280.20284; __utmt_douban=1; dbcl2="202846608:mj3UhN6ZbY4"; ck=aivV; _pk_id.100001.8cb4=101f7da4deb38711.1565949834.10.1566892278.1566886385.; __utmt=1; __utmb=30149280.23.10.1566890759',
    'bid=KDr0ry3Xn5o; ll="118281"; gr_user_id=6ea35de4-ad7b-415b-8a95-0781ec525004; _vwo_uuid_v2=DA62BB396B3E7249F974E2CDACD9D7C59|0583b5f97761053db60af2ed2775a954; ct=y; __gads=ID=63be7534ee366445:T=1566351934:S=ALNI_MYMa8QdtIz4ESy_82PzftVAxJncgw; viewed="3921921_1014278_26742663_1770782_26389895_1019568_30472543_25862578_30230061_1083435"; __utmc=30149280; push_noty_num=0; push_doumail_num=0; __yadk_uid=e1BC844JNKOA61MigB6hMIEQEe47uI55; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1566890758%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.1818568439.1565949828.1566886384.1566890759.33; __utmz=30149280.1566890759.33.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt_douban=1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=4f0364c0-b303-4f05-a735-d8d48a317e71; gr_cs1_4f0364c0-b303-4f05-a735-d8d48a317e71=user_id%3A1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_4f0364c0-b303-4f05-a735-d8d48a317e71=true; dbcl2="200525790:TO4Yj0bvEWk"; ck=5P71; _pk_id.100001.8cb4=101f7da4deb38711.1565949834.10.1566891385.1566886385.; __utmt=1; __utmv=30149280.20052; __utmb=30149280.13.10.1566890759'
    ,
    'bid=KDr0ry3Xn5o; ll="118281"; gr_user_id=6ea35de4-ad7b-415b-8a95-0781ec525004; _vwo_uuid_v2=DA62BB396B3E7249F974E2CDACD9D7C59|0583b5f97761053db60af2ed2775a954; ct=y; __gads=ID=63be7534ee366445:T=1566351934:S=ALNI_MYMa8QdtIz4ESy_82PzftVAxJncgw; viewed="3921921_1014278_26742663_1770782_26389895_1019568_30472543_25862578_30230061_1083435"; __utmc=30149280; push_noty_num=0; push_doumail_num=0; __yadk_uid=e1BC844JNKOA61MigB6hMIEQEe47uI55; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1566890758%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.100001.8cb4=*; __utma=30149280.1818568439.1565949828.1566886384.1566890759.33; __utmz=30149280.1566890759.33.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=4f0364c0-b303-4f05-a735-d8d48a317e71; gr_cs1_4f0364c0-b303-4f05-a735-d8d48a317e71=user_id%3A1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_4f0364c0-b303-4f05-a735-d8d48a317e71=true; __utmt=1; dbcl2="202845782:1TiJMnhnGhg"; ck=D5H2; ap_v=0,6.0; __utmv=30149280.20284; _pk_id.100001.8cb4=101f7da4deb38711.1565949834.10.1566891536.1566886385.; __utmb=30149280.18.10.1566890759'
    ,
    'bid=KDr0ry3Xn5o; __yadk_uid=dx9HW1Oldi8Sx5e8oyOA6mHgRHI1Qn67; ll="118281"; gr_user_id=6ea35de4-ad7b-415b-8a95-0781ec525004; _vwo_uuid_v2=DA62BB396B3E7249F974E2CDACD9D7C59|0583b5f97761053db60af2ed2775a954; ct=y; __gads=ID=63be7534ee366445:T=1566351934:S=ALNI_MYMa8QdtIz4ESy_82PzftVAxJncgw; viewed="3921921_1014278_26742663_1770782_26389895_1019568_30472543_25862578_30230061_1083435"; __utmc=30149280; __utmc=81379588; push_noty_num=0; push_doumail_num=0; __utma=30149280.1818568439.1565949828.1566886384.1566890759.33; __utmz=30149280.1566890759.33.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; dbcl2="202845014:WehYRXXSAuQ"; ck=StY6; __utmv=30149280.20284; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1566890819%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_id.100001.3ac3=3ac25d4c11ae389c.1565949828.32.1566890819.1566877721.; _pk_ses.100001.3ac3=*; __utmt_douban=1; __utmb=30149280.4.10.1566890759; __utma=81379588.1905919852.1565949838.1566874444.1566890819.32; __utmz=81379588.1566890819.32.4.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmb=81379588.1.10.1566890819; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=4f0364c0-b303-4f05-a735-d8d48a317e71; gr_cs1_4f0364c0-b303-4f05-a735-d8d48a317e71=user_id%3A1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_4f0364c0-b303-4f05-a735-d8d48a317e71=true']


def deal_requests(url):
    proxy = '180.117.232.106:8118'
    proxies = {
        'http': 'http://' + proxy,
        'https': 'https://' + proxy,
    }
    ua = fake_useragent.UserAgent()
    try:
        # req_result = requests.get(url, headers={'User-Agent': ua.random}, proxies=proxies)
        cookie = cookies[1]
        req_result = requests.get(url, headers={'User-Agent': ua.random,
                                                'Cookie': cookie}
                                  )
        print(req_result.status_code)
        if req_result.status_code == 200:
            return req_result
    except urllib3.exceptions.MaxRetryError:
        deal_requests(url)
    except requests.exceptions.ProxyError:
        deal_requests(url)

    deal_requests(url)


# return requests.get(url)


def get_book_tags():
    # req_result = requests.get(main_url, proxies=proxies)
    req_result = deal_requests(main_url)
    if req_result.status_code == 200:
        html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        tags = soup.select('#content > div > div.article > div:nth-child(2) > div')

        tag_count = 0
        for div in tags:
            trs = div.select('.tagCol > tbody > tr')
            for tr in trs:
                print(tr.a.attrs['href'] + '  ' + tr.a.text.strip())
                tag_count = tag_count + 1
                if tag_count >= tag_index:
                    get_book_list(tag_head_url + tr.a.attrs['href'])
                    return
                    global book_count
                    if 0 < end_index <= book_count:
                        return


def get_book_list(url):
    print('get_book_list: ' + url)
    # req_result = requests.get(url)
    req_result = deal_requests(url)
    # print('get_book_list: ' + str(req_result.status_code))

    if req_result.status_code == 200:
        html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        book_list = soup.select('#subject_list > ul > li')

        for book in book_list:
            book_detail_url = book.select('.info > h2')[0].a.attrs['href']
            book_detail_name = book.select('.info > h2')[0].a.attrs['title']

            global book_count
            if 0 < end_index <= book_count:
                return
            get_book_detail(book_detail_url, book_detail_name)
        # 下一页标签
        try:
            print(soup.select('#subject_list > div.paginator > span.next')[0].a.attrs['href'])
            next_tags = soup.select('#subject_list > div.paginator > span.next')[0].a.attrs['href']

            time.sleep(1)
            get_book_list(tag_head_url + next_tags)
        except IndexError:
            print("标签页异常")
        except AttributeError:
            print('标签页异常')


def get_book_detail(url, name):
    """ 获取书本信息 """
    global book_count
    book_count = book_count + 1
    print('第' + str(book_count) + '本书 ：' + name + ' url: ' + url)
    global tmp_book_info_json
    tmp_book_info_json = ''

    save_book_info_to_log(name, url)

    if not is_test_url:
        if start_index >= book_count:
            return

    try:
        # req_result = requests.get(url)
        req_result = deal_requests(url)

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
        write_book_info(tmp_book_info_json)
        time.sleep(1)


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


is_remove = False


def write_book_info(book_info):
    content = '{' + str(book_info)[1:] + '}'
    print(content)
    json_str = json.loads(content)
    print('test:' + str(json_str))

    print('检查json成功\n')
    if not is_test_url:
        if is_write:
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

    save_index(book_count)


def save_book_info_to_log(name, url):
    """ 用于数据保存"""

    if is_test_url:
        return
    log_file_r = open('Log', 'r+')
    log_content = log_file_r.read()
    log_file_r.close()
    content_json = json.loads(log_content)
    content_json['book_name'] = name
    content_json['book_url'] = url

    file_w = open('Log', 'w+')
    file_w.write(json.dumps(content_json))
    file_w.close()


def save_index(count):
    """ 用于数据保存 """
    if is_test_url:
        return
    log_file_r = open('Log', 'r+')
    log_content = log_file_r.read()
    log_file_r.close()
    content_json = json.loads(log_content)
    content_json['start_index'] = count

    file_w = open('Log', 'w+')
    file_w.write(json.dumps(content_json))
    file_w.close()


def init_log():
    """ 初始化信息 """
    log_file = open('Log', 'r+')
    content_json = json.loads(log_file.read())
    log_file.close()
    global start_index
    global end_index
    start_index = content_json['start_index']
    end_index = content_json['end_index']

    global is_write
    is_write = content_json['is_write']

    global isDebug
    isDebug = content_json['is_debug']


""" 开始 """

book_count = 0
init_log()
if is_test_url:
    get_book_detail(debug_url, debug_name)
else:
    get_book_tags()
