from django.conf.urls import url
from calender import views
from django.views.static import serve
from calender.views import get_calender_assets_path

urlpatterns = [
    url(r'^assets/(?P<path>.*)$', serve,  {'document_root': get_calender_assets_path()}),
    url(r'^get-month-data/$', views.get_month_data),
    url(r'^oauth2callback/$', views.oauth2callback),
    url(r'^$', views.calendar_view),
    url(r'^date/$', views.date_view),
    url(r'^add-event/$', views.add_event),
]
