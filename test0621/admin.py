from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Planet, Chapter, Character, Dialogue, Question,
    UserProgress, QuizRecord, GrowthTrack, FullStory, UserSetting,
    UnlockedAvatar, DailyCheckIn, StarUnlockLog, ChapterCharacter
)

# --- 客製化 User 模型的後台顯示 ---
# 我們繼承內建的 UserAdmin，並加入我們自訂的欄位
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # 在使用者列表頁要顯示的欄位
    list_display = ('username', 'nickname', 'email', 'login_type', 'is_guest', 'is_staff')
    # 可以用來篩選的欄位
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'login_type', 'is_guest')
    # 在使用者編輯頁面顯示的欄位分區
    # 這裡我們將自訂欄位加入到 fieldsets 中
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('個人資訊', {'fields': ('nickname', 'email', 'user_avatar', 'diamonds')}),
        ('登入類型', {'fields': ('login_type', 'is_guest')}),
        ('權限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )

# --- 客製化 Chapter 的後台顯示 ---
# 可以在章節頁面內直接編輯對話
class DialogueInline(admin.TabularInline):
    model = Dialogue
    extra = 1 # 在頁面中預設顯示1個空白的對話框，方便新增
    ordering = ('sequence',) # 讓內嵌的對話按順序排列

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('planet', 'chapter_number', 'title')
    list_filter = ('planet',)
    search_fields = ['title', 'chapter_number']
    inlines = [DialogueInline] # 將 Dialogue 的編輯功能嵌入到 Chapter 頁面

# --- 客製化 Question 的後台顯示 ---
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'question_text', 'difficulty')
    list_filter = ('chapter', 'difficulty')
    search_fields = ['question_text']

# --- 客製化 QuizRecord 的後台顯示 ---
@admin.register(QuizRecord)
class QuizRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'stars_earned', 'correct_count', 'created_at')
    list_filter = ('chapter', 'user', 'stars_earned')
    date_hierarchy = 'created_at' # 新增日期快速篩選條

# --- 客製化 Character 的後台顯示 ---
@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'intro')
    search_fields = ['name']

# --- 其他模型使用預設方式註冊 ---
# 這種方式簡單快速，適合不需要太多客製化的模型
admin.site.register(Planet)
admin.site.register(UserProgress)
admin.site.register(GrowthTrack)
admin.site.register(FullStory)
admin.site.register(UserSetting)
admin.site.register(UnlockedAvatar)
admin.site.register(DailyCheckIn)
admin.site.register(StarUnlockLog)
admin.site.register(ChapterCharacter)

# Dialogue 已經內嵌到 ChapterAdmin，如果也想單獨管理，可以取消下面這行的註解
# admin.site.register(Dialogue)