import copy
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


QUESTIONS = []
ANSWERS = []
for i in range(30):
    QUESTIONS.append({
    'title': f'title {i}',
    'id': i,
    'text': f'text for {i}'
    })
    ANSWERS.append(f'text for {i}')


def paginate(objects_list, request, per_page=5):
    page_str = request.GET.get('page', '1')
    try:
        page_num = int(page_str)
    except (ValueError, PageNotAnInteger):
        page_num = 1
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page = paginator.page(1)
    return page

def index(request):
    page = paginate(QUESTIONS, request)
    return render(
        request, 'index.html', 
        context = {'questions': page.object_list, 'page_obj' : page}
    )


def hot(request):
    hot_questions = copy.deepcopy(QUESTIONS)
    hot_questions.reverse()
    page = paginate(hot_questions, request)
    return render(
        request, 'hot.html', 
        context = {'questions': page.object_list, 'page_obj' : page}
    )

def question(request, question_id):
    page = paginate(ANSWERS, request, 3)
    one_question = QUESTIONS[question_id]
    return render(
        request, 'one_question.html', 
        context = {'question' : one_question, 'answers' : page.object_list,'page_obj' : page}
    )


def login(request):
    return render(
        request, 'login.html'
    )

def signup(request):
    return render(
        request, 'signup.html'
    )

def ask(request):
    return render(
        request, 'ask.html'
    )

def tag(request):
    page = paginate(QUESTIONS, request)
    return render(
        request, 'tag.html', 
        context = {'questions': page.object_list, 'page_obj' : page}
    )
