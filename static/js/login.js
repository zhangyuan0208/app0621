// static/js/login.js

// 使用 DOMContentLoaded 確保在 HTML 完全載入並解析後才執行
document.addEventListener('DOMContentLoaded', function() {

    // 取得啟動畫面和登入畫面的元素
    const splashScreen = document.getElementById('splash-screen');
    const loginContainer = document.getElementById('login-container');

    // 只有在啟動畫面存在時，才加上點擊事件
    if (splashScreen) {
        splashScreen.addEventListener('click', function() {
            // 讓啟動畫面淡出
            splashScreen.style.opacity = '0';
            splashScreen.style.visibility = 'hidden';

            // 為了讓淡出效果能完整呈現，延遲 500 毫秒再顯示登入畫面
            setTimeout(function() {
                // 徹底隱藏啟動畫面(設為none可以釋放空間)
                splashScreen.style.display = 'none'; 
                
                // 顯示登入畫面
                loginContainer.style.display = 'flex'; 
            }, 500); // 這個時間需與 CSS 的 transition-duration 一致
        });
    }
});