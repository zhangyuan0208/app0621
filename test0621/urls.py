from django.urls import path
from test0621 import views  # 從當前資料夾引入 views.py

urlpatterns = [
    # --- I. 使用者認證系統 ---
    # 註冊頁面
    path('register/', views.register_view, name='register_view'),
    # 登入頁面 (注意：allauth 也有自己的 login，但我們可以保留自訂的)
    path('login/', views.login_view, name='login_view'),
    # 登出功能
    path('logout/', views.logout_view, name='logout_view'),
    # 訪客登入功能
    path('guest-login/', views.guest_login_view, name='guest_login_view'),
    # Google 登入的 placeholder (雖然被 allauth 取代，但可以保留以防萬一)
    path('google-login-placeholder/', views.google_login_placeholder_view, name='google_login_placeholder_view'),

    # --- II. 主要流程與選單 ---
    # 網站首頁，對應到主選單
    path('', views.main_menu_view, name='main_menu'),
    # 每日打卡功能的 URL
    path('daily-check-in/', views.daily_check_in_view, name='daily_check_in_view'),

    # --- III. 遊戲核心系統 ---
    # 星球選擇列表
    path('planets/', views.planet_list_view, name='planet_list_view'),
    # 特定星球的章節列表，<int:planet_id> 是動態參數
    path('planet/<int:planet_id>/', views.chapter_list_view, name='chapter_list_view'),
    # 視覺小說頁面
    path('chapter/<int:chapter_id>/novel/', views.visual_novel_view, name='visual_novel_view'),
    # 問答遊戲頁面
    path('chapter/<int:chapter_id>/quiz/', views.quiz_view, name='quiz_view'),
    # 問答結果頁面
    path('quiz-result/<int:record_id>/', views.quiz_result_view, name='quiz_result_view'),
    # 在問答中，使用鑽石恢復生命的 URL (這是一個 API，不是頁面)
    path('use-diamond/', views.use_diamond_view, name='use_diamond_view'),


    # --- IV. 周邊系統 ---
    # 完整故事列表
    path('full-stories/', views.full_story_list_view, name='full_story_list_view'),
    # AI 小學堂
    path('ai-school/', views.ai_school_view, name='ai_school_view'),
    # 設定頁面
    path('settings/', views.settings_view, name='settings_view'),
    # 成長軌跡
    path('growth-track/', views.growth_track_view, name='growth_track_view'),
    # 頭像更換頁面
    path('avatar-inventory/', views.avatar_inventory_view, name='avatar_inventory_view'),
]