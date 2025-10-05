# get_cookie.py (v8.0 - 智能区分Command ID版)
import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext, Error as PlaywrightError
import os
import sys
import json
import re
import shutil

try:
    import pyperclip
except ImportError:
    print("\n[错误] pyperclip 模块未安装。请运行: pip install pyperclip")
    sys.exit(1)

# --- 配置 ---
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "playwright_user_data")

# --- 全局状态 ---
captured_data = {
    "cookie": "尚未捕获",
    "user_agent": "尚未捕获",
    "referer": "尚未捕获",
    "csrf_token": "尚未捕获",
    "lgw_csrf_token": "尚未捕获",
    "web_version": "尚未捕获",
    "cmd_history": "尚未捕获",
    "cmd_stream": "尚未捕获", # 明确区分
    "example_chat_id": "尚未捕获",
}

# 用于存储所有可能包含Chat ID的响应体
response_bodies = []
# 用于记录所有捕获到的 gateway command
gateway_commands = set()

def print_separator(char='-'):
    print(char * 100)

async def handle_response(response):
    """记录所有来自飞书API的响应体"""
    if "feishu.cn" in response.url:
        try:
            body = await response.body()
            if body:
                response_bodies.append(body)
        except (PlaywrightError, Exception):
            pass

async def handle_route(route):
    """捕获Header信息和Command ID"""
    request = route.request
    try:
        headers = await request.all_headers()
        
        if headers.get('cookie') and len(headers['cookie']) > len(captured_data.get("cookie", "")):
            captured_data["cookie"] = headers['cookie']

        headers_to_capture = {
            'user-agent': 'user_agent', 'referer': 'referer', 'x-csrf-token': 'csrf_token',
            'x-lgw-csrf-token': 'lgw_csrf_token', 'x-web-version': 'web_version'
        }
        for header_key, data_key in headers_to_capture.items():
            if headers.get(header_key) and "尚未" in str(captured_data.get(data_key)):
                captured_data[data_key] = headers[header_key]

        # --- 核心修正：智能区分 Command ID ---
        if "/im/gateway/" in request.url:
            command_id = headers.get('x-command')
            if command_id:
                gateway_commands.add(command_id)
                # 通常，有 post_data 的是拉取历史记录的请求
                if request.post_data_buffer and "尚未" in captured_data["cmd_history"]:
                    captured_data["cmd_history"] = command_id
                # 通常，没有 post_data 的是建立长连接、监听实时消息的请求
                elif not request.post_data_buffer and "尚未" in captured_data["cmd_stream"]:
                    captured_data["cmd_stream"] = command_id
        
        await route.continue_()
    except (PlaywrightError, Exception):
        if not route.is_handled():
            try:
                await route.abort()
            except PlaywrightError:
                pass

async def run_browser_tasks():
    """运行浏览器并记录所有网络活动"""
    async with async_playwright() as p:
        context: BrowserContext = None
        try:
            print(">>> 正在启动浏览器...")
            if os.path.exists(USER_DATA_DIR):
                shutil.rmtree(USER_DATA_DIR, ignore_errors=True)
                print(">>> 已清理旧的浏览器会话数据。")

            context = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                args=['--start-maximized'],
                no_viewport=True,
            )
            
            page = context.pages[0] if context.pages else await context.new_page()
            
            print(">>> 正在设置网络记录器...")
            page.on("response", handle_response)
            await page.route("**/*", handle_route)

            print(">>> 正在导航至飞书...")
            await page.goto("https://www.feishu.cn/messenger", timeout=90000, wait_until="domcontentloaded")

            print_separator('*')
            print("✅ 浏览器窗口已打开。请按以下步骤操作：")
            print("1. 【必须】在浏览器中完成扫码登录。")
            print("2. 【必须】登录后，点击进入您想监听的群聊。")
            print("3. 【关键】进入群聊后，请进行一些操作，例如【点击右上角的群设置】。")
            print("4. 【新增关键步骤】为了捕获实时消息ID，请【在群里发送一条消息】或等待别人发消息。")
            print("\n✅ 完成所有操作后，请回到本窗口，按【Ctrl + C】结束捕获。")
            print_separator('*')

            await asyncio.Event().wait()

        except (asyncio.CancelledError, KeyboardInterrupt):
             print("\n[信息] 检测到手动中断 (Ctrl+C)，即将开始分析数据...")
        except PlaywrightError as e:
            if "Target page, context or browser has been closed" not in str(e):
                 print(f"\n❌ 浏览器操作期间发生错误: {e}")
        finally:
            if context and not context.is_closed():
                await context.close()

def analyze_and_finalize():
    """在所有记录的数据中分析并提取最终信息"""
    print("\n>>> 正在分析已记录的网络数据...")
    
    # 如果智能区分失败，进行补救
    if "尚未" in captured_data["cmd_history"] and len(gateway_commands) > 0:
        captured_data["cmd_history"] = sorted(list(gateway_commands))[0]
    if "尚未" in captured_data["cmd_stream"] and len(gateway_commands) > 0:
        # 如果只有一个，就都用它
        if len(gateway_commands) == 1:
            captured_data["cmd_stream"] = list(gateway_commands)[0]
        # 如果有多个，通常 stream 的 ID 更大
        else:
            captured_data["cmd_stream"] = sorted(list(gateway_commands))[-1]

    # 从后往前分析，找到最后一个出现的Chat ID
    for body in reversed(response_bodies):
        match = re.search(b'(oc_[a-zA-Z0-9]{32})|(om_[a-zA-Z0-9]{32})|(?<=[\\\\"\'`])(7[0-9]{18})(?=[\\\\"\'`])', body)
        if match:
            chat_id_bytes = match.group(1) or match.group(2) or match.group(3)
            if chat_id_bytes:
                chat_id = chat_id_bytes.decode('utf-8')
                captured_data["example_chat_id"] = chat_id
                print(f"✅ [分析成功] 已找到您最后操作的 Chat ID: {chat_id}")
                break
    
    final_data = {k: v for k, v in captured_data.items() if "尚未" not in str(v)}
    
    print_separator('📊')
    print("📊 [最终捕获信息总览]")
    for key, value in captured_data.items():
        status = "✅" if key in final_data else "❌"
        display_value = str(value)
        if len(display_value) > 70:
            display_value = display_value[:67] + "..."
        print(f"  {status} {key:<20}: {display_value}")
    print_separator('📊')

    if "cookie" in final_data and "example_chat_id" in final_data and "cmd_history" in final_data and "cmd_stream" in final_data:
        output_json = json.dumps(final_data, indent=2, ensure_ascii=False)
        try:
            pyperclip.copy(output_json)
            print("\n✅ 认证信息 JSON 已自动复制到您的剪贴板！")
        except Exception as e:
            print(f"\n⚠️ 自动复制到剪贴板失败: {e}")
        
        print("\n--- 请将下方完整内容粘贴到 Web UI 的【飞书认证信息】输入框中 ---")
        print(output_json)
        print("---")
    else:
        print("\n❌ [失败] 未能捕获到足够的核心信息 (特别是 cmd_stream)。")
        print("   请确保您已成功登录、进入群聊，并【发送或接收了一条消息】。")

    if os.path.exists(USER_DATA_DIR):
        shutil.rmtree(USER_DATA_DIR, ignore_errors=True)
        print(f"\n✅ 已自动清理临时文件夹: {USER_DATA_DIR}")
    
    input("\n按 Enter 键退出...")

if __name__ == "__main__":
    try:
        asyncio.run(run_browser_tasks())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        analyze_and_finalize()
