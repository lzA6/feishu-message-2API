import os
from dotenv import load_dotenv
import json
import logging
import sys

load_dotenv()

class Settings:
    FEISHU_AUTH_JSON: str = os.getenv("FEISHU_AUTH_JSON", "{}")
    DEFAULT_CHAT_ID: str = os.getenv("DEFAULT_CHAT_ID", "")
    API_MASTER_KEY: str = os.getenv("API_MASTER_KEY", "")

    DEFAULT_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    DEFAULT_REFERER: str = "https://www.feishu.cn/messenger/"

    _auth_data = {}
    try:
        if FEISHU_AUTH_JSON and FEISHU_AUTH_JSON.strip():
            _auth_data = json.loads(FEISHU_AUTH_JSON)
    except json.JSONDecodeError:
        logging.critical("致命错误: .env 文件中的 FEISHU_AUTH_JSON 不是有效的 JSON 格式。")
        sys.exit(1)

    FEISHU_COOKIE: str = _auth_data.get("cookie", "")
    COMMAND_ID_HISTORY: str = _auth_data.get("cmd_history", "")
    COMMAND_ID_STREAM: str = _auth_data.get("cmd_stream", "")
    FEISHU_WEB_VERSION: str = _auth_data.get("web_version", "")
    CSRF_TOKEN: str = _auth_data.get("csrf_token", "")
    USER_AGENT: str = _auth_data.get("user_agent", "")
    REFERER: str = _auth_data.get("referer", "")

settings = Settings()
