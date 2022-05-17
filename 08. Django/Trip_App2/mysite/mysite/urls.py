"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    # 다른 URL 패턴을 포함할 때마다 항상 include()를 사용해야 함.
    # admin.site.urls가 유일한 예외임.
    path('admin/', admin.site.urls),

    # path 함수에는 route와 view(2개의 필수 인수) kwargs와 name(2개의 선택 가능 인수) 전달
    # route : URL 패턴을 가지는 문자열
    path('polls/', include('polls.urls'))
]
