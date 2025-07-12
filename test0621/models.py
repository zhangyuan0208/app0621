from django.db import models
from django.utils import timezone
# 【新增】引入 Django 內建的使用者模型工具
from django.contrib.auth.models import AbstractUser

#使用者登入的方式
class LoginType(models.TextChoices):
    NORMAL = 'normal', '一般'
    GOOGLE = 'google', 'Google'
    GUEST = 'guest', '訪客'

#使用者對於某個章節的進度狀態
class ChapterStatus(models.TextChoices):
    LOCKED = 'locked', '未解鎖'
    UNLOCKED = 'unlocked', '已解鎖'
    IN_PROGRESS = 'in_progress', '進行中'
    COMPLETED = 'completed', '已完成'

#測驗問題的難度等級
class DifficultyLevel(models.TextChoices):
    EASY = 'easy', '簡單'
    MEDIUM = 'medium', '中等'
    HARD = 'hard', '困難'

#遊戲中的「星球」，每個星球可以包含多個章節，作為一個大的分類。
class Planet(models.Model):
    planet_id = models.AutoField(primary_key=True)
    planet_name = models.CharField(max_length=100)

    def __str__(self):
        return self.planet_name
    
#玩家資訊，繼承自 Django 內建的 AbstractUser
class User(AbstractUser):

    # 1. 暱稱欄位
    nickname = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="暱稱"
    )

    # 2. 登入方式欄位
    login_type = models.CharField(
        max_length=10, 
        choices=LoginType.choices, 
        default=LoginType.NORMAL,
        verbose_name="登入方式"
    )

    # 3. 訪客標記欄位
    is_guest = models.BooleanField(
        default=False,
        verbose_name="是否為訪客"
    )

    # 4. 頭像路徑欄位
    #    使用 CharField 來儲存頭像圖片在 static 資料夾中的路徑，
    #    這完全符合您「頭像由遊戲獎勵，而非使用者上傳」的需求。
    user_avatar = models.CharField(
        max_length=255, 
        default='img/avatars/default.png', # 提供一個預設頭像的路徑
        verbose_name="頭像路徑"
    )

    diamonds = models.IntegerField(default=1, verbose_name="鑽石數量")

    def __str__(self):
        # 讓物件在後台顯示時，優先顯示暱稱，如果沒有暱稱就顯示 username
        return self.nickname or self.username

# 頭像庫模型，用來記錄玩家解鎖的所有頭像
class UnlockedAvatar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="使用者")
    # 儲存頭像圖片的路徑，例如 'img/avatars/reward_avatar_01.png'
    avatar_path = models.CharField(max_length=255, verbose_name="頭像路徑")
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name="解鎖時間")

    class Meta:
        # 確保同一個使用者對同一個頭像路徑只有一筆記錄
        unique_together = ('user', 'avatar_path')
        verbose_name = "玩家解鎖頭像"
        verbose_name_plural = "玩家解鎖頭像"

    def __str__(self):
        return f"{self.user.username} - {self.avatar_path}"


# 每日打卡模型
class DailyCheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="使用者")
    check_in_date = models.DateField(auto_now_add=True, unique=True, verbose_name="打卡日期")

    class Meta:
        ordering = ['-check_in_date']
        verbose_name = "每日打卡記錄"
        verbose_name_plural = "每日打卡記錄"

    def __str__(self):
        return f"{self.user.username} - {self.check_in_date}"

#文章
class Chapter(models.Model):
    chapter_id = models.AutoField(primary_key=True)
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    chapter_number = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    background_image = models.CharField(max_length=255)
    bg_music = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.planet.planet_name} - {self.chapter_number}"

#角色
class Character(models.Model):
    character_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    character_avatar = models.CharField(max_length=255)
    intro = models.TextField(blank=True, null=True)
    image_left = models.CharField(max_length=255, blank=True, null=True)
    image_right = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class ChapterCharacter(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('chapter', 'character')

    def __str__(self):
        return f"{self.chapter} - {self.character}"

#每個章節的狀態
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ChapterStatus.choices)
    last_played = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'chapter')

    def __str__(self):
        return f"{self.user.nickname} - {self.chapter} ({self.status})"

#對話
class Dialogue(models.Model):
    dialogue_id = models.AutoField(primary_key=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    sequence = models.IntegerField()
    text = models.TextField()
    voice_file = models.CharField(max_length=255, null=True, blank=True)
    background_image = models.CharField(max_length=255, null=True, blank=True)
    bg_music = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.chapter} - {self.character.name} ({self.sequence})"

#問題
class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10, choices=DifficultyLevel.choices)
    question_text = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=10)
    enemy_image = models.CharField(max_length=255, null=True, blank=True)
    player_image = models.CharField(max_length=255, null=True, blank=True)
    background = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.chapter} ({self.difficulty})"

#測驗記錄
class QuizRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    correct_count = models.IntegerField()
    stars_earned = models.IntegerField()
    life_crystal_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.nickname} - {self.chapter} - {self.stars_earned}星"

# 獎勵 (優化版)
class GrowthTrack(models.Model):
    # 【已修改】我們不再需要單獨儲存 user, planet, chapter，
    # 因為這些資訊都可以從下面的 quiz_record 中獲取。
    
    # 使用 OneToOneField，建立一個從「獎勵」到「觸發這次獎勵的測驗記錄」的一對一連結。
    # 這確保了一筆完美的測驗記錄，只會對應到一筆獎勵。
    quiz_record = models.OneToOneField(
        QuizRecord, 
        on_delete=models.CASCADE, 
        primary_key=True, # 將這個關聯設為主鍵，結構更清晰
        verbose_name="觸發的測驗記錄"
    )
    
    achievement = models.TextField(
    verbose_name="成就描述", 
    blank=True  # 允許表單為空，資料庫將儲存為空字串 ''
    )

    is_cracked = models.BooleanField(default=False, verbose_name="獎勵是否已領取")

    def __str__(self):
        # 現在我們可以從 quiz_record 中獲取所有需要的資訊
        achievement_preview = (self.achievement[:20] + '...') if len(self.achievement) > 20 else self.achievement
        return f"{self.quiz_record.user.nickname} 在「{self.quiz_record.chapter.title}」達成: {achievement_preview}"

#完整故事
class FullStory(models.Model):
    story_id = models.AutoField(primary_key=True)
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    character = models.CharField(max_length=100)
    introduction = models.TextField(blank=True, default='') 
    full_text = models.TextField()
    is_unlocked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.chapter}"


class UserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    music_volume = models.IntegerField(default=50)
    voice_toggle = models.BooleanField(default=True)
    font = models.CharField(max_length=100)

    def __str__(self):
        return f"設定 - {self.user.nickname}"

# 【建議修改】星星解鎖日誌
class StarUnlockLog(models.Model):
    # 關聯到使用者和章節
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="使用者")
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, verbose_name="解鎖的章節")
    
    # 自動記錄解鎖的當下時間
    unlocked_at = models.DateTimeField(default=timezone.now, verbose_name="解鎖時間")

    # 【已修改】__str__ 方法，提供更清晰的日誌資訊
    def __str__(self):
        # 格式化時間，讓它在後台更容易閱讀
        unlock_time = self.unlocked_at.strftime("%Y-%m-%d %H:%M")
        return f"{self.user.nickname} 於 {unlock_time} 解鎖 {self.chapter}"

    # 【建議新增】Meta 選項，讓日誌在後台預設按時間倒序排列
    class Meta:
        ordering = ['-unlocked_at']
        verbose_name = "關卡解鎖日誌"
        verbose_name_plural = "關卡解鎖日誌"
