from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib import auth
from django.db import IntegrityError,transaction
import re
from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponse


# Create your views here.

class SignupView(View):
    def get(self,request):
        return render(request,'accounts/signup.html')

    def post(self,request):
        reason = CsrfViewMiddleware().process_view(request,None,(),{})
        if reason is not None:
            return render(request,'accounts/signup.html',{'error': "invalid request"})
        try:
            with transaction.atomic():
                if request.POST['username'].strip() not in [None,''] \
                and request.POST['email'].strip() not in [None,''] \
                and request.POST['first_name'].strip() not in [None,''] \
                and request.POST['last_name'].strip() not in [None,''] \
                and request.POST['password'].strip() not in [None,''] \
                and request.POST['confirm_password'].strip() not in [None,'']:
                    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
                    if not re.search(regex,request.POST['email']):
                        return render(request,'accounts/signup.html',{'error': 'กรุณาระบุ email ให้ถูกต้อง'})
                        
                    if request.POST['password'] == request.POST['confirm_password']:
                        try:
                            user = User.objects.get(username = request.POST['username'])
                            return render(request,'accounts/signup.html',{'error': 'ชื่อผู้ใช้นี้ ถูกลงทะเบียนแล้ว'})
                        except User.DoesNotExist:
                            user = User.objects.create_user(request.POST['username'],request.POST['email'],request.POST['password'])
                            user.first_name = request.POST['first_name']
                            user.last_name = request.POST['last_name']
                            user.save()
                            auth.login(request,user)
                            return redirect('polls:IndexView')
                    else:
                        return render(request,'accounts/signup.html',{'error': 'รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน'})
                else:
                    return render(request,'accounts/signup.html',{'error': 'กรอกข้อมูลให้ครบถ้วน'})
        except IntegrityError as ex:
            return render(request,'accounts/signup.html',{'error': ex.__str__()})

class LoginView(View):
    def get(self,request):
        return render(request,'accounts/login.html')

    def post(self,request):
        reason = CsrfViewMiddleware().process_view(request,None,(),{})
        if reason is not None:
            return render(request,'accounts/login.html',{'error': "invalid request." })
        try:
            if request.POST['username'].strip() not in [None,''] and request.POST['password'].strip() not in [None,''] :
                username = request.POST['username']
                password = request.POST['password']
                user = auth.authenticate(username=username,password=password)
                # print(username)
                if user is not None:
                    auth.login(request,user)
                    # print("in")
                    return redirect('polls:IndexView')
                else:
                    return render(request,'accounts/login.html',{'error':'ชื่อผู้ใช้ หรือ รหัสผ่านไม่ถูกต้อง.'})
            else:
                return render(request,'accounts/login.html',{'error':'กรอกข้อมูลให้ครบถ้วน.'})
        except Exception as ex:
                return render(request,'accounts/login.html',{'error': ex.__str__()})

class LogoutView(View):
    def post(self,request):
        reason = CsrfViewMiddleware().process_view(request,None,(),{})
        if reason is not None:
            return HttpResponse('invalid request.')
        auth.logout(request)
        return render(request,'accounts/logout.html')

class InfoView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,'accounts/info.html')

    def post(self,request):
        reason = CsrfViewMiddleware().process_view(request,None,(),{})
        if reason is not None:
            return render(request,'accounts/info.html',{'error': 'invalid request.'})
        try:
            if request.POST['info-firstname'].strip() not in [None, ''] and request.POST['info-lastname'].strip() not in [None,'']:
                first_name = request.POST['info-firstname']
                last_name = request.POST['info-lastname']
                user = User.objects.get(username=request.user)
                if user:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                    return render(request,'accounts/info.html',{'success': 'อัพเดตข้อมูลสำเร็จ!'})
                else:
                    return render(request,'accounts/info.html',{'error': 'เกิดข้อผิดพลาดในการอัพเดตข้อมูล หรือไม่พบ ชื่อผู้ใช้รายนี้'})
            else:
                return render(request,'accounts/info.html',{'error': 'กรอกข้อมูลไม่พบถ้วน'})

        except Exception as ex:
            return render(request,'accounts/info.html',{'error': ex.__str__()})