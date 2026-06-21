"""
聊天消息和历史管理
"""

from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    """单条聊天消息"""
    role: str  # 'user' 或 'assistant'
    content: str
    timestamp: str = None


class ChatHistory:
    """管理聊天对话历史"""

    def __init__(self):
        """初始化空聊天历史"""
        self.messages: List[ChatMessage] = []

    def add_user_message(self, content: str):
        """添加用户消息到历史"""
        msg = ChatMessage(role='user', content=content)
        self.messages.append(msg)

    def add_assistant_message(self, content: str):
        """添加助手消息到历史"""
        msg = ChatMessage(role='assistant', content=content)
        self.messages.append(msg)

    def clear(self):
        """清空所有消息"""
        self.messages = []

    def get_messages(self) -> List[Dict]:
        """获取用于API调用的消息格式"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]

    def get_last_assistant_message(self) -> str:
        """获取最后一条助手消息"""
        for msg in reversed(self.messages):
            if msg.role == 'assistant':
                return msg.content
        return ""