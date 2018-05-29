#!/usr/bin/env python3

from urllib import request, parse, error
from lxml import etree
import requests
import math


AJAX_URL = 'https://www.lagou.com/jobs/positionAjax.json?'
REFERER_URL = 'https://www.lagou.com/jobs/list_'
JOB_DETAILS_URL = 'https://www.lagou.com/jobs/'
PAGE_SIZE = 15

default_headers = {
    'Host': 'www.lagou.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}


def get_url(city):
    par = {'city': city, 'needAddtionalResult': 'false'}
    return AJAX_URL + parse.urlencode(par)


def http_request(url, headers=None, data=None, method='GET'):
    form_data = None
    headers_data = default_headers

    if data:
        form_data = bytes(parse.urlencode(data), encoding='utf8')

    if headers:
        headers_data.update(headers)

    request_obj = request.Request(url=url, data=form_data, headers=headers_data, method=method)

    try:
        response_obj = request.urlopen(request_obj)
        return response_obj.read().decode('utf-8')
    except error.HTTPError as e:
        print('http request error:', e.args)


def get_page(session, page, keyword, city):
    if page == 1:
        is_first = 'true'
    else:
        is_first = 'false'

    search_param = {
        'first': is_first,
        'pn': page,
        'kd': keyword
    }

    ref_param = {
        'city': city,
        'cl': 'false',
        'fromSearch': 'true',
        'labelWords': '',
        'suginput': ''
    }

    default_headers['Referer'] = REFERER_URL + parse.quote(keyword) + '?' + parse.urlencode(ref_param)

    try:
        response = session.post(url=get_url(city), headers=default_headers, data=parse.urlencode(search_param))
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


def parse_result(json):
    if json:
        position_result = json.get('content').get('positionResult')
        items = position_result.get('result')
        for item in items:
            yield {
                'title': item.get('positionName'),
                'companyName': item.get('companyFullName'),
                'salary': item.get('salary'),
                'workYear': item.get('workYear'),
                'positionId': item.get('positionId')
            }


def get_job_details(job_id):
    html = http_request(JOB_DETAILS_URL + str(job_id) + '.html')
    tree = etree.HTML(html)
    return tree.xpath('//dl[@class="job_detail"]/dd[@class="job_bt"]/div/p/text()')


def search_job(keyword, city):
    session = requests.Session()
    session.get('https://www.lagou.com')
    page = 1
    while True:
        json = get_page(session, page, keyword, city)
        total_count = json.get('content').get('positionResult').get('totalCount')
        total_page = math.ceil(total_count/PAGE_SIZE)
        for item in parse_result(json):
            print(item)
            for job_info in get_job_details(item['positionId']):
                print(job_info)
        if total_page == page:
            break
        page += 1


if __name__ == '__main__':
    search_job('', '广州')
