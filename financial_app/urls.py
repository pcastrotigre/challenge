from django.conf.urls import url

from . import views

app_name = 'financial_app'
urlpatterns = [
    # url(r'^$', views.IndexView.as_view(), name='home'),
    # url(r'^$',  views.about, name='about'),
    url(r'^register/$', views.register_page),
    url(r'^post/$', views.Post, name='post'),
    url(r'^messages/$', views.Messages, name='messages'),
    # url(r'^$',  views.about, name='about'),
    # url(r'^new/$', views.new_room, name='new_room'),
    # url(r'^(?P<label>[\w-]{,50})/$', views.chat_room, name='chat_room'),
]