import pymongo

import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

client = pymongo.MongoClient("localhost")
db = client["maimai"]

detail_data = db["detail_page"]


def check_data(line, *args):
    tmp = None

    for field in args:
        if tmp is None:
            tmp = line[field]
        else:
            tmp = tmp[field]

    if tmp:
        return tmp
    else:
        return None


def generate_data():
    usr_info = []
    skill_info = []
    educate_info = []
    work_info = []

    for line in detail_data.find():
        user_line = []

        work_line = []
        skill_line = []

        user_line.append(check_data(line, 'uid'))
        user_line.append(check_data(line, 'name'))
        user_line.append(check_data(line, 'company'))
        user_line.append(check_data(line, 'position'))
        user_line.append(check_data(line, 'province'))
        user_line.append(check_data(line, 'city'))
        user_line.append(check_data(line, 'user_pfmj', 'pf_name1'))
        user_line.append(check_data(line, 'user_pfmj', 'mj_name1'))
        usr_info.append(tuple(user_line))

        i = 0
        if line['education'] is not None:
            for ed_item in line['education']:
                educate_line = []
                educate_line.append(check_data(line, 'uid'))
                educate_line.append(i)
                educate_line.append(check_data(ed_item, 'school'))
                educate_line.append(check_data(ed_item, 'degree'))
                educate_line.append(check_data(ed_item, 'start_date'))
                educate_line.append(check_data(ed_item, 'end_date'))
                educate_line.append(check_data(ed_item, 'department'))
                i += 1
                educate_info.append(tuple(educate_line))

        i = 0
        if line['work_exp'] is not None:
            for work_item in line['work_exp']:
                work_line = []
                work_line.append(check_data(line, 'uid'))
                work_line.append(i)
                work_line.append(check_data(work_item, 'pf_name'))
                work_line.append(check_data(work_item, 'mj_name'))
                work_line.append(check_data(work_item, 'company'))
                work_line.append(check_data(work_item, 'department'))
                work_line.append(check_data(work_item, 'position'))
                work_line.append(check_data(work_item, 'start_date'))
                work_line.append(check_data(work_item, 'end_date'))
                work_line.append(check_data(work_item, 'status'))
                work_line.append(check_data(work_item, 'description'))
                work_info.append(tuple(work_line))

        if line['skills'] is not None:
            skill_line.append(check_data(line, 'uid'))
            skill_line.append(check_data(line, 'skills'))
            skill_info.append(tuple(skill_line))

    usr_info = pd.DataFrame(usr_info,
                            columns=['uid', 'name', 'company', 'position', 'province', 'city', 'pf_name1', 'mj_name1'])
    educate_info = pd.DataFrame(educate_info,
                                columns=['uid', 'mark', 'school', 'degree', 'start_date', 'end_date', 'department'])
    work_info = pd.DataFrame(work_info,
                             columns=['uid', 'mark', 'pf_name', 'mj_name', 'company', 'department', 'position',
                                      'start_date', 'end_date', 'status', 'description'])

    return usr_info, educate_info, work_info, skill_info

usr_info, educate_info, work_info, skill_info = generate_data()


# 数据检查
## 公司分布
## 行业分布
## 省份分布


usr_info


# 问题一： 大厂数据发展路线是怎样的(抽象问题)
#     1.这些数据人都是哪一年入行的
#     2.学历是怎么样的(本科/研究生、985、留学)
#     3.专业是怎么样的
#     4.是一毕业就干数据分析，还是从其他行业转来的

# 问题二： 职业发展路线是怎么样的？
#       1.初级岗位的情况
#       2.中级岗位的情况
#       3.高级岗位的情况


# 问题三：当前适不适合转行数据分析

# 问题四：数据分析需要掌握什么技能

# 问题五：数据分析职业规划
#    - 第一份工作做多久
#    - 假如想转行，转去什么行业

# 问题六：跳槽路径是怎么样的

# 问题七: 大家都是什么时候换工作的？ 今年换工作很难吗？

