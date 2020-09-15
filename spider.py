from config import *
from mylogging import initLogging
import logging

import requests
from requests.exceptions import ConnectionError
from urllib.parse import urlencode

import time
import random

# 网页解析工具
import re
import json

# 数据存储
import pymongo

company = [
    "字节跳动", "拼多多", "阿里巴巴", "快手"
]

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

def get_page_index(keyword, page):
    data = {
        'count': 20,
        'page': page,
        'query': keyword,
        'dist': '0',
        'highlight': 'true',
        'jsononly': '1',
        'pc': '1'
    }

    url = 'https://maimai.cn/search/contacts?'+urlencode(data)

    reponse = requests.get(url, headers=HEADERS)

    try:
        if reponse.status_code == 200:
            return reponse.text
        print("Error! Status code: " + reponse.status_code)
        return None
    except ConnectionError:
        print("Connect Error!")
        return None

def parse_index(html):

    doc = json.loads(html)
    employees = doc['data']['contacts']

    for eply in employees:
        yield {
            'flag': 'no_detail' if 'encode_mmid' not in eply['contact'].keys() else 'detail',
            'uid': eply['uid'],
            'status': eply['contact']['status'],
            'rank': eply['contact']['rank'],
            'position': eply['contact']['position'],
            'profession': eply['contact']['profession'],
            'province': eply['contact']['province'],
            'city': eply['contact']['city'],
            'company': eply['contact']['company'],
            'pf_name1': eply['contact']['user_pfmj']['pf_name1'],
            'mj_name1': eply['contact']['user_pfmj']['mj_name1'],
            'line3': eply['contact']['line3'],
            'line4': eply['contact']['line4'],
            'url': None if 'encode_mmid' not in eply['contact'].keys() else "https://maimai.cn/contact/detail/" + eply['contact']['encode_mmid']
            }

def get_detail(url):
    reponse = requests.get(url, headers=HEADERS)

    try:
        if reponse.status_code == 200:
            return reponse.text
        return None
    except ConnectionError:
        print("Connect Error, statue code: " + reponse.status_code)
        return None

def check_re(pattern, string):
    tmp = re.search(pattern, string)
    if tmp:
        return tmp.group(1)
    else:
        return None

def parse_detail(html):

    # 将个人信息取出来
    pattern = re.compile('JSON\.parse\("(.*?)</script>')

    if pattern.search(html) is None:
        return None

    detail = pattern.search(html).group(1)
    detail = detail[:-3]
    detail = detail.replace('\\u0022', '\"')
    detail = detail.replace("\\u002D", '/')

    # 整理详情页数据
    uid = check_re('"uid":(.*?),', detail)
    rank = check_re('"rank":(\d+)', detail)
    province = check_re('"province":"(.*?)"', detail)
    city = check_re('"city":"(.*?)",', detail)
    company = check_re('"company":"(.*?)"', detail)
    position = check_re('"position":"(.*?)"', detail)
    user_pfmj = check_re('"user_pfmj":({.*?}),', detail)
    education = check_re('"education":(\[{.*?}\])', detail)
    work_exp = check_re('"work_exp":(\[{.*?}\]),"education"', detail)
    domain = check_re('"domains":(\[.*?\]),', detail)
    skills = check_re('"skills":(\[.*?\]),', detail)

    education_tmp = []
    if education:
        for item in education.replace('[', '').replace(']', '').replace('},{', '}SPLIT{').split('SPLIT'):
            education_tmp.append({
                "school": check_re('"school":"(.*?)"', item),
                "degree": check_re('"degree":(\d)', item),
                "start_date": check_re('"start_date":"(.*?)"', item),
                "end_date": check_re('"end_date":"(.*?)",', item),
                "description": check_re('"description":"(.*?)"', item),
                "uptime": check_re('"uptime":"(.*?)"', item),
                "department": check_re('"department":"(.*?)"', item)
            })
    else:
        education_tmp = None

    work_exp_tmp = []
    if work_exp:
        tmp_str = re.sub('{"avatar":.*?}', '', work_exp)
        tmp_str = tmp_str.replace('[', '').replace(']', '').replace('},{"files"', '}SPLIT{"files"').split('SPLIT')
        for item in tmp_str:
            work_exp_tmp.append({
                'pf_name': check_re('"pf_name":"(.*?)",', item),
                "mj_name": check_re('"mj_name":"(.*?)"', item),
                'company': check_re('"company":"(.*?)",', item),
                "department": check_re('"department":"(.*?)"', item),
                'position': check_re('"position":"(.*?)"', item),
                "start_date": check_re('"start_date":"(.*?)"', item),
                "end_date": check_re('"end_date":"(.*?)"', item),
                "status": check_re('"status":(\d),', item),
                'description': check_re('"description":"(.*?)",', item),
                'uptime': check_re('"uptime":"(.*?)"',item)
            })
    else:
        work_exp_tmp = None

    return {
        'uid': uid,
        'rank':rank,
        'province': province,
        'city': city,
        'company': company,
        'position': position,
        'user_pfmj': eval(user_pfmj) if user_pfmj else None,
        'education': education_tmp,
        'domain': eval(domain) if domain else None,
        'skills': eval(skills) if domain else None,
        'work_exp': work_exp_tmp
    }

def save_to_db(data, flag):
    if flag == "index":
        if db["index_page"].update({'uid': data['uid']}, {'$set': data}, True) is False:
            print("Index: Saved to Mongo Failed", data['uid'])
    else:
        if db["detail_page"].update({'uid': data['uid']}, {'$set': data}, True):
            print('----Detail: Save to Mongo', data['uid'])
        else:
            print("----Detail: Saved to Mongo Failed", data['uid'])

def main(keyword, page):
    html = get_page_index(keyword, page)

    if parse_index(html) is None:
        return None

    for item in parse_index(html):
        save_to_db(item, "index")

        if item['flag'] == 'detail':
            content = get_detail(item['url'])
            data = parse_detail(content)
            save_to_db(data, "other")
            time.sleep(random.randint(10, 15))

        time.sleep(random.randint(5, 8))

if __name__ == "__main__":
    initLogging(LOGFILENAME)

    for key2 in company:
        print("Company: "+key2)
        for i in range(1, 10):
            logging.info("KEYWORD: " + key2 + " " + KEYWORD)
            logging.info("Page " + str(i) + ":")
            main(key2 + " " + KEYWORD, i)

