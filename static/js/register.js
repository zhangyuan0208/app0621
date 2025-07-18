// static/js/register.js
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('register-form');
    
    // 只有在註冊表單存在時才執行
    if (registerForm) {
        // Django allauth 預設的密碼欄位 ID 是 'id_password1' 和 'id_password2'
        const passwordInput = document.getElementById('id_password1');
        const password2Input = document.getElementById('id_password2');
        const errorMessageDiv = document.getElementById('error-message');

        registerForm.addEventListener('submit', function(event) {
            // 每次提交前都先隱藏舊訊息
            errorMessageDiv.style.display = 'none';

            // 檢查兩個密碼欄位是否存在
            if (!passwordInput || !password2Input) return;
            
            const password = passwordInput.value;
            const password2 = password2Input.value;
            
            if (password.length < 8) {
                event.preventDefault(); // 阻止表單提交
                showError('密碼長度至少需要 8 個字元！');
                return;
            }

            if (password !== password2) {
                event.preventDefault(); // 阻止表單提交
                showError('兩次輸入的密碼不一致，請重新確認！');
                return;
            }
        });

        function showError(message) {
            errorMessageDiv.textContent = message;
            errorMessageDiv.style.display = 'block';
        }
    }
});