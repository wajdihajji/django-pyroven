import urllib

from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse

from pyroven.utils import setting, HttpResponseSeeOther

def raven_return(request):
    # Get the token which the Raven server sent us - this should really
    # have a try/except around it to catch KeyError
    token = request.GET['WLS-Response']

    # See if this is a valid token
    user = authenticate(response_str=token, request=request)

    if user is None:
        "Print no user"
    else:
        login(request, user)

    # Redirect somewhere sensible
    next_page = request.GET.get('next', '/')
    return HttpResponseRedirect(next_page)

def raven_login(request):
    # Get the Raven object and return a redirect to the Raven server
    login_url = setting('PYROVEN_LOGIN_URL')
    if login_url is None:
        raise Exception("pyroven error: You must define PYROVEN_LOGIN_URL in your project settings file.")
    next_page = request.GET.get('next', None)
    if next_page is not None:
        relative_return_url = "%s?next=%s" % (reverse('raven_return'), next_page)
    else:
        relative_return_url = reverse('raven_return')
    encoded_return_url = urllib.quote(request.build_absolute_uri(relative_return_url))
    return HttpResponseSeeOther("%s?ver=%d&url=%s" % (login_url, 2,
                                                      encoded_return_url)
                                )

def raven_logout(request):
    logout(request)
