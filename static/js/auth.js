document.addEventListener('DOMContentLoaded', () => {

    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const errorMessageDiv = document.getElementById('error-message');

    // --- 登入表單處理邏輯 (保持不變) ---
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(loginForm);
            const data = {
                account: formData.get('account'),
                password: formData.get('password'),
            };

            const response = await sendRequest(loginForm.action, data, formData.get('csrfmiddlewaretoken'));
            if (response && response.status === 'success') {
                window.location.href = '/home/';
            }
        });
    }

    // --- 【新增】註冊表單處理邏輯 ---
    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const formData = new FormData(registerForm);
            const password = formData.get('password');
            const password2 = formData.get('password2');

            // 前端密碼驗證
            if (password !== password2) {
                showError('兩次輸入的密碼不一致');
                return;
            }

            const data = {
                account: formData.get('account'),
                nickname: formData.get('nickname'),
                password: password,
            };

            const response = await sendRequest(registerForm.action, data, formData.get('csrfmiddlewaretoken'));
            if (response && response.status === 'success') {
                // 註冊成功後也跳轉到首頁
                window.location.href = '/home/';
            }
        });
    }

    /**
     * 發送請求到後端的通用函式
     * @param {string} url - 要發送請求的 URL
     * @param {object} data - 要發送的 JSON 資料
     * @param {string} csrfToken - CSRF 權杖
     * @returns {Promise<object|null>} - 後端返回的 JSON 資料或 null
     */
    async function sendRequest(url, data, csrfToken) {
        if (errorMessageDiv) errorMessageDiv.style.display = 'none';
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(data),
            });
            const result = await response.json();
            if (result.status !== 'success') {
                showError(result.error || '發生未知錯誤');
                return null;
            }
            return result;
        } catch (error) {
            console.error('請求失敗:', error);
            showError('無法連接到伺服器，請稍後再試。');
            return null;
        }
    }

    /**
     * 顯示錯誤訊息的函式
     * @param {string} message - 要顯示的錯誤訊息
     */
    function showError(message) {
        if (errorMessageDiv) {
            errorMessageDiv.textContent = message;
            errorMessageDiv.style.display = 'block';
        } else {
            alert(message);
        }
    }
});
