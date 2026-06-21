# Ollama GUI Client

一个现代化的Python GUI应用，用于连接Ollama服务器并与其部署的AI模型进行聊天交互。

## 功能特性

- 🖥️ 现代化GUI界面，使用CustomTkinter
- 🔌 连接任意Ollama服务器（通过IP:port）
- 📋 查看服务器部署的所有模型
- 💬 与选中模型进行流式聊天
- ⚡ 后台线程处理，保证UI响应

## 环境要求

- Python 3.6+
- 虚拟环境（可选但推荐）

## 安装依赖

```bash
# 安装GUI依赖
pip install -r requirements_gui.txt

# 或手动安装
pip install customtkinter requests
```

## 使用方法

### 1. 启动应用

```bash
python ollama_gui.py
```

### 2. 连接服务器

1. 在顶部输入框输入Ollama服务器的地址（格式：IP:PORT）
2. 点击"Connect"按钮
3. 等待连接成功并加载模型列表

**示例地址：**
- 本地服务器：`127.0.0.1:11434`
- 本地服务器（Windows）：`localhost:11434`
- 远程服务器：`192.168.1.100:11434`

### 3. 选择模型

1. 在左侧"Available Models"列表中双击要聊天的模型
2. 系统会自动加载模型并准备聊天

### 4. 开始聊天

1. 在右侧聊天面板底部的输入框输入消息
2. 点击"Send"按钮（或按Enter发送）
3. 模型会流式返回响应

## 界面说明

```
┌────────────────────────────────────────────────────┐
│ [Ollama Server: ______]  [CONNECT]  [DISCONNECT]  │  ← 服务器输入区
├──────────────┬──────────────────────────────────────┤
│              │                                      │
│  Model List  │            Chat Panel                │
│  - llama2    │  User: _____                         │
│  - glm-4.7   │  [SEND]                              │
│  - qwen2     │                                      │
│              │  Assistant: ...                      │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
```

### 顶部区域
- **Ollama Server (IP:Port)**: 输入要连接的服务器地址
- **Connect**: 点击连接服务器并获取模型列表

### 左侧区域
- **Available Models**: 显示服务器上的所有模型列表
- **双击列表项**: 选择要聊天的模型

### 右侧区域
- **Chat Panel**: 聊天消息显示区域
- **Message input**: 输入发送的消息
- **Send**: 发送按钮

## 系统要求

- Ollama服务器运行中
- 可通过浏览器访问Ollama API（默认端口11434）
- Python环境已配置虚拟环境（推荐）

## API端点

应用使用以下Ollama API端点：

- **查询模型列表**: `GET /api/tags`
- **聊天**: `POST /api/chat`

## 故障排除

### 无法连接到服务器
- 确认Ollama服务器正在运行
- 检查IP:port地址是否正确
- 确认防火墙允许访问该端口
- 尝试在浏览器中访问 `http://<ip>:<port>/api/tags`

### 模型列表为空
- 确认服务器有部署的模型
- 尝试重新连接服务器

### 聊天无响应
- 确认已选择模型（双击列表项）
- 检查服务器是否正常运行
- 查看底部状态栏的错误信息

## 代码结构

```
ollam_servers/
├── ollama_gui.py          # 主GUI应用程序
├── ollama_api.py          # Ollama API客户端封装
├── ollama_chat.py         # 聊天消息历史管理
├── ollama_config.py       # 配置和常量
├── requirements_gui.txt   # GUI依赖
└── README_GUI.md          # 本文档
```

## 开发相关

- **GUI框架**: CustomTkinter (基于Tkinter的现代化扩展)
- **HTTP请求**: requests库
- **线程安全**: 使用后台线程处理网络请求

## 许可证

本项目与Ollama项目保持一致。
