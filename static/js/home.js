// 使用 DOMContentLoaded 確保在 HTML 完全載入後才執行腳本
document.addEventListener('DOMContentLoaded', () => {

    const planets = document.querySelectorAll('.planet');
    const label = document.getElementById('planet-label');

    if (!label) {
        console.error('找不到 ID 為 "planet-label" 的元素！');
        return;
    }

    planets.forEach(planet => {
        // 滑鼠移入星球，顯示標籤
        planet.addEventListener('mouseover', (event) => {
            const planetName = planet.getAttribute('data-text');
            if (planetName) {
                label.textContent = planetName;
                label.style.display = 'block';
            }
        });
        
        // 滑鼠在星球上移動，更新標籤位置
        planet.addEventListener('mousemove', (event) => {
            // 將標籤放在滑鼠指標的右下方
            label.style.left = event.pageX + 15 + 'px';
            label.style.top = event.pageY + 15 + 'px';
        });

        // 滑鼠移出星球，隱藏標籤
        planet.addEventListener('mouseout', () => {
            label.style.display = 'none';
        });
        
        // 點擊星球，導向指定頁面
        planet.addEventListener('click', () => {
            const url = planet.getAttribute('data-url');
            // 檢查 data-url 是否存在且不是 '#'
            if (url && url !== '#') {
                window.location.href = url;
            } else {
                const planetName = planet.getAttribute('data-text');
                console.log(`你點擊了：${planetName}，但尚未設定有效的 URL。`);
                // 您也可以在這裡顯示一個提示訊息給使用者
            }
        });
    });
});
