from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    """
    使用者註冊表單。
    我們繼承 Django 內建的 UserCreationForm，它已經處理了使用者名稱、
    密碼和重複密碼的驗證，非常方便。我們只需要加入我們自訂的欄位。
    """
    # 我們在 User 模型中新增的額外欄位
    nickname = forms.CharField(max_length=50, required=False, label="暱稱", help_text="（選填）")
    email = forms.EmailField(required=True, label="電子郵件")

    class Meta(UserCreationForm.Meta):
        # 指定這個表單對應到我們的自訂 User 模型
        model = User
        # 指定在表單上要顯示的欄位順序
        fields = ('username', 'nickname', 'email')

    def save(self, commit=True):
        # 重寫 save 方法，以便在建立使用者後，儲存我們新增的 nickname 欄位
        user = super().save(commit=False)
        user.nickname = self.cleaned_data["nickname"]
        if commit:
            user.save()
        return user


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