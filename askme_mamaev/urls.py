"""
URL configuration for askme_mamaev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name = 'index'),
    path('hot/', views.hot, name = 'hot'),
    path('question/<int:question_id>', views.question, name = 'one_question'),
    path('admin/', admin.site.urls),
    path('login/', views.login, name = 'login'),
    path('signup/', views.signup, name = 'signup'),
    path('ask/', views.ask, name = 'ask'),
    path('tag/<str:tag_name>', views.tag, name = 'tag'),
    path('settings/', views.settings, name = 'settings'),
    path('logout', views.logout, name='logout'),
    path('like_question/<int:question_id>', views.like_question, name='like_question'),
    path('like_question_async/<int:question_id>', views.like_question_async, name='like_question_async'),
    path('like_answer_async/<int:question_id>/<int:answer_id>', views.like_answer_async, name='like_answer_async'),
    path('set_correct_answer/<int:question_id>/<int:answer_id>', views.set_correct_answer, name='set_correct_answer')
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 