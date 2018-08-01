from django.conf.urls import url
from . import views
from django.contrib.auth.views import login, logout   
from django.conf import settings
from django.conf.urls.static import static

urlpatterns =[

   url(r'^$', views.login_redirect, name = 'login_redirect'),
   url(r'^chart/', views.week_chart, name='week_chart'),
   url(r'^avArea/', views.average_area, name='api-data'),
   url(r'^HbA1c/', views.art_HbA1c, name = 'art_HbA1c' ),
   url(r'^dailyAv/', views.daily_reading, name = 'dailyAv' ),

   url(r'^login/$', login, {'template_name': 'registration/login.html' }),
   url(r'^logout/$', logout, {'template_name': 'registration/logout.html' }),
   url(r'^profile/$', views.profile, name = 'profile'),
   url(r'^carb_counter/$', views.get_carbs, name = 'carbs'),
   url(r'^profile/edit$', views.edit_profile, name = 'edit_profile'),
   url(r'^changepassword$', views.change_password, name = 'change_password'),
   url(r'^register/$', views.register, name = 'register'),
   url(r'^home/$', views.home, name = 'home'),

  # url(r'^home/read$', views.twenty_four_hour_date, name = 'dat'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # to allow static files uploaded by user 