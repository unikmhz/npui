from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from sqlalchemy.exc import DBAPIError
from pyramid.security import authenticated_userid, remember, forget, unauthenticated_userid, authenticated_userid
from pyramid.url import route_url

from .models import (
    DBSession,
    AccessEntity
    )
from netprofile.common.cache import cache


@view_config(route_name='home', renderer='main.mak')
def main_view(request):
    try:
        all_users = DBSession.query(AccessEntity).all()
        all_users_dict = dict(zip([l.nick for l in all_users], [l.password for l in all_users]))

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

#new user registration
@view_config(route_name='newuser', renderer='newuser.mak')
def newuser_view(request):
    if request.POST:
        #проверяем совпадение паролей, добавляем пользователея в базу, выводим сообщение об успешной регистрации. 
        login = request.POST.get('username', None)
        passwd = request.POST.get('userpass', None)
        confpass = request.POST.get('confirmpass', None)
        sameuser = DBSession.query(AccessEntity).filter(AccessEntity.nick==login).first()
        if sameuser is None:
            if passwd == confpass:
                #create a new user here
                #
                return {'request':request, 'message':"New user registered", 'login':login, 'passwd':passwd, 'back':'/'}
            else:
            #redirect to login page
                return {'request':request, 'message':"Password didn't match, try again", 'login':login, 'passwd':passwd}
        else:
            return {'request':request, 'message':"There's already a user with same login {0}".format(sameuser.nick), 'login':login, 'passwd':passwd}
        
        return {'request':request, 'message':'Registration form'}

    return {'request':request, 'message':'Registration form'}


#forgotpassword
#@view_config(route_name='forgotpassword')
