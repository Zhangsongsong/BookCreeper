import re

import requests
from bs4 import BeautifulSoup

main_url = 'https://www.kgbook.com/'


def get_category():
    req_result = requests.get(main_url)
    if req_result.status_code == 200:
        html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        categorys = soup.select('#category > div > ul > li')
        # categorys = soup.find_all(attrs={'id': 'category'})[0].ul
        i = 0
        for li in categorys:
            if i == 0:
                # print('开始抓取' + li.a.attrs['href'] + "--" + li.string)
                get_category_book_list(main_url + li.a.attrs['href'])
                # TODO
                # break


def get_category_book_list(url):
    print('get_category_book_list: ' + url)
    req_result = requests.get(url)
    if req_result.status_code == 200:
        book_html_str = req_result.content.decode('utf-8')
        soup = BeautifulSoup(book_html_str, 'html.parser')
        book_list = soup.select('.channel-item')
        # print(book_list)
        for book_info_div in book_list:
            book_title = book_info_div.select('.list-title')[0]
            book_url = book_title.a.attrs['href']
            get_book_detail(book_url)
            # TODO
            # break
        next_pag = soup.find(name='a', text=re.compile('下一页'))
        if next_pag is not None:
            next_url = next_pag.attrs['href']
            print('下一页: ' + next_url)
            # TODO
            get_category_book_list(next_url)


def get_book_detail(url):
    # 有些书的路径不是绝对路径 (也有一些url是反爬虫的)

    print('get_book_detail: ' + url)
    if 'kgbook.com' not in url:
        url = main_url + url
        print('get_book_detail 重制后: ' + url)
    if '.php' in url:
        url = url.replace('.php', '.html')
        print('get_book_detail 重制后: ' + url)
    try:
        req_result = requests.get(url)

        if req_result.status_code == 200:
            book_detail_str = req_result.content.decode('utf-8')
            soup = BeautifulSoup(book_detail_str, 'html.parser')
            book_title = soup.select('.news_title')[0].text.strip()
            book_author = soup.select('#news_details')[0].ul.li.find(text=re.compile('作者：(.*?)')).strip()
            book_author = book_author.replace('作者：', '')
            book_tmp = '《' + book_title + '》 - ' + book_author
            print(book_tmp)

    except requests.exceptions.MissingSchema:
        print('error  get_book_detail: ' + url)
    except requests.exceptions.ConnectionError:
        print('error  get_book_detail: ' + url)
    except IndexError:
        print('error  get_book_detail: ' + url)


get_category()
