from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Question, Tag, Profile
from .forms import LoginForm, RegisterForm, SettinsForm, AskForm, AnswerForm
from django.contrib import auth
from django.urls import reverse
from django.shortcuts import get_object_or_404

def paginate(objects_list, request, per_page=10):
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

def get_base_context():
    return{
        'popular_tags' : Tag.objects.get_popular(), 
        #'members' : Profile.objects.get_popular_users()
    }

def get_default_context(page):
    return{
        'questions': page.object_list, 
        'page_obj' : page,
        'popular_tags' : Tag.objects.get_popular(), 
        #'members' : Profile.objects.get_popular_users()
    }

def get_question_context(request, question_id):
    question_obj = get_object_or_404(Question, id=question_id)
    page = paginate(question_obj.answers.all(), request)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question_obj
            answer.author = request.user.profile  # Предполагается, что у вас есть связь между User и Profile
            answer.save()
            return f"{reverse('one_question', kwargs={'question_id': question_id})}#answer-{answer.id}"
    else:
        form = AnswerForm()
    context = get_base_context()
    context['form'] = form
    context['question'] = question_obj
    context['answers'] = page.object_list
    context['page_obj'] = page
    return context

def get_tag_context(tag_name, page):
    return{
        'tag_name':tag_name,
        'questions': page.object_list,
        'page_obj' : page, 
        'popular_tags' : Tag.objects.get_popular(),
        #'members' : Profile.objects.get_popular_users()
    }


def get_login_context(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                continue_url = request.GET.get('continue', reverse('index'))
                return continue_url
            else:
                form.add_error('password', 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
    context = get_base_context()
    context['form'] = form
    return context

def get_signup_context(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return reverse('index')
    else:
        form = RegisterForm()
    context = get_base_context()
    context['form'] = form
    return context

def get_settings_context(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = SettinsForm(request.POST, request.FILES, instance=user, profile=profile)
        if form.is_valid():
            form.save()
            return 'settings'
    else:
        form = SettinsForm(instance=user, profile=profile)
    context = get_base_context()
    context['form'] = form
    return context

def get_ask_context(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user.profile)
            return question.get_absolute_url()
    else:
        form = AskForm()
    context = get_base_context()
    context['form'] = form
    return context