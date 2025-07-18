// static/js/ai_school.js

document.addEventListener('DOMContentLoaded', function() {
    // --- 元素選擇 ---
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendMessageBtn');
    const listenBtn = document.getElementById('startListeningBtn');
    const voiceStatus = document.getElementById("voiceStatus");

    // --- 從 HTML 讀取後端傳來的變數 ---
    // AI_ASK_URL, CSRF_TOKEN, USER_AVATAR_URL, BOT_AVATAR_URL
    // 這些變數已在 HTML 模板中定義

    const messages = [
        { role: "system", content: "你是一位性別平等專家，只能自我介紹與回答上一句問甚麼與回應性別平等相關的問題，包括身體界線等等。遇到其他主題，請回答「抱歉，我只能回答有關於性別平等的問題，你可以換個問題問我！」。" }
    ];

    // --- 事件監聽 ---
    sendBtn.addEventListener('click', sendMessage);
    listenBtn.addEventListener('click', startListening);
    userInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    userInput.addEventListener("input", () => autoResize(userInput));

    // --- 函式定義 ---

    function trimHistory(messages, maxTurns = 6) {
        const systemPrompt = messages[0];
        const history = messages.slice(1);
        return [systemPrompt, ...history.slice(-maxTurns * 2)];
    }

    async function sendMessage() {
        const userText = userInput.value.trim();
        if (!userText) return;

        displayMessage(userText, "user");
        messages.push({ role: "user", content: userText });
        userInput.value = "";
        autoResize(userInput);

        const pendingBotMessage = displayMessage("正在思考中...", "bot", true);
        const messageDiv = pendingBotMessage.querySelector(".message");

        try {
            // 【修改】向我們的 Django 後端代理發送請求
            const response = await fetch(AI_ASK_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": CSRF_TOKEN // 【新增】帶上 CSRF Token
                },
                body: JSON.stringify({
                    messages: trimHistory(messages)
                })
            });

            if (!response.ok) {
                // 如果後端回傳錯誤 (例如 500 Server Error)
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP 錯誤: ${response.status}`);
            }
            
            const data = await response.json();
            const reply = data.choices?.[0]?.message?.content;
            
            messageDiv.innerText = reply || "抱歉，我無法理解您的問題。";
            if (reply) messages.push({ role: "assistant", content: reply });

        } catch (error) {
            console.error("API 錯誤:", error);
            messageDiv.innerText = "系統發生錯誤，請稍後再試。";
        }
    }

    function displayMessage(text, sender, isTemporary = false) {
        const chatbox = document.getElementById("chatbox");
        const container = document.createElement("div");
        container.classList.add("message-container", sender + "-container");

        const avatar = document.createElement("img");
        avatar.classList.add("avatar");
        // 【修改】使用從 Django 模板傳來的路徑
        avatar.src = sender === "user" ? USER_AVATAR_URL : BOT_AVATAR_URL;

        const messageGroup = document.createElement("div");
        messageGroup.classList.add("message-group");

        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        messageDiv.innerText = text;

        const timestamp = document.createElement("div");
        timestamp.classList.add("timestamp");
        timestamp.innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageGroup.appendChild(messageDiv);
        messageGroup.appendChild(timestamp);

        if (sender === "user") {
            container.appendChild(messageGroup);
            container.appendChild(avatar);
        } else {
            container.appendChild(avatar);
            container.appendChild(messageGroup);
        }

        chatbox.appendChild(container);
        chatbox.scrollTop = chatbox.scrollHeight;
        
        return isTemporary ? container : null;
    }
    
    function autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    // --- 語音辨識邏輯 (保持不變) ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'zh-TW';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            voiceStatus.style.display = "block";
            voiceStatus.textContent = "語音辨識中...";
        };
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            autoResize(userInput);
            sendMessage();
        };
        recognition.onerror = (event) => {
            console.error("語音錯誤:", event.error);
            voiceStatus.textContent = "語音辨識錯誤：" + event.error;
            setTimeout(() => voiceStatus.style.display = "none", 3000);
        };
        recognition.onend = () => {
            voiceStatus.style.display = "none";
        };
    } else {
        listenBtn.style.display = 'none'; // 如果不支援，直接隱藏按鈕
    }

    function startListening() {
        if (recognition) recognition.start();
    }
});