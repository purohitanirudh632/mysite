from contextlib import _RedirectStream
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.http import HttpResponse
# Create your views here.
from .models import *
from django.contrib.auth.models import User   #gives acess to the authorisedd users 
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import datetime
from django.conf import settings
import jwt


def generate_jwt_token(id):
    payload = {
        'id': id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=5),
            'iat': datetime.datetime.now(datetime.timezone.utc)
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')#encoding algo
    
    jwt_token =  token,  payload['exp'] 

    return jwt_token

def is_authenticated(request):
    token = request.session.get("token", False)
    if token:
        payload = jwt.decode(token, settings.SECRET_KEY, options={"verify_signature": False},  algorithms=['HS256'])
        expiry = payload.get("exp", False)
        print("\n\n", payload, "\n\n")
        if expiry:
            timestamp = datetime.datetime.now().timestamp() - expiry
            if timestamp <= 0 :
                return True
    return False


def home_page(request):
    normal = "this is normal"
    context ={"title":normal}
    
    if is_authenticated(request):
        return render(request,"home.html")
    logout(request)
    return redirect("signin")


    
def signup(request):

    if request.method =="POST":
       username = request.POST['username']
       fname = request.POST['username']
       lname = request.POST ['lname']
       email= request.POST['email']
       pass1 = request.POST['pass1']
       pass2 = request.POST['pass2']

         
       if User.objects.filter(username =username):
          messages.error(request,"username already exists please try other username")
          return redirect('signup')
        
       if pass1 != pass2:
          messages.error(request,"passwords did not match")
          return redirect('signup')

       myuser = User.objects.create_user(username,email,pass1) 
       myuser.first_name = fname
       myuser.last_name=lname
       
       myuser.save()

       messages.success(request,"your account has been created")
   
       return redirect('signin')

    return render(request,"registration/signup.html")    



def signin(request):

    if request.method == 'POST':
       username = request.POST['username']
       pass1 = request.POST['pass1']

       user = authenticate(username =username,password = pass1)
       
       if user is not None:
        fname = user.first_name
        token, expiry = generate_jwt_token(user.id)
        request.session["token"] = token
        login(request,user)
        return redirect('/')
    
       else:
        messages.error(request,"bad credentials")
        return redirect('/')

    return render(request,"registration/login.html")  



def signout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect('/')
    