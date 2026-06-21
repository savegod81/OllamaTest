"""
配置和常量管理
"""

class Config:
    """应用配置类"""

    # GUI设置
    DEFAULT_SERVER = "127.0.0.1:11434"
    WINDOW_TITLE = "Ollama GUI Client"
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700

    # 连接设置
    DEFAULT_TIMEOUT = 10
    MAX_RETRIES = 3

    # 颜色配置
    COLOR_PRIMARY = "#1a1a2e"
    COLOR_ACCENT = "#4ecca3"
    COLOR_TEXT = "#eeeeee"
    COLOR_BACKGROUND = "#16213e"
    COLOR_INPUT_BG = "#0f3460"
    COLOR_LIST_BG = "#1a1a2e"
    COLOR_DIALOG_BG = "#16213e"