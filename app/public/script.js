// public/script.js (v9.2 - 体验优化版)
document.addEventListener("DOMContentLoaded", () => {
    const elements = {
        authInfoInput: document.getElementById("auth-info-input"),
        messagesContainer: document.getElementById("chat-messages"),
        chatIdInput: document.getElementById("chat-id-input"),
        chatList: document.getElementById("chat-list"),
        sidebarTitle: document.getElementById("sidebar-title"),
        statusIndicator: document.getElementById("status-indicator"),
        currentChatTitle: document.getElementById("current-chat-title"),
        settingsBtn: document.getElementById("settings-btn"),
        modal: document.getElementById("settings-modal"),
        closeBtn: document.querySelector(".close-btn"),
        profileSelect: document.getElementById("profile-select"),
        deleteProfileBtn: document.getElementById("delete-profile-btn"),
        profileNameInput: document.getElementById("profile-name-input"),
        apiKeyInput: document.getElementById("api-key-input"),
        getCookieBtn: document.getElementById("get-cookie-btn"),
        cookieHelperModal: document.getElementById("cookie-helper-modal"),
        closeCookieHelper: document.querySelector(".close-cookie-helper"),
        chatIdsInput: document.getElementById("chat-ids-input"),
        saveProfileBtn: document.getElementById("save-profile-btn"),
        saveAsNewProfileBtn: document.getElementById("save-as-new-profile-btn"),
        importProfilesBtn: document.getElementById("import-profiles-btn"),
        exportProfileBtn: document.getElementById("export-profile-btn"),
        exportAllProfilesBtn: document.getElementById("export-all-profiles-btn"),
        importFileInput: document.getElementById("import-file-input"),
        curlHistoryOutput: document.getElementById("curl-history-output"),
        wsUrlOutput: document.getElementById("ws-url-output"),
        exportBtn: document.getElementById("export-btn"),
        exportContext: document.getElementById("export-context"),
        exportOutput: document.getElementById("export-output"),
        exportCountInput: document.getElementById("export-count-input"),
        curlAnalysisOutput: document.getElementById("curl-analysis-output"),
    };

    let state = {
        ws: null,
        currentChatId: null,
        profiles: JSON.parse(localStorage.getItem("feishuProfiles")) || {},
        activeProfileId: localStorage.getItem("activeProfileId") || null,
    };

    function appendMessage(data) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        const avatarUrl = data.sender?.avatar_url || `https://api.multiavatar.com/${data.sender?.id || 'system'}.svg`;
        const senderName = data.sender?.name || '系统消息';
        const content = data.content || '';
        if (senderName === '系统消息' || senderName === '系统错误') {
            messageElement.classList.add('system-message');
        }
        const time = data.create_time ? new Date(data.create_time).toLocaleTimeString() : '';
        messageElement.innerHTML = `<img src="${avatarUrl}" alt="avatar" class="avatar"><div class="message-content"><div class="sender-name">${senderName} <span style="color:#999; font-weight:normal;">${time}</span></div><div class="text">${content.replace(/\n/g, '<br>')}</div></div>`;
        elements.messagesContainer.insertBefore(messageElement, elements.messagesContainer.firstChild);
    }

    function renderChatHistory() {
        elements.chatList.innerHTML = "";
        if (!state.activeProfileId) return;
        const profile = state.profiles[state.activeProfileId];
        if (!profile || !profile.chatIds) return;

        profile.chatIds.forEach(chatId => {
            const li = document.createElement("li");
            li.textContent = chatId;
            li.dataset.chatId = chatId;
            if (chatId === state.currentChatId) li.classList.add("active");
            li.addEventListener("click", () => switchChat(chatId));
            elements.chatList.appendChild(li);
        });
    }

    function getAuthFromProfile(profile) {
        if (!profile || !profile.authInfo) return {};
        try {
            return JSON.parse(profile.authInfo);
        } catch (e) {
            console.error("解析认证信息失败:", e);
            return {};
        }
    }

    function updateApiUrlGenerators() {
        const baseUrl = `${window.location.protocol}//${window.location.host}`;
        const activeProfile = state.activeProfileId ? state.profiles[state.activeProfileId] : null;
        if (!activeProfile) return;
        const auth = getAuthFromProfile(activeProfile);
        
        if (state.currentChatId && activeProfile.apiKey && auth.cookie) {
            const headers = {
                "Authorization": `Bearer ${activeProfile.apiKey}`,
                "X-Feishu-Cookie": auth.cookie,
                "X-Cmd-History": auth.cmd_history,
                "X-User-Agent": auth.user_agent,
                "X-Referer": auth.referer,
                "X-Web-Version": auth.web_version,
                ...(auth.csrf_token && {"X-CSRF-Token": auth.csrf_token}),
                ...(auth.lgw_csrf_token && {"X-LGW-CSRF-Token": auth.lgw_csrf_token})
            };
            
            let curlHistory = `curl -X POST "${baseUrl}/api/v1/chat/messages?chat_id=${state.currentChatId}"`;
            for (const [key, value] of Object.entries(headers)) {
                curlHistory += ` \\\n-H "${key}: ${value}"`;
            }
            elements.curlHistoryOutput.value = curlHistory;
            
            const queryParams = new URLSearchParams({
                token: activeProfile.apiKey,
                cookie: auth.cookie,
                cmd_history: auth.cmd_history,
                cmd_stream: auth.cmd_stream || auth.cmd_history, // Fallback
                user_agent: auth.user_agent,
                referer: auth.referer,
                web_version: auth.web_version,
            });
            if (auth.csrf_token) queryParams.append('csrf_token', auth.csrf_token);
            if (auth.lgw_csrf_token) queryParams.append('lgw_csrf_token', auth.lgw_csrf_token);
            elements.wsUrlOutput.value = `${window.location.protocol === 'https:' ? 'wss://' : 'ws://'}${window.location.host}/ws/v1/chat/stream/${state.currentChatId}?${queryParams.toString()}`;

            let curlAnalysis = `curl -X POST "${baseUrl}/api/v1/chat/export_for_analysis?chat_id=${state.currentChatId}&count=${elements.exportCountInput.value}"`;
            for (const [key, value] of Object.entries(headers)) {
                curlAnalysis += ` \\\n-H "${key}: ${value}"`;
            }
            elements.curlAnalysisOutput.value = curlAnalysis;
        } else {
            const placeholder = "请先选择一个会话并配置一个有效的预设。";
            elements.curlHistoryOutput.value = placeholder;
            elements.wsUrlOutput.value = placeholder;
            elements.curlAnalysisOutput.value = placeholder;
        }
    }

    async function fetchHistory(chatId) {
        const activeProfile = state.profiles[state.activeProfileId];
        if (!activeProfile) return;
        const auth = getAuthFromProfile(activeProfile);
        if (!activeProfile.apiKey || !auth.cookie) return;
        
        try {
            const headers = {
                'Authorization': `Bearer ${activeProfile.apiKey}`,
                'X-Feishu-Cookie': auth.cookie,
                'X-Cmd-History': auth.cmd_history,
                'X-User-Agent': auth.user_agent,
                'X-Referer': auth.referer,
                'X-Web-Version': auth.web_version,
            };
            if (auth.csrf_token) headers['X-CSRF-Token'] = auth.csrf_token;
            if (auth.lgw_csrf_token) headers['X-LGW-CSRF-Token'] = auth.lgw_csrf_token;

            const response = await fetch(`/api/v1/chat/messages?chat_id=${chatId}`, { method: 'POST', headers });
            const responseText = await response.text();
            if (!response.ok) {
                 const errorData = JSON.parse(responseText);
                 throw new Error(`HTTP ${response.status}: ${errorData.detail}`);
            }
            const data = JSON.parse(responseText);
            data.messages.reverse().forEach(appendMessage);
        } catch (error) {
            appendMessage({ content: `获取历史消息失败: ${error.message}`, sender: { name: "系统错误" } });
        }
    }

    function connectWebSocket(chatId) {
        if (state.ws) state.ws.close();
        const activeProfile = state.profiles[state.activeProfileId];
        if (!activeProfile) return;
        const auth = getAuthFromProfile(activeProfile);

        const streamCmd = auth.cmd_stream || auth.cmd_history; // 使用历史记录ID作为备用

        if (!activeProfile.apiKey || !auth.cookie || !streamCmd || !auth.user_agent || !auth.referer || !auth.web_version) {
            appendMessage({ content: "当前预设认证信息不完整！请确保核心信息都已通过脚本获取并填充。", sender: { name: "系统提示" } });
            return;
        }

        const queryParams = new URLSearchParams({
            token: activeProfile.apiKey,
            cookie: auth.cookie,
            cmd_history: auth.cmd_history,
            cmd_stream: streamCmd,
            user_agent: auth.user_agent,
            referer: auth.referer,
            web_version: auth.web_version,
        });
        if (auth.csrf_token) queryParams.append('csrf_token', auth.csrf_token);
        if (auth.lgw_csrf_token) queryParams.append('lgw_csrf_token', auth.lgw_csrf_token);
        
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const finalWsUrl = `${wsProtocol}${window.location.host}/ws/v1/chat/stream/${chatId}?${queryParams.toString()}`;
        state.ws = new WebSocket(finalWsUrl);

        state.ws.onopen = () => {
            elements.statusIndicator.classList.add("connected");
            appendMessage({ content: "连接成功！正在等待实时消息...", sender: { name: "系统提示" } });
        };
        state.ws.onmessage = (event) => appendMessage(JSON.parse(event.data));
        state.ws.onclose = (event) => {
            elements.statusIndicator.classList.remove("connected");
            if (state.currentChatId === chatId) {
                appendMessage({ content: `连接已断开: ${event.reason || '未知原因'}`, sender: { name: "系统提示" } });
            }
        };
        state.ws.onerror = (error) => console.error("WebSocket 错误:", error);
    }

    function switchChat(chatId) {
        if (!state.activeProfileId) {
            alert("请先在设置中创建或选择一个预设！");
            elements.modal.style.display = "block";
            return;
        }
        if (state.currentChatId === chatId && state.ws && state.ws.readyState === WebSocket.OPEN) return;
        
        state.currentChatId = chatId;
        localStorage.setItem(`lastActiveChatId_${state.activeProfileId}`, chatId);
        
        elements.currentChatTitle.textContent = `正在监听: ${chatId}`;
        elements.messagesContainer.innerHTML = "";
        renderChatHistory();
        updateApiUrlGenerators();
        
        fetchHistory(chatId);
        connectWebSocket(chatId);
    }

    function clearProfileInputs() {
        elements.profileNameInput.value = "";
        elements.apiKeyInput.value = "";
        elements.authInfoInput.value = "";
        elements.chatIdsInput.value = "";
        elements.sidebarTitle.textContent = "会话列表";
    }

    function renderProfileList() {
        elements.profileSelect.innerHTML = "";
        const profileIds = Object.keys(state.profiles);
        if (profileIds.length === 0) {
            elements.profileSelect.add(new Option("请创建新预设...", ""));
            state.activeProfileId = null;
        } else {
            profileIds.forEach(id => {
                elements.profileSelect.add(new Option(state.profiles[id].name, id));
            });
            if (!state.activeProfileId || !state.profiles[state.activeProfileId]) {
                state.activeProfileId = profileIds[0];
            }
            elements.profileSelect.value = state.activeProfileId;
        }
        localStorage.setItem("activeProfileId", state.activeProfileId || "");
    }

    // --- 核心优化函数 ---
    function handleAuthInfoPaste(event) {
        try {
            const pastedData = (event.clipboardData || window.clipboardData).getData('text');
            const jsonData = JSON.parse(pastedData);
            
            // 1. 验证核心字段
            if (jsonData.cookie && jsonData.user_agent && jsonData.referer && jsonData.cmd_history && jsonData.web_version) {
                event.preventDefault(); // 阻止默认的粘贴行为
                
                // 2. 格式化并填充认证信息JSON
                elements.authInfoInput.value = JSON.stringify(jsonData, null, 2);
                
                let alertMessage = "已成功解析并填充认证信息！";

                // 3. 【您的优化建议】自动填充 Chat ID
                if (jsonData.example_chat_id) {
                    const existingChatIds = elements.chatIdsInput.value.split('\n').map(id => id.trim()).filter(Boolean);
                    if (!existingChatIds.includes(jsonData.example_chat_id)) {
                        elements.chatIdsInput.value = jsonData.example_chat_id + '\n' + existingChatIds.join('\n');
                        alertMessage += `\n\n示例 Chat ID "${jsonData.example_chat_id}" 已自动为您添加到列表中！`;
                    }
                }
                
                alert(alertMessage + "\n\n请继续填写预设名称和API密钥后保存。");
            }
        } catch (e) { 
            // 如果粘贴的不是有效的JSON，则忽略，不执行任何操作
        }
    }

    function loadProfile(profileId) {
        const profile = state.profiles[profileId];
        if (!profile) {
            clearProfileInputs();
            renderChatHistory();
            return;
        }
        elements.profileNameInput.value = profile.name;
        elements.apiKeyInput.value = profile.apiKey;
        elements.authInfoInput.value = profile.authInfo || "";
        elements.chatIdsInput.value = (profile.chatIds || []).join('\n');
        
        state.activeProfileId = profileId;
        localStorage.setItem("activeProfileId", profileId);
        if (elements.profileSelect.value !== profileId) {
            elements.profileSelect.value = profileId;
        }
        
        elements.sidebarTitle.textContent = `${profile.name} - 会话列表`;
        renderChatHistory();
        
        const lastChatId = localStorage.getItem(`lastActiveChatId_${profileId}`);
        const firstChatId = profile.chatIds && profile.chatIds[0] ? profile.chatIds[0] : null;
        const chatIdToLoad = (lastChatId && profile.chatIds.includes(lastChatId)) ? lastChatId : firstChatId;

        if (chatIdToLoad) {
            switchChat(chatIdToLoad);
        } else {
            state.currentChatId = null;
            if (state.ws) state.ws.close();
            elements.currentChatTitle.textContent = "未选择会话";
            elements.messagesContainer.innerHTML = '<div class="message system-message">当前预设没有会话，请在左侧输入框添加一个新的 Chat ID。</div>';
            updateApiUrlGenerators();
        }
    }

    function loadActiveProfile() {
        if (state.activeProfileId && state.profiles[state.activeProfileId]) {
            loadProfile(state.activeProfileId);
        } else if (Object.keys(state.profiles).length > 0) {
            loadProfile(Object.keys(state.profiles)[0]);
        } else {
            clearProfileInputs();
            renderChatHistory();
        }
    }

    function saveCurrentProfile(isNew = false) {
        const name = elements.profileNameInput.value.trim();
        if (!name) { alert("预设名称不能为空！"); return; }
        
        const authInfo = elements.authInfoInput.value.trim();
        try {
            const parsedAuth = JSON.parse(authInfo);
            // 放宽校验，不再强制要求 cmd_stream
            if (!parsedAuth.cookie || !parsedAuth.user_agent || !parsedAuth.referer || !parsedAuth.cmd_history || !parsedAuth.web_version) {
                alert("认证信息JSON不完整！请确保至少包含 cookie, user_agent, referer, cmd_history, web_version。");
                return;
            }
        } catch (e) {
            alert("认证信息不是有效的JSON格式！");
            return;
        }

        let profileId = isNew ? Date.now().toString() : state.activeProfileId;
        if (!profileId) profileId = Date.now().toString();

        const chatIds = elements.chatIdsInput.value.split('\n').map(id => id.trim()).filter(Boolean);

        state.profiles[profileId] = {
            name: name,
            apiKey: elements.apiKeyInput.value.trim(),
            authInfo: authInfo,
            chatIds: chatIds,
        };
        state.activeProfileId = profileId;
        
        localStorage.setItem("feishuProfiles", JSON.stringify(state.profiles));
        localStorage.setItem("activeProfileId", state.activeProfileId);
        
        renderProfileList();
        alert(`预设 "${name}" 已保存！`);
        
        loadActiveProfile();
        elements.modal.style.display = "none";
    }
    
    function deleteActiveProfile() {
        if (!state.activeProfileId) { alert("没有选中的预设可删除。"); return; }
        if (confirm(`确定要删除预设 "${state.profiles[state.activeProfileId].name}" 吗？`)) {
            delete state.profiles[state.activeProfileId];
            localStorage.removeItem(`lastActiveChatId_${state.activeProfileId}`);
            localStorage.setItem("feishuProfiles", JSON.stringify(state.profiles));
            state.activeProfileId = null;
            renderProfileList();
            loadActiveProfile();
        }
    }

    function exportProfiles(all = false) {
        if (!all && !state.activeProfileId) { alert("没有选中的预设可导出。"); return; }
        const data = all ? state.profiles : { [state.activeProfileId]: state.profiles[state.activeProfileId] };
        const profileName = all ? 'all_profiles' : state.profiles[state.activeProfileId].name.replace(/\s/g, '_');
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `feishu_ark_profiles_${profileName}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    function importProfiles() {
        const file = elements.importFileInput.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const importedProfiles = JSON.parse(event.target.result);
                if (typeof importedProfiles !== 'object' || importedProfiles === null) throw new Error("无效的JSON格式");
                let importedCount = 0;
                for (const id in importedProfiles) {
                    if (importedProfiles.hasOwnProperty(id) && importedProfiles[id].name) {
                        state.profiles[id] = importedProfiles[id];
                        importedCount++;
                    }
                }
                localStorage.setItem("feishuProfiles", JSON.stringify(state.profiles));
                renderProfileList();
                loadActiveProfile();
                alert(`成功导入 ${importedCount} 个预设！`);
            } catch (e) {
                alert(`导入失败: ${e.message}`);
            }
        };
        reader.readAsText(file);
    }

    async function exportForAnalysis() {
        const activeProfile = state.profiles[state.activeProfileId];
        if (!activeProfile) { alert("请先选择一个预设。"); return; }
        const auth = getAuthFromProfile(activeProfile);
        if (!state.currentChatId || !activeProfile.apiKey || !auth.cookie) {
            alert("请先选择一个会话并配置一个有效的预设。");
            return;
        }
        
        elements.exportOutput.value = "正在导出，请稍候...";
        elements.exportContext.textContent = "正在请求...";
        elements.exportBtn.disabled = true;
        const count = elements.exportCountInput.value;

        try {
            const headers = {
                'Authorization': `Bearer ${activeProfile.apiKey}`,
                'X-Feishu-Cookie': auth.cookie,
                'X-Cmd-History': auth.cmd_history,
                'X-User-Agent': auth.user_agent,
                'X-Referer': auth.referer,
                'X-Web-Version': auth.web_version,
            };
            if (auth.csrf_token) headers['X-CSRF-Token'] = auth.csrf_token;
            if (auth.lgw_csrf_token) headers['X-LGW-CSRF-Token'] = auth.lgw_csrf_token;

            const response = await fetch(`/api/v1/chat/export_for_analysis?chat_id=${state.currentChatId}&count=${count}`, { method: 'POST', headers });
            const responseText = await response.text();
            if (!response.ok) {
                const errorData = JSON.parse(responseText);
                throw new Error(`HTTP ${response.status}: ${errorData.detail}`);
            }
            const data = JSON.parse(responseText);
            elements.exportOutput.value = data.analysis_text;
            elements.exportContext.textContent = `${data.start_info}，${data.end_info}。共导出 ${data.message_count} 条有效消息。`;
        } catch (error) {
            elements.exportOutput.value = `导出失败: ${error.message}`;
            elements.exportContext.textContent = "导出时发生错误。";
        } finally {
            elements.exportBtn.disabled = false;
        }
    }

    elements.authInfoInput.addEventListener('paste', handleAuthInfoPaste);
    
    elements.chatIdInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            const newChatId = elements.chatIdInput.value.trim();
            if (newChatId && state.activeProfileId) {
                const profile = state.profiles[state.activeProfileId];
                if (!profile.chatIds.includes(newChatId)) {
                    profile.chatIds.unshift(newChatId);
                    elements.chatIdsInput.value = profile.chatIds.join('\n');
                    state.profiles[state.activeProfileId] = profile;
                    localStorage.setItem("feishuProfiles", JSON.stringify(state.profiles));
                    renderChatHistory();
                    switchChat(newChatId);
                }
                elements.chatIdInput.value = "";
            } else {
                alert("请先选择或创建一个预设！");
            }
        }
    });

    elements.settingsBtn.onclick = () => elements.modal.style.display = "block";
    elements.closeBtn.onclick = () => elements.modal.style.display = "none";
    window.onclick = (event) => { if (event.target == elements.modal) elements.modal.style.display = "none"; };
    
    elements.profileSelect.addEventListener("change", (e) => loadProfile(e.target.value));
    elements.saveProfileBtn.addEventListener("click", () => saveCurrentProfile(false));
    elements.saveAsNewProfileBtn.addEventListener("click", () => saveCurrentProfile(true));
    elements.deleteProfileBtn.addEventListener("click", deleteActiveProfile);
    elements.importProfilesBtn.addEventListener("click", () => elements.importFileInput.click());
    elements.importFileInput.addEventListener("change", importProfiles);
    elements.exportProfileBtn.addEventListener("click", () => exportProfiles(false));
    elements.exportAllProfilesBtn.addEventListener("click", () => exportProfiles(true));

    elements.exportBtn.addEventListener("click", exportForAnalysis);
    elements.exportCountInput.addEventListener("input", updateApiUrlGenerators);
    
    elements.getCookieBtn.onclick = () => elements.cookieHelperModal.style.display = "block";
    elements.closeCookieHelper.onclick = () => elements.cookieHelperModal.style.display = "none";

    ['profile-name-input', 'api-key-input', 'auth-info-input', 'chat-ids-input'].forEach(id => {
        document.getElementById(id).addEventListener('input', updateApiUrlGenerators);
    });

    window.openTab = function(evt, tabName) {
        let i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tab-content");
        for (i = 0; i < tabcontent.length; i++) tabcontent[i].style.display = "none";
        tablinks = document.getElementsByClassName("tab-link");
        for (i = 0; i < tablinks.length; i++) tablinks[i].className = tablinks[i].className.replace(" active", "");
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";
    }

    function init() {
        renderProfileList();
        loadActiveProfile();
    }

    init();
});
