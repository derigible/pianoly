"""
A package that is committed to taking the best of the Django ORM and fixing
the poor serialization efforts

It also attempts to intelligently determine what serialization to use depending
on the Accept header passed in to the service. If no Accept header is
found, or the type is not supported, will default to application/json.

To make this possible, a few more attributes must be added to a model:

    1) the base queryset for the model must be added as the qs attribute
"""


import json
from xml.etree import ElementTree

from django.http.response import HttpResponse as resp
from django.core.files.base import File
from django.core.serializers.json import DjangoJSONEncoder as djson
from django.db import models
from django.db.models.manager import Manager
from django.conf import settings

def _output_raw(field):
    """
    Helper function to output data in the correct format 
    """
    pass

def _serialize_xml(mview, qs, expand):
    """
    Serialize a queryset into xml.
    """
    raise NotImplementedError("Parsing of query sets to xml not yet supported.")

def foreign_obj_to_dict(base_type, fobj, depth, rootcall, max_depth=0, 
                        rels=set(), fos=set()):
    fields = getattr(fobj, "public_fields", fobj._meta.get_all_field_names())
    fkDict = {}
    for f in fields:
        try:
            fo = getattr(fobj, f)
        except AttributeError:
            fo = getattr(fobj, f+'_set')
        if isinstance(fo, Manager):
            if max_depth >= depth and type(fo) not in rels:
                fkDict[f] = foreign_rel_to_dict(base_type, 
                                                fo, 
                                                depth + 1,
                                                rootcall,
                                                max_depth,
                                                rels)
        elif isinstance(fo, models.Model):
            if (max_depth >= depth and type(fo) != type(base_type) 
                and type(fo) not in fos):
                fos.add(type(fobj))
                fkDict[f] = foreign_obj_to_dict(base_type, 
                                                fo, 
                                                depth + 1, 
                                                rootcall,
                                                max_depth,
                                                rels,
                                                fos)
                fos.remove(type(fobj))
        elif isinstance(fo, File):
            fkDict[f] = fo.name  
        else: 
            fkDict[f] = fobj.serializable_value(f)
    if getattr(settings, 'HYPERLINK_VALUES', True):
        fkDict["url"] = hyperlinkerize(fkDict[getattr(fobj, 'unique_id', 'id')], 
                                      rootcall, 
                                      fobj) 
    
    return fkDict

def foreign_rel_to_dict(base_type, frel, depth, rootcall, max_depth=0, 
                        rels=set()):
    rels.add(type(frel))
    fks = []
    for fk in frel.all():
        if max_depth >= depth:
            fkDict = foreign_obj_to_dict(base_type, fk, depth + 1, 
                                         rootcall, max_depth, rels)
            fks.append(fkDict)
    return fks

def objs_to_dict(base_type, qs, field_names, depth=0, rootcall=''):
    vals = []
    for m in qs:
        obj = {}
        vals.append(obj)
        for f in field_names:    
            try:
                field = getattr(m, f)
            except AttributeError:
                continue #not a field on the model
            if isinstance(field, Manager):
                obj[f] = foreign_rel_to_dict(base_type, field, 1, rootcall, depth) 
            elif isinstance(field, models.Model):
                obj[f] = foreign_obj_to_dict(base_type, field, 1, rootcall, depth) 
            elif isinstance(field, File):
                obj[f] = field.name               
            else:
                obj[f] = field
    return vals

def hyperlink(rootcall, mview, append = ''):
    """
    Produce a hyperlink for the call. Only produces a hyperlink if rootcall is
    not empty. If you don't want to hyperlink values, set the
    project setting HYPERLINK_VALUES = False.
    
    @param rootcall: the rootcall of the request
    @param mview: the model view of interest
    @param append: append a string (ie query) to the hyperlink
    @return the hyperlink to the base model
    """
    if rootcall and getattr(settings, 'HYPERLINK_VALUES', True):
        return "{}/{}/{}".format(rootcall, mview.url_path, append)
    return append

def hyperlinkerize(value, rootcall, mview):
    """
    Make the resource a hyperlink to the field. Only makes it as a hyperlink
    if rootcall is not empty. If you don't want to hyperlink values, set the
    project setting HYPERLINK_VALUES = False.
    
    @param value: the field value
    @param rootcall: the http(s)://domain
    @param mview: the model the field rests in
    @return the data to send back, either hyperlinked or not
    """
    if rootcall and getattr(settings, 'HYPERLINK_VALUES', True):
        return hyperlink(rootcall, mview, '{}/'.format(value))
    else:
        return value

def _create_paging_dict(mview, qs, rootcall):
    """
    Create the paging dictionary used for returns to the client.
    
    @param mview: the modelview to use
    @param qs: the queryset to paginate
    @param rootcall: the protocol-domain combo as string
    @return the new queryset and the paging dict
    """
    qs, paging = mview.paginate(qs)  
    page_count = paging.get("number_of_pages", 1)
    page_number = paging.get("page_num", 1)
    total_entities = paging.get("count", len(qs))
    number_per_page = paging.get("limit", len(qs))
    returned = paging.get("returned", len(qs))
    rslt = {
           "count" : len(qs),
           "page_count" : page_count,
           "last_page" : hyperlink(rootcall, 
                               mview, 
                               '?_page={}{}'.format(page_count,
                                                    '&_limit={}'.format(
                                                           number_per_page
                                                                        )
                                                    )
                                   ),
           "page_number" : page_number,
           "total_entities" : total_entities,
           "number_per_page" : number_per_page,
           "number_returned" : returned,
           "next" : (
                     hyperlink(rootcall, 
                               mview, 
                               '?_page={}{}'.format(page_number + 1,
                                                    '&_limit={}'.format(
                                                           number_per_page
                                                                        )
                                                    )
                               )
                     if page_number + 1 <= page_count else None
                     ),
           "previous" : (
                         hyperlink(rootcall, 
                                   mview, 
                                   '?_page={}{}'.format(page_number - 1,
                                                    '&_limit={}'.format(
                                                       number_per_page
                                                                    )
                                                        )
                                                    
                                   ) 
                     if page_number - 1 <= page_count and
                        page_number - 1 > 0 else None
                        )
            }
    return qs, rslt

def _serialize_json(mview, qs, rootcall, extra = None):
    """
    Serialize a queryset into json. If expand is true, will treat the qs as 
    models; if false, will treat as dictionaries. If the settings has included
    the RETURN_SINGLES=TRUE attribute, will return 1-length querysets as a 
    single object without meta-data attached (also the default behavior).
    
    Any extra values retrieved before serialization but not apart of the 
    mview can be passed with the extra param. This needs to be json serializable
    data.
    """
    paginate = mview.params.get('_page', getattr(mview, '__paginate', 0))
    return_single = (len(qs) > 1 
            or paginate 
            or not getattr(settings, "RETURN_SINGLES", True)
            or getattr(mview, 'no_singles', False))
    expand = mview.expand
    if mview.fields:
        #get all of the field names specified and in the model
        field_names = set(mview.fields).intersection(mview.field_names)
    else:
        field_names = set(mview.field_names)  

    if paginate:
        qs, rslt = _create_paging_dict(mview, qs, rootcall)
        rslt["data"] = []
    else:
        rslt = {"count" : len(qs), "data" : []}
    if not expand:
        if return_single:
            rslt["data"] = list(qs)
        else:
            rslt = list(qs)[0] if len(qs) > 0 else rslt
    else:  
        vals = objs_to_dict(mview, qs, field_names, mview.sdepth, rootcall)
        if return_single:
            rslt["data"] = vals
        else:
            rslt = vals.pop() if len(vals) else rslt
    if getattr(settings, 'HYPERLINK_VALUES', True) and not mview.fields:
        if return_single:
            for r in rslt["data"]:
                r["url"] = hyperlinkerize(r[mview.unique_id], 
                                          rootcall, 
                                          mview) 
        elif len(qs) != 0:
            rslt["url"] = hyperlinkerize(rslt[mview.unique_id], 
                                          rootcall, 
                                          mview) 
    if extra is not None:
        rslt['extra'] = extra
    return json.dumps(rslt, cls=djson)

def serialize(mview, qs, serializer=None, rootcall='', extra = None):
    """
    One of two public methods of this package. Pass in the ModelAsView object 
    and the qs you wish to serialize with the model it is querying
    and the return value will be either json or xml. Other values are not 
    currently supported, but a serializer that accepts a query set  
    as argument may be used by passing it in through the serializer keyword.
    
    It is assumed that the models have added the proper attributes to fit in
    with this packages idea of what a model should look like.
    
    @param mview: the mview object
    @param qs: the queryset being parsed
    @param serializer: the serializer to use
    @param rootcall: the root of the call to use in hyperlinked returns
    @param extra: any extra data to serialize that is not apart of the mview
    @return the serialized string of queryset qs
    """
    if serializer is not None:
        return serializer(qs)
#     if "xml" in mview.accept:
#         return _serialize_xml(qs, rootcall)
    return _serialize_json(mview, qs, rootcall, extra)
    
def serialize_to_response(mview, qs, serializer=None, rootcall='', extra = None):
    """
    One of two public methods of this package. Pass in the ModelAsView object
    and the qs you wish to serialize and the return value will be either json
    or xml. Other values are not currently supported, but a serializer that
    accepts a model as a single argument may be used by passing it in
    through the serializer keyword.
    
    The Accept header is used to set the content_type of the response and
    a django.http.response.HttpResponse object is returned. If you pass in
    a custom serializer, you must set the response's content_type to the
    correct content_type manually.
    
    It is assumed that the models have added the proper attributes to fit in
    with this packages idea of what a model should look like.
    
    @param mview: the mview object
    @param qs: the queryset being parsed
    @param serializer: the serializer to use
    @param rootcall: the root of the call to use in hyperlinked returns
    @param extra: any extra data to serialize that is not apart of the mview
    @return a response object with the serialized data as payload
    """
    retData = serialize(mview, qs, serializer, rootcall, extra)
    if "xml" in mview.accept:
        ct = "application/xml"
    else:
        ct = "application/json"
    return resp(retData, content_type=ct)