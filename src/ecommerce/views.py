from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.conf import settings

from .forms import ContactForm, LoginForm, RegisterForm

User = settings.AUTH_USER_MODEL

def home_page(request):
	context= {
		"title" : "home"
	}
	return render(request, "home_page.html",context)

def about_page(request):
	context= {
		"title" : "about"

	}
	return render(request, "home_page.html",context)

def contact_page(request):
	contact_form = ContactForm(request.POST or None)
	context = {
		
		"title"	: "contact",
		"form"	: contact_form,	
	}
	if contact_form.is_valid():
		print(contact_form.cleaned_data)
	# if request.method == "POST" :
	# 	print(request.POST)
	# 	print(request.POST.get)
	return render(request, "contact/view.html",context)


# reporter = Reporters.objects.get(name='Tintin')