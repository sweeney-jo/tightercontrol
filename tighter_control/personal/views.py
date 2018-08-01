import datetime
import requests
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Avg, Max, Min, Count, Q
from resInput.models import Input
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import View
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .forms import RegistrationForm, EditProfileForm, TwentyFourHourForm
from django.http import HttpResponse, HttpResponseRedirect


def login_redirect(request):
    return redirect('/login')


def index(request):  # always have to pass request, maybe its to be explicit
    return render(request, 'personal/home.html')


def home(request):
    return render(request, 'personal/home.html')


@login_required
def profile(request):
    args = {'user': request.user}
    return render(request, 'personal/profile.html', args)

# registration method


def register(request):
    if request.method == 'POST':
      #  form = UserCreationForm(request.POST)
        # Registration form extened from Usercreation form to add extra variables
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/login')
        else:
            print(form.errors)
    else:
        #  form = UserCreationForm()
        form = RegistrationForm()

        args = {'form': form}
        return render(request, 'registration/reg_form.html', args)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'personal/edit_profile.html', args)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            # keeps user logged in when changing password
            update_session_auth_hash(request, form.user)
            return redirect('profile')
        else:

            return redirect('/changepassword')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'personal/change_password.html', args)


@login_required
def art_HbA1c(request):
    """
    Main Method. Contains all the logic that was needed to alter the data stored in the database
    """
    # creating separate panda dataframe holding time and entire glucose,carbs,insulin history results
    df = pd.DataFrame(
        list(Input.objects.all().values('time', 'historic_glucose')))
    carb_df = pd.DataFrame(
        list(Input.objects.all().values('time', 'carbohydrates')))
    insulin_df = pd.DataFrame(
        list(Input.objects.all().values('time', 'rapid_acting_insulin')))
    # changing time string data type to datetime datatype
    df['time'] = pd.to_datetime(df['time'])
    carb_df['time'] = pd.to_datetime(carb_df['time'])
    insulin_df['time'] = pd.to_datetime(insulin_df['time'])
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
    # set time to new variable so value can be called as old time variable set to index in next step
    df['new time col'] = df['time']
    carb_df['new time col'] = df['time']
    insulin_df['new time col'] = df['time']
    # setting time as index//needed for methdos such as .resample
    df.set_index('time', inplace=True)
    carb_df.set_index('time', inplace=True)
    insulin_df.set_index('time', inplace=True)
    # last weeks average readings
    sliced_df.set_index('time', inplace=True)
    last_week_dAvg = sliced_df.resample('D').mean()
    # 2nd last week average readings
    week_prior_sliced_df.set_index('time', inplace=True)
    second_last_week_dAvg = week_prior_sliced_df.resample('D').mean()
    # 3rd last week average readings
    sliced_df_week3.set_index('time', inplace=True)
    third_last_week_dAvg = sliced_df_week3.resample('D').mean()
    # average daily value
    dAvg = df.resample('D').mean()
    # highest daily value
    dHigh = df.resample('D').max()
    # lowest daily average
    dLow = df.resample('D').min()

    labels = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]

    if request.GET.get('dat'):
        the_date = request.GET['dat'] #not working as inside JSONRESPONSE() instaed of HTTPRESPONSE()
        print(the_date)
        print("it get request worked") #for front end testing purposes
    else:
        the_date2 = range_max.strftime('%Y%m%d')
        the_date = range_min.strftime('%Y%m%d')
       # print(the_date)
     #   print("no it didn't work") for front end testing purposes
     
    twenty_four_hour_reading = df[the_date]  # df['2018-05-22']
    carb_reading = carb_df[the_date]  # carb_df['2018-05-22']
    # insulin_df['2018-05-22']
    insulin_reading = insulin_df[the_date]

    data = {
        "Highest Glucose reading": df['historic_glucose'].max(),
        "Lowest Glucose reading": df['historic_glucose'].min(),
        "hBA1c": (((2.59) + (df['historic_glucose'].mean()))/(1.59)),
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
        "2nd last week daily average": second_last_week_dAvg.to_json(orient='values'),
        "3rd last week daily average": third_last_week_dAvg.to_json(orient='values'),
        "daily average": dAvg.to_json(orient='values'),
        "daily highs": dHigh.to_json(orient='values'),
        "daily lows": dLow.to_json(orient='values'),
        "24 hour readings": twenty_four_hour_reading.to_json(orient='values'),
        "carb reading": carb_reading.to_json(orient='values'),
        "insulin dosage": insulin_reading.to_json(orient='values'),
        "days": labels,
        "the date": the_date
    }
    return JsonResponse(data)


def average_area(request, *args, **kwargs):
    """
    this method was used prior to HighChart Utilisation
    """
    df = pd.DataFrame(
        list(Input.objects.all().values('time', 'historic_glucose')))
    df['time'] = pd.to_datetime(df['time'])
    range_max = df['time'].max()
    range_min = range_max - datetime.timedelta(days=2)
    sliced_df = df[(df['time'] >= range_min) &
                   (df['time'] <= range_max)]
    sliced_df.plot(x='time', y='historic_glucose')
    plt.show()
    return render(request, 'personal/profile.html')


def daily_reading(request):
    """
    daily reading will take the last 24 hour glucose readings, this method was used prior to HighChart utilisation
    """
    df = pd.DataFrame(
        list(Input.objects.all().values('time', 'historic_glucose')))
    df['time'] = pd.to_datetime(df['time'])
    range_max = df['time'].max()
    range_min = range_max - datetime.timedelta(days=1)
    sliced_df = df[(df['time'] >= range_min) &
                   (df['time'] <= range_max)]
    sliced_df.plot(x='time', y='historic_glucose')
    plt.show()
    return render(request, 'personal/profile.html', {'sliced_df': sliced_df})


def week_chart(request):
    """
    old method prior to HighChart utilisation 
    """
    df = pd.DataFrame(
        list(Input.objects.all().values('time', 'historic_glucose')))
    df['time'] = pd.to_datetime(df['time'])
    range_max = df['time'].max()
    range_min = range_max - datetime.timedelta(days=7)
    sliced_df = df[(df['time'] >= range_min) &
                   (df['time'] <= range_max)]
    sliced_df.plot(x='time', y='historic_glucose')
    plt.show()
    return render(request, 'personal/profile.html')

def get_carbs(request):
    """
    Carb Counter view containing all the logic to make 3rd party API calls possible, API Keys and ID have been 
    hidden in the env
    """
    message = "Apple"
    food = {}
    if request.GET.get('q'):
        message = request.GET['q']

    data = {'query': message}

    headers = {
      'x-app-id': settings.N_IX_APP_ID,
      'x-app-key': settings.N_IX_APP_KEY

    }

    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'

    response = requests.post(url, data, headers=headers)

    print(response.status_code)
    r = response.json()
    print(response.url)
    search_was_successful = (response.status_code == 200)  # 200 = SUCCESS

    test = response.status_code
    if test == 200:
       reply = "We have found "+data['query']+" in the NutritionIX database"
       print(data['query']+" is in our database.")

       food['carb'] = r['foods'][0]['full_nutrients'][2]['value']
       food['name'] = r['foods'][0]['food_name']
       food['fat'] = r['foods'][0]['full_nutrients'][1]['value']
       food['success'] = search_was_successful

       print(r['foods'][0]['food_name'])
       print(r['foods'][0]['full_nutrients'][2]['value'])
       print(r['foods'][0]['full_nutrients'][1]['value'])
       print(message)

    elif test == 404:
       reply = "hmmm, are you absolutely sure that " + \
           data['query']+" is a food?"
       print("hmmm, are you absolutely sure that "+data['query']+" is a food?")
       food['query'] = message
    else:
       reply = "servers might be down today please contact dev team for more info"
       print("servers might be down today please contact dev team for more info")

    try:
        fat = r['foods'][0]['full_nutrients'][1]['value']
        carb = r['foods'][0]['full_nutrients'][2]['value']
        answer = "There are " + \
            str(carb)+"grams of carbohydrate in "+data['query']
        print("There are "+str(carb)+"grams of carbohydrate in "+data['query'])

    except:

        print('its not in our database')
        answer = 'its not in our database'

    return render(request, 'personal/carb_counter.html', {'food': food, 'answer': answer})

"""
def twenty_four_hour_date(request):
    results = {}
    # creating separate panda dataframe holding time and entire glucose,carbs,insulin history results
    df = pd.DataFrame(
        list(Input.objects.all().values('time', 'historic_glucose')))
    carb_df = pd.DataFrame(
        list(Input.objects.all().values('time', 'carbohydrates')))
    insulin_df = pd.DataFrame(
        list(Input.objects.all().values('time', 'rapid_acting_insulin')))
    # changing time string data type to datetime datatype
    df['time'] = pd.to_datetime(df['time'])
    carb_df['time'] = pd.to_datetime(carb_df['time'])
    insulin_df['time'] = pd.to_datetime(insulin_df['time'])
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
    # set time to new variable so value can be called as old time variable set to index in next step
    df['new time col'] = df['time']
    carb_df['new time col'] = df['time']
    insulin_df['new time col'] = df['time']
    # setting time as index//needed for methdos such as .resample
    df.set_index('time', inplace=True)
    carb_df.set_index('time', inplace=True)
    insulin_df.set_index('time', inplace=True)
    # last weeks average readings
    sliced_df.set_index('time', inplace=True)
    last_week_dAvg = sliced_df.resample('D').mean()
    # 2nd last week average readings
    week_prior_sliced_df.set_index('time', inplace=True)
    second_last_week_dAvg = week_prior_sliced_df.resample('D').mean()
    # 3rd last week average readings
    sliced_df_week3.set_index('time', inplace=True)
    third_last_week_dAvg = sliced_df_week3.resample('D').mean()
    # average daily value
    dAvg = df.resample('D').mean()
    # highest daily value
    dHigh = df.resample('D').max()
    # lowest daily average
    dLow = df.resample('D').min()

    labels = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]
    if request.GET.get('dat'):
        the_date = request.GET['dat']
        print("yo it worked here it is 24hr")
        print(the_date)
    else:
        the_date = '2018-05-29'
        print("no it didn't work here it is not 24hr")
        print(the_date)
    
    print("whats outside the loop 24hr")
    print(the_date)
    
    twenty_four_hour_reading = df[the_date]  # df['2018-05-22']
    carb_reading = carb_df[the_date]  # carb_df['2018-05-22']
    # insulin_df['2018-05-22']
    insulin_reading = insulin_df[the_date]



    return render(request, 'personal/24hr.html', {'the_date':the_date,'twenty_four_hour_reading':twenty_four_hour_reading, 'carb_reading':carb_reading,'insulin_reading':insulin_reading})
"""
