import random
from datetime import date, timedelta
import uuid  # 用於產生訪客ID

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse

# 建議將表單邏輯分離
from .forms import UserRegistrationForm, UserLoginForm

# 引入所有需要的模型
from .models import (
    User, Planet, Chapter, Dialogue, Question, UserProgress,
    QuizRecord, GrowthTrack, FullStory, UserSetting,
    UnlockedAvatar, DailyCheckIn
)

# ===================================================================
# I. 使用者認證系統 (Authentication Views)
# ===================================================================

def register_view(request):
    """處理使用者註冊 - 更新版"""
    if request.method == 'POST':
        # 如果是提交表單，則用 POST 資料建立表單實例
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # 如果表單資料全部合法
            user = form.save()  # 執行我們在 forms.py 中定義的 save 方法，建立使用者
            login(request, user)  # 註冊後自動登入
            messages.success(request, "註冊成功！歡迎加入我們的世界。")
            return redirect('main_menu') # 重定向到主選單
    else:
        # 如果是第一次訪問頁面，則建立一個空表單
        form = UserRegistrationForm()
    
    # 將表單物件傳遞給模板
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    """處理使用者登入 - 更新版"""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            # 取得驗證後的乾淨資料
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # 使用 Django 內建的 authenticate 方法驗證使用者
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # 如果驗證成功
                login(request, user) # 執行登入
                return redirect('main_menu') # 重定向到主選單
            else:
                # 如果驗證失敗
                messages.error(request, "使用者名稱或密碼錯誤，請重新輸入。")
    else:
        form = UserLoginForm()
        
    return render(request, 'auth/login.html', {'form': form})

def guest_login_view(request):
    """處理訪客登入"""
    # 產生一個獨一無二的訪客使用者名稱
    guest_username = f"guest_{uuid.uuid4().hex[:8]}"
    guest_user = User.objects.create_user(username=guest_username, password=None, is_guest=True)
    login(request, guest_user)
    messages.success(request, "歡迎以訪客身份體驗！請記得在設定中綁定帳號以保存進度。")
    return redirect('main_menu')

# Google 登入的框架，實際功能需依賴 django-allauth 套件
def google_login_placeholder_view(request):
    messages.info(request, "Google 登入功能需整合第三方服務。")
    return redirect('login_view')

@login_required
def logout_view(request):
    """處理使用者登出"""
    logout(request)
    messages.success(request, "您已成功登出。")
    return redirect('login_view')

# ===================================================================
# II. 主要流程與選單 (Main Flow & Menus)
# ===================================================================

@login_required
def main_menu_view(request):
    """遊戲主選單，顯示五顆星球"""
    today = date.today()
    # 檢查今天是否已打卡
    can_check_in = not DailyCheckIn.objects.filter(user=request.user, check_in_date=today).exists()
    
    context = {
        'can_check_in': can_check_in
    }
    return render(request, 'main_menu.html', context)

# ===================================================================
# III. 遊戲核心系統 (Planet 1: Game Core)
# ===================================================================

@login_required
def planet_list_view(request):
    """顯示所有遊戲星球 (九大行星)"""
    planets = Planet.objects.all()
    return render(request, 'game/planet_list.html', {'planets': planets})

@login_required
def chapter_list_view(request, planet_id):
    """顯示特定星球下的所有章節"""
    planet = get_object_or_404(Planet, pk=planet_id)
    chapters = Chapter.objects.filter(planet=planet).order_by('chapter_number')
    
    # 取得使用者在這些章節的進度
    progress = UserProgress.objects.filter(user=request.user, chapter__in=chapters).values('chapter_id', 'status')
    progress_map = {p['chapter_id']: p['status'] for p in progress}
    
    for chapter in chapters:
        chapter.status = progress_map.get(chapter.chapter_id, 'locked')
    
    # 第一個章節預設解鎖
    if chapters and chapters.first().status == 'locked':
        chapters.first().status = 'unlocked'

    return render(request, 'game/chapter_list.html', {'planet': planet, 'chapters': chapters})

@login_required
def visual_novel_view(request, chapter_id):
    """視覺小說呈現頁面"""
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    dialogues = Dialogue.objects.filter(chapter=chapter).order_by('sequence')
    return render(request, 'game/visual_novel.html', {'chapter': chapter, 'dialogues': dialogues})

@login_required
def quiz_view(request, chapter_id):
    """問答遊戲的核心視圖"""
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    
    # 處理回答
    if request.method == 'POST':
        user_answer = request.POST.get('answer')
        quiz_state = request.session.get('quiz_state', {})
        
        current_q_id = quiz_state['question_ids'][quiz_state['current_index']]
        current_question = Question.objects.get(pk=current_q_id)
        
        if user_answer != current_question.correct_answer:
            quiz_state['wrong_answers'] += 1

        if quiz_state['wrong_answers'] >= 5:
            del request.session['quiz_state']
            return render(request, 'game/quiz_failed.html', {'chapter': chapter})
        
        quiz_state['current_index'] += 1
        
        if quiz_state['current_index'] >= len(quiz_state['question_ids']):
            record = process_quiz_results(request.user, chapter, quiz_state['wrong_answers'])
            del request.session['quiz_state']
            return redirect('quiz_result_view', record_id=record.record_id)

        request.session['quiz_state'] = quiz_state
        return redirect('quiz_view', chapter_id=chapter.id)

    # 開始新測驗
    else:
        # 從題庫中隨機抽取題目
        easy_q = list(Question.objects.filter(chapter=chapter, difficulty='easy').values_list('id', flat=True))
        medium_q = list(Question.objects.filter(chapter=chapter, difficulty='medium').values_list('id', flat=True))
        hard_q = list(Question.objects.filter(chapter=chapter, difficulty='hard').values_list('id', flat=True))

        question_ids = (
            random.sample(easy_q, min(len(easy_q), 5)) +
            random.sample(medium_q, min(len(medium_q), 5)) +
            random.sample(hard_q, min(len(hard_q), 5))
        )
        
        request.session['quiz_state'] = {
            'chapter_id': chapter_id,
            'question_ids': question_ids,
            'current_index': 0,
            'wrong_answers': 0,
        }
        
        current_q_id = question_ids[0]
        question = Question.objects.get(pk=current_q_id)
        return render(request, 'game/quiz.html', {'chapter': chapter, 'question': question})

def process_quiz_results(user, chapter, wrong_answers):
    """測驗結束後的後端處理邏輯 (不是一個 view)"""
    stars_earned = 0
    if wrong_answers == 0: stars_earned = 3
    elif 1 <= wrong_answers <= 2: stars_earned = 2
    elif 3 <= wrong_answers <= 4: stars_earned = 1

    record = QuizRecord.objects.create(user=user, chapter=chapter, correct_count=15 - wrong_answers, stars_earned=stars_earned)

    if stars_earned >= 2:
        next_chapters = Chapter.objects.filter(planet=chapter.planet, chapter_number__gt=chapter.chapter_number).order_by('chapter_number')
        if next_chapters.exists():
            next_chapter = next_chapters.first()
            UserProgress.objects.update_or_create(user=user, chapter=next_chapter, defaults={'status': 'unlocked'})
    
    if stars_earned == 3 and not GrowthTrack.objects.filter(quiz_record__user=user, quiz_record__chapter=chapter).exists():
        GrowthTrack.objects.create(quiz_record=record, achievement=f"完美通關 {chapter.title}！")
        user.diamonds += 1
        user.save(update_fields=['diamonds'])
        avatar_path_to_unlock = f'img/avatars/chapter_{chapter.id}.png' # 這裡的路徑您可以自訂
        UnlockedAvatar.objects.get_or_create(user=user, avatar_path=avatar_path_to_unlock)
    
    return record # 回傳記錄物件，方便重定向

@login_required
def quiz_result_view(request, record_id):
    """顯示測驗結果"""
    record = get_object_or_404(QuizRecord, pk=record_id, user=request.user)
    return render(request, 'game/quiz_result.html', {'record': record})


# ===================================================================
# IV. 周邊系統 (Other Planets & Features)
# ===================================================================

@login_required
def full_story_list_view(request):
    """星球2: 完整故事列表"""
    # 假設玩家完成(2星以上)即可解鎖完整故事
    completed_chapters_ids = QuizRecord.objects.filter(user=request.user, stars_earned__gte=2).values_list('chapter_id', flat=True)
    FullStory.objects.filter(chapter_id__in=completed_chapters_ids).update(is_unlocked=True)
    
    stories = FullStory.objects.all().order_by('planet', 'chapter__chapter_number')
    return render(request, 'features/full_story_list.html', {'stories': stories})

@login_required
def ai_school_view(request):
    """星球3: AI小學堂 (框架)"""
    if request.method == 'POST':
        # user_question = request.POST.get('question')
        # ai_answer = call_gemini_api(user_question) # 呼叫 AI API
        # return JsonResponse({'answer': ai_answer})
        return JsonResponse({'answer': "AI 回答功能開發中，請期待！"})
    return render(request, 'features/ai_school.html')

@login_required
def settings_view(request):
    """星球4: 設定頁面"""
    if request.method == 'POST':
        # ... 處理音量、字體等設定的儲存 ...
        if request.user.is_guest:
            # 處理訪客帳號綁定邏輯
            # ...
            messages.success(request, "帳號已成功綁定！")
        return redirect('settings_view')
        
    settings, created = UserSetting.objects.get_or_create(user=request.user)
    return render(request, 'features/settings.html', {'settings': settings})

@login_required
def growth_track_view(request):
    """星球5: 成長軌跡"""
    records = QuizRecord.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'features/growth_track.html', {'records': records})

@login_required
def avatar_inventory_view(request):
    """頭像更換頁面"""
    if request.method == 'POST':
        selected_avatar = request.POST.get('avatar')
        if UnlockedAvatar.objects.filter(user=request.user, avatar_path=selected_avatar).exists() or selected_avatar == 'img/avatars/default.png':
            request.user.user_avatar = selected_avatar
            request.user.save(update_fields=['user_avatar'])
            messages.success(request, "頭像已更新！")
        return redirect('avatar_inventory_view')

    unlocked_avatars = UnlockedAvatar.objects.filter(user=request.user)
    return render(request, 'features/avatar_inventory.html', {'unlocked_avatars': unlocked_avatars})

@login_required
def daily_check_in_view(request):
    """處理每日打卡"""
    today = date.today()
    user = request.user
    
    if DailyCheckIn.objects.filter(user=user, check_in_date=today).exists():
        messages.warning(request, "您今天已經打過卡了！")
        return redirect('main_menu')

    DailyCheckIn.objects.create(user=user, check_in_date=today)
    
    # 檢查是否連續7天
    consecutive_days = 0
    for i in range(14): 
        d = today - timedelta(days=i)
        if DailyCheckIn.objects.filter(user=user, check_in_date=d).exists():
            consecutive_days += 1
        else:
            break
    
    if consecutive_days > 0 and consecutive_days % 7 == 0:
        user.diamonds += 1
        user.save(update_fields=['diamonds'])
        messages.success(request, f"恭喜您連續打卡 {consecutive_days} 天，獲得 1 顆鑽石！")
    else:
        messages.success(request, "打卡成功！")

    return redirect('main_menu')