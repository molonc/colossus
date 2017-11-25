"""
Created on June 17, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

#============================
# Django imports
#----------------------------
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from core.helpers import Render


#============================
# Helpers
#----------------------------
def user_authenticate(username, password):
    user = authenticate(
        username=username,
        password=password
        )
    if user is not None:
        if user.is_active:
            res = 'active'
        else:
            res = 'inactive'
    else:
        res = 'invalid'
    return user, res


#============================
# Login view
#----------------------------
@Render("account/login.html")
def login_view(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user, res = user_authenticate(username, password)
        if res == 'active':
            login(request, user)
            print "%s, successully logged in." % username
            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                return HttpResponseRedirect(reverse("index"))
        elif res == 'inactive':
            msg = "This account has been disabled."
            print msg
            messages.error(request, msg)
        else:
            msg = "The username and/or password were incorrect."
            print msg
            messages.error(request, msg)

    contex = {
        'next': next_url,
        }
    return contex


#============================
# Logout view
#----------------------------
def logout_view(request):
    logout(request)
    msg = "Successfully logged out."
    print msg
    messages.success(request, msg)
    return HttpResponseRedirect(reverse("index"))


#============================
# Password update view
#----------------------------
@Render("account/password_update.html")
@login_required()
def password_update(request):
    if request.method == 'POST':
        new_pwd = request.POST.get('new_pwd')
        re_new_pwd = request.POST.get('re_new_pwd')
        if new_pwd != re_new_pwd:
            msg = "The fields don't match."
            messages.error(request, msg)

        else:
            username = request.POST.get('username')
            curr_pwd = request.POST.get('curr_pwd')
            user, res = user_authenticate(username, curr_pwd)
            if res == 'active':
                user.set_password(new_pwd)
                user.save()
                login(request, user)
                msg = "Successfully changed the password!"
                print msg
                messages.success(request, msg)
                return HttpResponseRedirect(reverse("index"))
            elif res == 'inactive':
                msg = "This account has been disabled."
                print msg
                messages.error(request, msg)
            else:
                msg = "The current password was incorrect."
                print msg
                messages.error(request, msg)

    contex = {}
    return contex


#============================
# Password forget view
#----------------------------
@Render("account/password_forget.html")
def password_forget(request):
    contex = {}
    return contex
