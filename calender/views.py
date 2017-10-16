# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.conf import settings
from apiclient import discovery
from oauth2client import client
import httplib2
from datetime import datetime, timedelta
import pytz
import time
import json
import calendar


def get_month_data(request):
    '''
    This functions checks for auth from google calendar api then returns data for a specified month/year if given
    else defaults to the current month.
    '''
    url = '/%soauth2callback/' % settings.BASE_URL
    if 'credentials' not in request.session:
        return HttpResponseRedirect(url)
    credentials = client.OAuth2Credentials.from_json(request.session['credentials'])
    if credentials.access_token_expired:
        return HttpResponseRedirect(url)
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http_auth)
        requested_date = datetime.utcnow()
        month = requested_date.month
        year = requested_date.utcnow().year
        start = 1
        if 'month' in request.GET:
            month = int(request.GET['month']) + 1
        if 'year' in request.GET:
            year = int(request.GET['year'])
        end = calendar.monthrange(year, month)[1]

        start_of_month = datetime.strptime('%s %s %s' % (start, month, year), '%d %m %Y').isoformat() + 'Z'
        end_of_month = datetime.strptime('%s %s %s' % (end, month, year), '%d %m %Y') + timedelta(days=1)
        end_of_month = end_of_month.isoformat() + 'Z'

        eventsResult = service.events().list(
            calendarId='primary',
            timeMin=start_of_month,
            timeMax=end_of_month,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        appointments = []

        for event in eventsResult['items']:
            if 'start' in event.keys():
                if 'dateTime' in event['start'].keys():
                    appointments.append({
                        'date': event['start']['dateTime'].split('T')[0],
                        'summary': event['summary']
                    })
                elif 'date' in event['start'].keys():
                    appointments.append({
                        'date': event['start']['date'],
                        'summary': event['summary']
                    })
        return HttpResponse(json.dumps({'appointments': appointments}))


def oauth2callback(request):
    '''
    handles oauth back back from gcal api and returns the calendar view.
    '''
    if 'code' in request.GET:
        request.session['code'] = request.GET['code']
    else:
        if 'code' in request.session:
            del request.session['code']

    flow = client.flow_from_clientsecrets(
        'client_secret.json',
        scope='https://www.googleapis.com/auth/calendar',
        redirect_uri='%s://%s/oauth2callback/' % (
            request.META['wsgi.url_scheme'],
            request.META['HTTP_HOST']
        )
    )
    flow.params['access_type']
    flow.params['include_granted_scopes'] = 'true'   # incremental auth
    if 'code' not in request.session:
        auth_uri = flow.step1_get_authorize_url()
        return HttpResponseRedirect(auth_uri)
    else:
        auth_code = request.session['code']
        credentials = flow.step2_exchange(auth_code)
        request.session['credentials'] = credentials.to_json()
        url = '%s' % settings.BASE_URL
        return HttpResponseRedirect(url)


def calendar_view(request):
    '''
    servers up calendar view.
    '''
    template_data = {
        'BASE_URL': settings.BASE_URL
    }
    url = '/%soauth2callback/' % settings.BASE_URL

    if 'credentials' not in request.session:
        return HttpResponseRedirect(url)
    credentials = client.OAuth2Credentials.from_json(request.session['credentials'])
    if credentials.access_token_expired:
            return HttpResponseRedirect(url)
    if request.META['HTTP_HOST'].startswith('2.localhost'):
        template = 'green_calender.html'
    else:
        template = 'blue_calender.html'

    return render(request, template, template_data)


def date_view(request):
    '''
    handles the request for data for a single day as well, rendering the page.
    '''
    template_data = {
        'BASE_URL': settings.BASE_URL
    }
    if 'date' in request.GET:

        date = datetime.strptime(request.GET['date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.GET['date'], '%Y-%m-%d') + timedelta(hours=23) + timedelta(minutes=59)
        template_data['date'] = date.date()
        date = date.replace(tzinfo=pytz.timezone(settings.TIME_ZONE), hour=0, minute=0).isoformat()
        end_date = end_date.replace(tzinfo=pytz.timezone(settings.TIME_ZONE)).isoformat()

        if 'credentials' not in request.session:
            url = '/%soauth2callback/' % settings.BASE_URL
            return HttpResponseRedirect(url)
        credentials = client.OAuth2Credentials.from_json(request.session['credentials'])
        if credentials.access_token_expired:
            return HttpResponseRedirect(url)
        else:
            http_auth = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http_auth)
            eventsResult = service.events().list(
                calendarId='primary',
                timeMin=date,
                timeMax=end_date,
                timeZone='Africa/Johannesburg',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            data = []
            for event in eventsResult['items']:
                if 'dateTime' in event['start'].keys() and 'dateTime' in event['end'].keys():
                    start = datetime.strptime(event['start']['dateTime'].split(':00+')[0], '%Y-%m-%dT%H:%M')
                    end = datetime.strptime(event['end']['dateTime'].split(':00+')[0], '%Y-%m-%dT%H:%M')
                    start = int(time.mktime(start.timetuple()))
                    end = int(time.mktime(end.timetuple()))
                    total_minutes = (end - start)/60
                    minute = int(event['start']['dateTime'].split('T')[1].split('+')[0].split(':')[01])
                    slots = 0
                    hour = event['start']['dateTime'].split('T')[1].split('+')[0].split(':')[0]
                    if request.META['HTTP_HOST'].startswith('2.localhost'):
                        # The amount of slots need
                        if total_minutes <= 30:
                            slots = 1
                        elif total_minutes > 30:
                            slots = 2

                        # Starting position to block out cells
                        if minute < 30:
                            start_slot = 1
                        elif minute >= 30:
                            start_slot = 2

                    else:
                        # The amount of slots need
                        if total_minutes <= 15:
                            slots = 1
                        elif total_minutes > 15 and total_minutes <= 30:
                            slots = 2
                        elif total_minutes > 30 and total_minutes <= 45:
                            slots = 3
                        else:
                            slots = 4

                        # Starting position to block out cells
                        if minute < 15:
                            start_slot = 1
                        elif minute >= 15 and minute < 30:
                            start_slot = 2
                        if minute >= 30 and minute < 45:
                            start_slot = 3
                        if minute >= 45:
                            start_slot = 4
                    data.append({
                        'summary': event['summary'],
                        'description': event['description'],
                        'hour': hour,
                        'slots': slots,
                        'start_slot': start_slot,
                        })
                else:
                    data.append({
                        'summary': event['summary'],
                        'description': event['description'],
                        'hour': 0,
                        'slots': 24,
                        'start_slot': 1,
                        })

    if request.META['HTTP_HOST'].startswith('2.localhost'):
        template = 'green_date.html'
    else:
        template = 'blue_date.html'

    template_data['data'] = data
    return render(request, template, template_data)


def add_event(request):
    '''
    creates an event for a given time.
    '''
    if request.POST:
        description = request.POST['description']
        summary = request.POST['summary']
        length = request.POST['length']
        hour, minute = request.POST['coords'].split('_')

        if request.META['HTTP_HOST'].startswith('2.localhost'):
            if minute == '30':
                start_minute = '00'
            else:
                start_minute = '30'
        else:
            if minute == '15':
                start_minute = '00'
            elif minute == '30':
                start_minute = '15'
            elif minute == '45':
                start_minute = '30'
            else:
                start_minute = '45'

        time = '%s:%s' % (hour, start_minute)
        date = request.POST['date']
        event_start = datetime.strptime('%s %s:00' % (date, time), '%b. %d, %Y %X')
        end_date = event_start + timedelta(minutes=int(length))

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': event_start.isoformat(),
                'timeZone': 'Africa/Johannesburg'
            },
            'end': {
                'dateTime': end_date.isoformat(),
                'timeZone': 'Africa/Johannesburg'
            },
        }
        url = '/%soauth2callback/' % settings.BASE_URL
        if 'credentials' not in request.session:
            return HttpResponseRedirect(url)
        credentials = client.OAuth2Credentials.from_json(request.session['credentials'])
        if credentials.access_token_expired:
            return HttpResponseRedirect(url)
        else:
            http_auth = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http_auth)
            insert = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
    return HttpResponse('Event created: %s' % insert.get('htmlLink'))


def get_calender_assets_path():
    from os import path
    CURRENT_DIRECTORY = path.abspath(path.join(path.dirname(__file__)))
    assets_path = '%s/assets/' % CURRENT_DIRECTORY
    return assets_path
