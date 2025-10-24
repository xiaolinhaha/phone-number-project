import pandas as pd
import requests
import json
import re
import time
from urllib.parse import quote
import openpyxl
from fake_useragent import UserAgent


class PhoneNumberMarker:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()

    def get_baidu_search_url(self, phone_number):
        """构建百度搜索URL"""
        encoded_phone = quote(phone_number)
        url = f"https://www.baidu.com/s?wd={encoded_phone}"
        return url

    def extract_json_from_html(self, html_content, phone_number):
        """从HTML中提取JSON数据"""
        try:
            # 使用正则表达式匹配包含电话号码的JSON数据
            pattern = r'<div class="new-pmd"><!--s-data:({.*?})-->'
            matches = re.findall(pattern, html_content, re.DOTALL)

            for match in matches:
                try:
                    json_data = json.loads(match)
                    # 检查是否包含目标电话号码
                    if json_data.get('phoneno') == phone_number or phone_number in match:
                        return json_data
                except json.JSONDecodeError:
                    continue

            # 如果没有找到精确匹配，尝试其他模式
            pattern2 = r'<!--s-data:({.*?"phoneno":"' + re.escape(phone_number) + r'".*?})-->'
            matches2 = re.findall(pattern2, html_content, re.DOTALL)

            for match in matches2:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            print(f"解析HTML时出错: {e}")

        return None

    def get_phone_marker(self, phone_number):
        """获取电话号码标记信息"""
        try:
            # 构建请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'cookie':'BIDUPSID=8D2DE3A42C79F5B3C5128F6307052602; PSTM=1758696313; BAIDUID=8D2DE3A42C79F5B353103F9154E3B291:FG=1; BDUSS=tDS2VSYVQ3aXl-SWJneDNuLWpyaHVQS2pOYVltYUgwa3Qxbn5jbTBaUXZLfnRvSUFBQUFBJCQAAAAAAAAAAAEAAAAr9cFIYWt4eG8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC-e02gvntNobk; BDUSS_BFESS=tDS2VSYVQ3aXl-SWJneDNuLWpyaHVQS2pOYVltYUgwa3Qxbn5jbTBaUXZLfnRvSUFBQUFBJCQAAAAAAAAAAAEAAAAr9cFIYWt4eG8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC-e02gvntNobk; BDSFRCVID=1i4OJexroGWN3M5scjitwgy0qeKK0gOTDYrEOwXPsp3LGJLVvfe5EG0PtOi2xEPM4ch-ogKK0eOTHkCF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tbC8VCD5JCt3H48k-4QEbbQH-UnLq58ftgOZ04n-ah3RhJPl5RbP5R3Q5UJ8JnoBfI5Koqcm3UTKsq76Wh35K5tTQP6rLtnGX264KKJxbPjphpnwyPK-MxDBhUJiB5O-Ban7BhOIXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtpChbCKxD6_BDjc0epJf-K6ba5Ta3RA8Kb7Vbn3RLfnkbJkXhPJUWjJuJ672Kpb9bb3Bh-jNyU42bU47QbrH0lRWBR7rWpcxt-odS4QIbjopQT8r5-n0JJv4LgDJ3bPEab3vOIJNXpO1MUtzBN5thURB2DkO-4bCWJ5TMl5jDh3Mb6ksD-FtqjLjtJI8oCIaf-3bfTrghnoD-tRH-UnLq5Oz02OZ04n-ah3R8COEjJbjQM0i5UJ8Jno-W20j0h7m3UTKsf780MuVLP--QbbALJ5h5RT4KKJxbp7Eh4nH0MFM-PvDhUJiB5O-Ban7BhOIXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtpChbCKxD6_BDjc0eU5eetjK2CntsJOOaCv4oqjOy4oWK4413PIeW6QeKKQ0hP3jMCJaeqvoD-Jc3M04K4o9-hvT-54e2p3FBUQ-eRKGQft20b0gMH5O0lOuJI73sR7jWhk2eq72y-RTQlRX5q79atTMfNTJ-qcH0KQpsIJM5-DWbT8IjHCtJTDtfRC8_Cvt-5rDHJTg5DTjhPrMDfuJWMT-MTryKM3kthChqnOFMJObbncQKfoiB5OMBanRh4oNB-3iV-OxDUvnyxAZ5xj-txQxtNRJ2bI-Mp5m8DbnMKcobUPUDMo9LUvW02cdot5yBbc8eIna5hjkbfJBQttjQn3hfIkj2CKLK-oj-DKlejrP; H_PS_PSSID=60277_63141_63326_64814_64815_64864_64833_64902_64969_64984_65017_65116_65140_65188_65230_65242_65256_65274_65325_65382_65361_65368_65421_65427_65456_65503_65477; kleck=e449075e259927a91a5e38778f0c940c29148ea49662638a; H_WISE_SIDS=60277_63141_63326_64814_64815_64864_64833_64902_64969_64984_65017_65116_65140_65188_65230_65242_65256_65274_65325_65382_65361_65368_65421_65427_65456_65503_65477; delPer=1; PSINO=3; BAIDUID_BFESS=8D2DE3A42C79F5B353103F9154E3B291:FG=1; BDSFRCVID_BFESS=1i4OJexroGWN3M5scjitwgy0qeKK0gOTDYrEOwXPsp3LGJLVvfe5EG0PtOi2xEPM4ch-ogKK0eOTHkCF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF_BFESS=tbC8VCD5JCt3H48k-4QEbbQH-UnLq58ftgOZ04n-ah3RhJPl5RbP5R3Q5UJ8JnoBfI5Koqcm3UTKsq76Wh35K5tTQP6rLtnGX264KKJxbPjphpnwyPK-MxDBhUJiB5O-Ban7BhOIXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtpChbCKxD6_BDjc0epJf-K6ba5Ta3RA8Kb7Vbn3RLfnkbJkXhPJUWjJuJ672Kpb9bb3Bh-jNyU42bU47QbrH0lRWBR7rWpcxt-odS4QIbjopQT8r5-n0JJv4LgDJ3bPEab3vOIJNXpO1MUtzBN5thURB2DkO-4bCWJ5TMl5jDh3Mb6ksD-FtqjLjtJI8oCIaf-3bfTrghnoD-tRH-UnLq5Oz02OZ04n-ah3R8COEjJbjQM0i5UJ8Jno-W20j0h7m3UTKsf780MuVLP--QbbALJ5h5RT4KKJxbp7Eh4nH0MFM-PvDhUJiB5O-Ban7BhOIXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtpChbCKxD6_BDjc0eU5eetjK2CntsJOOaCv4oqjOy4oWK4413PIeW6QeKKQ0hP3jMCJaeqvoD-Jc3M04K4o9-hvT-54e2p3FBUQ-eRKGQft20b0gMH5O0lOuJI73sR7jWhk2eq72y-RTQlRX5q79atTMfNTJ-qcH0KQpsIJM5-DWbT8IjHCtJTDtfRC8_Cvt-5rDHJTg5DTjhPrMDfuJWMT-MTryKM3kthChqnOFMJObbncQKfoiB5OMBanRh4oNB-3iV-OxDUvnyxAZ5xj-txQxtNRJ2bI-Mp5m8DbnMKcobUPUDMo9LUvW02cdot5yBbc8eIna5hjkbfJBQttjQn3hfIkj2CKLK-oj-DKlejrP; BA_HECTOR=ah05ah850524002400a52h8h2400031kdcmcb25; ZFY=Z6HrazFHwFGntR:B6VkDVscHQf9mEGVUffFHjgTfw8nM:C; BDORZ=FFFB88E999055A3F8A630C64834BD6D0',
                'Host':'ug.baidu.com',
                'origin':'https://www.baidu.com',
                'referer':'https://www.baidu.com/',
                'sec-ch-ua':'"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"'
            }

            # 发送请求
            url = self.get_baidu_search_url(phone_number)
            response = self.session.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return ""

            # 提取JSON数据
            json_data = self.extract_json_from_html(response.text, phone_number)
            print(json_data)

            if json_data:
                # 提取tag字段
                #tag = json_data.get('tag', '')
                tag = json_data.get('markerTitle', '')
                if tag=='':
                    return "无标记"
                else:
                    return tag
            else:
                return ""

        except requests.RequestException as e:
            print(f"网络请求错误: {e}")
            return ""
        except Exception as e:
            print(f"处理号码 {phone_number} 时出错: {e}")
            return ""

    def process_excel_file(self, input_file, output_file):
        """处理Excel文件，从第一行开始读取"""
        try:
            # 读取Excel，假设第一行是标题（若无标题行，使用 header=None）
            df = pd.read_excel(input_file, dtype={0: str}, header=0)

            # 检查是否有数据
            if df.empty:
                print("Excel文件为空！")
                return False

            # 获取第一列数据（号码列）
            phone_numbers = df.iloc[:, 0].tolist()

            # 添加结果列（如果尚未存在）
            if '标记结果' not in df.columns:
                df['标记结果'] = ''

            batch_size = 21

            # 从第一行数据开始处理
            for idx, phone in enumerate(phone_numbers):
                clean_phone = str(phone).strip() if pd.notna(phone) else None
                if not clean_phone or clean_phone == 'nan':
                    df.at[idx, '标记结果'] = "无效号码"
                    continue

                print(f"正在处理第 {idx + 1}/{len(phone_numbers)} 个号码: {clean_phone}")
                marker = self.get_phone_marker(clean_phone)
                # ------------------- 关键修改 -------------------
                # 将原本的"无标记"改为"查询失败"
                if marker=='':
                    for i in range(5):
                        print(f"号码： {clean_phone}开始第{i+1}次重试")
                        marker = self.get_phone_marker(clean_phone)
                        if marker!='':
                            break


                df.at[idx, '标记结果'] = marker if marker else "查询失败或无标记"
                # ------------------------------------------------

                if (idx + 1) % batch_size == 0 and idx != len(phone_numbers) - 1:
                    print("已处理21个号码，暂停32秒...")
                    time.sleep(32)  # 暂停32秒
                else:
                    time.sleep(0.1)  # 默认短暂延迟

            # 保存结果
            df.to_excel(output_file, index=False)
            print(f"处理完成！结果已保存到: {output_file}")
            return True

        except Exception as e:
            print(f"处理Excel文件时出错: {e}")
            return False


def main():
    # 配置输入输出文件
    input_excel = r"D:\工作\py\号码显示解析\123.xlsx"  # 输入Excel文件
    output_excel = r"D:\工作\py\号码显示解析\123out.xlsx"  # 输出Excel文件

    # 创建处理器实例
    processor = PhoneNumberMarker()

    # 处理Excel文件
    success = processor.process_excel_file(input_excel, output_excel)

    if success:
        print("程序执行成功！")
    else:
        print("程序执行失败！")


if __name__ == "__main__":
    main()