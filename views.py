from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import TemplateView, ListView, DetailView # Import TemplateView
from django.contrib.auth.decorators import login_required
from account import views
from django.db.models import Q
import json
from django.http import JsonResponse
from django.db import connection
from hashids import Hashids
from hashid_field import HashidField
from .models import PrivacyType, PrivacyOn, UserPrivacy,BlockedUser,UserSpecificContacts
from .models import NotificationEventTypes, NotificationType, Notification
from django.shortcuts import render
from django.views.decorators.cache import cache_control

"""
Method:             settingStat
Developer:          Bhushan
Created Date:       06-07-2018
Purpose:            Setting data
Params:             []
Return:             []
"""
@login_required
def __settingStat(request):
    hashids = Hashids(min_length=16)
    try:
        userPrivacyType = PrivacyType.objects.all()
    except PrivacyType.DoesNotExist:
        userPrivacyType = None
    try:
        privacyData = UserPrivacy.objects.filter(user_id = request.user.id)
    except UserPrivacy.DoesNotExist:
        privacyData = None

    context = {
        "privacyType" : userPrivacyType,
        "userPrivacy" : privacyData,
    }
    return context
"""end function __settingStat"""

"""
Method:             getAllUsersData
Developer:          Bhushan
Created Date:       20-06-2018
Purpose:            User data for input search
Params:             null
Return:             [list]
"""
@login_required
def getAllUsersData(request):
    hashids = Hashids(min_length=16)
    try:
        user = User.objects.filter(~Q(id = 1),~Q(id = request.user.id))[:10]
    except User.DoesNotExist:
        user = None
    userData = []
    for user in user:
        listdata = {'id': hashids.encode(user.id), 'name': user.first_name}
        userData.append(listdata)
    response = HttpResponse(json.dumps(userData))
    return response
"""end function getAllUsersData"""

"""
Method:             getAllUsersByName
Developer:          Bhushan
Created Date:       20-06-2018
Purpose:            User data for input search
Params:             null
Return:             [list]
"""
@login_required
def getUsersByName(request):
    if request.method == 'GET':
        searchName = request.GET.get('search_name')
        try:
            user = User.objects.filter(first_name__icontains=searchName)
        except User.DoesNotExist:
            user = None
        userData = []
        for user in user:
            listdata = {'value': user.id, 'label': user.first_name}
            userData.append(listdata)
        response = HttpResponse(json.dumps({'data':userData }),content_type='application/json')
        response.status_code = 200
        return response
"""end function getAllUsersData"""

"""
Method:             userPrivacySetting
Developer:          Bhushan
Created Date:       17-06-2018
Purpose:            User forgot password and send email to rest password
Params:             null
Return:             CMS []
"""
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def userPrivacySetting(request):
    hashids = Hashids(min_length=16)
    template_name = 'user_privacy_setting.html'
    currentUser = request.user
    userInfo = views.__userStats(request) #defined in accounts views.py
    settingData = __settingStat(request)

    try:
        user = User.objects.filter(~Q(id = 1),~Q(id = request.user.id))
    except User.DoesNotExist:
        user = None

    userData = []
    for user in user:
        listdata = (user.id,user.username)
        userData.append(listdata)
    userData = json.dumps(userData)
    resuestUserId = hashids.encode(request.user.id)

    cursor = connection.cursor()
    cursor.execute("SELECT id, zone FROM timezone")
    timezone = cursor.fetchall()
    context = {
        "userData": userData,
        "resuestUserId" : resuestUserId,
        "profile" : userInfo['profile'],
        "privacyOn" : settingData['privacyOn'],
        "privacyType" : settingData['privacyType'],
    }

    return render(request, template_name, context)
"""end function userPrivacySetting"""

"""
Method:             __addPrivacySetting
Developer:          Bhushan
Created Date:       06-06-2018
Purpose:            Add user Privacy setting
Params:             null
Return:             []
"""
def __addPrivacySetting(evetType, privacyType, userId):
    userprivacy = UserPrivacy()
    userprivacy.privacyon_id = evetType
    userprivacy.privacytype_id = privacyType
    userprivacy.user_id = userId
    userprivacy.save()
    return True
"""end function __addPrivacySetting"""

"""
Method:             addUserPrivacy
Developer:          Bhushan
Created Date:       06-06-2018
Purpose:            Add user Privacy
Params:             null
Return:             CMS []
"""
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addUserPrivacy(request):
    if request.user.is_authenticated():
        template_name = 'user_privacy_setting.html'
        currentUser = request.user
        if request.method == 'POST':
            try:
                userPrivacyData = UserPrivacy.objects.all().filter(user_id = currentUser.id)
            except UserPrivacy.DoesNotExist:
                userPrivacyData = None

            if userPrivacyData is not None:
                userPrivacyData.delete()
                privacyContent = None
            else:
                privacyContent = None

            if privacyContent is None:
                __addPrivacySetting(request.POST['privacy_event_type_1'],request.POST['privacy_type_id_1'],currentUser.id)
                __addPrivacySetting(request.POST['privacy_event_type_2'],request.POST['privacy_type_id_2'],currentUser.id)
                __addPrivacySetting(request.POST['privacy_event_type_3'],request.POST['privacy_type_id_3'],currentUser.id)
                __addPrivacySetting(request.POST['privacy_event_type_4'],request.POST['privacy_type_id_4'],currentUser.id)
                __addPrivacySetting(request.POST['privacy_event_type_5'],request.POST['privacy_type_id_5'],currentUser.id)
                __addPrivacySetting(request.POST['privacy_event_type_6'],request.POST['privacy_type_id_6'],currentUser.id)
                messages.success(request, 'Information has been saved successfully')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('/')
"""end function addUserPrivacy"""

"""
Method:             loadUsersByName
Developer:          Bhushan
Created Date:       19-07-2018
Purpose:            Ajax Method to load data on search to block user
Params:             [name]
Return:             [user list]
"""
@login_required
def loadUsersByName(request):
    if request.user.is_authenticated():
        hashids = Hashids(min_length=16)
        if request.method == 'GET':
            name = request.GET.get('search')
            sname = "%%%s%%" % name
            if name:
                cursor = connection.cursor()
                cursor.execute("SELECT auth_user.id id, auth_user.id, auth_user.first_name, auth_user.last_name, profile.profile_image, bu.is_blocked as blocked FROM auth_user LEFT JOIN followers_and_followings ff ON (auth_user.id = ff.follower_id AND ff.user_id = %s) LEFT JOIN profile ON profile.user_id = auth_user.id LEFT JOIN block_users bu ON (bu.blocked_user_id = auth_user.id AND bu.user_id = %s) where (auth_user.first_name LIKE %s OR auth_user.username LIKE %s OR auth_user.email LIKE %s ) AND auth_user.id != %s ORDER BY auth_user.id ASC LIMIT 0,10 ", [request.user.id,request.user.id,sname,sname,sname, request.user.id])
                print request.user.id
                row = cursor.fetchall()
                userData = []
                for data in row:
                    print data
                    firstid = data[0]
                    eid = hashid = hashids.encode(firstid) #__encrypt_val(firstid)
                    lst = list(data)
                    lst[0] = eid
                    t = tuple(lst)
                    userData.append(t)
                response = HttpResponse(json.dumps({'data': userData}), content_type='application/json')
                return response
"""end function loadUsersByName"""

"""
Method:             blockUnblockUsers
Developer:          Bhushan
Created Date:       19-07-2018
Purpose:            block and unblock user
Params:             [request]
Return:             user data[]
"""
@login_required
def blockUnblockUsers(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            hashids = Hashids(min_length=16)
            dataType = request.POST.get('data_type')
            setUserId = request.POST.get('user_id')
            uId = hashids.decode(setUserId)
            currentUser = uId[0]
            try:
                userData = BlockedUser.objects.filter(blocked_user_id = currentUser, user_id = request.user.id)
            except BlockedUser.DoesNotExist:
                userData = None
            if('0' == dataType):
                if not userData:
                    blockUser = BlockedUser()
                    blockUser.blocked_user_id = currentUser
                    blockUser.user_id = request.user.id
                    blockUser.is_blocked = 1
                    blockUser.save()
                else:
                    blockUser = BlockedUser.objects.get(blocked_user_id=currentUser)
                    blockUser.blocked_user_id = currentUser
                    blockUser.user_id = request.user.id
                    blockUser.is_blocked = 1
                    blockUser.save()
                response = HttpResponse(json.dumps({'type':dataType,'id':currentUser,'success': 'Added successfully'}),content_type='application/json')
                response.status_code = 200
                return response
            else:
                if userData:
                    userData.delete()
                    print "there"
                    response = HttpResponse(json.dumps({'id':currentUser,'type':dataType,'success': 'Deleted successfully'}),content_type='application/json')
                    response.status_code = 200
                    return response
"""end function blockUnblockUsers"""

"""
Method:             getSpecificUsers
Developer:          Bhushan
Created Date:       19-07-2018
Purpose:            get user's specific contacts
Params:             [request]
Return:             user data[]
"""
@login_required
def getSpecificUsers(request):
    if request.user.is_authenticated():
        hashids = Hashids(min_length=16)
        if request.method == 'GET':
            privacyType = request.GET.get('privacyType')
            cursor = connection.cursor()
            cursor.execute("SELECT auth_user.id id,auth_user.id, auth_user.first_name, auth_user.last_name, profile.profile_image FROM auth_user LEFT JOIN user_specific_contacts ON auth_user.id = user_specific_contacts.specific_user_id LEFT JOIN profile ON auth_user.id = profile.user_id Where user_specific_contacts.user_id = %s AND user_specific_contacts.privacytype_id = %s AND auth_user.id != 1 ORDER BY auth_user.id ASC", [request.user.id, privacyType])
            specificUserList = cursor.fetchall()
            specificUserData = []
            for user in specificUserList:
                firstid = user[0]
                eid = hashid = hashids.encode(firstid)
                lst = list(user)
                lst[0] = eid
                t = tuple(lst)
                specificUserData.append(t)

            response = HttpResponse(json.dumps({'data': specificUserData, 'success': 'Added successfully'}),content_type='application/json')
            response.status_code = 200
            return response
"""end function getSpecificUsers"""

"""
Method:             deleteSpecificUser
Developer:          Bhushan
Created Date:       19-07-2018
Purpose:            delete specific user
Params:             [id]
Return:             []
"""
@login_required
def deleteSpecificUser(request):
    if request.user.is_authenticated():
        hashids = Hashids(min_length=16)
        if request.method == 'POST':
            userId = request.POST.get('user_id')
            uId = hashids.decode(userId)
            currentUser = uId[0]
            try:
                userData = UserSpecificContacts.objects.filter(specific_user_id = currentUser, user_id = request.user.id)
                userCount = UserSpecificContacts.objects.filter(user_id = request.user.id).count()
            except UserSpecificContacts.DoesNotExist:
                userData = None
                userCount = 0
            if userData:
                userData.delete()
            response = HttpResponse(json.dumps({'id': currentUser,'type':1, 'count':userCount, 'success': 'Added successfully'}),content_type='application/json')
            response.status_code = 200
            return response
"""end function deleteSpecificUser"""
