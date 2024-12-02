from django import forms
from django.contrib.auth.models import User

# 创建表单，用于提交用户名和密码
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='密码', widget=forms.PasswordInput) # 注册时第一次输入的密码
    password2 = forms.CharField(label='再次输入密码', widget=forms.PasswordInput) # 确认密码（第二次）
    class Meta:
        model = User
        fields = ('username',)

    # 检查两次输入的密码是否一致
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']: # 如果两次输入的密码不一致，则抛出错误信息
            raise forms.ValidationError("两次输入的密码不一致")
        return cd['password2'] # 保存第二次（确认）的密码