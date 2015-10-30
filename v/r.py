'''
Created on Oct 26, 2015

@author: derigible

Ad-hoc endpoints.
'''

from django.http.response import JsonResponse as jr
from django.views.generic.base import View

from db.models import Assignment
from db.models import User
from mviews.serializer import objs_to_dict
from django.core.exceptions import ObjectDoesNotExist
from mviews.utils import err


class Assignments(View):
    """
    Returns information on assignments that don't fit into the lookups
    defined in the mavs.
    """
    
    routes = [{"pattern" : "assignment-students/{}",
               "map" : [["(?P<id>\d*)"]],
               "kwargs" : {"assign2students" : True}
               }
              ]
    
    def get(self, request, *args, **kwargs):
        """
        Determine which response should be sent.
        """
        if "assign2students" in kwargs:
            return self._get_assignments_and_students_enrolled_and_not_enrolled(request, *args, **kwargs)
        
    def _get_assignments_and_students_enrolled_and_not_enrolled(self, request, *args, **kwargs):
        """
        Retrieves the given assignment and returns a separate list of all of
        the students with their name and their id. If they are assigned to
        the assignment, they will be in the assigned_to attribute, and the
        to_assign will the others go.
        """
        try:
            assigned = Assignment.objects.prefetch_related().get(id=kwargs['id'])
        except ObjectDoesNotExist:
            return err("Assignment with id {} does not exist."
                            .format(kwargs['id'])
                       )
        students = User.objects.exclude(id__in=assigned.users.all())
        
        respDict = {
                    "assignment" : {
                                    "description" : assigned.description,
                                    "due_date" : assigned.due_date
                                    },
                    "assigned_to" : objs_to_dict(User, 
                                                 assigned.users.all(),
                                                 ("id", "lname", "fname")
                                                 ),
                    "to_assign" : objs_to_dict(User, 
                                                 students,
                                                 ("id", "lname", "fname")
                                                 )
                    }
        return jr(respDict)
        