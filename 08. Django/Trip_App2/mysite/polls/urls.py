from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    # path 함수에는 route와 view(2개의 필수 인수) kwargs와 name(2개의 선택 가능 인수) 전달
    # Route : 요청이 처리될때, Django는 urlpatterns의 첫 번째 패턴부터 시작하여, 일치하는 패턴을 찾을 때까지 요청된 URL을 각 패턴과 리스트의 순서대로 비교
    # View : Django에서 일정한 패턴을 찾으면, HttpRequest 객체를 첫번째 인수로 하고 경로로부터 캡처된 값을 키워드 인수로 하여 특정한 view 함수 호출
    # name : URL에 이름을 지으면, 템플릿을 포함한 Django 어디에서나 참조 가능.
    path('', views.IndexView.as_view(), name = 'index'),
    path('<int:pk>/', views.DetailView.as_view(), name = 'detail'),
    path('<int:pk>/results/', views.ResultView.as_view(), name = 'results'),
    path('<int:question_id>/vote/', views.vote, name = 'vote')
]