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
from django.urls import path, include # 確保 include 已被引入

urlpatterns = [
    # 1. Django 後台管理介面的 URL
    path('admin/', admin.site.urls),

    # 2. Django-allauth 的 URL，所有帳號相關功能（登入、登出、密碼重設、Google認證）都由它處理
    path('accounts/', include('allauth.urls')),

    # 3. 將所有其他的請求，全部轉交給我們的 app (test0621) 去處理
    # 空字串 '' 代表網站的根目錄 (例如 http://127.0.0.1:8000/)
    path('', include('test0621.urls')), # 請確認您的 app 名稱是否為 test0621
]