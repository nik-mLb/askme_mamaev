import json
from cent import Client, PublishRequest
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Question, Tag, Profile, QuestionLike, Answer, AnswerLike
from .forms import LoginForm, RegisterForm, SettinsForm, AskForm, AnswerForm
from django.contrib import auth
from django.urls import reverse
from django.shortcuts import get_object_or_404
from askme_mamaev.settings import CENTRIFUGO_API_KEY, CENTRIFUGO_API_URL, CENTRIFUGO_SECRET_KEY, CENTRIFUGO_WS_URL
import jwt
import time
from django.core.cache import cache

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

def get_cache_cont():
    popular_tags = cache.get('popular_tags')
    members = cache.get('members')
    if not popular_tags:
        popular_tags = Tag.objects.get_popular()
        cache.set('popular_tags', popular_tags, 3600)  # Кэшируем на 1 час

    if not members:
        members = Profile.objects.get_popular_users()
        cache.set('members', members, 3600)  # Кэшируем на 1 час
    return popular_tags, members

def get_non_base_context(request):
    popular_tags, members = get_cache_cont()
    secret = CENTRIFUGO_SECRET_KEY
    ws_url = CENTRIFUGO_WS_URL
    if request.user.is_authenticated:
        claims = {"sub": str(request.user.profile.id), "exp": int(time.time()) + 5*60}
    else:
        claims = {"exp": int(time.time()) + 5*60}
    token = jwt.encode(claims, secret, "HS256")
    return{
        'popular_tags' : popular_tags, 
        'members' : members,
        'token': token,
        'ws_url': ws_url,
    }

def get_base_context(request):
    popular_tags, members = get_cache_cont()
    secret = CENTRIFUGO_SECRET_KEY
    ws_url = CENTRIFUGO_WS_URL
    if request.user.is_authenticated:
        claims = {"sub": str(request.user.profile.id), "exp": int(time.time()) + 5*60}
    else:
        claims = {"exp": int(time.time()) + 5*60}
    token = jwt.encode(claims, secret, "HS256")
    return{
        'popular_tags' : popular_tags, 
        'members' : members,
        'token': token,
        'ws_url': ws_url,
    }

def get_default_context(request, page):
    context = get_base_context(request)
    context['questions'] = page.object_list
    context['page_obj'] = page
    return context

def get_tag_context(request, tag_name, page):
    context = get_default_context(request, page)
    context['tag_name'] = tag_name
    return context

def get_question_context(request, question_id):
    question_obj = get_object_or_404(Question, id=question_id)
    has_liked = False
    sorted_answers = Question.objects.sorted_answers(question_id)
    answer_likes = []
    context = get_base_context(request)

    if request.user.is_authenticated:
        has_liked = QuestionLike.has_user_liked(request.user.profile, question_obj)
        for answer in sorted_answers:
            answer_has_like = AnswerLike.has_user_liked(request.user.profile, answer)
            answer_likes.append({
                'answer' : answer,
                'answer_has_like' : answer_has_like
            })
    else:
        answer_likes = [{'answer': answer, 'answer_has_like': False} for answer in sorted_answers]

    page = paginate(answer_likes, request)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            context['new_answer_id'] = answer.id
            answer.question = question_obj
            answer.author = request.user.profile  # Предполагается, что у вас есть связь между User и Profile
            answer.save()
            answer_likes.append({
                'answer' : answer,
                'answer_has_like' : False
            })
            page = paginate(answer_likes, request)
            client = Client(CENTRIFUGO_API_URL, CENTRIFUGO_API_KEY)
            paginator = page.paginator
            new_answer_page = paginator.num_pages
            redirect_url = reverse('one_question', args=[question_id]) + f"?page={new_answer_page}#answer_{answer.id}"
            data = {
                "answer": answer.body,
                "user_id": answer.author.id,
                "username": answer.author.user.username,
                "current": False  # Добавлено поле current
            }
            if answer.author.avatar:
                data["avatar"] = answer.author.avatar.url
            else:
                data["avatar"] =  "/static/img/base_avatar.jpg" 
            publish_request = PublishRequest(channel=str(question_id), data = data)
            try:
                result = client.publish(publish_request)
                print("Centrifugo publish result:", result)  # Логирование
            except Exception as e:
                print("Centrifugo publish error:", e)  # Логирование ошибок
            return redirect_url
    else:
        form = AnswerForm()
    context['form'] = form
    context['question'] = question_obj
    context['answers_likes'] = page.object_list
    context['page_obj'] = page
    context['has_liked'] = has_liked
    return context

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
                form.add_error('password', 'Invalid username or password.')
    else:
        form = LoginForm()
    context = get_non_base_context(request)
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
    context = get_non_base_context(request)
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
    context = get_base_context(request)
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
    context = get_base_context(request)
    context['form'] = form
    return context


def get_like_question_context(request, question_id):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user=request.user)
        question = get_object_or_404(Question, pk=question_id)
        existing_like = QuestionLike.objects.filter(user=profile, question=question).first()

        if existing_like:
            existing_like.delete()
        else:
            QuestionLike.objects.create(user=profile, question=question)
    return reverse('one_question', kwargs={'question_id': question_id})

def get_like_question_context_async(request, question_id):
    profile = get_object_or_404(Profile, user=request.user)
    question = get_object_or_404(Question, pk=question_id)
    existing_like = QuestionLike.objects.filter(user=profile, question=question).first()
    liked = False
    if existing_like:
        existing_like.delete()
    else:
        QuestionLike.objects.create(user=profile, question=question)
        liked = True

    question.update_like_count()
    return JsonResponse({
        'likes_count' : question.like_count,
        'liked': liked,
    })

def get_like_answer_context_async(request, question_id, answer_id):
    profile = get_object_or_404(Profile, user=request.user)
    question = get_object_or_404(Question, pk=question_id)
    answer = get_object_or_404(Answer, pk=answer_id)
    existing_like = AnswerLike.objects.filter(user=profile, answer=answer)
    liked = False
    if existing_like:
        existing_like.delete()
    else:
        AnswerLike.objects.create(user=profile, answer=answer)
        liked = True
    
    likes_count = answer.like_count
    return JsonResponse({
        'likes_count' : likes_count,
        'liked': liked,
    })

def get_correct_answer_context(request, question_id, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if answer.is_correct:
        answer.is_correct = False
    else:
        answer.is_correct = True
    answer.save()
    return JsonResponse({'is_correct': answer.is_correct})