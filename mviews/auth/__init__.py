'''
Created on Aug 27, 2015

@author: derigible
'''

from functools import wraps

from django.contrib.auth import login, SESSION_KEY, authenticate as auth
from django.utils.decorators import available_attrs

from mviews.utils import err
from mviews.utils import read
from mviews.errors import AuthenticationError
from mviews.errors import AuthorizationError

def authenticated(func):
    '''
    A decorator to check if the user is authenticated. Since it is undesirable 
    in an api to redirect to a login, this was made to replace the 
    requires_login django decorator. This should be wrapped in method_decorator 
    if a class-based view.
    
    @param func: the view function that needs to have an authenticated user
    @return the response of the function if authenticated, or an error response
    '''
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return func(request, *args, **kwargs)
        return err("Unauthenticated.", 401)
    return wrapper

def has_level(level):
    '''
    A decorator to check if the user has the correct level to view the object. 
    If not, return a 403 error. Also checks if the user is authenticated
    and return a 401 on false.
    
    @param func: the view function that needs to have proper level
    @param level: the level to check
    @return the response of the function if allowed, or an error response
    '''
    def wrapper(func):
        @wraps(func, assigned=available_attrs(func))
        def _wrapped(request, *args, **kwargs):
            from db.models import User
            if not request.user.is_authenticated():
                return err("Unauthenticated", 401)
            if request.user.level >= User.get_level_by_name(level):
                return func(request, *args, **kwargs)
            return err("Unauthorized. You are not of level {} or above.".format(level), 403)
        return _wrapped
    return wrapper

def has_level_or_is_obj_creator(level):
    '''
    A decorator to check if the user has the correct level to view the object,
    or if user is the creator of the object. If not, will set a flag in the 
    kwargs called _authenticated to False. This flag can be used to determine
    what needs to be done with the unauthenticated user.
     
    Also checks if the user is authenticated and return a 401 on false.
    
    @param func: the view function that needs to have proper level
    @param level: the level to check
    @return the response of the function if allowed, or an error response
    '''
    def wrapper(func):
        @wraps(func, assigned=available_attrs(func))
        def _wrapped(request, *args, **kwargs):
            from db.models import User
            if not request.user.is_authenticated():
                return err("Unauthenticated", 401)
            if request.user.level >= User.get_level_by_name(level):
                return func(request, *args, _authenticated=True, **kwargs)
            return func(request, *args, _authenticated=False, **kwargs)
        return _wrapped
    return wrapper

def authenticate(request, email = None, password = None):
    '''
    Log the Poster in or raise an Unauthenticated error. If email or password 
    is None, will attempt to extract from the request object. This assumes it 
    is a json object. If other formats are used, you must pass in email and 
    password separately. The user object will be placed in the request object 
    after successful login.
    
    @param request: the request to log in
    @param email: the email of the poster
    @param password: the password of the poster
    @return the sessionid, the user object
    '''
    if email is None or password is None:
        try:
            j = read(request)
            email = j["email"]
            password = j["password"]
        except ValueError:
            raise ValueError("Faulty json. Could not parse.")
        except KeyError as ke:
            KeyError(ke)
    user = auth(username = email, password = password)
    if user is None:
        raise AuthenticationError()
    login(request, user)
#     if not user.check_password(password):
    return request.session[SESSION_KEY]