from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Question, Choice
from django.urls import reverse
from django.views import generic
from django.utils import timezone

# ListView : 개체 목록 표시
# DetailView : 턱정 개체 유형에 대한 세부 정보 페이지 표시
# DetailView는 URL에서 캡처된 기본 키값이 "pk"라고 기대하기 때문에 question_id를 pk로 변경한다.
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.filter(
            pub_date__lte = timezone.now()
        ).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte= timezone.now())

class ResultView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice']) # request.Post는 키로 전송된 자료에 접근할 수 있도록 해주는 사전과 같은 객체
                # 위의 경우 request.POST는 선택된 설문의 ID를 문자열로 반환함.
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # reverse는 /polls/3/results 반환함. 여기서 3은 question.id이며 이렇게 리디렌션된 URL은 최종 페이지를 표시하기 위해 'resutls' 뷰를 호출함.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))