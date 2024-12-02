from django.shortcuts import render
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required

# 检查用户是否成功登录，登录则重定向到主页面
@login_required
def index(request):
    return render(request, 'app/index.html')

# 用户注册
def register(request):
    if request.method == "POST": # 如果是‘POST’请求
        user_form = UserRegistrationForm(request.POST) # 实例化表单对象
        if user_form.is_valid(): # 验证表单数据是否合法
            new_user = user_form.save(commit=False) # commit=False告诉Django先不提交到数据库
            new_user.set_password(user_form.cleaned_data['password']) # 使用set_password方法将用户的密码进行加密后再进行保存操作
            new_user.save()
            return render(request, 'account/register_done.html', {'new_user': new_user}) # 当用户注册成功，返回register_done页面
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form}) # 初始访问的时候返回register页面