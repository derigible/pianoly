'''
Created on Sep 22, 2015

@author: derigible

The basic structure for the piano_submission website. Basically lays out the
user model and who can see what, as well as what it is that will be submitted.

This is built using the Model as View framework, v0.5
'''

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.decorators import method_decorator
from django.utils import timezone as dt

from mviews.modelviews import ModelAsView as m
from mviews.modelviews import UserModelAsView as um
from mviews.auth import authenticated
from mviews.auth import has_level
from mviews.auth import has_level_or_is_obj_creator
from mviews.errors import AuthorizationError
from mviews.utils import err

class ModPerms(m):
    
    def _check_objs_for_perm(self, request, *args, **kwargs):
        if not self.data or not isinstance(self.data['data'], list):
            qs = self._get_qs(*args, **kwargs).select_related()
            for model in qs:
                if model.owner is None or model.owner.pk != request.user.pk:
                    raise AuthorizationError("You do not have permission to edit "
                                             "or delete the requested object(s); "
                                             "you did not create "
                                             "the object(s).")
        else:
            qslookup = self.data.get('lookup', self.unique_id)
            for i, d in enumerate(self.data['data']):
                if qslookup in d["data"]:
                    qs = self.__class__.objects.filter(
                                     **{qslookup:d['data'][qslookup]}
                                                     ).select_related()
                    if ((len(qs) 
                        and qs[0].owner is not None 
                        and qs[0].owner.pk != request.user.pk) or
                        (len(qs) and qs[0].owner is None)):
                        raise AuthorizationError("Object {} in submitted list "
                                                  "does not have update "
                                                  "permissions. Please remove "
                                                  "and resubmit.".format(i))
                else:
                    raise KeyError("Lookup {} was not found in object "
                                   "number {}".format(qslookup, i))
        
    @method_decorator(authenticated)
    def put(self, request, *args, **kwargs):
        try:
            self._check_objs_for_perm(request, *args, **kwargs)
        except AuthorizationError as e:
            return err(e, e.status)
        except KeyError as e:
            return err(e)
        except FieldDoesNotExist as e:
            return err(e)
        return super(ModPerms, self).put(request, *args, **kwargs)
    
    @method_decorator(authenticated)
    def delete(self, request, *args, **kwargs):
        try:
            self._check_objs_for_perm(request, *args, **kwargs)
        except AuthorizationError as e:
            return err(e, e.status)
        return super(ModPerms, self).delete(request, *args, **kwargs)
        
    class Meta:
        abstract = True    
    
class User(um):
    '''
    The basic user model that interacts with the system. This has been overridden
    to be a custom model since we want to be able to set levels instead of 
    setting up groups (which is much more annoying). Another advantage of
    doing it this way is that it falls in line nicely with the model as view
    framework that allows for easy reading and editing of user entities.
    
    There are three levels within the system:
    
        creator : can create entities (except User entities)
        modifier : can modify entities (except User, TimerRun, XlgStat, and 
                    default TimerSetView for a TimerSet). Models have a level
                    of granularity to them that no one can edit.
        deleter : can delete anything in the system (including User). This
                  level can also grant any of the other levels to any user.
                  
    Of note is the fact that each higher level has the same right as the one
    below. Also, the following entities are tracked by user created and can
    be deleted and modified by the creator:
    
        Non-default TimerSetView
        DailyReport
        Project
        
    A special fourth level is available known as submitter. This is an 
    anonymous user and can submit data via the submit/* endpoints only.
    Anonymous users can only view, they do not have permission to do anything
    else.
    
    Level granting has to be done by someone on SystemTest, who are all granted
    a deleter level.
    
    The User model is only available to see if the user is of deleter level.
    '''
    joined_on = models.DateTimeField('The time the poster first joined '
                                     'our blog.', auto_now_add = True)
    
    public_fields = set(["id", "email", "joined_on", "level", "last_login"])
    register_route = True
    
    USERNAME_FIELD = 'email'
    
    levels = {
              0 : "student",
              1 : "teacher"
              }
    
    rev_levels = {
              "student" : 0,
              "teacher" : 1
                  }
    
    _perms = {x : "deleter" for x in m.allowed_methods}
    
    def get_full_name(self):
        '''
       Mandatory Override of AbstractBaseUser.get_full_name(self)
       '''
        return self.email
    
    def get_short_name(self):
        '''
        Mandatory Override of AbstractBaseUser.get_short_name(self)
        '''
        return self.email.split('@')[0] #get just the username
    
    def set_password(self, raw_password, *args, **kwargs):
        '''
        Override of AbstractBaseUser.set_password(self, raw_password):
        
        This method will do some constraint validation on the password before saving it if settings.VALIDATE_PASSWORD_RULES is set to True
        '''
        if getattr(settings, 'VALIDATE_PASSWORD_RULES' , False):
            if len(self.password) < 5:
                raise ValueError("The password needs to be over 5 characters long.")
        super(User, self).set_password(raw_password, *args, **kwargs)
    
    @classmethod    
    def get_level_name(self, level):
        return self.levels[level]
    
    @classmethod
    def get_level_by_name(self,level_name):
        return self.rev_levels[level_name]
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'User'

class UserSubmissions(ModPerms):
    register_route = True
    register_user_on_create = 'owner'
    submission = models.DateTimeField("the time it was first submitted.",
                                      default=dt.now, 
                                      db_index=True
                                      )
    owner = models.ForeignKey(User)
    
    def do_get(self, *args, **kwargs):
        """
        Only the teacher can see objects that they did not create.
        """
        qs = super(UserSubmissions, self).do_get(self, *args, **kwargs)
        if not kwargs['_authenticated']:
            qs = qs.filter(owner=self.user)
        return qs
    
    @method_decorator(has_level_or_is_obj_creator('teacher'))
    def get(self, request, *args, **kwargs):
        return super(ModPerms, self).get(request, *args, **kwargs)
    
    class Meta:
        abstract = True
        
class PracticeSubmission(UserSubmissions):
    occurred = models.DateTimeField("the time the practice occurred.")
    duration = models.IntegerField("the duration in seconds")
    notes = models.TextField("any notes for the teacher.", null=True)
    
class Assignment(m):
    register_user_on_create = 'creator'
    register_route = True
    created_on = models.DateTimeField("the time it was first created.",
                                      default=dt.now, 
                                      db_index=True
                                      )
    description = models.TextField("A description of what the assignment is.")
    creator = models.ForeignKey(User)
    
    @method_decorator(has_level('teacher'))
    def dispatch(self, request, *args, **kwargs):
        return super(Assignment, self).dispatch(request, *args, **kwargs)

class AssignmentInstance(m):
    register_route = True
    due_date = models.DateTimeField("the date that it is due.",
                                    db_index=True)
    requirements = models.TextField("a json object of requirements the "
                                    "assignment entails, which can be different "
                                    "per instance intialization")
    models.ManyToManyField(User, 
                           through="UserAssignment", 
                           related_name="students")
    
    @method_decorator(has_level('teacher'))
    def post(self, request, *args, **kwargs):
        return super(AssignmentInstance, self).post(request, *args, **kwargs)
    
    @method_decorator(has_level('teacher'))    
    def put(self, request, *args, **kwargs):
        return super(AssignmentInstance, self).put(request, *args, **kwargs)
    
    @method_decorator(has_level('teacher'))    
    def delete(self, request, *args, **kwargs):
        return super(AssignmentInstance, self).delete(request, *args, **kwargs)
        
class RealField(models.FloatField):
    '''
    Subclassing the models.FloatField to allow for the real datatype found in 
    postgres. To see more about this feature, go to
    https://docs.djangoproject.com/en/dev/howto/custom-model-fields/
    
    Got the idea to sublass float from 
    https://groups.google.com/forum/#!topic/django-users/vqUPaaq3QGM
    '''
    def db_type(self, connection):
        return 'REAL'
        
class UserAssignment(m):
    register_route = True
    assignment = models.ForeignKey(AssignmentInstance)
    owner = models.ForeignKey(User)
    reviewed = models.BooleanField("teacher has reviewed the assignment.", 
                                   default=False)
    first_view = models.DateTimeField("the time the student first viewed the"
                                      "assignment.", null=True)
    requirements = models.TextField("the json object of the assignment but with"
                                    "the fields marked as completed or not.")
    completed = RealField("the percentage of the assignment done.", default=0.0)
    score = RealField("the score of the assignment", null=True)
    
    @method_decorator(has_level('teacher'))
    def post(self, request, *args, **kwargs):
        assignment = self.data["data"].get("assignment_id", None)
        if assignment is None:
            return err("Must include an assignment_id to create a user assignment.")
        if 'owner_id' not in self.data["data"]:
            return err("Must include an owner_id to create a user assignment.")
        self.data["requirements"] = (AssignmentInstance
                                        .objects
                                        .filter(id=assignment)
                                        .values_list("requirements", flat=True)[0]
                                    )
        return super(UserAssignment, self).post(request, *args, **kwargs)
    
    @method_decorator(authenticated)   
    def put(self, request, *args, **kwargs):
        def remove_prohibited(d):
            removed = ""
            if "assignment" in d:
                del d['assignment_id']
                removed += "assignment_id"
            if "owner" in d:
                del d['owner_id']
                removed += "owner_id"
            if "reviewed" in d:
                del d['reviewed']
                removed += "reviewed"
            if "score" in d:
                del d['score']
                removed += "score"
            return removed
                
        if request.user.level > 0:
            return super(UserAssignment, self).put(request, *args, **kwargs)
        else:
            expand = self.expand #ensure that it returns dictionaries
            self.expand = False
            qs = self.do_get(request, *args, **kwargs)
            self.expand = expand 
            print(qs, request.user.pk)
            if any([request.user.pk != x['owner_id'] for x in qs]):
                return err("Unauthorized. Cannot make change for someone other"
                           " than yourself.", 403)
            if isinstance(self.data, list):
                removed = []
                for d in self.data:
                    removed.append(remove_prohibited(d['data']))
                if removed:
                    removed = '|'.join(["{} : {}".format(i, r) 
                                         for i, r in enumerate(removed)])
            else:
                removed = remove_prohibited(self.data['data'])
            
            resp = super(UserAssignment, self).put(request, *args, **kwargs)
            if removed:
                setattr(resp, "X-Removed", removed)
                print(removed)
            return resp
    
    @method_decorator(has_level('teacher'))    
    def delete(self, request, *args, **kwargs):
        return super(UserAssignment, self).delete(request, *args, **kwargs)