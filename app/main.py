import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, WebSocket, Query, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from logging_config import setup_logging
setup_logging()

from feishu_provider import FeishuProvider, get_feishu_provider
from config import settings
import feishu_im_pb2

app = FastAPI(
    title="飞书消息方舟",
    description="一个具备完全动态配置能力、多会话管理、并能生成API调用链接的终极Web应用。",
    version="7.0.0"
)

STATIC_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

@app.on_event("startup")
async def startup_event():
    logging.info("应用启动...")
    if not os.path.isdir(STATIC_FILES_DIR):
        logging.critical(f"致命错误: 静态文件目录 '{STATIC_FILES_DIR}' 不存在。前端界面将无法加载。")
    elif not os.path.isfile(os.path.join(STATIC_FILES_DIR, "index.html")):
        logging.critical(f"致命错误: 静态文件目录 '{STATIC_FILES_DIR}' 中缺少 'index.html' 文件。")
    else:
        logging.info(f"静态文件目录已确认: {STATIC_FILES_DIR}")

security = HTTPBearer()

def format_timestamp(ts: int) -> str:
    return datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if settings.API_MASTER_KEY and (credentials.scheme != "Bearer" or credentials.credentials != settings.API_MASTER_KEY):
        logging.warning(f"API 密钥验证失败, 访问被拒绝。")
        raise HTTPException(status_code=403, detail="无效的 API 密钥")

async def get_websocket_provider(
    cookie: Optional[str] = Query(None),
    cmd_history: Optional[str] = Query(None),
    cmd_stream: Optional[str] = Query(None),
    user_agent: Optional[str] = Query(None),
    web_version: Optional[str] = Query(None),
    csrf_token: Optional[str] = Query(None),
    referer: Optional[str] = Query(None),
) -> FeishuProvider:
    return FeishuProvider(
        cookie=cookie or settings.FEISHU_COOKIE,
        history_cmd=cmd_history or settings.COMMAND_ID_HISTORY,
        stream_cmd=cmd_stream or settings.COMMAND_ID_STREAM,
        user_agent=user_agent or settings.USER_AGENT or settings.DEFAULT_USER_AGENT,
        referer=referer or settings.REFERER or settings.DEFAULT_REFERER,
        web_version=web_version or settings.FEISHU_WEB_VERSION,
        csrf_token=csrf_token or settings.CSRF_TOKEN
    )

@app.get("/api/v1/config", summary="获取前端所需的默认配置")
async def get_config():
    return {
        "defaultChatId": settings.DEFAULT_CHAT_ID,
        "defaultAuthJson": settings.FEISHU_AUTH_JSON,
        "apiMasterKey": settings.API_MASTER_KEY,
    }

@app.post("/api/v1/chat/messages", summary="获取历史消息", dependencies=[Depends(verify_api_key)])
async def get_chat_messages(
    chat_id: str, count: int = 50, cursor: str = "0",
    provider: FeishuProvider = Depends(get_feishu_provider)
):
    try:
        response_pb = await provider.get_history_messages(chat_id, count, cursor)
        messages_list = [format_message_to_dict(msg) for msg in response_pb.items]
        return { "has_more": response_pb.has_more, "next_cursor": str(response_pb.next_cursor), "messages": messages_list }
    except Exception as e:
        logging.error(f"获取历史消息时发生错误: {e}")
        raise HTTPException(status_code=502, detail=f"请求飞书服务器失败: {e}。请检查您的所有认证信息是否都正确且有效。")

@app.post("/api/v1/chat/export_for_analysis", summary="导出对话用于AI分析", dependencies=[Depends(verify_api_key)])
async def export_chat_for_analysis(
    chat_id: str,
    count: int = Query(default=100, gt=0, le=500),
    provider: FeishuProvider = Depends(get_feishu_provider)
):
    try:
        response_pb = await provider.get_history_messages(chat_id, count, "0")
        if not response_pb.items:
            return {"analysis_text": "没有找到任何消息。", "start_info": "无", "end_info": "无", "message_count": 0}
        messages = list(reversed(response_pb.items))
        formatted_lines = []
        for msg in messages:
            sender_name = msg.sender.name or "未知用户"
            content_text = msg.text_content.text.strip() if msg.HasField("text_content") else ""
            if not content_text: continue
            timestamp_str = format_timestamp(msg.create_time)
            formatted_lines.append(f"{timestamp_str} - {sender_name}: {content_text}")
        analysis_text = "\n".join(formatted_lines)
        start_msg, end_msg = messages[0], messages[-1]
        start_info = f"从 {format_timestamp(start_msg.create_time)} ({start_msg.sender.name}) 的消息开始"
        end_info = f"到 {format_timestamp(end_msg.create_time)} ({end_msg.sender.name}) 的消息结束"
        return {"analysis_text": analysis_text, "start_info": start_info, "end_info": end_info, "message_count": len(formatted_lines)}
    except Exception as e:
        logging.error(f"导出对话时发生错误: {e}")
        raise HTTPException(status_code=502, detail=f"请求飞书服务器失败: {e}。请检查您的所有认证信息是否都正确且有效。")

@app.websocket("/ws/v1/chat/stream/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: str,
    token: str,
    provider: FeishuProvider = Depends(get_websocket_provider)
):
    if settings.API_MASTER_KEY and token != settings.API_MASTER_KEY:
        await websocket.close(code=1008, reason="无效的 API 密钥")
        return
    
    await websocket.accept()
    logging.info(f"WebSocket 连接已建立, Chat ID: {chat_id}")
    
    try:
        async for new_msg in provider.stream_latest_messages(chat_id):
            await websocket.send_json(format_message_to_dict(new_msg))
    except ValueError as e:
        logging.error(f"WebSocket 因认证信息无效而关闭: {e}")
        await websocket.close(code=1008, reason=str(e))
    except WebSocketDisconnect:
        logging.info(f"客户端主动断开 WebSocket 连接, Chat ID: {chat_id}")
    except Exception as e:
        logging.error(f"WebSocket 发生未知错误: {e}")
        await websocket.close(code=1011, reason=f"发生内部错误: {e}")
    finally:
        logging.info(f"WebSocket 连接已关闭, Chat ID: {chat_id}")

def format_message_to_dict(msg: feishu_im_pb2.Message) -> dict:
    content_text = ""
    if msg.HasField("text_content"): content_text = msg.text_content.text
    sender_info = {}
    if msg.HasField("sender"): sender_info = { "id": msg.sender.sender_id, "name": msg.sender.name, "avatar_url": msg.sender.avatar_url }
    return { "message_id": msg.message_id, "chat_id": msg.chat_id, "sender": sender_info, "create_time": msg.create_time, "content": content_text }

app.mount("/", StaticFiles(directory=STATIC_FILES_DIR, html=True), name="public")