document.addEventListener('DOMContentLoaded', () => {

    // ===============================================
    // ==== 1. 星球選單邏輯
    // ===============================================
    const planets = document.querySelectorAll('.planet');
    const label = document.getElementById('planet-label');

    if (label) {
        planets.forEach(planet => {
            // 【修改】對於設定星球，點擊事件由 HTML 中的 onclick 處理，此處僅處理其他星球的導航
            if (!planet.classList.contains('settings')) {
                 planet.addEventListener('click', () => {
                    const url = planet.getAttribute('data-url');
                    if (url && url !== '#') {
                        window.location.href = url;
                    } else {
                        console.log(`點擊了 ${planet.getAttribute('data-text')}，但 URL 無效`);
                    }
                });
            }

            // 以下滑鼠懸停邏輯保持不變
            planet.addEventListener('mouseover', (event) => {
                const planetName = planet.getAttribute('data-text');
                if (planetName) {
                    label.textContent = planetName;
                    label.style.display = 'block';
                }
            });
            planet.addEventListener('mousemove', (event) => {
                label.style.left = event.pageX + 15 + 'px';
                label.style.top = event.pageY + 15 + 'px';
            });
            planet.addEventListener('mouseout', () => {
                label.style.display = 'none';
            });
        });
    }

    // ===============================================
    // ==== 2. 每日打卡邏輯 (無變動)
    // ===============================================
    let playerData = {};
    let loginType = 'guest';
    let storageKey = 'guestUserData';
    const djangoUserNicknameEl = document.getElementById('django-user-nickname');
    const djangoUserAvatarEl = document.getElementById('django-user-avatar');
    const playerInfoPanel = document.getElementById('player-info-panel');
    const checkInModal = document.getElementById('check-in-modal');
    const closeBtn = document.getElementById('check-in-close-btn');
    const calendarContainer = document.getElementById('check-in-calendar');
    const crystalAmountElement = document.getElementById('crystal-amount');
    const consecutiveDaysCountElement = document.getElementById('consecutive-days-count');
    const panelNickname = document.getElementById('player-nickname');
    const panelAvatar = document.getElementById('player-avatar');

    function savePlayerData() { localStorage.setItem(storageKey, JSON.stringify(playerData)); }
    function loadPlayerData() {
        const saved = localStorage.getItem(storageKey);
        if (saved) { return JSON.parse(saved); }
        if (loginType === 'user') { return { nickname: djangoUserNicknameEl.textContent, avatar: djangoUserAvatarEl.dataset.avatarUrl, lifeCrystals: 0, checkInRecords: [] }; }
        return { nickname: "訪客", avatar: "/static/img/avatars/default_avatar.png", lifeCrystals: 0, checkInRecords: [] };
    }
    function openModal() { updateCheckInModal(); checkInModal.style.display = 'flex'; const card = checkInModal.querySelector('.modal-card'); card.classList.remove('pop-close'); card.classList.add('pop-in'); }
    function closeModal() { const card = checkInModal.querySelector('.modal-card'); card.classList.remove('pop-in'); card.classList.add('pop-close'); card.addEventListener('animationend', () => { checkInModal.style.display = 'none'; card.classList.remove('pop-close'); }, { once: true }); }
    function performCheckIn(cell) {
        const todayString = getTodayString();
        if (playerData.checkInRecords.includes(todayString)) { showCustomAlert("今天已經打過卡囉！"); return; }
        const consecutiveDaysBeforeToday = calculateConsecutiveDays(playerData.checkInRecords);
        const newConsecutiveDays = consecutiveDaysBeforeToday + 1;
        let crystalReward = 0;
        if (newConsecutiveDays > 0 && newConsecutiveDays % 7 === 0) { crystalReward = 1; showCustomAlert(`🎉 恭喜！連續打卡第 ${newConsecutiveDays} 天，獲得 1 顆生命結晶！`); }
        else { showCustomAlert(`✅ 成功打卡！連續天數：${newConsecutiveDays}`); }
        playerData.lifeCrystals += crystalReward;
        playerData.checkInRecords.push(todayString);
        playerData.checkInRecords.sort();
        savePlayerData();
        cell.classList.remove('can-check-in', 'today');
        cell.classList.add('checked-in', 'day-pop-animation');
        cell.addEventListener('animationend', () => cell.classList.remove('day-pop-animation'), { once: true });
        animateValue(crystalAmountElement, parseInt(crystalAmountElement.textContent), playerData.lifeCrystals, 500);
        consecutiveDaysCountElement.textContent = newConsecutiveDays;
    }
    function calculateConsecutiveDays(records) {
        const recordSet = new Set(records); if (recordSet.size === 0) return 0;
        let consecutiveCount = 0; const todayString = getTodayString();
        let dateToCheck = new Date(todayString);
        if (!recordSet.has(todayString)) { dateToCheck.setDate(dateToCheck.getDate() - 1); }
        while (recordSet.has(formatDate(dateToCheck))) { consecutiveCount++; dateToCheck.setDate(dateToCheck.getDate() - 1); }
        return consecutiveCount;
    }
    function generateCalendar(checkInRecords) {
        calendarContainer.innerHTML = ''; const today = new Date(); const todayString = getTodayString();
        const year = today.getFullYear(); const month = today.getMonth();
        const firstDayOfMonth = new Date(year, month, 1); const daysInMonth = new Date(year, month + 1, 0).getDate();
        const startDayOfWeek = firstDayOfMonth.getDay();
        for (let i = 0; i < startDayOfWeek; i++) { calendarContainer.innerHTML += '<div class="calendar-day empty"></div>'; }
        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement('div'); dayCell.className = 'calendar-day'; dayCell.textContent = day;
            const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            if (checkInRecords.includes(dateString)) { dayCell.classList.add('checked-in'); }
            else if (dateString === todayString) { dayCell.classList.add('today', 'can-check-in'); }
            calendarContainer.appendChild(dayCell);
        }
    }
    function updateCheckInModal() { crystalAmountElement.textContent = playerData.lifeCrystals; consecutiveDaysCountElement.textContent = calculateConsecutiveDays(playerData.checkInRecords); generateCalendar(playerData.checkInRecords); }
    function initializePlayerPanel() { panelNickname.textContent = playerData.nickname; panelAvatar.src = playerData.avatar; }
    function formatDate(date) { const year = date.getFullYear(); const month = String(date.getMonth() + 1).padStart(2, '0'); const day = String(date.getDate()).padStart(2, '0'); return `${year}-${month}-${day}`; }
    function getTodayString() { return formatDate(new Date()); }
    function showCustomAlert(message) { const alertOverlay = document.getElementById('custom-alert'); document.getElementById('custom-alert-message').textContent = message; alertOverlay.style.display = 'flex'; document.getElementById('custom-alert-ok').onclick = () => { alertOverlay.style.display = 'none'; }; }
    function animateValue(element, start, end, duration) { let startTimestamp = null; const step = (timestamp) => { if (!startTimestamp) startTimestamp = timestamp; const progress = Math.min((timestamp - startTimestamp) / duration, 1); element.innerHTML = Math.floor(progress * (end - start) + start); if (progress < 1) window.requestAnimationFrame(step); }; window.requestAnimationFrame(step); }
    
    // ===============================================
    // ==== 【新增】3. 設定介面邏輯
    // ===============================================
    // 為了讓 HTML 中的 onclick 能呼叫到，我們將這些函式附加到 window 物件上
    
    window.openSettings = function() { document.getElementById("settingsModal").style.display = "flex"; }
    window.closeSettings = function() { document.getElementById("settingsModal").style.display = "none"; }
    
    window.showTab = function(tabName, clickedButton) {
        document.querySelectorAll(".tab-panel").forEach(panel => panel.style.display = "none");
        document.getElementById(`tab-${tabName}`).style.display = "block";
        document.querySelectorAll(".settings-menu button").forEach(btn => btn.classList.remove("active"));
        if (clickedButton) { clickedButton.classList.add("active"); }
    }
    
    window.showToast = function(message) {
        const toast = document.getElementById("toast");
        toast.textContent = message; toast.style.display = "block";
        setTimeout(() => { toast.style.display = "none"; }, 2000);
    }

    let modalAction = "";
    window.showModal = function(message, action) {
        document.getElementById("modal-message").textContent = message;
        document.getElementById("modal").style.display = "flex";
        modalAction = action; 
    }
    
    window.confirmModal = function(confirmed) {
        document.getElementById("modal").style.display = "none";
        if (confirmed) {
            if (modalAction === "delete") {
                showToast("帳號已刪除");
                // 在此處添加實際的帳號刪除後端邏輯
            } else if (modalAction === "logout") {
                showToast("已登出");
                // 在此處添加實際的登出後端邏輯，例如：
                // window.location.href = "/your-logout-url/";
            }
        }
    }
    
    const volumeStatus = { bgm: true, voice: true };
    window.toggleVolume = function(button, type) {
        volumeStatus[type] = !volumeStatus[type];
        button.textContent = volumeStatus[type] ? "🔊" : "🔇";
    }
    
    window.updateVolume = function(type, value) {
        document.getElementById(`${type}-volume`).textContent = value;
        localStorage.setItem(`${type}-volume`, value);
    }
    
    function loadVolumeSettings() {
        const bgm = localStorage.getItem('bgm-volume');
        const voice = localStorage.getItem('voice-volume');
        if (bgm !== null) { document.getElementById('bgm-slider').value = bgm; document.getElementById('bgm-volume').textContent = bgm; }
        if (voice !== null) { document.getElementById('voice-slider').value = voice; document.getElementById('voice-volume').textContent = voice; }
    }
    
    window.submitSettings = function() {
        showToast('設定已儲存');
        closeSettings();
    }

    // ===============================================
    // ==== 4. 頁面載入後的初始化工作
    // ===============================================

    // ---- 打卡系統的事件監聽與初始化 ----
    playerInfoPanel.addEventListener('click', openModal);
    closeBtn.addEventListener('click', closeModal);
    checkInModal.addEventListener('click', (e) => { if (e.target === checkInModal) closeModal(); });
    calendarContainer.addEventListener('click', (event) => {
        const clickedCell = event.target.closest('.calendar-day.can-check-in');
        if (clickedCell) {
            if (loginType === 'guest') { showCustomAlert("註冊或登入會員，就能開始打卡並永久保存您的紀錄喔！"); }
            else { performCheckIn(clickedCell); }
        }
    });

    if (djangoUserNicknameEl) { loginType = 'user'; storageKey = `userData-${djangoUserNicknameEl.textContent}`; }
    playerData = loadPlayerData();
    initializePlayerPanel();
    savePlayerData();

    // ---- 【新增】設定系統的初始化 ----
    const firstButton = document.querySelector(".settings-menu button");
    if (firstButton) {
        showTab('music', firstButton);
    }
    loadVolumeSettings();

});