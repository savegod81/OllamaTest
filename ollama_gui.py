"""
主GUI应用
Ollama GUI客户端，支持服务器连接和聊天界面
"""

import customtkinter as ctk
from tkinter import scrolledtext, Listbox, END, messagebox
import threading
import time
from typing import Optional

from ollama_api import OllamaClient, ModelInfo, ServerResponse
from ollama_chat import ChatHistory
from ollama_config import Config


class OllamaGUI(ctk.CTk):
    """主GUI应用类"""

    def __init__(self):
        """初始化GUI应用"""
        super().__init__()

        # 配置窗口
        self.title(Config.WINDOW_TITLE)
        self.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 初始化组件
        self.client = OllamaClient()
        self.current_server: Optional[str] = None
        self.current_model: Optional[str] = None
        self.chat_history = ChatHistory()

        # 创建GUI组件
        self.create_widgets()

        # 状态标签（在create_widgets之后创建）
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=10)

    def create_widgets(self):
        """创建所有GUI组件"""
        # 主容器，使用网格布局
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 顶部框架 - 服务器输入和连接
        self.top_frame = ctk.CTkFrame(self.main_container)
        self.top_frame.pack(fill="x", pady=(0, 10))

        self.create_server_input_widgets()
        self.create_connect_button()

        # 中间框架 - 分栏视图
        self.middle_frame = ctk.CTkFrame(self.main_container)
        self.middle_frame.pack(fill="both", expand=True, pady=(0, 10))

        # 左侧面板 - 模型列表
        self.left_panel = ctk.CTkFrame(self.middle_frame, width=300)
        self.left_panel.pack(side="left", fill="both", padx=(0, 10))

        self.create_model_list_widgets()

        # 右侧面板 - 聊天区域
        self.right_panel = ctk.CTkFrame(self.middle_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.create_chat_widgets()

    def create_server_input_widgets(self):
        """创建服务器输入组件"""
        # 标签
        ctk.CTkLabel(
            self.top_frame,
            text="Ollama Server (IP:Port):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10))

        # 输入框
        self.server_entry = ctk.CTkEntry(
            self.top_frame,
            placeholder_text=Config.DEFAULT_SERVER,
            width=250
        )
        self.server_entry.pack(side="left", padx=(0, 10))

    def create_connect_button(self):
        """创建连接/断开按钮"""
        self.connect_btn = ctk.CTkButton(
            self.top_frame,
            text="Connect",
            command=self.on_connect,
            width=100
        )
        self.connect_btn.pack(side="left", padx=(0, 10))

        # Reset button
        self.reset_btn = ctk.CTkButton(
            self.top_frame,
            text="Reset",
            command=self.on_reset,
            width=100
        )
        self.reset_btn.pack(side="left", padx=(0, 10))

    def create_model_list_widgets(self):
        """创建模型列表组件"""
        # 标签
        ctk.CTkLabel(
            self.left_panel,
            text="Available Models",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        # 列表框
        self.model_listbox = Listbox(
            self.left_panel,
            height=400,
            bg=Config.COLOR_LIST_BG,
            fg=Config.COLOR_TEXT,
            selectbackground=Config.COLOR_ACCENT,
            selectforeground=Config.COLOR_PRIMARY,
            highlightthickness=0
        )
        self.model_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # 绑定双击事件
        self.model_listbox.bind('<Double-Button-1>', self.on_model_double_click)

    def create_chat_widgets(self):
        """创建聊天组件"""
        # 聊天消息区域标签
        ctk.CTkLabel(
            self.right_panel,
            text="Chat Panel",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 可滚动聊天区域
        self.chat_text = scrolledtext.ScrolledText(
            self.right_panel,
            wrap="word",
            font=("Consolas", 10),
            bg=Config.COLOR_DIALOG_BG,
            fg=Config.COLOR_TEXT,
            insertbackground=Config.COLOR_ACCENT,
            selectbackground=Config.COLOR_ACCENT,
            selectforeground=Config.COLOR_PRIMARY
        )
        self.chat_text.pack(fill="both", expand=True, padx=5, pady=5)

        # 输入框架
        self.input_frame = ctk.CTkFrame(self.right_panel)
        self.input_frame.pack(fill="x", padx=5, pady=5)

        # 消息输入框
        self.message_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type a message..."
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        # 绑定Enter键发送
        self.message_entry.bind('<Return>', lambda event: self.on_send_message())

        # 发送按钮
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="Send",
            command=self.on_send_message
        )
        self.send_btn.pack(side="left", padx=(0, 5))

    def on_connect(self):
        """处理连接按钮点击"""
        server = self.server_entry.get().strip()

        if not server:
            messagebox.showerror("Error", "Please enter a server IP:port")
            return

        # 更新按钮状态
        self.connect_btn.configure(state="disabled", text="Connecting...")
        self.update_status("Connecting...")

        # 在后台线程执行，避免GUI阻塞
        threading.Thread(
            target=self.connect_to_server,
            args=(server,),
            daemon=True
        ).start()

    def on_reset(self):
        """处理重置按钮点击"""
        # 清空服务器输入
        self.server_entry.delete(0, END)

        # 清空聊天区域
        self.chat_text.delete(1.0, END)

        # 清空模型列表
        self.model_listbox.delete(0, END)

        # 重置状态
        self.current_server = None
        self.current_model = None
        self.chat_history.clear()

        # 重置按钮状态
        self.connect_btn.configure(state="normal", text="Connect")
        self.update_status("Ready")

    def connect_to_server(self, server: str):
        """连接服务器并获取模型列表"""
        try:
            # 提取IP和端口
            ip, port = server.split(":")
            print(ip,"&",port)
            # 创建新的客户端实例，使用指定服务器
            self.client = OllamaClient(host=f"http://{ip}:{port}")

            # 测试连通性
            if not self.client.get_server_status():
                self.update_status("Server unreachable")
                messagebox.showerror("Error", f"Server {server} is unreachable")
                self.connect_btn.configure(state="normal", text="Connect")
                return

            # 获取模型
            response = self.client.list_models()

            # 显示连接信息
            self.chat_text.insert(END, f"\n[Connection] Server: {server}\n", "debug")
            self.chat_text.insert(END, f"[Connection] Models found: {len(response.models)}\n", "debug")

            self.current_server = server
            self.current_model = None
            self.chat_history.clear()

            # 清空并填充列表
            self.model_listbox.delete(0, END)

            if response.success:
                for model in response.models:
                    print("Model -> ", model)
                    self.model_listbox.insert(END, model.name)

                self.update_status(f"Connected: {len(response.models)} models")
                self.connect_btn.configure(state="disabled", text="Connected")
            else:
                self.update_status("Failed to fetch models")
                messagebox.showerror("Error", response.error)
                self.connect_btn.configure(state="normal", text="Connect")

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
            self.connect_btn.configure(state="normal", text="Connect")

    def on_model_double_click(self, event):
        """处理模型列表中的双击事件"""
        selection = self.model_listbox.curselection()
        if selection:
            model_name = self.model_listbox.get(selection[0])
            self.current_model = model_name
            self.chat_history.clear()
            self.chat_text.delete(1.0, END)
            self.chat_text.insert(END, f"Selected model: {model_name}\n\n")
            self.update_status(f"Model selected: {model_name}")

    def on_send_message(self):
        """处理发送消息按钮点击"""
        message = self.message_entry.get().strip()

        if not message:
            return

        if not self.current_server or not self.current_model:
            messagebox.showwarning("Warning", "Please connect to a server and select a model")
            return

        # 清空输入
        self.message_entry.delete(0, END)

        # 添加用户消息到聊天
        self.chat_history.add_user_message(message)
        self._append_chat_text(f"User: {message}\n", "user")
        self.chat_text.tag_config("user", foreground=Config.COLOR_ACCENT)
        self.chat_text.tag_config("debug", foreground="#aaaaaa", font=("Consolas", 9))

        # 在后台线程发送消息
        threading.Thread(
            target=self.send_chat_message,
            args=(message,),
            daemon=True
        ).start()

    def send_chat_message(self, message: str):
        """发送聊天消息到服务器并显示响应"""
        try:
            # 发送消息并获取完整响应（流式）
            self.update_status("Sending message...")

            # 显示请求信息
            api_url = f"http://{self.current_server}/api/chat"
            '''
            self._append_chat_text(f"\n[Request] URL: {api_url}\n", "debug")
            self._append_chat_text(f"[Request] Model: {self.current_model}\n", "debug")
            self._append_chat_text(f"[Request] Message length: {len(message)} chars\n", "debug")
            '''
            
            # 调用流式API并收集完整响应
            full_response = ""
            try:
                messages = [{"role": "user", "content": message}]
                for chunk in self.client.chat(self.current_model, messages=messages, stream=True):
                    if chunk:
                        full_response += chunk
                        # 使用self.after确保UI刷新
                        self.after(0, lambda c=chunk: self._append_chat_text(c))
                        self.after(0, lambda: self.chat_text.see(END))

                # 显示响应信息
                if full_response:
                    self._append_chat_text(f"[Response] Success! Length: {len(full_response)} chars\n", "debug")
                    self._append_chat_text(f"\nAssistant: {full_response}\n")
                else:
                    self._append_chat_text(f"[Response] Empty response received\n", "debug")
            except Exception as api_error:
                self._append_chat_text(f"[Response] API Error: {str(api_error)}\n", "debug")

            # 添加助手消息到历史
            if full_response:
                self.chat_history.add_assistant_message(full_response)

            self.update_status("Ready")

        except Exception as e:
            error_msg = f"\n[Error: {str(e)}]\n"
            self._append_chat_text(error_msg)
            self.chat_history.add_assistant_message(error_msg)
            self.update_status("Error")

    def _append_chat_text(self, text: str, tag: str = None):
        """在聊天文本框中追加文本"""
        if tag:
            self.chat_text.insert(END, text, tag)
        else:
            self.chat_text.insert(END, text)


    def update_status(self, message: str):
        """更新状态标签"""
        self.status_var.set(message)


def main():
    """主入口"""
    app = OllamaGUI()
    app.mainloop()


if __name__ == "__main__":
    main()