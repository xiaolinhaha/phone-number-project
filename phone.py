# -*- coding: utf-8 -*-
import os.path
import glob
import pandas as pd
import requests
import json
import re
import time
from urllib.parse import quote
import openpyxl
import random
import string
from datetime import datetime
from common_api import create_api_client
import logging

# 配置日志，输出到控制台和文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phone.log'),
        logging.StreamHandler()
    ]
)


# ------------------- 工具函数：随机生成字符串 -------------------
def random_hex(length):
    return ''.join(random.choices('0123456789abcdef', k=length))


def random_upper_hex(length):
    return ''.join(random.choices('ABCDEF0123456789', k=length))


def random_digits(length):
    return ''.join(random.choices('0123456789', k=length))


def generate_random_baiduid():
    # BAIDUID 格式：8位大写HEX + :FG=1
    part1 = random_upper_hex(8)
    part2 = random_upper_hex(24)
    return f"{part1}{part2}:FG=1"


def generate_random_bidupsid():
    return random_upper_hex(16)


def generate_random_bduess():
    # 模拟 BDUSS 格式（实际需登录获取，这里用随机 Base64-like 字符串）
    part1 = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=192))
    part2 = 'CQAAAAAAAAAAAAAAAIuk0FIYd3h4bwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHp4eGh6eHh4eg'
    return part1 + part2


# ----------------------------------------------------------------

# ------------------- 文件处理函数 -------------------
def get_latest_number_list_file():
    """
    获取最新的numberList JSON文件路径

    Returns:
        str: 最新的JSON文件路径，如果没有找到则返回None
    """

    # 使用相对路径
    files_dir = "files"
    pattern = os.path.join(files_dir, "numberList_*.json")

    try:
        # 查找所有匹配的文件
        json_files = glob.glob(pattern)

        if not json_files:
            logging.error(f"❌ 在 {files_dir} 目录中未找到 numberList_*.json 文件")
            return None

        # 按修改时间排序，获取最新的文件
        latest_file = max(json_files, key=os.path.getmtime)
        logging.info(f"📁 找到最新的numberList文件: {latest_file}")

        return latest_file

    except Exception as e:
        logging.error(f"❌ 查找numberList文件时出错: {e}")
        return None


def load_phone_numbers_from_json(json_path):
    """
    从JSON文件中读取手机号码列表

    Args:
        json_path: JSON文件路径

    Returns:
        list: 手机号码列表
    """

    logging.info(f"📊 读取JSON文件: {json_path}")

    try:
        # 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 从新的JSON格式中提取numberList
        if isinstance(data, dict) and 'numberList' in data:
            phone_numbers = data['numberList']
            logging.info(f"📏 从numberList中读取到 {len(phone_numbers)} 个号码")
        else:
            # 兼容旧格式（直接是数组）
            phone_numbers = data if isinstance(data, list) else []
            logging.info(f"📏 使用兼容模式，读取到 {len(phone_numbers)} 个号码")

        # 确保所有号码都是字符串格式，保持原始格式不变
        formatted_phones = []
        for phone in phone_numbers:
            if phone:  # 去除空值
                phone_str = str(phone).strip()
                formatted_phones.append(phone_str)

        logging.info(f"📱 成功读取 {len(formatted_phones)} 个手机号码")
        logging.info(f"📋 前3个号码示例: {formatted_phones[:3]}")
        return formatted_phones

    except Exception as e:
        logging.error(f"❌ 读取JSON文件失败: {e}")
        return []


# ------------------- API客户端类 -------------------
class APIClient:
    def __init__(self):
        # 这里初始化API配置，你可以根据实际情况修改
        self.api_url = "你的API地址"  # 请替换为实际API地址
        self.headers = {
            "Content-Type": "application/json"
        }




class PhoneNumberMarker:
    def __init__(self):
        # 删除 fake_useragent，使用固定 UA
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.api_client = APIClient()

    def get_baidu_search_url(self, phone_number):
        """构建百度搜索URL"""
        encoded_phone = quote(phone_number)
        url = f"https://www.baidu.com/s?wd={encoded_phone}"
        return url

    def extract_json_from_html(self, html_content, phone_number):
        """从HTML中提取JSON数据"""
        try:
            pattern = r'<div class="new-pmd"><!--s-data:({.*?})-->'
            matches = re.findall(pattern, html_content, re.DOTALL)

            for match in matches:
                try:
                    json_data = json.loads(match)
                    if json_data.get('phoneno') == phone_number or phone_number in match:
                        return json_data
                except json.JSONDecodeError:
                    continue

            pattern2 = r'<!--s-data:({.*?"phoneno":"' + re.escape(phone_number) + r'".*?})-->'
            matches2 = re.findall(pattern2, html_content, re.DOTALL)

            for match in matches2:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            logging.error(f"解析HTML时出错: {e}")
        return None

    def get_phone_marker(self, phone_number):
        """获取电话号码标记信息"""
        try:
            # 每次请求都生成全新的随机 Cookie
            baiduid = generate_random_baiduid()
            bidupsid = generate_random_bidupsid()
            bduess = generate_random_bduess()  # 即使无效，也能绕过基础检测

            cookie_str = f'''
                BIDUPSID={bidupsid}; 
                PSTM=1758696313; 
                BAIDUID={baiduid}; 
                BDUSS={bduess}; 
                BDUSS_BFESS={bduess}; 
                BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; 
                kleck=1bb067a159c71a0558708c751898565d7b6448bc70be3bec; 
                H_WISE_SIDS=60277_63141_64984_65242_65361_65427_65536_65603_65633_65650_65663_65669_65682_65686_65754_65737_65759_65772_65793_65840_65873_65857_65924; 
                ab_sr=1.0.1_NDJkZWQ2NDU4MjMxOGZjMzEzY2FhODliYzhlNmM3MjlmZDg5ZjVjMDc0OTFiOTM2ZmVhYWQwZjc2MGJkNTkzOTMzYjU2NzJjMDU2ZjJlM2Y5NjMyM2RmMTU4ODM0ZWJjNjEyZDQ5NTczZTc4ZDQwNDkyZmZjZTc4MmYyYzg0ZWVmZDA0YTZiZGMyYzc0ZmExZTc1MWM2M2Q3ODZiYTM4OWIzMDUyMTMzM2E2MWQ1Yzg4ODAyMjMyZDIwMzI0NTMx; 
                H_PS_PSSID=60277_63141_64984_65242_65361_65427_65536_65603_65633_65650_65663_65669_65682_65686_65754_65737_65759_65772_65793_65840_65873_65857_65924; 
                BAIDUID_BFESS={baiduid}; 
                BA_HECTOR=a4200k2g848l0kal80ag8085002kam1kfm0ad24; 
                delPer=1; 
                PSINO=3; 
                ZFY=Z6HrazFHwFGntR:B6VkDVscHQf9mEGVUffFHjgTfw8nM:C
            '''
            # 清理空白
            cookie_str = '; '.join([line.strip() for line in cookie_str.split(';') if line.strip()])

            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cookie': cookie_str,
                'Host': 'www.baidu.com',
                'Origin': 'https://www.baidu.com',
                'Referer': 'https://www.baidu.com/',
                'Sec-Ch-Ua': '"Chromium";v="141", "Not=A?Brand";v="8", "Google Chrome";v="141"',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Site': 'same_origin',
                'Sec-Fetch-Mode': 'navigate',
            }

            url = self.get_baidu_search_url(phone_number)
            response = self.session.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                logging.error(f"请求失败，状态码: {response.status_code}")
                return ""

            json_data = self.extract_json_from_html(response.text, phone_number)
            logging.info(f"解析到的JSON数据: {json_data}")

            if json_data:
                tag = json_data.get('markerTitle', '')
                return tag if tag else "无标记"
            else:
                return ""

        except requests.RequestException as e:
            logging.error(f"网络请求错误: {e}")
            return ""
        except Exception as e:
            logging.error(f"处理号码 {phone_number} 时出错: {e}")
            return ""

    def process_phone_numbers(self, phone_numbers):
        """处理手机号码列表"""
        try:
            success_results = []
            failed_numbers = []

            batch_size = 21

            for idx, phone in enumerate(phone_numbers):
                clean_phone = str(phone).strip() if phone else None
                if not clean_phone or clean_phone == 'nan':
                    failed_numbers.append({
                        'phone_number': phone,
                        'error': '无效号码',
                        'timestamp': datetime.now()
                    })
                    continue

                logging.info(f"正在处理第 {idx + 1}/{len(phone_numbers)} 个号码: {clean_phone}")
                marker = self.get_phone_marker(clean_phone)

                if marker == '':
                    for i in range(5):
                        logging.info(f"号码： {clean_phone} 开始第 {i + 1} 次重试")
                        marker = self.get_phone_marker(clean_phone)
                        if marker != '':
                            break
                        time.sleep(2)

                if marker and marker != "查询失败或无标记":
                    # 查询成功，调用API
                    try:
                        # 创建API客户端并调用
                        api_client = create_api_client()
                        tag = f"百度-{marker}"

                        logging.info(f"📞 调用公共API...")
                        logging.info(f"   📱 Number: {clean_phone}")
                        logging.info(f"   🏷️  Tag: {tag}")

                        api_result = api_client.call_api_with_number_tag(clean_phone, tag)

                        if api_result.get('success'):
                            logging.info(f"✅ 公共API调用成功!")
                            success_results.append({
                                'phone_number': clean_phone,
                                'marker': marker,
                                'api_status': '成功',
                                'timestamp': datetime.now()
                            })
                        else:
                            logging.error(f"❌ 公共API调用失败: {api_result.get('error', '未知错误')}")
                            success_results.append({
                                'phone_number': clean_phone,
                                'marker': marker,
                                'api_status': f"API失败: {api_result.get('error', '未知错误')}",
                                'timestamp': datetime.now()
                            })

                    except Exception as api_e:
                        logging.error(f"❌ 调用公共API时发生异常: {api_e}")
                else:
                    # 查询失败
                    failed_numbers.append({
                        'phone_number': clean_phone,
                        'error': marker if marker else "查询失败",
                        'timestamp': datetime.now()
                    })
                    logging.warning(f"❌ 号码 {clean_phone} 查询失败")

                if (idx + 1) % batch_size == 0 and idx != len(phone_numbers) - 1:
                    logging.info("已处理21个号码，暂停32秒...")
                    time.sleep(32)
                else:
                    time.sleep(2)

            # 保存成功结果 - 使用固定文件名
            if success_results:
                success_df = pd.DataFrame(success_results)
                success_file = "success_results_baidu.xlsx"
                success_df.to_excel(success_file, index=False)
                logging.info(f"✅ 成功结果已保存到: {success_file}")

            # 保存失败号码 - 使用固定文件名
            if failed_numbers:
                failed_df = pd.DataFrame(failed_numbers)
                failed_file = "failed_numbers_baidu.xlsx"
                failed_df.to_excel(failed_file, index=False)
                logging.warning(f"❌ 失败号码已保存到: {failed_file}")

            return len(success_results), len(failed_numbers)

        except Exception as e:
            logging.error(f"处理手机号码时出错: {e}")
            return 0, 0


def main():
    # 获取最新的JSON文件
    json_file = get_latest_number_list_file()
    if not json_file:
        logging.error("❌ 未找到有效的JSON文件，程序退出")
        return

    # 读取手机号码
    phone_numbers = load_phone_numbers_from_json(json_file)
    if not phone_numbers:
        logging.error("❌ 未读取到有效的手机号码，程序退出")
        return

    # 处理号码
    processor = PhoneNumberMarker()
    success_count, failed_count = processor.process_phone_numbers(phone_numbers)

    logging.info(f"\n📊 处理完成!")
    logging.info(f"✅ 成功处理: {success_count} 个号码")
    logging.info(f"❌ 失败号码: {failed_count} 个")
    logging.info(f"📁 结果文件保存在当前目录:")
    logging.info(f"   - 成功结果: success_results.xlsx")
    logging.info(f"   - 失败号码: failed_numbers.xlsx")


if __name__ == "__main__":
    main()