'''
Created on Aug 27, 2015

@author: derigible
'''

from json import loads as load
from json import dumps as d
import math

from django.http.response import HttpResponse

def err(msg, status = 400):
    '''
    Send an error response.
    
    @param msg: the reason for the error
    @param status: the status code of the error
    @return the HttpResponse object
    '''
    resp = HttpResponse(d({"err" : "{}".format(msg)}), 
                        content_type = "application/json", 
                        status = status)
    resp.reason_phrase = msg
    return resp
    
def read(request):
    '''
    Read and decode the payload.
    
    @param request: the request object to read
    @return the decoded request payload
    '''
    d = request.read()
    if d:
        try:
            d = load(d.decode('utf-8'))
        except ValueError as e:
            raise ValueError("Not a valid json object: {}".format(e))
    return d

def paginator(queryset, limit=10, page_num=1):
    '''
    Figures out the pagination for the queryset provided. This queryset should
    be a select statement only that does not do any sort of counting or 
    limiting to the call. I didn't like the way Django does pagination, 
    so I wrote my own.
    
    @param request: the request of the call
    @param queryset: the queryset to paginate
    @param limit: the limit of the entities in the page
    @return the sliced queryset by page
    @return a dictionary of values: {count: the number of entities, 
                number_pages: number of pages, 
                page_num: the page number, 
                limit: number of entities for page}
    '''
    try:
        to_return = limit = 10 if int(limit) <= 0 else int(limit)
    except TypeError:
        to_return = limit = 10
    try:
        page_num = int(page_num)
    except TypeError:
        page_num = 1
    count = queryset.count()
    number_pages = max(math.floor(count/ limit), 2 if count > limit else 1)
    page_num = page_num if page_num <= number_pages else number_pages
    offset = limit * (page_num-1) #get the start of the page
    #get the rest of the runs for the last page
    if page_num == number_pages and count - offset > 0 and page_num > 1:
        to_return = count - offset
    end = to_return * page_num
    return queryset[offset:end], {"count" : count, 
                                  "number_of_pages" : number_pages, 
                                  "page_num" : page_num, 
                                  "limit" : limit,
                                  "returned" : to_return}