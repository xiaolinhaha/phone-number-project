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


# ------------------- 工具函数：随机生成字符串 -------------------
def random_hex(length):
    return ''.join(random.choices('0123456789abcdef', k=length))


def random_upper_hex(length):
    return ''.join(random.choices('ABCDEF0123456789', k=length))


def random_digits(length):
    return ''.join(random.choices('0123456789', k=length))


def generate_random_360_headers(phone_number):
    """生成360搜索所需的随机headers"""
    headers = {
        'Pragma': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'sreferer': f'https://www.so.com/s?q={phone_number}&src=360portal&_re=0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': f'https://www.so.com/s?q={phone_number}',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    return headers


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
            print(f"❌ 在 {files_dir} 目录中未找到 numberList_*.json 文件")
            return None

        # 按修改时间排序，获取最新的文件
        latest_file = max(json_files, key=os.path.getmtime)
        print(f"📁 找到最新的numberList文件: {latest_file}")

        return latest_file

    except Exception as e:
        print(f"❌ 查找numberList文件时出错: {e}")
        return None


def load_phone_numbers_from_json(json_path):
    """
    从JSON文件中读取手机号码列表

    Args:
        json_path: JSON文件路径

    Returns:
        list: 手机号码列表
    """

    print(f"📊 读取JSON文件: {json_path}")

    try:
        # 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 从新的JSON格式中提取numberList
        if isinstance(data, dict) and 'numberList' in data:
            phone_numbers = data['numberList']
            print(f"📏 从numberList中读取到 {len(phone_numbers)} 个号码")
        else:
            # 兼容旧格式（直接是数组）
            phone_numbers = data if isinstance(data, list) else []
            print(f"📏 使用兼容模式，读取到 {len(phone_numbers)} 个号码")

        # 确保所有号码都是字符串格式，保持原始格式不变
        formatted_phones = []
        for phone in phone_numbers:
            if phone:  # 去除空值
                phone_str = str(phone).strip()
                formatted_phones.append(phone_str)

        print(f"📱 成功读取 {len(formatted_phones)} 个手机号码")
        print(f"📋 前3个号码示例: {formatted_phones[:3]}")
        return formatted_phones

    except Exception as e:
        print(f"❌ 读取JSON文件失败: {e}")
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
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.api_client = APIClient()

    def get_360_search_url(self, phone_number):
        """构建360搜索URL - 使用您提供的格式"""
        encoded_phone = quote(phone_number)
        # 使用您提供的URL格式，包含必要的参数
        url = f"https://www.so.com/s?q={encoded_phone}&src=srp&ssid=&fr=360portal&sp=aec&cp=006b00032b&nlpv=&psid={random_hex(32)}"
        return url

    def extract_marker_from_html(self, html_content, phone_number):
        """从HTML中提取标记信息"""
        try:
            # 匹配指定的HTML标签结构
            pattern = r'<div class="mohe-tips">.*?<div style="color:#d73130;" class="mohe-tips-zp">(.*?)</div>.*?</div>'
            matches = re.findall(pattern, html_content, re.DOTALL)

            if matches:
                marker_text = matches[0].strip()
                print(f"📄 找到标记文本: {marker_text}")

                # 检查是否包含目标关键词
                if "用户标记，疑似为骚扰电话！" in marker_text:
                    # 提取标记数量
                    count_match = re.search(r'被<b>(\d+)</b>位', marker_text)
                    count = count_match.group(1) if count_match else "未知"
                    return f"被{count}位用户标记为骚扰电话"
                else:
                    return "无标记"
            else:
                # 尝试其他可能的标记格式
                if "骚扰电话" in html_content or "诈骗电话" in html_content:
                    # 查找其他标记模式
                    alternative_patterns = [
                        r'被.*?(\d+).*?位.*?标记',
                        r'标记.*?(\d+).*?次',
                        r'(\d+).*?人.*?标记'
                    ]

                    for pattern in alternative_patterns:
                        match = re.search(pattern, html_content)
                        if match:
                            count = match.group(1)
                            return f"被{count}位用户标记"

                return "无标记"

        except Exception as e:
            print(f"解析HTML时出错: {e}")
            return "解析失败"

    def get_phone_marker(self, phone_number):
        """获取电话号码标记信息 - 使用您提供的请求格式"""
        try:
            url = self.get_360_search_url(phone_number)
            headers = generate_random_360_headers(phone_number)

            print(f"🌐 请求URL: {url}")

            response = self.session.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return "请求失败"

            # 打印部分响应内容用于调试
            print(f"📄 响应内容预览: {response.text[:500]}...")

            # 检查是否包含目标标记信息
            if 'mohe-tips' in response.text and '用户标记，疑似为骚扰电话！' in response.text:
                marker = self.extract_marker_from_html(response.text, phone_number)
                return marker
            elif '骚扰电话' in response.text or '诈骗电话' in response.text:
                # 即使没有精确匹配，也尝试提取标记信息
                marker = self.extract_marker_from_html(response.text, phone_number)
                if marker != "无标记":
                    return marker
                else:
                    return "有标记但格式不匹配"
            else:
                return "无标记"

        except requests.RequestException as e:
            print(f"网络请求错误: {e}")
            return "网络错误"
        except Exception as e:
            print(f"处理号码 {phone_number} 时出错: {e}")
            return "处理错误"

    def process_phone_numbers(self, phone_numbers):
        """处理手机号码列表"""
        try:
            success_results = []
            failed_numbers = []

            batch_size = 15  # 减少批次大小

            for idx, phone in enumerate(phone_numbers):
                clean_phone = str(phone).strip() if phone else None
                if not clean_phone or clean_phone == 'nan':
                    failed_numbers.append({
                        'phone_number': phone,
                        'error': '无效号码',
                        'timestamp': datetime.now()
                    })
                    continue

                print(f"\n🔍 正在处理第 {idx + 1}/{len(phone_numbers)} 个号码: {clean_phone}")
                marker = self.get_phone_marker(clean_phone)

                # 重试逻辑
                if marker in ["请求失败", "网络错误", "处理错误"]:
                    for i in range(2):  # 减少重试次数
                        print(f"🔄 号码 {clean_phone} 开始第 {i + 1} 次重试")
                        time.sleep(3)
                        marker = self.get_phone_marker(clean_phone)
                        if marker not in ["请求失败", "网络错误", "处理错误"]:
                            break

                if marker and marker not in ["无标记", "请求失败", "网络错误", "处理错误", "解析失败"]:
                    # 查询成功，调用API
                    try:
                        # 创建API客户端并调用
                        api_client = create_api_client()
                        tag = f"360-{marker}"

                        print(f"📞 调用公共API...")
                        print(f"   📱 Number: {clean_phone}")
                        print(f"   🏷️  Tag: {tag}")

                        api_result = api_client.call_api_with_number_tag(clean_phone, tag)

                        if api_result.get('success'):
                            print(f"✅ 公共API调用成功!")
                            success_results.append({
                                'phone_number': clean_phone,
                                'marker': marker,
                                'api_status': '成功',
                                'timestamp': datetime.now()
                            })
                        else:
                            print(f"❌ 公共API调用失败: {api_result.get('error', '未知错误')}")
                            success_results.append({
                                'phone_number': clean_phone,
                                'marker': marker,
                                'api_status': f"API失败: {api_result.get('error', '未知错误')}",
                                'timestamp': datetime.now()
                            })

                    except Exception as api_e:
                        print(f"❌ 调用公共API时发生异常: {api_e}")
                        success_results.append({
                            'phone_number': clean_phone,
                            'marker': marker,
                            'api_status': f"API异常: {str(api_e)}",
                            'timestamp': datetime.now()
                        })
                else:
                    # 查询失败或无标记
                    failed_numbers.append({
                        'phone_number': clean_phone,
                        'error': marker if marker else "无标记",
                        'timestamp': datetime.now()
                    })
                    print(f"❌ 号码 {clean_phone} 无标记或查询失败")

                # 批次控制 - 更保守的频率控制
                if (idx + 1) % batch_size == 0 and idx != len(phone_numbers) - 1:
                    wait_time = 30
                    print(f"已处理{batch_size}个号码，暂停{wait_time}秒...")
                    time.sleep(wait_time)
                else:
                    time.sleep(2)  # 单个请求间隔

            # 保存成功结果
            if success_results:
                success_df = pd.DataFrame(success_results)
                success_file = "success_results_360.xlsx"
                success_df.to_excel(success_file, index=False)
                print(f"✅ 成功结果已保存到: {success_file}")

            # 保存失败号码
            if failed_numbers:
                failed_df = pd.DataFrame(failed_numbers)
                failed_file = "failed_numbers_360.xlsx"
                failed_df.to_excel(failed_file, index=False)
                print(f"❌ 失败号码已保存到: {failed_file}")

            return len(success_results), len(failed_numbers)

        except Exception as e:
            print(f"处理手机号码时出错: {e}")
            return 0, 0


def main():
    # 获取最新的JSON文件
    json_file = get_latest_number_list_file()
    if not json_file:
        print("❌ 未找到有效的JSON文件，程序退出")
        return

    # 读取手机号码
    phone_numbers = load_phone_numbers_from_json(json_file)
    if not phone_numbers:
        print("❌ 未读取到有效的手机号码，程序退出")
        return

    # 处理号码
    processor = PhoneNumberMarker()
    success_count, failed_count = processor.process_phone_numbers(phone_numbers)

    print(f"\n📊 处理完成!")
    print(f"✅ 成功处理: {success_count} 个号码")
    print(f"❌ 失败号码: {failed_count} 个")
    print(f"📁 结果文件保存在当前目录:")
    print(f"   - 成功结果: success_results_360.xlsx")
    print(f"   - 失败号码: failed_numbers_360.xlsx")


if __name__ == "__main__":
    main()