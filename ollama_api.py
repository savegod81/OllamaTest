"""
Ollama API客户端封装
处理与Ollama服务器的所有交互
"""

import requests
from ollama import Client
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass


@dataclass
class ModelInfo:
    """模型信息数据类"""
    name: str
    size: int
    modified_at: str
    digest: str


@dataclass
class ServerResponse:
    """服务器响应数据类"""
    server: str
    models: List[ModelInfo]
    success: bool
    error: Optional[str] = None


class OllamaClient:
    """Ollama服务器客户端"""

    def __init__(self, host: str = None):
        """初始化客户端"""
        self.host = host
        self.client = Client(host=host)

    def get_server_status(self, timeout: int = 5) -> bool:
        """检查服务器是否可达"""
        url = f"{self.host}/api/tags"
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> ServerResponse:
        """从服务器获取所有模型"""
        try:
            models_data = self.client.list()

            # Handle both Pydantic model and dict response
            if hasattr(models_data, 'models'):
                # It's a Pydantic model
                model_list = models_data.models
            else:
                # It's a dict
                model_list = models_data.get('models', [])
            #print("ollam_api: ",model_list)        
            models = [
                ModelInfo(
                    name=m.get('model', '') if isinstance(m, dict) else getattr(m, 'model', ''),
                    size=m.get('size', 0) if isinstance(m, dict) else getattr(m, 'size', 0),
                    modified_at=m.get('modified_at', '') if isinstance(m, dict) else str(getattr(m, 'modified_at', '')),
                    digest=m.get('digest', '') if isinstance(m, dict) else getattr(m, 'digest', '')
                )
                for m in model_list
                if not (isinstance(m, dict) and m.get('model', '').endswith('cloud')) and not (isinstance(m, object) and getattr(m, 'model', '').endswith('cloud'))
            ]
            # Extract host to get server info
            server = self.host.replace('http://', '').replace('https://', '')
            return ServerResponse(
                server=server,
                models=models,
                success=True
            )
        except Exception as e:
            # Extract host to get server info
            server = self.host.replace('http://', '').replace('https://', '')
            return ServerResponse(
                server=server,
                models=[],
                success=False,
                error=str(e)
            )

    def chat(
        self,
        model: str,
        messages: list,
        stream: bool = True
    ) -> Generator[str, None, None]:
        """发送聊天消息到服务器并流式返回响应"""
        try:
            for part in self.client.chat(model, messages=messages, stream=stream):
                yield part.message.content

        except Exception as e:
            yield f"[Error: {str(e)}]"