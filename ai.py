#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024-08-12 14:39
# @Author  : 1o00
# @Site    : 
# @File    : ai.py
# @Software: PyCharm
import base64
import json

import requests
import yaml

from util.log import logger


class AI:
    def __init__(self):
        with open('./config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            self.url = config.get('url')
            self.token = config.get('token')
            self.encoded_string_example = config.get('encoded_string_example')
            self.headers = {
                'Content-Type': 'application/json',  # 根据API要求调整
                'Authorization': 'Bearer ' + self.token
            }

    def start_conversation(self) -> str:
        # # 读取xlsx文件并进行Base64编码
        # with open(file_path_example, 'rb') as file:
        #     encoded_string_example = base64.b64encode(file.read()).decode('utf-8')

        encoded_string_example = self.encoded_string_example
        # 将Base64编码的字符串转换为URL
        url_encoded_string_example = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,' + encoded_string_example

        payload_example = {
            # 模型名称随意填写，如果不希望输出检索过程模型名称请包含silent_search
            "model": "kimi",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file_url": {
                                "url": url_encoded_string_example
                            }
                        },
                        {
                            "type": "text",
                            "text": '我这里有一堆excel，里面都是各个部门的金额，我需要你帮我提取各个部门的金额及各个部门的占比。在计算之前，我先给你个样例.xlsx来帮你理解计算逻辑。我们可以从表中看出来部门1的总价是100万，部门2的总价是200万，所以部门1和部门2的金额和占比分别是{ "部门1": { "total": 100, "rate": 0.3333 }, "部门2": { "total": 200, "rate": 0.6667 } }，其中total是金额，rate是占比。你如果看懂了就回复OK'
                        }
                    ]
                }
            ],
            "use_search": False,
            "conversation_id": "none"
        }
        # 发送HTTP POST请求
        response_example = requests.post(self.url, headers=self.headers, json=payload_example, timeout=60.0)

        # 检查响应状态
        if response_example.status_code != 200:
            logger.error('样例文件分析失败，状态码：', response_example.status_code)

        # 打印服务器响应的内容
        res_example_str = response_example.text
        logger.info(f'样例文件分析结果：{res_example_str}')

        res_example = json.loads(res_example_str)
        return res_example.get("id")

    def analysis(self, file_path, depts):
        conversation_id = self.start_conversation()
        # 读取xlsx文件并进行Base64编码
        with open(file_path, 'rb') as file:
            encoded_string = base64.b64encode(file.read()).decode('utf-8')

        # 将Base64编码的字符串转换为URL
        url_encoded_string = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,' + encoded_string

        departments = '和'.join(depts)
        payload = {
            "model": "kimi",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file_url": {
                                "url": url_encoded_string
                            }
                        },
                        {
                            "type": "text",
                            "text": f'好的，你现在已经理解了逻辑，那你帮我提取这个表中{departments}的金额及占比'
                        }
                    ]
                }
            ],
            "use_search": False,
            "conversation_id": conversation_id
        }

        # 发送HTTP POST请求
        response = requests.post(self.url, headers=self.headers, json=payload, timeout=60.0)

        # 检查响应状态
        if response.status_code != 200:
            logger.error(f'自研成本测算表 {file_path} 分析失败，状态码：{response.status_code}')

        # 打印服务器响应的内容
        res_str = response.text
        logger.info(f'自研成本测算表文件 {response.status_code} 分析结果:{res_str}')
        if res_str.find("内容由于不合规被停止生成") != -1:
            raise Exception("AI分析异常")

        payload_summary = {
            # 模型名称随意填写，如果不希望输出检索过程模型名称请包含silent_search
            "model": "kimi",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": '很好，你现在理解了计算过程，那你现在把结果用json的格式回复我，格式{ "部门1": { "total": 100, "rate": 0.3333 }, "部门2": { "total": 200, "rate": 0.6667 } }，其中total是金额，rate是占比。不需要说明计算过程，回复的内容中也不需要除了最终结果外的任何其它字符，比如```json标签'
                        }
                    ]
                }
            ],
            "use_search": False,
            "conversation_id": conversation_id
        }

        # 发送HTTP POST请求
        response_summary = requests.post(self.url, headers=self.headers, json=payload_summary, timeout=60.0)

        # 检查响应状态
        if response_summary.status_code != 200:
            logger.error('获取总结失败，状态码：', response_summary.status_code)

        # 打印服务器响应的内容
        res_summary_str = response_summary.text
        logger.info(f'获取总结内容:{res_summary_str}')
        if res_summary_str.find("内容由于不合规被停止生成") != -1:
            raise Exception("AI分析异常")

        res_summary = json.loads(res_summary_str)
        result = res_summary.get("choices")[0].get("message").get("content")

        return json.loads(result)


if __name__ == '__main__':
    ai_client = AI()
    # 要上传的Excel文件路径
    # file_path_example = 'C:\\Users\\linli\\Desktop\\在岗创新\\具体项目\\样例.xlsx'
    # file_path = 'C:\\Users\\linli\\Desktop\\在岗创新\\具体项目\\内蒙北斗数据中心项目自研成本评估明细.xlsx'
    # file_path_1 = 'C:\\Users\\linli\\Desktop\\在岗创新\\1-7月涉及多部门的自研成本测算表-修改\\I233914106PD008内蒙北斗一期自研成本测算表.xlsx'
    file_path_2 = 'C:\\Users\\linli\\Desktop\\在岗创新\\1-7月涉及多部门的自研成本测算表-修改\\I243914106P6001内蒙北斗二期自研成本测算依据.xlsx'
    # file_path_3 = 'C:\\Users\\linli\\Desktop\\在岗创新\\1-7月涉及多部门的自研成本测算表-修改\\I233914101CD011【西藏邮政智慧仓储物流园区项目】自研成本评估导入模板-20231124-【已完成】.xlsx'
    # file_path = 'C:\\Users\\linli\\Desktop\\在岗创新\\ICT项目收入明细表（2024）-7.xlsx'
    # file_path = 'C:\\Users\\linli\\Desktop\\测试.xlsx'

    depts_1 = ["沈阳分公司", "时空信息产品部"]
    depts_2 = ["金融科技产品部", "时空信息产品部"]
    depts_3 = ["沈阳分公司", "工业能源产品部"]
    # result_1 = ai_client.analysis(file_path_1, depts_1)
    # logger.info(result_1)
    result_2 = ai_client.analysis(file_path_2, depts_2)
    logger.info(result_2)
    # result_3 = ai_client.analysis(file_path_3, depts_3)
    # logger.info(result_3)
