from django.http.response import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib import auth
from django.db import IntegrityError,transaction
from .models import Question,Choice,Vote
from django.forms.models import model_to_dict
from django.http import HttpResponse
from pprint import pp, pprint
from django.db.models import F,Sum,Q,Value,IntegerField,CharField
from django.urls import reverse

# Create your views here.


def userVoted(request,question_id):
    try:
        question = Question.objects.get(pk = question_id)
        choices = Choice.objects.filter(question = question)
        extra = {}
        if not request.user:
            return None
        for c in choices:
            vote = Vote.objects.filter(user = request.user,choice = c)
            if vote:
                return vote
        return None
    except Exception as ex:
        return None

def countVotedInChoice(question_id):
    question = Question.objects.get(pk = question_id)
    count = Choice.objects.filter(question = question).aggregate(total = Sum('count_vote'))
    return int(count['total'])


def isOwner(request,question_id):
    if not request.user:
        return None
    try:
        owner = Question.objects.get(pk = question_id,created_by = request.user)
    except Question.DoesNotExist:
        return None
    except Exception as ex:
        print(ex.__str__())
        return None
    return True
 

def annotationTotalVoteQuestion(obj):
    total = countVotedInChoice(obj.id)
    obj.totalVote = total
    return obj
    

class CreateView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,'polls/create.html')
    def post(self,request):
        try:
            with transaction.atomic():
                if request.POST['question'].strip() in [None,'']:
                    return render(request,'polls/create.html',{'error': 'กรุณากรอกข้อมูลแบบสอบถาม'})
                count = 0
                choices = []
                for i in range(1,11):
                    if request.POST['choice{number}'.format(number = i)].strip() not in [None,'']:
                        count += 1
                        choices.append(i)
                if count < 2:
                    return render(request,'polls/create.html',{'error': 'ต้องระบุตัวเลือกอย่างน้อย 2 ตัวเลือก'})
                question = Question()
                question.name = request.POST['question']
                question.created_by = request.user
                question.save()
                for c in choices:
                    choice = Choice()
                    choice.question = question
                    choice.name = request.POST['choice{number}'.format(number = c)]
                    choice.save()
                ownQuestion = Question.objects.filter(created_by = request.user).order_by('-created_at')
                _questions = [ annotationTotalVoteQuestion(q)  for q in ownQuestion ]
                return redirect(reverse('polls:OwnView') + '?createSuccess=True')
        except IntegrityError as ex:
            return render(request,'polls/create.html',{'error': ex.__str__()})

class DetailView(View):
    def get(self,request,question_id = None):
        if question_id:
            try:
                voted = userVoted(request,question_id)
                question = Question.objects.get(pk=question_id)
                choices = Choice.objects.filter(question = question).order_by('id')
            except Question.DoesNotExist:
                return render(request,'404.html')
            except Exception as ex:
                return HttpResponse('Error : {error}'.format(error = ex.__str__()))
            if voted:
                return render(request,'polls/detail.html',{'question': question, 'choices' : choices, 'voted': voted[0].choice.id})
            else:
                return render(request,'polls/detail.html',{'question': question, 'choices' : choices })

    def post(self,request,question_id = None):
        if question_id:
            question = Question.objects.get(pk = question_id)
            choices = Choice.objects.filter(question = question).order_by('id')
            try:
                with transaction.atomic():
                    
                    _choices = [ model_to_dict(choice,"id") for choice in choices]
                    isFound = False
                    for c in _choices:
                        if c["id"] == int(request.POST['opt']):
                            isFound = True
                            choiceById = Choice.objects.get(pk = c["id"])
                            if request.user.is_authenticated:
                                voted = userVoted(request,question_id)
                                if voted:
                                    return render(request,"polls/detail.html",{'question': question, 'choices' : choices,'error': 'คุณได้ทำการ Vote แบบสอบถามนี้แล้ว' })    
                                vote = Vote(user = request.user,choice = choiceById)
                                vote.save()
                            else:
                                vote = Vote(choice = choiceById)
                                vote.save()

                            choiceById.count_vote = F('count_vote') + 1
                            choiceById.save()
                            return redirect('polls:ResultView',question_id = question_id )
                    if not isFound:
                        return render(request,"polls/detail.html",{'question': question, 'choices' : choices,'error': 'กรุณาเลือกตัวเลือก ก่อนกดปุ่มให้คะแนน vote' })
            except IntegrityError as ex:
                return render(request,"polls/detail.html",{'question': question, 'choices' : choices,'error': ex.__str__() })

class EditView(LoginRequiredMixin,View):
    def get(self,request,question_id=None):
        if question_id:
            try:
                if not isOwner(request,question_id):
                    return render(request,'404.html')
                question = Question.objects.get(pk=question_id)
            except Question.DoesNotExist:
                return render(request,'404.html')
            try:
                choices = Choice.objects.filter(question = question).order_by('id')
                return render(request,'polls/edit.html',{'question' : question,'choices': choices})
            except Exception as ex:
                return HttpResponse('Error : {error}'.format(error = ex.__str__()))
    def post(self,request,question_id=None):
        if question_id:
            if not isOwner(request,question_id):
                return render(request,'404.html')
            initQuestion = Question.objects.get(pk = question_id)
            initChoices = Choice.objects.filter(question = question_id)
            try:
                with transaction.atomic():
                    if request.POST['question_title'].strip() in [None,'']:
                        return render(request,'polls/edit.html',{'question' : initQuestion,'choices': initChoices,'error': 'กรุณากรอกข้อมูลหัวข้อแบบสอบถามให้ครบถ้วน เมื่อต้องการปรับปรุงข้อมูล'})

                    initQuestion.name = request.POST['question_title']
                    initQuestion.save()
                    _choices = [ model_to_dict(choice,"id") for choice in initChoices]

                    for c in _choices:
                        if request.POST['choice_{qid}'.format(qid = c['id'] )].strip() in [None,'']:
                            return render(request,'polls/edit.html',{'question' : initQuestion,'choices': initChoices,'error': 'กรุณากรอกข้อมูลตัวเลือกให้ครบถ้วน เมื่อต้องการปรับปรุงข้อมูล'})   

                    for c in _choices:
                        choice = Choice.objects.get(pk = c['id'])
                        choice.name = request.POST['choice_{qid}'.format(qid = c['id'] )]    
                        choice.save()
                    updateQuestion = Question.objects.get(pk = question_id)
                    updatedChoices = Choice.objects.filter(question = question_id)
                    return render(request,'polls/edit.html',{'question' : updateQuestion,'choices': updatedChoices,'success': 'ปรับปรุงแบบสอบถามสำเร็จ'})
            except IntegrityError as ex:
                return render(request,'polls/edit.html',{'question' : initQuestion,'choices': initChoices,'error': ex.__str__()})

class IndexView(View):
    def get(self,request):
        questions = Question.objects.filter(closed=False).order_by('-created_at')
        return render(request,'polls/index.html',{'questions': questions})

class OwnView(LoginRequiredMixin,View):
    def get(self,request):
        questions = Question.objects.filter(created_by = request.user).order_by('-created_at')
        _questions = [ annotationTotalVoteQuestion(q)  for q in questions ]
        return render(request,'polls/own.html',{'questions': questions})

class ResultView(View):
    colors = ['','bg-success','bg-info','bg-warning','bg-danger','#6c757d','#e578a0','#605ca8','#ffff00','#a52a2a']

    def get(self,request,question_id=None):
        if question_id:
            try:
                question = Question.objects.get(pk=question_id)
                owner = isOwner(request,question_id)
            except Question.DoesNotExist:
                return render(request,'404.html')
            try:
                choices = Choice.objects.filter(question = question).order_by('id')
                totalVote = 0
                choiceIds = []
                i = 0

                for c in choices:
                    totalVote += c.count_vote
                _choices = [ choice.__dict__ for choice in choices ]

                for c in _choices:
                    choiceIds.append(c['id'])
                    
                    c['color'] = self.colors[i]
                    if totalVote == 0:
                        c['percent'] = 0
                    else:
                        c['percent'] = round(c['count_vote'] * 100 / totalVote,2)
                    i += 1

                guestVote = Vote.objects.filter(Q(choice_id__in=choiceIds) & Q(user_id__isnull=True)).count()
                memberVote = Vote.objects.filter(Q(choice_id__in=choiceIds) & Q(user_id__isnull=False)).count()

                _question = Question.objects.annotate(totalVote = Value(0,output_field=IntegerField())).get(pk=question_id)
                count = countVotedInChoice(question_id)
                if count > 0:
                    _question.totalVote = count
                return render(request,'polls/result.html',{'question': _question,'choices': _choices,'totalVote' : totalVote,'guestVote': guestVote,'memberVote': memberVote, 'owner' : owner})
            except Exception as ex:
                return HttpResponse('Error : {error}'.format(error = ex))