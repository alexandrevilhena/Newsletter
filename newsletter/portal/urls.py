from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import render

def custom_page_not_found_view(request, exception):
    return render(request, "404.html", {}, status=404)

handler404 = custom_page_not_found_view

urlpatterns = [
    path('', views.abertura, name='abertura'),
    path('index', views.index, name='home'),
    path('newsletter', views.newsletter, name='newsletter'),
    path('newsletter/add', views.newsletter_add, name='newsletter_add'),
    path('abertura', views.abertura, name ='abertura'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_pagina, name='login'),
    path('inscrever-newsletter/<int:newsletter_id>/', views.inscrever_newsletter, name='inscrever_newsletter'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    path('logout/', auth_views.LogoutView.as_view(next_page='abertura'), name='logout'),
    path('desinscrever-newsletter/<int:newsletter_id>/', views.unsubscribe_newsletter, name='unsubscribe_newsletter'),
]
