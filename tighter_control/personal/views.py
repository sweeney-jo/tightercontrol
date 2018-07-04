import datetime
from django.http import JsonResponse
import json
from django.shortcuts import render
from django.db.models import Avg, Max, Min, Count, Q
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from resInput.models import Input

from rest_framework.views import APIView
from rest_framework.response import Response

from django.views.generic import View




def index(request):#always have to pass request, maybe its to be explicit
    return render(request, 'personal/home.html')
    
def art_HbA1c(request):
    # creating panda dataframe holding time and entire glucose history results
    df = pd.DataFrame(list(Input.objects.all().values('time','historic_glucose')))
    # changing time string data type to datetime datatype
    df['time'] = pd.to_datetime(df['time'])
    # storing the last time regestired in range_max variable
    range_max = df['time'].max()
    #work back 7 days to get the earliest time and store in range_min variable
    range_min = range_max - datetime.timedelta(days=7)
    #sliced_df variable stores the range 
    sliced_df = df[(df['time'] >= range_min) & 
               (df['time'] <= range_max)]
    data = { 
         "Highest Glucose reading": df['historic_glucose'].max(),
         "Lowest Glucose reading": df['historic_glucose'].min(),
         "hBA1c":(((2.59) +(df['historic_glucose'].mean()))/(1.59)),
         "Average reading for last 7 days": sliced_df['historic_glucose'].mean(),
         "Last 7 day Highest Glucose reading":sliced_df['historic_glucose'].max(),
         "last 7 day Lowest Glucose reading": sliced_df['historic_glucose'].min()     
         
     }
    return JsonResponse(data, safe=False)


def average_area(request, *args, **kwargs):
    dataset =  pd.DataFrame(list(Input.objects.all().values('time', 'historic_glucose')))
    #dataset.to_pickle("./dataset.pkl")
    #dataset.to_msgpack()
    Input.objects.all().aggregate(Avg('historic_glucose'))
    data = {
         "sales":100,
         "customer":10,
         "Input": Input.objects.all().count(),
         "Max time": dataset['time'].max()
         
     }
    #pick_dataset = pd.read_pickle("./dataset.pkl")   
    return JsonResponse(dataset, safe=False)

def daily_reading(request):
    """
    daily reading will take the last 24 hour glucose readings
    """
    df = pd.DataFrame(list(Input.objects.all().values('time', 'historic_glucose')))
    df = df.loc[df['record_type'] == 0.0]
    df['time'] = pd.to_datetime(df['time'])
    range_max = df['time'].max()
    range_min = range_max - datetime.timedelta(days=2)
    sliced_df = df[(df['time'] >= range_min) &
               (df['time'] <= range_max)]
    return render(request, 'personal/header.html', {'sliced_df': sliced_df})

def week_chart(request):
    df = pd.DataFrame(list(Input.objects.all().values('time', 'historic_glucose')))
    df['time'] = pd.to_datetime(df['time'])
    range_max = df['time'].max()
    range_min = range_max - datetime.timedelta(days=7)
    sliced_df = df[(df['time'] >= range_min) &
               (df['time'] <= range_max)]
    sliced_df.plot(x='time', y='historic_glucose')
    plt.show()
    return render(request, 'personal/header.html')

class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        qs_count = Input.objects.all().count()
        labels = ["Inputs", "Blue", "Yellow", "Green", "Purple", "Orange"]
        default_items = [qs_count, 23, 2, 3, 12, 2]
        data = {
                "labels": labels,
                "default": default_items,
        }
        return Response(data)

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'personal/chart.html', {"customers": 10})