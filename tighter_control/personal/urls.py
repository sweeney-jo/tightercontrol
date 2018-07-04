from django.conf.urls import url
from . import views

urlpatterns =[

   url(r'^$', views.index, name = 'index'),
   url(r'^chart/', views.week_chart, name='week_chart'),
   url(r'^avArea/', views.average_area, name='api-data'),
   url(r'^HbA1c/', views.art_HbA1c, name = 'art_HbA1c' ),
   url(r'^api/chart/data/$', views.ChartData.as_view()),
   url(r'^pie/', views.HomeView.as_view(), name='home'),
]