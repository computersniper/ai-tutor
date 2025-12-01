"""
DeepSeek API 客户端封装
使用 OpenAI SDK 与 DeepSeek API 交互（DeepSeek API 兼容 OpenAI 格式）
"""

from openai import OpenAI
import time
import os
from typing import List, Dict  # 添加这行导入

class DeepSeekClient:
    """DeepSeek API 客户端类"""

    def __init__(self):
        """初始化 DeepSeek 客户端"""
        # 验证配置
        # ==================== API Configuration ====================
        DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_api_key")
        DEEPSEEK_BASE_URL = "https://api.deepseek.com"
        MODEL_NAME = "deepseek-chat"

        # 创建 OpenAI 客户端，指向 DeepSeek API
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )

        
    # ==================== AI Behavior Parameters ====================
        TEMPERATURE = 0.9
        MAX_TOKENS = 1500
    
        self.model = MODEL_NAME
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS

    def chat(self, system_prompt: str, user_message: str, temperature: float = None) -> str:
        """
        发送聊天请求到 DeepSeek API

        参数:
            system_prompt: 系统提示词（定义 AI 角色）
            user_message: 用户消息内容
            temperature: 温度参数（可选，默认使用配置值）

        返回:
            AI 生成的回复内容
        """
        try:
            # 记录开始时间
            start_time = time.time()

            # 调用 DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=self.max_tokens
            )

            # 记录结束时间
            elapsed_time = time.time() - start_time

            # 提取回复内容
            reply = response.choices[0].message.content

            # 打印调试信息（可选）
            print(f"⏱️  API 响应时间: {elapsed_time:.2f}秒")

            return reply

        except Exception as e:
            error_msg = f"❌ DeepSeek API 调用失败: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

    def chat_with_context(
        self,
        system_prompt: str,
        messages: list,
        temperature: float = None
    ) -> str:
        """
        带上下文的聊天请求（支持多轮对话）

        参数:
            system_prompt: 系统提示词
            messages: 消息历史列表 [{"role": "user/assistant", "content": "..."}]
            temperature: 温度参数（可选）

        返回:
            AI 生成的回复内容
        """
        try:
            # 构建完整的消息列表
            full_messages = [{"role": "system", "content": system_prompt}] + messages

            # 调用 API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=self.max_tokens
            )

            # 提取回复
            reply = response.choices[0].message.content
            return reply

        except Exception as e:
            error_msg = f"❌ DeepSeek API 调用失败: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def chat_with_history(self, system_prompt: str, messages: List[Dict], temperature: float = 0.0) -> str:
        """
        支持历史记录的聊天方法（兼容之前的 chat_with_context）
        
        参数:
            system_prompt: 系统提示词
            messages: 消息历史列表 [{"role": "user/assistant", "content": "..."}]
            temperature: 温度参数
            
        返回:
            AI 生成的回复内容
        """
        return self.chat_with_context(system_prompt, messages, temperature)


# 测试代码
if __name__ == "__main__":
    # 简单测试
    try:
        client = DeepSeekClient()
        print("✅ DeepSeek 客户端初始化成功！")

        # 测试简单对话
        response = client.chat(
            system_prompt="你是一个友好的助手。",
            user_message="你好！请用一句话介绍你自己。"
        )
        print(f"\n🤖 AI 回复:\n{response}")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
