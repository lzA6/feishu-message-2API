# feishu_provider.py (v9.1 - 健壮版)
import requests
import uuid
import asyncio
from fastapi import Header
from typing import Optional, AsyncGenerator
from urllib.parse import urlparse
import logging

from config import settings
try:
    import feishu_im_pb2
except ImportError:
    logging.critical("致命错误: 无法导入 feishu_im_pb2.py。请确保 Dockerfile 正确生成了此文件。")
    exit(1)

class FeishuProvider:
    def __init__(self, cookie: str, history_cmd: str, stream_cmd: str, user_agent: str, referer: str, web_version: str, csrf_token: Optional[str] = None, lgw_csrf_token: Optional[str] = None):
        logging.info("FeishuProvider 正在初始化...")
        
        # 核心验证：history_cmd 是必须的
        if not all([cookie, user_agent, referer, history_cmd, web_version]):
            raise ValueError("认证信息不完整，缺少 cookie, user_agent, referer, history_cmd 或 web_version 之一。")
        
        self.base_url = "https://internal-api-lark-api.feishu.cn"
        self.history_command_id = history_cmd
        
        # 核心修正：如果 stream_cmd 不存在或与 history_cmd 相同，发出警告，但程序继续
        if not stream_cmd or stream_cmd == history_cmd:
            logging.warning(f"警告: 未提供有效的实时消息 Command ID (stream_cmd)，或其与历史消息ID相同 ({history_cmd})。实时消息功能可能无法正常工作。")
            self.stream_command_id = history_cmd # 使用历史ID作为备用
        else:
            self.stream_command_id = stream_cmd

        parsed_uri = urlparse(referer)
        origin = f"{parsed_uri.scheme}://{parsed_uri.netloc}"

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Content-Type": "application/x-protobuf",
            "Accept": "*/*",
            "Cookie": cookie,
            "Referer": referer,
            "Origin": origin,
            "x-web-version": web_version,
            "x-source": "web",
        })
        if csrf_token: self.session.headers["x-csrf-token"] = csrf_token
        if lgw_csrf_token: self.session.headers["x-lgw-csrf-token"] = lgw_csrf_token
        
        logging.info(f"FeishuProvider 初始化成功。History Cmd: {self.history_command_id}, Stream Cmd: {self.stream_command_id}")

    def _build_request_frame(self, biz_payload: bytes, request_id: str, command_id: str) -> bytes:
        biz_request = feishu_im_pb2.BizRequest(payload=biz_payload)
        frame = feishu_im_pb2.Frame(
            sequence_id=1,
            log_id=int(command_id),
            service_id=int(command_id) // 1000,
            payload=biz_request.SerializeToString(),
            device_id=request_id
        )
        return frame.SerializeToString()

    async def get_history_messages(self, chat_id: str, count: int, cursor: str) -> feishu_im_pb2.GetMessagesResponse:
        if not chat_id:
            raise ValueError("Chat ID 不能为空。")

        url = f"{self.base_url}/im/gateway/"
        request_id = str(uuid.uuid4())
        
        get_messages_payload = feishu_im_pb2.GetMessagesRequest(
            chat_id=chat_id, count=count, cursor=cursor,
            scene=feishu_im_pb2.GetMessagesRequest.SCENE_CHAT
        ).SerializeToString()
        
        request_data = self._build_request_frame(get_messages_payload, request_id, self.history_command_id)
        
        headers = self.session.headers.copy()
        headers["x-command"] = self.history_command_id
        headers["x-request-id"] = request_id
        
        logging.info(f"准备请求历史消息, Chat ID: {chat_id}, Command: {headers['x-command']}")

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.session.post(url, headers=headers, data=request_data, timeout=15)
            )
            response.raise_for_status()

            frame_response = feishu_im_pb2.Frame()
            frame_response.ParseFromString(response.content)

            biz_response = feishu_im_pb2.BizResponse()
            biz_response.ParseFromString(frame_response.payload)

            if biz_response.code != 0:
                raise Exception(f"飞书 API 错误: Code={biz_response.code}, Message='{biz_response.message}'")

            response_pb = feishu_im_pb2.GetMessagesResponse()
            response_pb.ParseFromString(biz_response.payload)
            logging.info(f"成功获取 {len(response_pb.items)} 条历史消息。")
            return response_pb
        except Exception as e:
            logging.error(f"获取历史消息时发生错误: {e}")
            raise

    async def stream_latest_messages(self, chat_id: str) -> AsyncGenerator[feishu_im_pb2.Message, None]:
        if self.stream_command_id == self.history_command_id:
            logging.error("实时消息 Command ID 与历史消息 ID 相同，无法建立有效的实时监听。请使用新版脚本重新获取认证信息。")
            # 直接返回，不再尝试连接，避免无效循环
            return

        if not chat_id:
            raise ValueError("Chat ID 不能为空。")

        url = f"{self.base_url}/im/gateway/"
        
        logging.info(f"正在为 Chat ID: {chat_id} 追赶最新消息...")
        latest_timestamp = 0
        try:
            initial_response = await self.get_history_messages(chat_id, 1, "0")
            if initial_response.items:
                latest_timestamp = initial_response.items[0].create_time
                logging.info(f"追赶同步完成，最新消息时间戳: {latest_timestamp}")
        except Exception as e:
            logging.warning(f"追赶机制执行失败: {e}。将从当前时间开始接收。")

        logging.info(f"开始监听 Chat ID: {chat_id} 的实时消息 (Command: {self.stream_command_id})")
        
        empty_biz_payload = feishu_im_pb2.BizRequest().SerializeToString()
        
        while True:
            try:
                request_id = str(uuid.uuid4())
                headers = self.session.headers.copy()
                headers["x-command"] = self.stream_command_id
                headers["x-request-id"] = request_id

                request_data = self._build_request_frame(b'', request_id, self.stream_command_id)

                with self.session.post(url, headers=headers, data=request_data, timeout=60, stream=True) as response:
                    response.raise_for_status()
                    if response.content:
                        frame_response = feishu_im_pb2.Frame()
                        frame_response.ParseFromString(response.content)
                        
                        biz_response = feishu_im_pb2.BizResponse()
                        biz_response.ParseFromString(frame_response.payload)
                        
                        if biz_response.code != 0:
                            logging.warning(f"实时消息流收到非零状态码: Code={biz_response.code}, Message='{biz_response.message}'")
                            if biz_response.code in [401, 403]: 
                                logging.error("认证失败，中断连接。请更新认证信息。")
                                break
                            continue

                        if biz_response.payload:
                            stream_response_pb = feishu_im_pb2.StreamResponse()
                            stream_response_pb.ParseFromString(biz_response.payload)
                            
                            if stream_response_pb.new_messages:
                                new_messages = sorted(stream_response_pb.new_messages, key=lambda msg: msg.create_time)
                                for msg in new_messages:
                                    if msg.create_time > latest_timestamp:
                                        logging.info(f"收到新消息: {msg.message_id}")
                                        yield msg
                                        latest_timestamp = msg.create_time
            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.RequestException as e:
                logging.error(f"实时消息流网络连接中断: {e}。5秒后重试...")
                await asyncio.sleep(5)
            except Exception as e:
                logging.error(f"实时消息流处理异常: {e}。5秒后重试...")
                await asyncio.sleep(5)

def get_feishu_provider(
    cookie: Optional[str] = Header(None, alias="X-Feishu-Cookie"),
    history_cmd: Optional[str] = Header(None, alias="X-Cmd-History"),
    stream_cmd: Optional[str] = Header(None, alias="X-Cmd-Stream"),
    user_agent: Optional[str] = Header(None, alias="X-User-Agent"),
    referer: Optional[str] = Header(None, alias="X-Referer"),
    web_version: Optional[str] = Header(None, alias="X-Web-Version"),
    csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token"),
    lgw_csrf_token: Optional[str] = Header(None, alias="X-LGW-CSRF-Token")
) -> FeishuProvider:
    lgw_token_from_settings = settings._auth_data.get("lgw_csrf_token", "")
    return FeishuProvider(
        cookie=cookie or settings.FEISHU_COOKIE,
        history_cmd=history_cmd or settings.COMMAND_ID_HISTORY,
        stream_cmd=stream_cmd or settings.COMMAND_ID_STREAM,
        user_agent=user_agent or settings.USER_AGENT or settings.DEFAULT_USER_AGENT,
        referer=referer or settings.REFERER or settings.DEFAULT_REFERER,
        web_version=web_version or settings.FEISHU_WEB_VERSION,
        csrf_token=csrf_token or settings.CSRF_TOKEN,
        lgw_csrf_token=lgw_csrf_token or lgw_token_from_settings
    )
