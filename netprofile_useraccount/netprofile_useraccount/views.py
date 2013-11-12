from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from sqlalchemy.exc import DBAPIError
from pyramid.security import authenticated_userid, remember, forget, unauthenticated_userid, authenticated_userid

from .models import (
    DBSession,
    )

from netprofile_entities import AccessEntity, Entity
from netprofile_core import User
from netprofile_devices import Device
from netprofile.common.cache import cache

@view_config(route_name='home', renderer='main.mak')
def main_view(request):
    try:
        all_users = DBSession.query(AccessEntity).all()
        all_users_dict = dict(zip([l.acc_entity.nick for l in all_users], [l.password for l in all_users]))

    except DBAPIError:
        return Response("Error connecting to database", content_type='text/plain', status_int=500)

    
    if not authenticated_userid(request):
        return  HTTPFound(request.route_url("login"))
    else:
        return {'users': all_users, 'project': 'netprofile_useraccount', 'login':authenticated_userid(request), 'passwd':all_users_dict[authenticated_userid(request)]}

    
#login view
@view_config(route_name='login', renderer='login.mak')
def login_view(request):
    try:
        all_users = DBSession.query(AccessEntity).all()
    except DBAPIError:
        return Response("Error connecting to database", content_type='text/plain', status_int=500)

    if request.POST:
        login = request.POST.get('username', None)
        passwd = request.POST.get('userpass', None)
        user_passwd = DBSession.query(AccessEntity.password).filter(AccessEntity.nick==login).first()
        #user exists, passwd is wrong
        if user_passwd is not None:
            if passwd == user_passwd[-1]:
                print("OK")
                headers = remember(request, login)
                request.response.headerlist.extend(headers)
                return  HTTPFound(request.route_url("home"), headers=headers)
        
            else:
            #here we have to return error message about wrong authentication
            #and redirect to login page with promt to try logging in again
                message = 'Something is wrong, try again'
                return {'request':request, 'message':message}
        #user doesn't exists
        else:
            message = 'Something gone wrong, try again'
            return {'request':request, 'message':message}

    if not authenticated_userid(request):
        return {'request':request, 'message':'Login page'}
    else:
        return HTTPFound(request.route_url("home"))   

#logout
@view_config(route_name='logout')
def logout_view(request):
    if authenticated_userid(request):
        headers = forget(request)
        return HTTPFound(request.route_url("login"), headers=headers)   
    else:
        return HTTPFound(request.route_url("login"))   
