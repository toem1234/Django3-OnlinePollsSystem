from rest_framework import serializers
from .models import Question,Choice,Vote
from pprint import pprint
from rest_framework import status
from django.db import transaction
import traceback



class ChoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Choice
        fields = ['id','name','count_vote']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id','name','closed','choices','created_at','updated_at','created_by','updated_by']
        extra_kwargs = {
            'created_by': {'required': False}
        }
    choices = ChoiceSerializer(many=True)

    def create(self,validated_data):
        try:
            with transaction.atomic():
                choices = validated_data.pop('choices')
                question = Question.objects.create(**validated_data)
                for choice in choices:
                    Choice.objects.create(question=question,**choice)
                serializers.ValidationError()
                return question
        except Exception as ex:
            res = serializers.ValidationError(detail= ex.__str__(),code="error")
            res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise res

    def update(self,instance,validated_data):
        try:
            pprint(validated_data)
            with transaction.atomic():
                choices = validated_data.pop('choices')
                instance.name = validated_data.get('name',instance.name)
                instance.closed = validated_data.get('closed',instance.closed)
                instance.created_at = validated_data.get('created_at',instance.created_at)
                instance.updated_at = validated_data.get('updated_at',instance.updated_at)
                instance.created_by = validated_data.get('created_by',instance.created_by)
                instance.updated_by = validated_data.get('updated_by',instance.updated_by)
                instance.save()
                for choice in choices:
                    if not 'id' in choice:
                        raise Exception('invalid data update.')
                    c = Choice.objects.get(pk=choice["id"],question=instance)
                    c.name = choice["name"]
                    c.save()
                return instance
        except Exception as ex:
            res = serializers.ValidationError(detail=ex.__str__(),code="error")
            res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise res

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['user','choice','voted_at']


class CloseVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
    
    def update(self,instance,validated_data):
        try:
            with transaction.atomic():
                instance.name = validated_data.get('name',instance.name)
                instance.closed = validated_data.get('closed',instance.closed)
                instance.created_at = validated_data.get('created_at',instance.created_at)
                instance.updated_at = validated_data.get('updated_at',instance.updated_at)
                instance.created_by = validated_data.get('created_by',instance.created_by)
                instance.updated_by = validated_data.get('updated_by',instance.updated_by)
                instance.save()
                return instance
        except Exception as ex:
            print(traceback.format_exc())
            res = serializers.ValidationError(detail=ex.__str__(),code='error')
            res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise res