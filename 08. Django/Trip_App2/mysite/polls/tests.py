import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days = 1, seconds = 1)
        old_question = Question(pub_date = time)
        self.assertIs(old_question.was_published_recently, False)

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days = days)
    return Question.objects.create(question_text=question_text, pub_date = time)

class QuestionIndexViewTests(TestCase):
    # 사용 가능한 투표가 없다는 것을 출력 + latest_question_list가 비어 있음을 확인
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list', []])
    
    # 질문을 생성하고 그 질문이 리스트에 나타나는 지 확인
    def test_past_questions(self):
        question = create_question(question_text = "Past question.", days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_qeustion_list'],
            [question]
        )
    
    # 미래의 pub_date로 질문을 만듬.
    def test_future_question(self):
        create_question(question_text="Future question", days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_questions(self):
        question = create_question(question_text = "Past question", days = -30)
        create_question(question_text="Future qustion.", days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )

    def test_two_past_question(self):
        question1 = create_question(question_text = "Past question 1", days = -30)
        question2 = create_question(question_text = "Past question 2", days = -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1]
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text = "Future question", days = 5)
        url = reverse('polls:detail', args = (future_question.id, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text = 'Past Question', days = -5)
        url = reverse('polls:detail', args = (past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)