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

# creating panda dataframe holding time and entire glucose history results
df = pd.DataFrame(list(Input.objects.all().values('time', 'historic_glucose')))
# changing time string data type to datetime datatype
df['time'] = pd.to_datetime(df['time'])
# storing the last time regestired in range_max variable
range_max = df['time'].max()
# work back 7 days to get the earliest time and store in range_min variable
range_min = range_max - datetime.timedelta(days=6)
# sliced_df variable stores the range
sliced_df = df[(df['time'] >= range_min) &
               (df['time'] <= range_max)]

# one week worth of data prior to sliced_df
week_prior_sliced_df = df[(df['time'] >= (range_min - datetime.timedelta(days=6))) &
                      (df['time'] <= range_min)]
# one week worth of data prior to week_prior_sliced_df
sliced_df_week3 = df[(df['time'] >= (range_min - datetime.timedelta(days=12))) &
                      (df['time'] <= range_min - datetime.timedelta(days=6))]
df['new time col']=df['time']
# setting time as index//needed for methdos such as .resample
df.set_index('time', inplace=True)
# last weeks average readings
sliced_df.set_index('time', inplace=True)
last_week_dAvg=sliced_df.resample('D').mean()
# 2nd last week average readings
week_prior_sliced_df.set_index('time', inplace=True)
second_last_week_dAvg=week_prior_sliced_df.resample('D').mean()
# 3rd last week average readings
sliced_df_week3.set_index('time', inplace=True)
third_last_week_dAvg=sliced_df_week3.resample('D').mean()



# average daily value
dAvg=df.resample('D').mean()
# highest daily value
dHigh=df.resample('D').max()
# lowest daily average
dLow=df.resample('D').min()

labels=[
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday'
            ]


def index(request):  # always have to pass request, maybe its to be explicit
    return render(request, 'personal/home.html')


def art_HbA1c(request):

    data={
        "Highest Glucose reading": df['historic_glucose'].max(),
        "Lowest Glucose reading": df['historic_glucose'].min(),
        "hBA1c": (((2.59) + (df['historic_glucose'].mean()))/(1.59)),
        # causing ajax calls to crash as returning NAN
        "Average reading for last 7 days": sliced_df['historic_glucose'].mean(),
        "Last 7 day highest Glucose reading": sliced_df['historic_glucose'].max(),
        "last 7 day Lowest Glucose reading": sliced_df['historic_glucose'].min(),
        "how many rows = ": Input.objects.all().count(),

        # "last month reading list": sugar_list.to_json(orient='values'),
        #  "Date Time": sliced_df.to_json(orient='table') #sliced_df is glucose and time .to_json allows series to be serialised to json format
        #  "days of dataframe": sliced_df['time'].dt.weekday_name.to_json(orient="table"),
       # "last week daily averages" :last_week_dAvg.to_json(orient='values'),
       # "last week daily averages" :"[[8.2631578947], [7.9227848101], [9.3042105263], [10.3252631579], [10.66125], [9.6817204301], [5.9903846154]]",
        "last week daily averages": last_week_dAvg.to_json(orient='values'),
        "2nd last week daily average": second_last_week_dAvg.to_json(orient = 'values'),
        "3rd last week daily average": third_last_week_dAvg.to_json(orient = 'values'),
        "daily average": dAvg.to_json(orient='values'),
        "daily highs": dHigh.to_json(orient='values'),
        "daily lows": dLow.to_json(orient='values'),
        "days": labels


    }
    return JsonResponse(data)


def average_area(request, *args, **kwargs):
    dataset=pd.DataFrame(
        list(Input.objects.all().values('time', 'historic_glucose')))
    Input.objects.all().aggregate(Avg('historic_glucose'))
    data={
        "sales": 100,
        "customer": 10,
        "Input": Input.objects.all().count(),
        "Max time": dataset['time'].max()

    }
    return JsonResponse(dataset, safe=False)


def daily_reading(request):
    """
    daily reading will take the last 24 hour glucose readings
    """
    df=pd.DataFrame(
        list(Input.objects.all().values('time', 'historic_glucose')))
    df=df.loc[df['record_type'] == 0.0]
    df['time']=pd.to_datetime(df['time'])
    range_max=df['time'].max()
    range_min=range_max - datetime.timedelta(days=2)
    sliced_df=df[(df['time'] >= range_min) &
                   (df['time'] <= range_max)]
    return render(request, 'personal/header.html', {'sliced_df': sliced_df})


def week_chart(request):
    df=pd.DataFrame(
        list(Input.objects.all().values('time', 'historic_glucose')))
    df['time']=pd.to_datetime(df['time'])
    range_max=df['time'].max()
    range_min=range_max - datetime.timedelta(days=7)
    sliced_df=df[(df['time'] >= range_min) &
                   (df['time'] <= range_max)]
    sliced_df.plot(x='time', y='historic_glucose')
    plt.show()
    return render(request, 'personal/header.html')


class ChartData(APIView):
    authentication_classes=[]
    permission_classes=[]

    def get(self, request, format=None):
        qs_count=Input.objects.all().count()
        labels=["Inputs", "Blue", "Yellow", "Green", "Purple", "Orange"]
        default_items=[qs_count, 23, 2, 3, 12, 2]
        data={
            "labels": labels,
            "default": default_items,
        }
        return Response(data)


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'personal/chart.html', {"customers": 10})
