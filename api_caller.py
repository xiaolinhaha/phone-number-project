#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
import logging
import glob

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_calls.log'),
        logging.StreamHandler()
    ]
)

class APIWorkflowCaller:
    def __init__(self, config_file="config.json"):
        """
        初始化API调用器
        
        Args:
            config_file (str): 配置文件路径
        """
        self.config = self.load_config(config_file)
        self.api_key = self.config['api']['api_key']
        self.base_url = self.config['api']['base_url']
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self.payload = {
            "inputs": {
                "allPhone": 'all'
            },
            "response_mode": self.config['api']['response_mode'],
            "user": self.config['api']['user']
        }
    
    def save_number_list_to_file(self, number_list, files_dir="files"):
        """
        保存numberList到JSON文件（默认保存到项目目录下的 files/）
        
        Args:
            number_list (list): 电话号码列表
            files_dir (str): 保存文件的目录；相对路径将以当前脚本目录为基准
        """
        try:
            # 统一为脚本目录相对路径，避免服务器上的绝对路径问题
            script_dir = os.path.dirname(os.path.abspath(__file__))
            target_dir = files_dir if os.path.isabs(files_dir) else os.path.join(script_dir, files_dir)

            # 确保files目录存在
            os.makedirs(target_dir, exist_ok=True)
            
            # 删除前一天的JSON文件
            self.cleanup_old_files(target_dir)
            
            # 生成今天的文件名
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"numberList_{today}.json"
            filepath = os.path.join(target_dir, filename)
            
            # 准备保存的数据
            data = {
                "date": today,
                "timestamp": datetime.now().isoformat(),
                "numberList": number_list,
                "count": len(number_list)
            }
            
            # 保存到JSON文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"💾 成功保存 {len(number_list)} 个号码到文件: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"❌ 保存文件失败: {str(e)}")
            return None
    
    def cleanup_old_files(self, files_dir):
        """
        删除前一天及更早的JSON文件
        
        Args:
            files_dir (str): 文件目录
        """
        try:
            # 获取昨天的日期
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # 查找所有numberList_*.json文件
            pattern = os.path.join(files_dir, "numberList_*.json")
            old_files = glob.glob(pattern)
            
            for file_path in old_files:
                filename = os.path.basename(file_path)
                # 提取文件中的日期
                if filename.startswith("numberList_") and filename.endswith(".json"):
                    file_date = filename[11:-5]  # 提取日期部分
                    if file_date <= yesterday:  # 如果是昨天或更早的文件
                        os.remove(file_path)
                        logging.info(f"🗑️ 删除旧文件: {file_path}")
                        
        except Exception as e:
            logging.error(f"❌ 清理旧文件失败: {str(e)}")
    
    def extract_number_list_from_response(self, response_text):
        """
        从流式响应文本中提取号码列表，优先解析 numberListBody.callingNumbers
        
        Args:
            response_text (str): 响应文本
            
        Returns:
            list: 提取的号码列表
        """
        number_list = []
        try:
            lines = response_text.split('\n')
            for line in lines:
                if line.strip().startswith('data: '):
                    data_str = line.strip()[6:]  # 去掉 'data: ' 前缀
                    try:
                        data = json.loads(data_str)
                        if data.get('event') == 'workflow_finished':
                            outputs = (data.get('data') or {}).get('outputs')
                            if isinstance(outputs, dict):
                                # 新结构：outputs.numberListBody.callingNumbers
                                number_list_body = outputs.get('numberListBody')
                                if isinstance(number_list_body, dict):
                                    calling_numbers = number_list_body.get('callingNumbers')
                                    if isinstance(calling_numbers, list):
                                        number_list = calling_numbers
                                        break
                                # 兼容旧结构：outputs.numberList 为数组
                                if isinstance(outputs.get('numberList'), list):
                                    number_list = outputs.get('numberList')
                                    break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logging.error(f"❌ 提取numberList失败: {str(e)}")
        
        return number_list
    
    def load_config(self, config_file):
        """
        加载配置文件
        
        Args:
            config_file (str): 配置文件路径
            
        Returns:
            dict: 配置信息
        """
        try:
            # 获取脚本所在目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, config_file)
            
            if not os.path.exists(config_path):
                logging.error(f"❌ 配置文件不存在: {config_path}")
                # 返回默认配置
                return self.get_default_config()
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logging.info(f"✅ 成功加载配置文件: {config_path}")
                return config
                
        except json.JSONDecodeError as e:
            logging.error(f"❌ 配置文件格式错误: {e}")
            return self.get_default_config()
        except Exception as e:
            logging.error(f"❌ 加载配置文件失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """
        获取默认配置
        
        Returns:
            dict: 默认配置信息
        """
        logging.warning("⚠️ 使用默认配置")
        return {
            "api": {
                "api_key": "app-4djToLaTnYL1NYdlHv75knvx",
                "base_url": "https://malla.leagpoint.com/rssz/v1/workflows/run",
                "all_phone": "all",
                "response_mode": "blocking",
                "user": "abc-123"
            }
        }
    
    def _extract_calling_numbers_from_outputs(self, outputs):
        """
        从 outputs 提取号码数组，支持两种结构：
        1) outputs.numberListBody.callingNumbers（字典或JSON字符串）
        2) 兼容旧结构 outputs.numberList（数组）
        """
        number_list = []
        try:
            if not isinstance(outputs, dict):
                return []
            body = outputs.get('numberListBody')
            # 情况1：字典结构
            if isinstance(body, dict):
                cn = body.get('callingNumbers')
                if isinstance(cn, list):
                    number_list = cn
            # 情况2：字符串结构（需要反序列化）
            elif isinstance(body, str):
                parsed = None
                try:
                    parsed = json.loads(body)
                except json.JSONDecodeError:
                    # 尝试兼容单引号
                    try:
                        parsed = json.loads(body.replace("'", '"'))
                    except json.JSONDecodeError:
                        parsed = None
                if isinstance(parsed, dict):
                    cn = parsed.get('callingNumbers')
                    if isinstance(cn, list):
                        number_list = cn
            # 兼容旧结构
            if not number_list:
                legacy = outputs.get('numberList')
                if isinstance(legacy, list):
                    number_list = legacy
        except Exception:
            pass
        return number_list
    
    def call_api(self):
        """
        调用API接口
        
        Returns:
            dict: API响应结果
        """
        try:
            logging.info("🚀 开始调用API...")
            logging.info(f"📡 请求URL: {self.base_url}")
            logging.info(f"📊 请求数据: {json.dumps(self.payload, indent=2)}")
            
            # 发送POST请求
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=self.payload,
                timeout=30
            )
            
            # 检查响应状态
            if response.status_code == 200:
                logging.info("✅ API调用成功!")
                logging.info(f"📋 响应状态码: {response.status_code}")
                
                # 处理响应
                if self.payload["response_mode"] == "streaming":
                    logging.info("📡 处理流式响应...")
                    response_text = ""
                    number_list = []
                    
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            logging.info(f"📥 接收数据: {decoded_line}")
                            response_text += decoded_line + "\n"
                            
                            # 尝试从当前行提取号码列表（优先 numberListBody.callingNumbers）
                            if decoded_line.strip().startswith('data: '):
                                data_str = decoded_line.strip()[6:]  # 去掉 'data: ' 前缀
                                try:
                                    data = json.loads(data_str)
                                    if data.get('event') == 'workflow_finished':
                                        outputs = (data.get('data') or {}).get('outputs')
                                        number_list = self._extract_calling_numbers_from_outputs(outputs)
                                        if number_list:
                                            logging.info(f"🎯 提取到号码列表，共 {len(number_list)} 个")
                                            # 保存到JSON文件（键名保持为 'numberList' 供下游脚本使用）
                                            self.save_number_list_to_file(number_list)
                                except json.JSONDecodeError:
                                    continue
                    
                    return {
                        "success": True,
                        "numberList": number_list,
                        "response_text": response_text
                    }
                else:
                    # 处理阻塞式响应
                    logging.info("📡 处理阻塞式响应...")
                    result = response.json()
                    logging.info(f"📥 响应数据: {json.dumps(result, indent=2)}")
                    
                    # 从阻塞式响应中提取号码列表，优先读取 numberListBody.callingNumbers
                    number_list = []
                    try:
                        data_section = result.get('data') or {}
                        outputs = data_section.get('outputs')
                        number_list = self._extract_calling_numbers_from_outputs(outputs)
                        if not number_list:
                            status = result.get('status')
                            if status == 'failed':
                                logging.error(f"❌ 工作流返回失败: {json.dumps(result, ensure_ascii=False)}")
                    except Exception as e:
                        logging.error(f"❌ 解析响应提取号码失败: {str(e)}")

                    if number_list:
                        logging.info(f"🎯 提取到号码列表，共 {len(number_list)} 个")
                        # 保存numberList到JSON文件（为下游脚本保持键名 'numberList'）
                        self.save_number_list_to_file(number_list)
                    
                    return {
                        "success": True,
                        "numberList": number_list,
                        "result": result
                    }
                    
            else:
                logging.error(f"❌ API调用失败!")
                logging.error(f"📋 响应状态码: {response.status_code}")
                logging.error(f"📋 响应内容: {response.text}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except requests.exceptions.Timeout:
            logging.error("⏰ 请求超时!")
            return {"success": False, "error": "请求超时"}
            
        except requests.exceptions.ConnectionError:
            logging.error("🔌 连接错误!")
            return {"success": False, "error": "连接错误"}
            
        except Exception as e:
            logging.error(f"💥 发生未知错误: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_connection(self):
        """
        测试API连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            logging.info("🔍 测试API连接...")
            response = requests.get(
                "https://malla.leagpoint.com",
                timeout=10
            )
            if response.status_code in [200, 404]:  # 404也表示服务器可达
                logging.info("✅ API服务器连接正常")
                return True
            else:
                logging.warning(f"⚠️ API服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"❌ API服务器连接失败: {str(e)}")
            return False

def main():
    """主函数 - 用于测试API调用"""
    # 支持命令行参数指定配置文件
    config_file = "config.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    # 创建API调用器实例（从配置文件读取参数）
    caller = APIWorkflowCaller(config_file)
    
    # 显示当前配置信息
    logging.info(f"📋 当前配置:")
    logging.info(f"  🔑 API密钥: {caller.api_key[:10]}...")
    logging.info(f"  📞 电话号码: {caller.config['api']['all_phone']}")
    logging.info(f"  👤 用户: {caller.config['api']['user']}")
    
    # 测试连接
    if caller.test_connection():
        # 调用API
        result = caller.call_api()
        logging.info(f"🎯 最终结果: {result}")
    else:
        logging.error("❌ 无法连接到API服务器，请检查网络连接")

if __name__ == "__main__":
    main()