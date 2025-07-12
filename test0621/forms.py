from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from .models import User


# --- 表單 1：暱稱修改表單 (新增) ---
class NicknameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname']
        labels = {
            'nickname': '新的暱稱'
        }
        help_texts = {
            'nickname': '（可隨時修改）'
        }

# --- 表單 2：密碼修改表單 (新增) ---
# 繼承內建的 PasswordChangeForm，它會自動處理舊密碼驗證
class CustomPasswordChangeForm(PasswordChangeForm):
    # 我們可以覆寫欄位來加上 CSS class，使其更好看
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': '請輸入您的舊密碼'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '請輸入您的新密碼'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '請再次輸入新密碼'})


class UserRegistrationForm(UserCreationForm):
    """
    使用者註冊表單。
    我們繼承 Django 內建的 UserCreationForm，它已經處理了使用者名稱、
    密碼和重複密碼的驗證，非常方便。我們只需要加入我們自訂的欄位。
    """
    # 我們在 User 模型中新增的額外欄位
    nickname = forms.CharField(max_length=50, required=False, label="暱稱", help_text="（選填）")
    email = forms.EmailField(required=False, label="電子郵件", help_text="（選填，建議填寫以便找回密碼）")

    class Meta(UserCreationForm.Meta):
        # 指定這個表單對應到我們的自訂 User 模型
        model = User
        # 指定在表單上要顯示的欄位順序
        fields = ('username', 'nickname', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        # 重寫 save 方法，以便在建立使用者後，儲存我們新增的 nickname 欄位
        user.nickname = self.cleaned_data.get("nickname")
        user.email = self.cleaned_data.get("email") # 從乾淨資料中獲取 email
        if commit:
            user.save()
        return user

# 表單 2：訪客升級專用表單
class GuestUpgradeForm(forms.ModelForm):
    """專門用於訪客升級為正式帳號的表單"""
    password2 = forms.CharField(label="確認密碼", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        help_texts = {
            'username': '設定後不可更改。',
            'email': '（選填）設定後可用於找回密碼。',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()
        self.fields['email'].required = False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username.lower().startswith('guest_'):
            raise forms.ValidationError("使用者名稱不能以 'guest_' 開頭。")
        if User.objects.filter(username=username, is_guest=False).exists():
            raise forms.ValidationError("這個使用者名稱已經被使用了。")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("這個 Email 已經被其他帳號使用了。")
        return email

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("兩次輸入的密碼不一致。")
        validate_password(password)
        return password2

# 表單 3：已登入用戶綁定 Email 的表單
class EmailBindForm(forms.Form):
    """專門用於使用者綁定 Email 的表單"""
    email = forms.EmailField(label="要綁定的電子郵件", required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': '請輸入您的電子郵件'}
    ))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("這個 Email 已經被其他帳號使用了。")
        return email
    
class UserLoginForm(forms.Form):
    """
    使用者登入表單。
    登入不需要與模型直接綁定，所以我們繼承 forms.Form 即可。
    """
    username = forms.CharField(max_length=150, label="使用者名稱", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '請輸入您的使用者名稱'}
    ))
    password = forms.CharField(label="密碼", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '請輸入您的密碼'}
    ))