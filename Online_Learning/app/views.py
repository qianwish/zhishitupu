import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def graph(request):
    return render(request, 'app/graph.html')
from .forms import SearchForm
@login_required
def search(request):
    result = "" # 初始化变量
    if request.method == "POST": # 如果是‘POST’请求
        question_form = SearchForm(request.POST) # 实例化表单对象
        if question_form.is_valid(): # 验证表单数据是否合法
            data = question_form.cleaned_data # question_form.cleaned_data是字典类型，得到全部字段的有效值，即干净的数据
            result = requests.get('http://127.0.0.1:5000/query/' + data['question']).text # 向后端发送GET请求
    else: #不是POST请求时，直接返回没有查询结果的表单
        question_form = SearchForm()
    # 将{"question_form": question_form, "result": result}的json数据传递给search.html
    return render(request, 'app/search.html', {"question_form": question_form, "result": result})