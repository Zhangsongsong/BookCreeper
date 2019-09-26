import json
import os
import time

import requests
from bs4 import BeautifulSoup

dir_path = '../tags'

book_count = 0  # 书的统计
book_current_index = 0  # 当前获取进度
search_url = 'https://search.jd.com/Search?keyword='

is_test_url = True
test_url = 'https://item.jd.com/34870119640.html'


# https://search.jd.com/Search?keyword=9780751572858


def get_file_list():
    dir_list = os.listdir('../tags')
    for book_dir in dir_list:
        for book_name in os.listdir(dir_path + '/' + book_dir):
            book_path = dir_path + '/' + book_dir + '/' + book_name
            file_to_json(book_path)
            continue


def file_to_json(path):
    book_info = open(path, 'r+', encoding='utf-8')
    file_content = book_info.read()
    book_info.close()
    book_dir_json = json.loads(file_content)

    global book_count
    for book_json in book_dir_json:
        # print(book_json)
        book_count = book_count + 1

        book_name = book_json['bookName']
        print('第' + str(book_count) + '本书: ' + str(book_name))
        if book_current_index > book_count:
            continue
        try:
            isbn = book_json['isbn']

            search_bg_jd(isbn)
        except KeyError:
            print(book_json)
            print('isbn error')
        write_log_current_index(book_count)
        time.sleep(5)


def url_get(url):
    req_result = requests.get(url, headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'})
    return req_result


# 按照京东ISBN搜索  https://search.jd.com/Search?keyword=9787101138795
def search_bg_jd(isbn):
    url = search_url + str(isbn)
    print(url)
    req_result = url_get(url)
    if req_result.status_code == 200:
        html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        div_list = soup.select('#J_goodsList > ul > li:nth-child(1) > div > div.p-img')
        try:
            first_item = div_list[0]
            book_detail_url = 'https:' + first_item.a.attrs['href']
            get_book_detail(book_detail_url)
        except IndexError:
            print('没有这本书')


def get_book_detail(url):
    print(url)
    req_result = url_get(url)
    if req_result.status_code == 200:
        html_str = req_result.text
        soup = BeautifulSoup(html_str, 'html.parser')
        div_list = soup.select('#crumb-wrap > div > div.crumb.fl.clearfix > div')
        _tag = div_list[2].text.strip()
        __tag = div_list[4].text.strip()
        # print(_tag + '\t' + __tag)
        if is_write_service:
            write_tag_to_service(_tag, __tag)


def write_log_current_index(index):
    log_file_r = open('Log', 'r+')
    r_json = json.loads(log_file_r.read())
    log_file_r.close()
    r_json['current_index'] = index

    log_file_w = open('Log', 'w+')
    log_file_w.write(json.dumps(r_json))
    log_file_w.close()
    print()


def init_log():
    global book_current_index
    log_file = open('Log', 'r+')
    log_json = json.loads(log_file.read())
    log_file.close()
    book_current_index = log_json['current_index']
    global current_page
    current_page = log_json['current_page']
    global current_page_pos
    current_page_pos = log_json['current_page_to_pos']
    global is_write_service
    is_write_service = log_json['is_write_service']


java_base_url = 'http://39.105.187.28:8080/readhelper/web/'

current_page = 0
current_page_pos = 0
is_write_service = False

tmp_isbn = ''


def write_page_to_log(page, pos):
    log_file_r = open('Log', 'r+')
    r_json = json.loads(log_file_r.read())
    log_file_r.close()
    r_json['current_page'] = page
    r_json['current_page_to_pos'] = pos

    log_file_w = open('Log', 'w+')
    log_file_w.write(json.dumps(r_json))
    log_file_w.close()


def search_all():
    """
    获取服务器书籍
    :return:
    """
    url_str = java_base_url + 'app/search/all'
    global current_page
    global current_page_pos
    global tmp_isbn

    res_request = requests.get(url_str, params={'page_num': current_page})

    print('------------------------------------')
    print('当前page: ' + str(current_page) + '\t\t\t当前page_pos：' + str(current_page_pos))
    if res_request.status_code == 200:
        print(res_request.text)
        result_json = json.loads(res_request.text)
        pos = 0
        for isbn in result_json['data']:
            pos = pos + 1
            if current_page_pos >= pos:
                continue
            current_page_pos = pos
            tmp_isbn = isbn
            # 写进缓存
            write_page_to_log(current_page, current_page_pos)
            # 京东搜索
            search_bg_jd(isbn)
            time.sleep(3)
        current_page_pos = 0
        current_page = current_page + 1
        # print('当前page: ' + str(current_page) + '\t\t\t当前page_pos：' + str(current_page_pos))
        search_all()
    else:
        print(res_request.status_code)


def write_tag_to_service(first_tag, second_tag):
    """写进服务器"""
    print('当前page: ' + str(current_page) + '\t\t\t当前page_pos：' + str(current_page_pos))
    print(tmp_isbn)
    print(first_tag)
    if str(second_tag).find('/') != -1:
        second_tag = ''
    print(second_tag)

    url_str = java_base_url + 'web/app/search/updateBookCateName'
    # res_requests = requests.post(url_str, data={'isbn': tmp_isbn})

    print()


""" 
9787532336609
9787563344772
9787547728963
9787571001483
9781882324194
9787030275059
9787513310888
9787100005272
9787500694892
9787550247086"""
# search_bg_jd('9787563344772')


if is_test_url:
    # get_book_detail(test_url)
    init_log()
    search_all()
else:
    init_log()
    get_file_list()
