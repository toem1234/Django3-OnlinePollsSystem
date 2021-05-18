from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Question(models.Model):
    name = models.CharField(max_length=300)
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='created_by_question')
    updated_by = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='updated_by_question',null=True)
    
    class Meta:
        ordering = ('-id',)
    def __str__(self):
        return self.name

    

class Choice(models.Model):
    question = models.ForeignKey(Question,on_delete=models.DO_NOTHING,related_name='choices')
    name = models.CharField(max_length=100)
    count_vote = models.IntegerField(default=0)

    class Meta:
        ordering = ('-id',)
    def __str__(self):
        return self.name

class Vote(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='votes',null=True)
    choice = models.ForeignKey(Choice,on_delete=models.DO_NOTHING,related_name='votes')
    voted_at = models.DateTimeField(auto_now_add=True)
