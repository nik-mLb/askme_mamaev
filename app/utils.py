from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Question, Tag, Profile

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
        # 'members' : Profile.objects.get_popular_users()
    }

def get_default_context(page):
    return{
        'questions': page.object_list, 
        'page_obj' : page,
        'popular_tags' : Tag.objects.get_popular(), 
        'members' : Profile.objects.get_popular_users()
    }

def get_question_context(question_obj, page):
    return {
        'question' : question_obj, 
        'answers' : page.object_list,
        'page_obj' : page, 
        'popular_tags' : Tag.objects.get_popular(), 
        #'members' : Profile.objects.get_popular_users()
    }

def get_tag_context(tag_name, page):
    return{
        'tag_name':tag_name,
        'questions': page.object_list,
        'page_obj' : page, 
        'popular_tags' : Tag.objects.get_popular(),
        #'members' : Profile.objects.get_popular_users()
    }