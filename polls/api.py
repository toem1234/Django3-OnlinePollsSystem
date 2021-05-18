from .models import Question,Choice,Vote
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import QuestionSerializer,ChoiceSerializer,VoteSerializer,CloseVoteSerializer
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly 
from rest_framework.pagination import PageNumberPagination,NotFound
from rest_framework.authentication import BasicAuthentication,SessionAuthentication
# from rest_framework.settings import api_settings
from django.http import Http404
from pprint import pprint
from django.utils import timezone
from django.db.models import Sum
from django.db import transaction

class CustomPaginator(PageNumberPagination):
    page_size = 10
    def generate_respone(self,query_set,serializer_obj,request):
        try:
            pprint(request.query_params)
            if "all" in request.query_params:
                print("In")
                all = request.query_params["all"] 
                print(type(all))
                if all == "true":
                    serializer = serializer_obj(query_set,many=True)
                    return Response(serializer.data)
                else:
                    return Response({"error" :  "No result found for the requested page"},status=status.HTTP_400_BAD_REQUEST)
            else:
                data = self.paginate_queryset(query_set,request)
                serializer = serializer_obj(data,many=True)
                return self.get_paginated_response(serializer.data)
        except Exception as ex:
            return Response({"error" : ex.__str__()},status=status.HTTP_400_BAD_REQUEST)

class PollList(APIView):
    """
    List All Question and Choics, Create New Polls.
    """
    authentication_classes = [BasicAuthentication,SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    
    def get(self,request):
        question = Question.objects.all()
        paginator = CustomPaginator()
        response = paginator.generate_respone(question,QuestionSerializer,request)
        return response
        
    def post(self,request):
        serializer = QuestionSerializer(data=request.data)
        pprint(serializer)
        if serializer.is_valid():
            serializer.save(created_by = request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class PollDetail(APIView):
    """
    Retrieve, update or delete a Polls instance.
    """

    # permission_classes =[permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly,]
    authentication_classes = [BasicAuthentication,SessionAuthentication]
    permission_classes =[permissions.IsAuthenticated,IsOwnerOrReadOnly,]

    def get_object(self,pk):
        try:
            question = Question.objects.get(pk=pk)
            self.check_object_permissions(self.request,question)
            return question
        except Question.DoesNotExist:
            raise Http404

    def get(self,request,pk):
        question = self.get_object(pk)
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    def put(self,request,pk):
        question = self.get_object(pk)
        serializer = QuestionSerializer(question,data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by = request.user,updated_at = timezone.now() )
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,request,pk):
        question = self.get_object(pk)
        serializer = CloseVoteSerializer(question,data=request.data,partial = True)
        if serializer.is_valid():
            serializer.save(updated_by = request.user,updated_at = timezone.now() )
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk,format=None):
        
        try:
            with transaction.atomic():
                question = self.get_object(pk)
                question = Question.objects.get(pk = pk)
                count = Choice.objects.filter(question = question).aggregate(total = Sum('count_vote'))
                if count['total'] > 0:
                    return Response({'error': "ลบแบบสอบถามไม่สำเร็จ เนื่องจากแบบสอบถามเก็บบันทึกผล Vote แล้ว"},status=status.HTTP_400_BAD_REQUEST)
                # print(question.choices.all())
                question.choices.all().delete()
                question.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Question.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
                return Response({"error": ex.__str__()})