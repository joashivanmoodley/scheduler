SET UP
================
 1. follow https://virtualenvwrapper.readthedocs.io/en/latest/ this will set up a env for the app to run
 2. pip install -r requirements.txt
 3. python manage.py runserver 5000

Notes:
 > Call back for Oauth is set to localhost:5000/oauth2callback/ or localhost:5000/calender/oauth2callback/
 > BASE_URL for the calender app can set in settings.py - if changed from the default
  eg: 'BASE_URL = "calender/" 
 >  To run another django site, add 'calender' to INSTALLED_APPS
    And url(r'^%s' % settings.BASE_URL, include(calender_urls)), to urls.py
 > App uses Jquery, Bootstrap
 > TODO: Would have liked to have added some unit tests.
 > Google API does not allow for sub-domian of localhost, so it wasnt possible for me to authenicate 1.localhost/ 2.localhost, however I have added code in place that will switch between templates based on the Request META HTTP Host. So for Oauth Testing purposes please use no sub-domain ie: localhost:5000
 > The HTML / CSS is not up to standard (sorry). 