'''
Created on May 19, 2015

@author: derigible
'''

from django.contrib.auth import logout
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.http.response import JsonResponse as jr
from django.views.generic.base import View

from . import authenticate
from db.models import User
from mviews.errors import AuthenticationError
from mviews.serializer import objs_to_dict
from mviews.utils import err
from mviews.utils import read

class CreateUser(View):
    '''
    The class that handles the poster objects.
    '''
    routes = [{"pattern" : "admin/register"}]
    
    def post(self, request, *args, **kwargs):
        '''
        Creates a new poster. The poster object should be of the following json 
        type:
        
            {
                "email" : "<email>",
                "password" : "<password>"
            }
        '''
        j = read(request)
        try:
            print(j)
            p = User.objects.create_user(**j)
            resp = objs_to_dict(p, [p], p.field_names)[0]
            return jr(resp)
        except IntegrityError as ie:
            return err(ie)

class Authentication(View):
    '''
    Handles the authentication requests of the site.
    '''
    routes = [{"pattern" : "admin/login"}]
    
    def post(self, request, *args, **kwargs):
        '''
        Log the person in. Login requires the following json to work:
        
            {
                "email" : "<email>",
                "password" : "<password>"
            }
        '''
        try:
            session_id = authenticate(request)
            resp = HttpResponse(request, status=204)
            resp.set_cookie("sessionid", session_id, max_age=30)
            return resp
        except (KeyError, ValueError) as e:
            return err(e)
        except AuthenticationError as ae:
            return err(ae, 401)
    
    def delete(self, request, *args, **kwargs):
        '''
        Log the person out. Logout requires nothing but the cookie to work. 
        Will always return 204.
        ''' 
        logout(request)
        return HttpResponse(request, status=204)
    
class Permission(View):
    '''
    Handles the permissions of the user. 
    '''
    routes = [{"pattern" : "admin/permission"}]
    
    def get(self, request, *args, **kwargs):
        '''
        Return the permission level of the user.
        '''
        if not request.user.is_authenticated():
            return jr({'level' : User.get_level_name(0)})
        else:
            return jr({'level' : User.get_level_name(
                                        getattr(request.user, 'level', 0))})