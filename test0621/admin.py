# game/admin.py

from django.contrib import admin
from .models import (
    LoginType, ChapterStatus, DifficultyLevel,
    User, Planet, Chapter, Character, ChapterCharacter,
    UserProgress, Dialogue, Question, QuizRecord,
    GrowthTrack, FullStory, UserSetting, StarUnlockLog
)

# --- 客製化後台顯示 ---

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    使用者模型的後台設定
    """
    # 【已修改】在列表中加入 'password' 欄位，方便您檢查是否已加密
    list_display = ('user_id', 'nickname', 'account', 'password', 'login_type', 'is_guest', 'created_at')
    search_fields = ('nickname', 'account')
    list_filter = ('login_type', 'is_guest', 'created_at')
    ordering = ('-created_at',)
    # 為了不讓密碼欄位可以被編輯（因為它是加密過的），可以設定為唯讀
    readonly_fields = ('password',)

@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    """
    星球模型的後台設定
    """
    list_display = ('planet_id', 'planet_name')
    search_fields = ('planet_name',)

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """
    章節模型的後台設定
    """
    list_display = ('chapter_id', 'title', 'planet', 'chapter_number')
    search_fields = ('title',)
    list_filter = ('planet',)
    ordering = ('planet', 'chapter_number')

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    """
    角色模型的後台設定
    """
    list_display = ('character_id', 'name')
    search_fields = ('name',)

@admin.register(Dialogue)
class DialogueAdmin(admin.ModelAdmin):
    """
    對話模型的後台設定
    """
    list_display = ('dialogue_id', 'chapter', 'character', 'sequence', 'text')
    list_filter = ('chapter', 'character')
    search_fields = ('text',)
    ordering = ('chapter', 'sequence')

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    """
    使用者進度模型的後台設定
    """
    list_display = ('user', 'chapter', 'status', 'last_played')
    list_filter = ('status', 'user', 'chapter')
    ordering = ('-last_played',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    問題模型的後台設定
    """
    list_display = ('question_id', 'chapter', 'difficulty', 'question_text')
    list_filter = ('chapter', 'difficulty')
    search_fields = ('question_text',)

@admin.register(QuizRecord)
class QuizRecordAdmin(admin.ModelAdmin):
    """
    測驗記錄模型的後台設定
    """
    list_display = ('record_id', 'user', 'chapter', 'stars_earned', 'correct_count', 'created_at')
    list_filter = ('user', 'chapter', 'stars_earned')
    ordering = ('-created_at',)

# --- 對於關聯性或較簡單的模型，可以直接註冊 ---

admin.site.register(ChapterCharacter)
admin.site.register(GrowthTrack)
admin.site.register(FullStory)
admin.site.register(UserSetting)
admin.site.register(StarUnlockLog)
