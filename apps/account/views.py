"""
Created on June 17, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

#============================
# Django imports
#----------------------------
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

#============================
# Login view
#----------------------------
def login_view(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(
            username=username,
            password=password
            )
        if user is not None:
            if user.is_active:
                login(request, user)
                print "%s, successully logged in." % user.username
                if next_url:
                    return HttpResponseRedirect(next_url)
                else:
                    return HttpResponseRedirect(reverse("index"))                    
            else:
                msg = "This account has been disabled!"
                messages.error(request, msg)
        else:
            msg = "The username and/or password were incorrect."
            messages.error(request, msg)

    contex = {
        'next': next_url,
        }
    return render(request, "account/login.html", contex)

#============================
# Logout view
#----------------------------
def logout_view(request):
    logout(request)
    msg = "Successfully logged out."
    messages.success(request, msg)
    return HttpResponseRedirect(reverse("index"))