// 使用 DOMContentLoaded 確保在 HTML 完全載入並解析後才執行我們的腳本，
// 這樣可以避免找不到元素的錯誤。
document.addEventListener('DOMContentLoaded', () => {

    // --- 元素選擇 ---
    // 【已修改】使用更精準的 ID 選擇器來定位登入表單
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form'); // 為了註冊頁面
    const googleLoginButton = document.getElementById('google-login');
    const errorMessageDiv = document.getElementById('error-message');


    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); 

            const formData = new FormData(loginForm);
            
            // 【最終確認】從 name="account" 的欄位獲取資料
            const account = formData.get('account'); 
            const password = formData.get('password');
            const csrfToken = formData.get('csrfmiddlewaretoken');

            if (errorMessageDiv) errorMessageDiv.style.display = 'none';

            try {
                const response = await fetch(loginForm.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ account, password }),
                });

                const result = await response.json();

                if (result.status === 'success') {
                    window.location.href = '/home/';
                } else {
                    showError(result.error || '發生未知錯誤');
                }

            } catch (error) {
                console.error('登入請求失敗:', error);
                showError('無法連接到伺服器。');
            }
        });
    }

    function showError(message) {
        if (errorMessageDiv) {
            errorMessageDiv.textContent = message;
            errorMessageDiv.style.display = 'block';
        } else {
            alert(message);
        }
    }

    // --- 2. 註冊邏輯 (如果您的註冊頁也使用此 JS) ---
    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const formData = new FormData(registerForm);
            const password = formData.get('password');
            const password2 = formData.get('password2');

            if (password !== password2) {
                showError('兩次輸入的密碼不一致');
                return;
            }

            const data = {
                account: formData.get('account'),
                nickname: formData.get('nickname'),
                password: password,
            };
            const csrfToken = formData.get('csrfmiddlewaretoken');

            // ... (發送註冊請求的邏輯) ...
        });
    }


    // --- 3. Google 第三方登入邏輯 ---
    if (googleLoginButton) {
        googleLoginButton.addEventListener('click', () => {
            const clientId = 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com'; // 【請替換成您自己的 Client ID】
            const redirectUri = 'http://127.0.0.1:8000/auth/google/callback/'; // 【請替換成您後端處理回調的網址】
            const scope = 'email profile openid';
            const responseType = 'code';
            const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=${responseType}&scope=${scope}&access_type=online`;
            window.location.href = authUrl;
        });
    }

    /**
     * 用於在頁面上顯示錯誤訊息的輔助函式
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
