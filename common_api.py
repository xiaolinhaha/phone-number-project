#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

class CommonAPIClient:
    """
    公共API调用客户端
    支持新的接口配置和参数格式
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化API客户端
        
        Args:
            config: 可选的配置字典，如果不提供则使用默认配置
        """
        # 默认配置
        self.default_config = {
            "api": {
                "api_key": "app-ZjOjg2nbvzUxzcxr8WtFD6So",
                "base_url": "https://malla.leagpoint.com/rssz/v1/workflows/run",
                "response_mode": "blocking",
                "user": "abc-123"
            },
            "schedule": {
                "time": "10:00",
                "description": "每天执行API调用的时间"
            },
            "logging": {
                "level": "INFO",
                "api_log_file": "api_calls.log",
                "scheduler_log_file": "scheduler.log"
            }
        }
        
        # 使用提供的配置或默认配置
        self.config = config if config else self.default_config
        
        # 设置日志
        self._setup_logging()
        
        # API配置
        self.api_key = self.config["api"]["api_key"]
        self.base_url = self.config["api"]["base_url"]
        self.user = self.config["api"]["user"]
        
        logging.info(f"🔧 CommonAPIClient 初始化完成")
        logging.info(f"🔑 API Key: {self.api_key[:20]}...")
        logging.info(f"🌐 Base URL: {self.base_url}")
    
    def _setup_logging(self):
        """设置日志配置"""
        log_level = getattr(logging, self.config["logging"]["level"])
        log_file = self.config["logging"]["api_log_file"]
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def call_api_with_number_tag(self, number: str, tag: str) -> Dict[str, Any]:
        """
        调用API接口，传入number和tag参数
        
        Args:
            number: 电话号码
            tag: 标签
            
        Returns:
            Dict: API响应结果
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"📞 开始API调用 - {current_time}")
            logging.info(f"📱 Number: {number}")
            logging.info(f"🏷️  Tag: {tag}")
            logging.info("=" * 60)
            
            # 构建请求头
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 构建请求体
            data_json = json.dumps({
                "number": number,
                "tag": tag
            }, ensure_ascii=False)
            
            payload = {
                "inputs": {
                    "data": data_json
                },
                "response_mode": self.config["api"]["response_mode"],
                "user": self.user
            }
            
            logging.info(f"📤 请求头: {json.dumps(headers, indent=2, ensure_ascii=False)}")
            logging.info(f"📤 请求体: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            # 发送请求
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logging.info(f"📊 响应状态码: {response.status_code}")
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                logging.info(f"✅ API调用成功")
                logging.info(f"📋 响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": result,
                    "timestamp": current_time,
                    "request": {
                        "number": number,
                        "tag": tag
                    }
                }
            else:
                error_msg = f"API调用失败，状态码: {response.status_code}"
                logging.error(f"❌ {error_msg}")
                
                try:
                    error_data = response.json()
                    logging.error(f"💥 错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    error_data = response.text
                    logging.error(f"💥 错误详情: {error_data}")
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_msg,
                    "error_data": error_data,
                    "timestamp": current_time,
                    "request": {
                        "number": number,
                        "tag": tag
                    }
                }
                
        except requests.exceptions.Timeout:
            error_msg = "API请求超时"
            logging.error(f"⏰ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": current_time,
                "request": {
                    "number": number,
                    "tag": tag
                }
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API请求异常: {str(e)}"
            logging.error(f"💥 {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": current_time,
                "request": {
                    "number": number,
                    "tag": tag
                }
            }
            
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logging.error(f"💥 {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": current_time,
                "request": {
                    "number": number,
                    "tag": tag
                }
            }
    
    def batch_call_api(self, number_tag_pairs: list) -> list:
        """
        批量调用API接口
        
        Args:
            number_tag_pairs: 支持两种格式:
                - [(number, tag), ...] 元组格式
                - [{"number": number, "tag": tag}, ...] 字典格式
            
        Returns:
            list: 批量调用结果列表
        """
        results = []
        total_count = len(number_tag_pairs)
        
        logging.info(f"🚀 开始批量API调用，共 {total_count} 个请求")
        
        for i, item in enumerate(number_tag_pairs, 1):
            logging.info(f"📞 处理第 {i}/{total_count} 个请求")
            
            # 支持字典和元组两种格式
            if isinstance(item, dict):
                number = item.get('number', '')
                tag = item.get('tag', '')
            else:
                # 假设是元组格式
                number, tag = item
                
            result = self.call_api_with_number_tag(number, tag)
            results.append(result)
            
            # 添加延迟避免请求过于频繁
            if i < total_count:
                import time
                time.sleep(1)  # 1秒延迟
        
        # 统计结果
        success_count = sum(1 for r in results if r.get('success', False))
        fail_count = total_count - success_count
        
        logging.info(f"🎉 批量调用完成！")
        logging.info(f"📊 成功: {success_count} 个，失败: {fail_count} 个")
        
        return results


def create_api_client(config: Optional[Dict] = None) -> CommonAPIClient:
    """
    创建API客户端实例的便捷函数
    
    Args:
        config: 可选的配置字典
        
    Returns:
        CommonAPIClient: API客户端实例
    """
    return CommonAPIClient(config)


# 示例使用方法
if __name__ == "__main__":
    # 创建API客户端
    client = create_api_client()
    
    # 单个调用示例
    result = client.call_api_with_number_tag("13800138000", "测试标签")
    print(f"单个调用结果: {result}")
    
    # 批量调用示例
    number_tag_pairs = [
        ("13800138001", "标签1"),
        ("13800138002", "标签2"),
        ("13800138003", "标签3")
    ]
    
    batch_results = client.batch_call_api(number_tag_pairs)
    print(f"批量调用结果: {len(batch_results)} 个结果")