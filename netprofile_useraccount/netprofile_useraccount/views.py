import hashlib
import smtplib
import transaction
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from sqlalchemy.exc import DBAPIError
from pyramid.security import authenticated_userid, remember, forget, unauthenticated_userid, authenticated_userid
from pyramid.url import route_url

from .models import (
    DBSession,
    AccessEntity,
    PhysicalEntity,
    EntityType,
    EntityFlag, 
    EntityFlagType,
    Stash
    )
from netprofile.db.fields import DeclEnum
from netprofile.common.cache import cache

fr = "help@piggy.thruhere.net"

@view_config(route_name='home', renderer='main.mak')
def main_view(request):
    if not authenticated_userid(request):
        return  HTTPFound(request.route_url("login"))
    else:
        access_user = DBSession.query(AccessEntity).filter(PhysicalEntity.nick==authenticated_userid(request),  AccessEntity.parent_id != None).join(Stash).first()
        parent_id = access_user.parent_id
        stash = access_user.stash
        physical_user = DBSession.query(PhysicalEntity).filter(PhysicalEntity.id==parent_id).first()
        
        return {'project': 'netprofile_useraccount, {0}'.format(request.application_url), 'current_user':physical_user, 'login':authenticated_userid(request), 'stash':stash}

    
#login view
@view_config(route_name='login', renderer='login.mak')
def login_view(request):
    if request.POST:
        login = request.POST.get('username', None)
        passwd = request.POST.get('userpass', None)
        user = DBSession.query(AccessEntity).filter(AccessEntity.nick==login, AccessEntity.parent_id != None).first()

        if user is not None:
            user_flag = DBSession.query(EntityFlag).filter(EntityFlag.entity_id==user.id).first()
            user_flag_type = DBSession.query(EntityFlagType).filter(EntityFlagType.id==user_flag.type_id).first()
            #user exists, passwd is wrong
            if user.password is not None:
                if passwd == user.password:
                    print("OK")
                    if user_flag_type.name != "Inactive":
                        headers = remember(request, login)
                        request.response.headerlist.extend(headers)
                        return  HTTPFound(request.route_url("home"), headers=headers)
                #user is registered but account isn't activated yet
                    else:
                        message = """It looks like you haven't activate your account yet, check your mail and try again."""
                        return {'request':request, 'message':message}
                else:
            #here we have to return error message about wrong authentication
            #and redirect to login page with promt to try logging in again
                    message = 'Something is wrong, try again'
                    return {'request':request, 'message':message}
        #user doesn't exists
            else:
                message = 'Something gone wrong, try again'
                return {'request':request, 'message':message}
        else:
            message = """It seems that there's no user with this login. You can register a new user <a href={0}/newuser>here</a>""".format(request.application_url)
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
        #!!!check password strenght
        passwd = request.POST.get('userpass', None)
        confpass = request.POST.get('confirmpass', None)
        #!!!add validation
        email = request.POST.get('email', None)
        name_given = request.POST.get('name_given', None)
        name_family = request.POST.get('name_family', None)
        sameuser = DBSession.query(AccessEntity).filter(AccessEntity.nick==login).first()

        if sameuser is None:
            if passwd == confpass:
                DBSession.execute("SET @ACCESSLOGIN = 'admin'")
                DBSession.execute("SET @ACCESSUID = 0")
                DBSession.execute("SET @ACCESSGID = 0")
                new_physical_entity = PhysicalEntity(nick=login, relative_dn="cn=%s" % login, type=EntityType.physical, name_family=name_family, name_given=name_given, email=email)
                DBSession.add(new_physical_entity)
                DBSession.flush()
                DBSession.refresh(new_physical_entity)

                new_stash = Stash(entity_id=new_physical_entity.id, name="Основной счет")
                DBSession.add(new_stash)
                DBSession.flush()
                DBSession.refresh(new_stash)

                new_access_entity = AccessEntity(nick=login, relative_dn="cn=%s" % login, type=EntityType.access, parent_id=new_physical_entity.id, password=passwd, stash_id=new_stash.id, rate_id=1)
                DBSession.add(new_access_entity)
                DBSession.flush()
                DBSession.refresh(new_access_entity)

                new_access_entity_flag = EntityFlag(entity_id=new_access_entity.id, type_id=2)
                DBSession.add(new_access_entity_flag)
                DBSession.flush()

                #now we generate a hash string from user login, password and email. 
                #to make it valid for an hour we shoud add to hashfunction something like "2001-01-01 10AM". So the link will work only for 1 hour
                #+datetime.datetime.today().strftime("%d-%m-%y %H")
                secret_link = "{0}/activate?uid={1}&secretlink={2}".format(request.application_url, new_physical_entity.id, hashlib.md5(login.encode("utf-8")+passwd.encode("utf-8")+email.encode("utf-8")).hexdigest())
                ##and send it to the given email
                serv = smtplib.SMTP('localhost')
                serv.sendmail(fr, email, "Hi. Here's the activation link for your account: {0}".format(secret_link))
                return {'request':request, 'message':"New user registered, confirmation link sent to your email %s" % email, 'login':login, 'passwd':passwd, 'back':'/'}
            else:
            #redirect to login page
                return {'request':request, 'message':"Password didn't match, try again", 'login':login, 'passwd':passwd}
        else:
            return {'request':request, 'message':"There's already a user with same login {0}".format(sameuser.nick), 'login':login, 'passwd':passwd}
        
        return {'request':request, 'message':'Registration form'}
    
    return {'request':request, 'message':'Registration form'}


#account activation
@view_config(route_name='activate', renderer='activate.mak')
def activate_view(request):
    user_id = int(request.GET.get('uid', None))
    secretlink = request.GET.get('secretlink', None)
    if user_id is not None and secretlink is not None:
        db_user = DBSession.query(PhysicalEntity).filter(PhysicalEntity.id==user_id).first()
        if db_user is not None:
            db_access = DBSession.query(AccessEntity).filter(AccessEntity.id==db_user.children[-1].id).first()
            # + datetime.datetime.today().strftime("%d-%m-%y %H")
            db_hash = hashlib.md5(db_user.nick.encode("utf-8") + db_access.password.encode("utf-8") + db_user.email.encode("utf-8")).hexdigest()
            if secretlink == db_hash:
                #setting access_flag to active state
                access_flag = DBSession.query(EntityFlag).filter(EntityFlag.entity_id==db_user.children[-1].id).first()
                if access_flag.type_id == 1:
                    return {'request':request, 'login': db_user, 'message':'It looks like you have already activated your account'}
                else:
                    access_flag.type_id=1
                    DBSession.add(access_flag)
                    DBSession.flush()
                    return {'request':request, 'login': db_user}
            else:
                return {'request':request, 'login': db_user, 'message':"Something gone wrong, sorry :("}
        else:
            return {'request':request, 'message':"It looks like there is no user with requested ID. You can try to register a new one <a href={0}/newuser>here</a>".format(request.application_url)}
    else:
        return HTTPFound(request.route_url("home"))   

#forgotpassword
@view_config(route_name='forgotpassword', renderer='forgot.mak')
def forgotpassword_view(request):
    if request.POST:
        login = request.POST.get('username', None)
        sameuser = DBSession.query(AccessEntity).filter(AccessEntity.nick==login).first()
        email = DBSession.query(PhysicalEntity.email).filter(PhysicalEntity.id==sameuser.parent_id).first()

        if sameuser is None:
            return {'request':request, 'message':"It looks like we haven't a user with this login, try to register a new one", 'login':login, 'back':'<a href="/newuser">New user registration</a>'}
        else:
            #send password to relevant email
            serv = smtplib.SMTP('localhost')
            serv.sendmail(fr, email, "Here's your password, don't forget it! \n {0}".format(sameuser.password))

            return {'request':request, 'message':"Your password is sent to your email", 'back':'<a href="/">Back</a>'}
        
    
    return {'request':request, 'message':'Remind me my password!'}
    
    
