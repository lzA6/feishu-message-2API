<div align="center">
  <img src="https://raw.githubusercontent.com/lzA6/feishu-message-2API/main/docs/logo.png" alt="Feishu Message Ark Logo" width="200"/>
  <h1>飞书消息方舟 (Feishu Message Ark)</h1>
  <p>
    <strong>一个能将任意飞书群聊消息，稳定转化为标准化 API 接口的终极解决方案。</strong>
  </p>
  <p>
    <a href="https://github.com/lzA6/feishu-message-2API"><img src="https://img.shields.io/github/stars/lzA6/feishu-message-2API?style=social" alt="GitHub Stars"></a>
    <a href="https://github.com/lzA6/feishu-message-2API/blob/main/LICENSE"><img src="https://img.shields.io/github/license/lzA6/feishu-message-2API" alt="License"></a>
    <a href="https://github.com/lzA6/feishu-message-2API/issues"><img src="https://img.shields.io/github/issues/lzA6/feishu-message-2API" alt="Issues"></a>
  </p>
</div>

---

> 🌌 **“信息是宇宙的熵减，而我们，是信息的摆渡人。”**
>
> 在数字化浪潮中，每一个群聊都是一个流淌着信息、知识与情感的星系。然而，这些宝贵的信息往往被禁锢在应用的孤岛里，无法自由流淌、碰撞出新的火花。**飞书消息方舟** 的诞生，就是为了打破这堵墙。我们相信，信息应该像水一样，能够被引导、被利用、被创造。这个项目不仅仅是代码，它是一种哲学：**赋予每个普通人掌控信息、实现自动化的能力，让创造力不再受限于工具。**

## ✨ 项目亮点与核心价值

*   **🚀 终极便利性**：提供一个美观、易用的 Web 操作界面，所有配置、监听、API生成都在网页上完成，告别繁琐的命令行。
*   **🔑 一键获取认证**：内置 `get_cookie.py` 自动化脚本，通过 `Playwright` 模拟浏览器操作，一键获取所有复杂的认证信息，小白用户也能轻松上手。
*   **🛡️ 健壮且稳定**：深度逆向飞书 Web 端 `Protobuf` 协议，而非简单的 `JSON` 抓包。这意味着即使前端接口变更，我们的核心逻辑依然稳如泰山。
*   **⚡️ 实时与历史兼得**：同时支持 `WebSocket` 实时消息流 和 `HTTP` 历史消息拉取，满足不同场景的全部需求。
*   **🎭 多身份管理**：首创“预设(Profile)”管理系统，你可以轻松切换不同账号、不同配置，同时监听多个群聊，互不干扰。
*   **🤖 AI 友好**：一键导出格式化的对话文本，无缝对接到 `ChatGPT`、`Kimi` 等大语言模型进行分析、总结。
*   **📦 Docker 一键部署**：提供 `docker-compose.yml`，一条命令即可启动整个服务，将复杂的环境依赖彻底封装。
*   **🔓 开源与开放**：采用 `Apache-2.0` 协议，鼓励二次开发、分享与创新，共同构建更强大的信息生态。

## 🎯 我们能做什么？—— 场景与需求

想象一下，当你的飞书群聊变成了一个 24 小时待命的机器人助手，你可以：

*   **建立信息归档库**：将重要的群聊记录永久保存到你自己的数据库中。
*   **创建关键词警报**：当群里提到“BUG”、“紧急”、“服务器宕机”时，自动给你发送电话、短信或 `Server酱` 通知。
*   **打造智能问答机器人**：将群聊内容接入 AI，自动回答新成员的常见问题。
*   **进行舆情分析**：对产品用户群的消息进行情感分析，量化用户反馈。
*   **同步信息到其他平台**：将飞书群的消息实时同步到 `Telegram`、`Discord` 或 `Slack`。
*   **...以及任何你能想到的自动化流程！**

---

## 🚀 懒人一键部署指南 (小白友好)

让我们一起，三步之内，发射你的“消息方舟”！

### 准备工作

请确保你的电脑已经安装了以下“三件套”：
1.  [Git](https://git-scm.com/downloads) - 用于下载代码。
2.  [Python 3.8+](https://www.python.org/downloads/) - 用于运行“一键获取认证”脚本。
3.  [Docker](https://www.docker.com/products/docker-desktop/) - 我们的“方舟”将运行在它之上。

### 第一步：克隆方舟本体

打开你的终端（命令行工具），找一个你喜欢的文件夹，运行：

```bash
git clone https://github.com/lzA6/feishu-message-2API.git
cd feishu-message-2API
```

### 第二步：配置你的专属密钥

我们提供了一个模板文件 `.env.example`。你需要复制一份并重命名为 `.env`。

```bash
# Windows 用户
copy .env.example .env

# macOS / Linux 用户
cp .env.example .env
```

然后，用记事本或任何文本编辑器打开这个新的 `.env` 文件，**强烈建议**修改 `API_MASTER_KEY` 为一个你自己知道的、足够复杂的密码。这是保护你 API 的“总钥匙”。

```dotenv
# .env
# ... 其他配置可以暂时不动 ...
API_MASTER_KEY="change-this-to-your-own-super-secret-password"
```

### 第三步：启动方舟！

在项目根目录（就是 `feishu-message-2API` 文件夹）下，运行 Docker Compose 命令：

```bash
docker-compose up -d --build
```

第一次启动会需要一些时间来构建镜像（就像造船一样）。当终端显示 `done` 时，恭喜你，你的方舟已经成功启航！

现在，打开浏览器，访问 `http://localhost:8008`，你应该能看到“飞书消息方舟”的界面了！

---

## 🧭 使用教程：驾驭你的方舟

### 1. 获取“航行许可证” (认证信息)

这是最关键的一步，但我们已经把它变成了全自动！

1.  在方舟的 Web 界面，点击右上角的 **设置** ⚙️ 图标。
2.  在弹出的窗口中，点击 **“一键获取”** 按钮，会弹出一个操作指南。
3.  **打开你的电脑终端**，确保你还在 `feishu-message-2API` 目录下，运行我们的“神器”脚本：

    ```bash
    # 首次运行前，请确保安装了依赖
    pip install -r requirements.txt
    playwright install

    # 运行神器
    python get_cookie.py
    ```
4.  脚本会自动打开一个**新的浏览器窗口**。请按照终端里的提示操作：
    a. **扫码登录**你的飞书。
    b. **点击进入**你想要监听的那个群聊。
    c. **关键一步**：进入群聊后，随便点点，比如**点击右上角的“群设置”**，或者**在群里发一条消息**。这能确保脚本捕获到所有必要的信息。
5.  当终端出现 `🎉🎉🎉 [完美成功]` 的提示时，说明所有信息都已捕获，并且**自动复制到了你的剪贴板**！现在你可以关闭那个浏览器窗口了。
6.  回到方舟的 Web 界面，在“飞书认证信息 (JSON)”的输入框里，**直接粘贴 (Ctrl+V)**。你会看到一大段 `JSON` 文本被填了进去。

### 2. 创建并保存你的第一个“预设”

1.  **预设名称**：给你这个配置起个名字，比如“公司技术交流群”。
2.  **API 密钥**：填入你在 `.env` 文件里设置的 `API_MASTER_KEY`。
3.  **Chat ID 列表**：`get_cookie.py` 脚本会自动把示例 Chat ID 加到认证信息里，我们的前端会自动提取并填入这里。你也可以手动把其他群的 ID 加进去，每行一个。
4.  点击 **“另存为新预设”**。

### 3. 开始监听！

保存后，设置窗口会自动关闭。你会看到左侧的会话列表出现了你的 Chat ID。

*   **点击一个 Chat ID**：右侧聊天窗口会立即加载最新的历史消息。
*   **观察状态灯**：右上角的状态指示灯如果变为 **绿色**，代表已经通过 `WebSocket` 连接成功，现在任何新消息都会被实时推送过来！

至此，你已经成功驾驭了方舟！你可以在“设置” -> “API 调用”中找到为你动态生成的 `Curl` 命令和 `WebSocket` 地址，把它们用到你自己的程序里去吧！

---

## 🧠 技术核心原理解析 (给爱钻研的你)

这个项目不是魔法，它是对技术细致入微的观察和实践。

<details>
<summary><strong>1. 核心通信协议：为什么是 Protobuf？ (★★★★★)</strong></summary>

*   **专业术语 (The What)**: Protocol Buffers (Protobuf) 是 Google 开发的一种语言无关、平台无关、可扩展的序列化结构化数据的方法，常用于通信协议、数据存储等。它比 XML、JSON 更小、更快、更简单。
*   **大白话 (The Why)**: 想象一下，JSON 就像是用白话文写信，谁都看得懂，但有点啰嗦。Protobuf 就像是军队里的加密电报，它把信息（比如谁、在哪个群、发了什么）压缩成一种非常紧凑的二进制格式。飞书的 Web 端和服务器之间传递核心消息数据时，用的就是这种“电报”。
*   **我们的做法**: 我们没有满足于抓取浏览器开发者工具里看到的那些零散的 JSON 接口，而是直接深入到网络传输的二进制层面。通过分析 `feishu_im.proto` 文件，我们精确地定义了飞书消息的“电报”格式。`feishu_provider.py` 中的 `_build_request_frame` 方法就是一个“电报打包机”，它把我们的请求（比如“给我10条历史消息”）打包成飞书服务器能听懂的二进制格式。
*   **这样做的好处**: 这让我们的项目异常稳定。因为这种底层的二进制协议极少变动，远比上层的业务 API 稳定得多。**这是一种“降维打击”，我们在更基础的层面与飞书对话。**

</details>

<details>
<summary><strong>2. 双命令通道：`cmd_history` vs `cmd_stream` (★★★★☆)</strong></summary>

*   **现象观察**: 在逆向分析时，我们发现飞书的 `/im/gateway/` 接口很有趣。拉取历史消息和建立实时长连接，虽然是同一个 URL，但它们 HTTP Header 里的 `x-command` ID 是不同的。
*   **大胆猜测**:
    *   `cmd_history` (如 `1011741`)：这是一个“请求-响应”式的命令。客户端发送一个带有具体参数（要哪个群、要多少条）的请求包，服务器返回一个包含消息列表的响应包。
    *   `cmd_stream` (如 `1103941`)：这是一个“订阅-推送”式的命令。客户端发送一个近乎空的请求，告诉服务器“我要开始听这个群了”，然后服务器会保持这个连接不断开 (长轮询)，一旦有新消息，就主动把消息“推”给客户端。
*   **智能区分**: `get_cookie.py` 脚本通过一个巧妙的启发式规则来自动区分这两个 ID：通常，发送数据包 (`post_data`) 的是拉取历史的请求，而发送空包的是建立长连接的请求。这大大降低了用户手动配置的难度。

</details>

<details>
<summary><strong>3. 全自动化认证：Playwright 的魔法 (★★★★☆)</strong></summary>

*   **痛点**: 飞书的认证信息非常复杂，包含 `Cookie`、`User-Agent`、多个 `CSRF-Token`、`Web-Version` 等一大堆动态生成的 Headers。手动去浏览器里一点点复制粘贴，不仅痛苦，而且容易出错。
*   **解决方案**: 我们使用 `Playwright` 这个强大的浏览器自动化工具。`get_cookie.py` 脚本启动一个真实的浏览器，你像正常人一样登录操作，`Playwright` 就在后台默默地监听所有的网络请求，像一个敬业的侦探，把所有我们需要的信息都记录下来。
*   **用户体验 (UX)**: 这将一个原本需要10分钟、充满技术细节的繁琐任务，变成了一个只需1分钟、几乎无需动脑的简单流程。**好的技术，就应该让人感觉不到技术本身的存在。**

</details>

<details>
<summary><strong>4. 前后端架构：FastAPI + Vanilla JS (★★★☆☆)</strong></summary>

*   **后端 (Backend)**: 选用 `FastAPI` 框架。
    *   **优点**: 性能极高 (基于 `asyncio`)；代码优雅简洁；自动生成交互式 API 文档 (虽然本项目没用到，但潜力巨大)；非常适合构建 API 服务。
    *   **逻辑分层**: `main.py` 负责定义 API 路由（URL路径），`feishu_provider.py` 负责处理所有与飞书服务器打交道的脏活累活，`config.py` 负责管理配置。结构清晰，易于维护。
*   **前端 (Frontend)**: 选用原生 `JavaScript`、`HTML`、`CSS` (常被称为 `Vanilla JS`)。
    *   **优点**: **零依赖，无编译！** 这意味着项目非常轻量，不需要 `Node.js`、`Webpack` 等复杂的前端工程化工具。克隆下来就能直接用，极大降低了贡献和二次开发的门槛。
    *   **组件化思想**: 尽管是原生 JS，但 `script.js` 中通过 `elements` 对象和一系列函数，实现了功能的模块化，代码并不混乱。

</details>

---

## 🏗️ 项目文件结构一览

```
feishu-message-2API/
├── app/
│   ├── public/
│   │   ├── index.html       # 网页主界面
│   │   ├── script.js        # 前端核心交互逻辑
│   │   └── style.css        # 界面样式
│   ├── config.py            # 配置加载模块
│   ├── feishu_im.proto      # Protobuf 消息定义文件 (核心)
│   ├── feishu_im_pb2.py     # 由 .proto 文件编译生成的 Python 代码
│   ├── feishu_provider.py   # 封装了所有与飞书服务器通信的逻辑
│   ├── logging_config.py    # 日志配置
│   └── main.py              # FastAPI 应用主入口，定义 API 接口
├── .env                     # 你的本地配置文件 (由 .env.example 复制而来)
├── .env.example             # 配置文件模板
├── docker-compose.yml       # Docker 一键部署编排文件
├── Dockerfile               # Docker 镜像构建文件
├── get_cookie.py            # 一键获取认证信息的自动化脚本
├── LICENSE                  # Apache 2.0 开源许可证
├── nginx.conf               # Nginx 配置文件，用于反向代理
├── README.md                # 就是你正在看的这个文件
└── requirements.txt         # Python 依赖库列表
```

---

## 🗺️ 未来蓝图与改进方向

我们深知，任何伟大的作品都始于一个不完美的初版。方舟已经启航，但星辰大海的征途才刚刚开始。

### 💔 当前的不足与待办 (TODO)

*   **功能欠缺**:
    *   [ ] **发送消息**：目前只能接收，实现发送功能将解锁更多互动玩法。
    *   [ ] **富媒体支持**：暂不支持图片、文件、表情等消息的解析。
    *   [ ] **历史消息分页**：尚未在前端实现加载更多历史消息的功能。
*   **技术待完善**:
    *   [ ] **认证持久化**：`Cookie` 等信息会过期，尚未实现自动续期或刷新机制。
    *   [ ] **错误处理**：可以对飞书返回的更多错误码进行精细化处理和提示。
    *   [ ] **数据库集成**：目前消息是易失的，集成一个轻量级数据库 (如 `SQLite`) 进行持久化存储会很有价值。
*   **体验待优化**:
    *   [ ] **前端框架**：未来若功能复杂化，可以考虑引入 `Vue` 或 `React` 来提升开发效率和体验。
    *   [ ] **国际化 (i18n)**：为界面提供多语言支持。

### ✨ 未来可能的扩展方向

*   **插件化架构**：建立一个插件系统，用户可以轻松编写自己的插件来处理消息（例如，`telegram_bot.py`, `discord_webhook.py`），实现真正的“开箱即用”。
*   **多协议支持**：除了 `Protobuf`，研究并支持飞书的其他通信方式，如移动端的协议，增强兼容性。
*   **可视化数据分析**：在 Web 界面内置一个简单的仪表盘，对群聊活跃度、关键词频率等进行可视化分析。
*   **提供公共服务**：探索在合规前提下，为非技术用户提供一个公共的、多租户的“消息方舟”服务的可能性。

我们热切地欢迎每一位开发者参与进来，无论是提交一个 `Issue`、修复一个 `BUG`，还是实现一个新功能，你的每一次贡献，都在为这艘方舟增添动力！

---

## 📜 开源协议

本项⽬采⽤ **Apache License 2.0** 开源许可证。

这意味着你可以自由地：
*   **商业化使用**：你可以在自己的产品中免费使用本项目的代码。
*   **修改**：你可以对代码进行任意修改。
*   **分发**：你可以自由地分发原始或修改后的代码。
*   **私有使用**：你可以将代码用于个人目的而无需开源。

唯一的限制是，你需要在你的项目中包含原始的许可证声明。

---

<div align="center">
  <strong>“我们不是在编写代码，我们是在构建连接未来的桥梁。”</strong><br>
  <strong>感谢你的阅读，期待与你一同远航！</strong><br>
  <a href="https://github.com/lzA6/feishu-message-2API">🌟 Star us on GitHub! 🌟</a>
</div>
