document.addEventListener('DOMContentLoaded', () => {

    const scrollAmount = window.innerWidth / 2; // 每次要捲動的寬度為「螢幕寬度的一半」
    const leftArrow = document.getElementById("leftArrow");
    const rightArrow = document.getElementById("rightArrow");
    const resetButton = document.getElementById("resetButton");

    // 更新箭頭顯示狀態的函式
    function updateArrows() {
        // scrollWidth 是元素的總寬度，包括看不到的部分
        const maxScroll = document.body.scrollWidth - window.innerWidth;
        const currentScroll = window.scrollX;

        leftArrow.style.display = currentScroll <= 0 ? "none" : "block";
        rightArrow.style.display = currentScroll >= maxScroll ? "none" : "block";
    }

    // 向左捲動
    function scrollLeft() {
        window.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        setTimeout(updateArrows, 500); // 捲動動畫需要時間，延遲更新箭頭狀態
    }

    // 向右捲動
    function scrollRight() {
        window.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        setTimeout(updateArrows, 500);
    }

    // 重置進度 (測試用)
    function resetProgress() {
        // 注意：在真實專案中，這裡應該是向後端 API 發送請求來重置資料庫中的使用者進度，
        // 而不是只清除 localStorage。
        // localStorage.clear(); 
        alert("這是一個測試按鈕！真實功能需串接後端。");
        // location.reload(); // 重整頁面以看到變化
    }

    // --- 綁定事件 ---
    if (leftArrow) leftArrow.addEventListener("click", scrollLeft);
    if (rightArrow) rightArrow.addEventListener("click", scrollRight);
    if (resetButton) resetButton.addEventListener("click", resetProgress);

    // 鍵盤左右鍵控制
    document.addEventListener("keydown", function (e) {
        if (e.key === "ArrowRight") {
            scrollRight();
        } else if (e.key === "ArrowLeft") {
            scrollLeft();
        }
    });

    // 頁面載入、視窗大小改變、捲動時，都更新箭頭狀態
    window.addEventListener("load", updateArrows);
    window.addEventListener("resize", updateArrows);
    window.addEventListener("scroll", updateArrows);

});
