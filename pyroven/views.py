import urllib.request, urllib.parse, urllib.error

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse

from pyroven.utils import setting, HttpResponseSeeOther
import pyroven

def raven_return(request):
    # Get the token which the Raven server sent us - this should really
    # have a try/except around it to catch KeyError
    token = request.GET['WLS-Response']

    # See if this is a valid token
    try:
        user = authenticate(response_str=token, request=request)
    except pyroven.MalformedResponseError:
        return HttpResponseRedirect("/")
    except Exception as e:
        return HttpResponse(e)

    if user is None:
        "Print no user"
    elif not user.is_active:
        return HttpResponse("Your account has been disabled")
    else:
        login(request, user)

    # Redirect somewhere sensible
    next_page = request.GET.get('next', '/')
    if next_page == "":
        next_page = "/"

    extra_url_arg_values = {}
    extra_url_args = set(setting('PYROVEN_PASSTHROUGH_URL_ARGS', []))
    for k in extra_url_args:
        if k in request.GET:
            extra_url_arg_values[k] = request.GET.get(k)

    url_extra = ''
    if len(extra_url_args) > 0:
        url_extra = "?%s" % "&".join(["%s=%s" % (k, v) for (k, v) in list(extra_url_arg_values.items())])

    return HttpResponseRedirect(next_page + url_extra)

def raven_login(request):
    # Get the Raven object and return a redirect to the Raven server
    login_url = setting('PYROVEN_LOGIN_URL')
    if login_url is None:
        raise Exception("pyroven error: You must define PYROVEN_LOGIN_URL in your project settings file.")

    extra_url_arg_values = {}
    extra_url_args = set(setting('PYROVEN_PASSTHROUGH_URL_ARGS', []))
    extra_url_args.add('next')
    for k in extra_url_args:
        if k in request.GET:
            extra_url_arg_values[k] = request.GET.get(k)

    url_extra = ''
    if len(extra_url_args) > 0:
        url_extra = "?%s" % "&".join(["%s=%s" % (k, v) for (k, v) in list(extra_url_arg_values.items())])

    relative_return_url = "%s%s" % (reverse('raven_return'), url_extra)

    encoded_return_url = urllib.parse.quote(request.build_absolute_uri(relative_return_url))
    return HttpResponseSeeOther("%s?ver=%d&url=%s" % (login_url, 2,
                                                      encoded_return_url)
                                )

def raven_logout(request):
    logout(request)
