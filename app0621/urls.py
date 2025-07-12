"""
URL configuration for app0621 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from test0621 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('guest_login/', views.guest_login, name='guest_login'),
    path('logout/', views.user_logout, name='logout'),

    # --- 遊戲核心路徑 ---
    # 「開始遊戲」會連到這裡 
    path('planets/', views.planet_select, name='planet_select'),
    path('planets/<int:planet_id>/chapters/', views.chapter_select, name='chapter_select'),
    path('chapters/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    
    
    # --- 新增的主選單功能路徑 ---
    # 「成長軌跡」
    path('growth/<int:user_id>/', views.growth_track_view, name='growth_track'),
    
    # 【新增】「完整故事」列表頁
    path('stories/', views.full_story_list_view, name='full_story_list'),
    # 原本的單一故事頁面
    path('story/<int:chapter_id>/', views.full_story_view, name='full_story_detail'),

    # 【新增】「設定」頁面
    path('settings/', views.settings_view, name='settings'),

    # 【新增】「AI 小學堂」頁面
    path('classroom/', views.ai_classroom_view, name='ai_classroom'),

]





