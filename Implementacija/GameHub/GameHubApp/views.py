# Author: Nemanja Mićanović 0595/2021
# Author: Mihajlo Blagojevic 0283/2021
# Author: Viktor Mitrovic 0296/2021
# Author: Tadija Goljic 0272/2021

import base64
import json
import os
import re
import typing

from math import log
from datetime import datetime, date
from io import BytesIO
from PIL import Image
from uuid import uuid4

from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.db import ProgrammingError, IntegrityError
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from GameHub.settings import EMAIL_HOST_USER

from .custom_errors import MyHttp404, MyPermissionDenied, MySuspiciousOperation
from .forms import ForumCreateForm, PostForm, CommentForm, ProfileForm
from .models import (Tournament, ForumNumOfPlayers, Forum, CreateTournamentUser, RegisteredUser, Participate,
                     Team, Post, LikedPost, Moderates, Moderator, ForumNotification, Notification, Admin, TeamMember,
                     Follow, Comment, LikedComment, ForgotPassword, TeamNotification, RequestToJoin)
from .views_helpers import (forum_check, post_check, comment_check, get_tournaments, team_check, admin_check,
                            get_is_tournament_knockout, delete_tournament, leave_tournament, tournament_check,
                            check_is_user_privileged, moderator_check, find_teams, get_team, get_team_names_and_points,
                            get_members_and_messages, get_error_messages_tournament, join_tournament, start_tournament,
                            finish_tournament, kick_from_tournament, create_a_team_base_context, create_notification,
                            get_tournament_knockout_formats, get_tournament_formats, user_profile_base_context)


def sign_in(request):
    """
    A function that logs the user into the system
    :param request: Http request
    :returns: index page if username and password are correct, sign_in page otherwise
    """
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST.get('username-field')
        password = request.POST.get('password-field')
        if username == '' or password == '':
            context = {
                'message': 'All fields must be filled out, try again!'
            }
            return render(request, 'GameHubApp/sign_in.html', context, 'text/html', 200)
        email = RegisteredUser.objects.filter(username=username, status='ACT').first()
        try:
            user = authenticate(username=email, password=password)
            if user is not None and user.username == username:
                login(request, user)
                return redirect('/')
        except ProgrammingError:
            pass
        context = {
            'message': 'Wrong credentials, try again!'
        }
        return render(request, 'GameHubApp/sign_in.html', context, 'text/html', 200)
    else:
        context = {
            'message': ''
        }
        return render(request, 'GameHubApp/sign_in.html', context, 'text/html', 200)


def register(request):
    """
    A function that registers a user to the system
    :param request: Http request
    :returns: sign_in page if all fields are correct, register page otherwise
    """
    if request.method == 'POST':
        email = request.POST.get('email-field')
        username = request.POST.get('username-field')
        password = request.POST.get('password-field')
        password_again = request.POST.get('password-again-field')
        profile_about_section = request.POST.get('description-field')
        if email == '' or username == '' or password == '' or password_again == '' or profile_about_section == '':
            context = {
                'email': email,
                'username': username,
                'description': profile_about_section,
                'message': 'All fields must be filled out, try again!'
            }
            return render(request, 'GameHubApp/register.html', context, 'text/html', 200)
        if password != password_again:
            context = {
                'email': email,
                'username': username,
                'message': 'Passwords don\'t match, try again!',
                'description': profile_about_section
            }
            return render(request, 'GameHubApp/register.html', context, 'text/html', 200)
        try:
            users = RegisteredUser.objects.filter(username=username, status='ACT').first()
            if users is not None:
                raise IntegrityError
            user = RegisteredUser.objects.create_user(username=username, password=password, email=email,
                                                      aboutsection=profile_about_section, status='ACT',
                                                      dateregistered=datetime.now())  # TODO raises timezone warning
            user.save()
            return redirect('sign_in')
        except IntegrityError:
            context = {
                'email': '',
                'username': '',
                'message': 'The account already exists, try again!',
                'description': profile_about_section
            }
            return render(request, 'GameHubApp/register.html', context, 'text/html', 200)
    else:
        context = {
            'email': '',
            'username': '',
            'message': '',
            'description': ''
        }
        return render(request, 'GameHubApp/register.html', context, 'text/html', 200)


def forgot_password(request):
    """
    Forgot password view
    :param request: Http request
    :returns: sign_in page if mail is correct, forgot_password page otherwise
    """
    if request.method == 'POST':
        email = request.POST.get('email-field')
        if email == '':
            context = {
                'email': '',
                'message': 'All fields must be filled out, try again!'
            }
            return render(request, 'GameHubApp/forgot_password.html', context, 'text/html', 200)
        user = RegisteredUser.objects.filter(email=email).first()
        if user is not None:
            # create row in table ForgotPassword
            id_reset = uuid4()
            # calculating expiration date
            now = datetime.now()
            expiration_date = datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=now.hour + 1 if now.month + 5 > 59 else now.hour,
                minute=(now.minute + 5) % 60,
                second=now.second,
                microsecond=now.microsecond
            )
            data = ForgotPassword.objects.create(resetkey=id_reset, expirationdate=expiration_date, iduser=user)
            data.save()
            # send mail
            send_mail(
                subject='Reset your password',
                from_email=EMAIL_HOST_USER,
                recipient_list=[email],
                message=f'To change the password, click on the link: http://localhost:8000/reset-password/{id_reset}'
            )
        else:
            context = {
                'email': email,
                'message': 'There is no account in the system with the entered email, try again!'
            }
            return render(request, 'GameHubApp/forgot_password.html', context, 'text/html', 200)
        return redirect('sign_in')
    else:
        context = {
            'email': '',
            'message': ''
        }
        return render(request, 'GameHubApp/forgot_password.html', context, 'text/html', 200)


def reset_password(request, id_reset):
    """
    Reset password view
    :param request: Http request
    :param id_reset: key for row in ForgotPassword table
    :returns: sign_in page if the password is successfully reset, the reset_password page otherwise.
    :raises: MySuspiciousOperation in case id_reset does not exist in table ForgotPassword
    """
    if request.method == 'POST':
        password = request.POST.get('password-field')
        password_again = request.POST.get('password-again-field')
        if password == '' or password_again == '':
            context = {
                'id_reset': str(id_reset),
                'message': 'All fields must be filled out, try again!'
            }
            return render(request, 'GameHubApp/reset_your_password.html', context, 'text/html', 200)
        if password != password_again:
            context = {
                'id_reset': str(id_reset),
                'message': 'Passwords don\'t match, try again!'
            }
            return render(request, 'GameHubApp/reset_your_password.html', context, 'text/html', 200)
        else:
            # get reset uuid from database
            data = ForgotPassword.objects.get(resetkey=id_reset)
            # Find the user whose password is being reset
            id_user = data.iduser
            if id_user is None:
                raise MySuspiciousOperation('Something went wrong')
            else:
                # delete temporary data
                data.delete()
                # reset user's password
                user = RegisteredUser.objects.get(iduser=id_user.iduser)
                user.set_password(password)
                user.save()
                return redirect('sign_in')
    else:
        context = {
            'id_reset': str(id_reset),
            'message': ''
        }
        return render(request, 'GameHubApp/reset_your_password.html', context, 'text/html', 200)


@login_required(login_url='sign_in')
def user_profile(request, id_user):
    """
    The function can only be called by a logged-in user. The function displays information about the user
    with the given ID. If the given ID is also the ID of the logged-in user, or the logged-in user is admin,
    options for editing the profile are additionally displayed on the page.
    :param request: Http request
    :param id_user: User whose profile will be shown
    :returns: profile page
    :raises: MyHttp404 if account does not exist
    """
    try:
        context = user_profile_base_context(request, id_user)
        return render(request, 'GameHubApp/profile.html', context, 'text/html', 200)
    except RegisteredUser.DoesNotExist:
        raise MyHttp404('The account does not exist!')


@login_required(login_url='sign_in')
def delete_profile(request, id_user):
    """
    A function that deletes the profile with given ID
    :param request: Http request
    :param id_user: User whose profile is being deleted
    :returns: index page
    :raises: MyHttp404 if account has already been deleted
    """
    password = request.POST.get('password-delete-account')
    # user whose account will be deleted
    user = RegisteredUser.objects.get(iduser=request.user.iduser)
    user = authenticate(username=user.email, password=password)
    if user is None:
        context = user_profile_base_context(request, id_user)
        context.update({
            'delete_message': 'Password is wrong!'
        })
        return render(request, 'GameHubApp/profile.html', context, 'text/html', 200)
    else:
        if (not admin_check(user)) or (admin_check(user) and user.iduser == id_user):
            # if user deletes his own password and user is not admin or admin deletes random account
            logout(request)
        # delete account
        if user.iduser != id_user:
            # if admin deletes account
            user = RegisteredUser.objects.get(iduser=id_user)
        user.is_active = 0
        user.status = 'DEL'
        user.save()
        for member in TeamMember.objects.filter(iduser=user.iduser):
            for participate in Participate.objects.filter(idteam=member.idteam.idteam):
                if participate.idtour.status == 'NOT_STARTED':
                    participate.delete()
            member.delete()
            if member.isleader:
                # If the member was the team leader, make someone else leader
                all_team_members = TeamMember.objects.filter(idteam=member.idteam)
                other_team_members = [
                    team_member for team_member in all_team_members if team_member.iduser.iduser != user.iduser
                ]
                # If there are still other players in the team
                if len(other_team_members) > 0:
                    # make someone a leader
                    other_team_members[0].isleader = 1
                    other_team_members[0].save()
                else:
                    # change team status to 'DEL'
                    team_to_delete = Team.objects.get(idteam=member.idteam.idteam)
                    team_to_delete.status = 'DEL'
                    team_to_delete.save()
        return redirect('/')


def logout_user(request):
    """
    A function that logs the user out of the system
    :param request: Http request
    :returns: index page
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect('/')


@login_required(login_url='sign_in')
def change_password(request, id_user):
    """
    A function that changes the password of a user with a given ID
    :param request: Http request
    :param id_user: User for whom the password is being changed
    :returns: Profile page if the user successfully changed the password, otherwise the password change page
    """
    if request.method == 'POST':
        # post request arguments
        old_password = request.POST.get('old-password-field')
        new_password = request.POST.get('new-password-field')
        new_password_again = request.POST.get('new-password-again-field')
        if old_password == '' or new_password == '' or new_password_again == '':
            context = {
                'id_user': id_user,
                'message': 'All fields must be filled out, try again!'
            }
            return render(request, 'GameHubApp/change_password.html', context, 'text/html', 200)
        # user authentication
        user = authenticate(username=request.user.email, password=old_password)
        if new_password != new_password_again:
            context = {
                'id_user': id_user,
                'message': 'Passwords don\'t match, try again!'
            }
            return render(request, 'GameHubApp/change_password.html', context, 'text/html', 200)
        elif user is None:
            context = {
                'id_user': id_user,
                'message': 'Old password isn\'t correct, try again!'
            }
            return render(request, 'GameHubApp/change_password.html', context, 'text/html', 200)
        # save new password
        logout(request)
        user.set_password(new_password)
        user.save()
        login(request, user)
        return redirect('user_profile', id_user)
    else:
        context = {
            'id_user': id_user,
            'message': ''
        }
        return render(request, 'GameHubApp/change_password.html', context, 'text/html', 200)


@login_required(login_url='sign_in')
def save_profile_changes(request, id_user):
    """
    A function that updates user information
    :param request: Http request
    :param id_user: User for whom data is being changed
    :returns: User's profile
    :raises: 403 Forbidden page
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            new_picture: InMemoryUploadedFile = form.cleaned_data.get('profile_picture')
            new_aboutsection = form.cleaned_data.get('profile_about_section')
            if new_picture is not None:
                _, new_picture_extension = os.path.splitext(new_picture.name)
                # Check if picture has supported extensions
                supported_extensions = ['.jpg', '.jpeg', '.png']
                if new_picture_extension.lower() not in supported_extensions:
                    context = user_profile_base_context(request, id_user)
                    context.update({
                        'message': 'Unsupported picture type!'
                    })
                    return render(request, 'GameHubApp/profile.html', context, 'text/html', 200)
                picture = new_picture.read()
                user.profilepicture = picture
            if new_aboutsection is not None:
                user.aboutsection = new_aboutsection
            user.save()
        return redirect(f'/user-profile/{id_user}')
    else:
        raise PermissionDenied('You don\'t have permissions for this operation')


def index(request):
    """
    Display index page with list of active forums

    Args:
        request (django.http.HttpRequest): HttpRequest object.

    Returns:
        HttpResponse: Rendered index.html template.
    """

    forums = Forum.objects.filter(status__exact='ACT').order_by("name")
    forum_data = []
    for forum in forums:
        name_of_forum = forum.name
        id_of_forum = forum.idforum
        forum_img_data = forum.coverimage

        forum_img_data_64 = 0
        ext = "None"
        if forum_img_data is not None:
            forum_img_data_64 = base64.b64encode(forum_img_data).decode('utf-8')
            # Fetching file extension of image
            ext = (Image.open(BytesIO(forum_img_data))).format
            ext = ext.lower()

        forum_data.append((id_of_forum, name_of_forum, forum_img_data_64, ext))

    # Check if the user can access forum creation page
    check_access_create_forum = 0
    if request.user.is_authenticated and admin_check(request.user):
        check_access_create_forum = 1

    context = {
        "forums": forum_data,
        "check_access_create_forum": check_access_create_forum
    }
    return render(request, 'GameHubApp/index.html', context, 'text/html', 200)


@login_required(login_url='sign_in')
def create_forum(request):
    """
    Function that allows admins to create a forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object.

    Returns:
        django.http.HttpResponse if the http request is a GET request or http request is a POST request and data
        received from form is not in correct format return rendered create_forum.html page.
        django.http.HttpResponseRedirect if the http request is a POST request and data received from form is in the
        correct format, redirect to the index page.
    """

    context = {
        'err_message_name': '-1',
        'err_message_possible_number_of_players': '-1',
        'err_extension_cover': '-1',
        'err_extension_banner': '-1',
        'err_message_description': '-1'
    }

    # Check if the user can access forum creation page
    if request.user.is_authenticated and not admin_check(request.user):
        return redirect("index")

    form = ForumCreateForm()
    if request.method == 'POST':
        form = ForumCreateForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('forum_name')
            cover_image = form.cleaned_data.get('cover_image')
            banner_image = form.cleaned_data.get('banner_image')
            description = form.cleaned_data.get('description')
            possible_number_of_players = form.cleaned_data.get('possible_number_of_players')
            if name == "":
                context['form'] = form
                context['err_message_name'] = 'You must specify name of the forum!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)
            if re.findall("^[a-zA-Z0-9\s]{3,}$", name) == []:
                context['form'] = form
                context['err_message_name'] = 'Name of the forum is not in the right format!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)
            if len(name) > 50:
                context['form'] = form
                context['err_message_name'] = 'Name of the forum is too long!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)
            if cover_image == None:
                context['form'] = form
                context['err_extension_cover'] = 'You must provide cover image!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)
            if banner_image == None:
                context['form'] = form
                context['err_extension_banner'] = 'You must provide banner image!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)
            if description == "":
                context['form'] = form
                context['err_message_description'] = 'You must specify description of the forum!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)
            if len(description) > 1000:
                context['form'] = form
                context['err_message_description'] = 'Description of the forum is too long!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)
            if re.findall(".{5,}", description) == []:
                context['form'] = form
                context['err_message_description'] = 'Description of the forum is not in the right format!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)

            if possible_number_of_players == "":
                context['form'] = form
                context['err_message_possible_number_of_players'] = 'You must specify possible number of players!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)


            cover_image_data = cover_image.read()
            banner_image_data = banner_image.read()
            cover_filename, cover_extension = os.path.splitext(cover_image.name)
            banner_filename, banner_extension = os.path.splitext(banner_image.name)

            check_forum_already_exists = Forum.objects.filter(name__exact=name, status__exact='ACT')
            if check_forum_already_exists:
                context['form'] = form
                context['err_message_name'] = 'Already exists active forum with the same name!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)

            # Check if files sent via form have supported extensions
            supported_extensions = ['.jpg', '.jpeg', '.png']
            if cover_extension.lower() not in supported_extensions:
                context['form'] = form
                context['err_extension_cover'] = 'File for cover does not have a supported extension!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)
            if banner_extension.lower() not in supported_extensions:
                context['form'] = form
                context['err_extension_banner'] = 'File for banner does not have a supported extension!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)

            check_game_is_singleplayer_game = False
            array_str_possible_number_of_players = None
            if possible_number_of_players == '/':
                check_game_is_singleplayer_game = True
            if (check_game_is_singleplayer_game == False and
                    re.findall("^\d+(,\d+)*$", possible_number_of_players) == []):
                context['form'] = form
                context['err_message_possible_number_of_players'] = 'Format is not fulfilled!'
                return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)

            if not check_game_is_singleplayer_game:
                array_str_possible_number_of_players = possible_number_of_players.split(',')
                array_int_possible_number_of_players = [int(number) for number in array_str_possible_number_of_players]
                check_duplicate_number = False
                for i in range(len(array_str_possible_number_of_players) - 1):
                    for j in range(i + 1, len(array_str_possible_number_of_players)):
                        if i != j and array_str_possible_number_of_players[i] == array_str_possible_number_of_players[j]:
                            check_duplicate_number = True
                if check_duplicate_number:
                    context['form'] = form
                    context['err_message_possible_number_of_players'] = 'There are repeated number of players!'
                    return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)

            new_forum = Forum(name=name, coverimage=cover_image_data,
                              bannerimage=banner_image_data, description=description,
                              status='ACT', datecreated=date.today())
            new_forum.save()

            if not check_game_is_singleplayer_game:
                for number in array_int_possible_number_of_players:
                    new_forum_num_of_players = ForumNumOfPlayers(idforum=new_forum, numberofplayers=number)
                    new_forum_num_of_players.save()

            return redirect('index')

    context['form'] = form
    return render(request, 'GameHubApp/create_forum.html', context, 'text/html', 200)


@login_required(login_url='sign_in')
def find_a_team(request, id_forum):
    """
    Find a team view
    :param request: Http request
    :param id_forum: Forum where the team is being sought
    :returns: find_a_team page
    :raises: MyHttp404 exception if forum's game is single player
    """
    forum_info = Forum.objects.get(idforum=id_forum)
    forum_name = forum_info.name
    try:
        # teams on forum
        teams = find_teams(id_forum)
        # check if user is already a team member on the forum
        already_in_team = TeamMember.objects.filter(idforum=id_forum, iduser=request.user.iduser)
        context = {
            'forum_name': forum_name,
            'teams': teams,
            'id_forum': id_forum,
            'already_team_member': already_in_team.exists()
        }
        return render(request, 'GameHubApp/find_a_team.html', context, 'text/html', 200)
    except TeamMember.DoesNotExist:
        raise MyHttp404('You cannot search for a team on forums that are not team-based.')


@login_required(login_url='sign_in')
def request_join(request, id_forum, id_team):
    """
    A function that sends TeamNotification to team leader of id_team
    :param request: Http request
    :param id_forum: Team Forum
    :param id_team: Team for which the request is being made
    :returns: Forum page
    """
    # team leader info
    team_leader = TeamMember.objects.get(idteam=id_team, isleader=1)
    # team to join
    team_to_join = Team.objects.get(idteam=id_team)
    # notification to be sent
    requests = RequestToJoin.objects.filter(iduser=request.user.iduser, idteam=id_team)
    if not requests.exists():
        RequestToJoin.objects.create(iduser=request.user, idteam=team_to_join, requestdate=datetime.now())
        notification = create_notification(team_leader.iduser)
        team_notification = TeamNotification(
            idnot=notification, iduser=request.user, idteam=team_to_join, type='TEAM_INVITE'
        )
        team_notification.save()
    # return Forum page
    return redirect(f'/forum/{id_forum}')


@login_required(login_url='sign_in')
def create_a_team(request, id_forum):
    """
    A function that creates a team on forum with the given ID
    :param request: Http request containing information about the user who creates a team
    :param id_forum: Forum where the team will be created
    :returns: forum page if the team was created, create_a_team page otherwise
    :raises: MyHttp404 in case something goes wrong
    """
    user = request.user
    # user teams on the forum
    teams = TeamMember.objects.filter(idforum=id_forum, iduser=user.iduser)
    if request.method == 'POST':
        if teams.exists():
            # if user is a member of any team raise exception
            raise MyHttp404('You are already a member of a team on this forum')
        else:
            # team name from post request
            team_name = request.POST.get('team-name-field')
            # team description from post request
            team_description = request.POST.get('team-description-field')
            # teams with provided name
            teams = Team.objects.filter(name=team_name, idforum=id_forum, status='ACT')
            # base context
            context = create_a_team_base_context(id_forum)
            if context is None:
                # raise exception
                raise MyHttp404('You cannot create a team on forums that are not team-based')
            elif team_name == '' or team_description == '':
                context.update({
                    'message': 'All fields must be filled out, try again!',
                    'description': team_description
                })
                return render(request, 'GameHubApp/create_a_team.html', context, 'text/html', 200)
            elif teams.exists():
                context.update({
                    'message': f'There is a team with name "{team_name}" on this forum, try again!',
                    'description': team_description
                })
                # return create_a_team page with message and description field
                return render(request, 'GameHubApp/create_a_team.html', context, 'text/html', 200)
            # create a team
            team_num_of_players = request.POST.get('team-num-of-players-field')
            # it would be '/' if it is single player game
            team_num_of_players = int(team_num_of_players) if team_num_of_players.isdigit() else 0
            team_forum = Forum.objects.get(idforum=id_forum)
            new_team = Team.objects.create(name=team_name, description=team_description, datecreated=datetime.now(),
                                           numberofplayers=team_num_of_players, idforum=team_forum, status='ACT')
            new_team.save()
            new_team_member = TeamMember.objects.create(iduser=user, idforum=team_forum,
                                                        isleader=1, datejoined=datetime.now(),
                                                        lastmsgreaddate=datetime.now(), idteam=new_team)
            new_team_member.save()
            # return forum page
            return redirect(f'/forum/{id_forum}')
    else:
        context = create_a_team_base_context(id_forum)
        if context is not None:
            context.update({
                'message': '',
                'description': ''
            })
            return render(request, 'GameHubApp/create_a_team.html', context, 'text/html', 200)
        else:
            raise MyHttp404('You cannot create a team on forums that are not team-based')


@login_required(login_url='sign_in')
def leave_a_team(request, id_forum):
    """
    A function that removes a user from the team
    :param request: Http request containing information about the user being removed from the team
    :param id_forum: Forum id
    :returns: Forum page
    :raises: MyHttp404 error with the appropriate message
    """
    user = request.user
    team_member_object = TeamMember.objects.filter(idforum=id_forum, iduser=user.iduser)
    id_team = team_member_object.first().idteam
    # TeamMember object to be deleted
    member = TeamMember.objects.filter(idteam=id_team, iduser=user.iduser)
    if member.exists():
        member = member.first()
        # delete TeamMember object
        member.delete()
        if member.isleader:
            # If the member was the team leader, make someone else leader
            all_team_members = TeamMember.objects.filter(idteam=id_team)
            other_team_members = [
                team_member for team_member in all_team_members if team_member.iduser.iduser != user.iduser
            ]
            # If there are still other players in the team
            if len(other_team_members) > 0:
                # make someone a leader
                other_team_members[0].isleader = 1
                other_team_members[0].save()
            else:
                # change team status to 'DEL'
                team_to_delete = Team.objects.get(idteam=id_team.idteam)
                team_to_delete.status = 'DEL'
                team_to_delete.save()
        return redirect(f'/forum/{id_forum}')
    else:
        raise MyHttp404('The user is not a member on this team')


def forum(request, id_forum):
    """
    Display forum page of the specified forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object.
        id_forum (int): Unique forum identifier of the forum that should be displayed.

    Returns:
        django.http.HttpResponse: Rendered forum.html template.

    Raises:
        django.http.Http404: If the specified forum does not exist.
    """

    forum_check(id_forum)
    context = dict()

    # Get forum information
    context["forum"] = Forum.objects.get(idforum=id_forum)
    # Get posts on the forum
    context["posts"] = Post.objects.filter(idforum=id_forum, status__exact='ACT').order_by("-datecreated")
    # Get current user
    context["user"] = request.user
    # Is current user an admin
    context["is_admin"] = False
    # Is current user a moderator on the forum
    context["is_moderator"] = False
    # A user who is not logged in cannot have any liked posts
    context["liked_posts"] = []
    # A user who is not logged in cannot be a part of a team
    context["team_member"] = False
    # A user who is not legged in cannot follow a forum
    context["follow"] = False

    # Forum banner image
    forum_banner_image_b64 = base64.b64encode(context["forum"].bannerimage).decode('utf-8')
    forum_banner_image_ext = (Image.open(BytesIO(context["forum"].bannerimage))).format.lower()

    context["forum_banner_image"] = {
        "base64": forum_banner_image_b64,
        "extension": forum_banner_image_ext
    }

    context["has_tournaments"] = ForumNumOfPlayers.objects.filter(idforum=id_forum).exists()

    if request.user.is_authenticated:
        context["is_admin"] = admin_check(request.user)
        context["is_moderator"] = moderator_check(request.user, context["forum"])

        # Get liked posts for user
        context["liked_posts"] = [liked_post.idpost for liked_post in
                                  LikedPost.objects.filter(iduser__exact=request.user, idpost__in=context["posts"])]

        try:
            # Get user's team on the forum
            context["team"] = get_team(request.user, context["forum"])
            context["team_member"] = True
        except (TeamMember.DoesNotExist, Team.DoesNotExist):
            # User doesn't have a team on the forum
            context["team_member"] = False

        try:
            # Check if the user is following this forum
            follow = Follow.objects.get(iduser__exact=request.user, idforum__exact=id_forum)
            context["follow"] = True
        except Follow.DoesNotExist:
            context["follow"] = False

    return render(request, 'GameHubApp/forum.html', context, 'text/html', 200)


@login_required(login_url='sign_in')
def follow_forum(request, id_forum):
    """
    Allow a registered user to follow or unfollow a forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): The unique identifier of the forum the current
                        registered user wants to follow or unfollow.

    Returns:
        django.http.JsonResponse: A JSON response containing the new follow status of the forum.

    Raises:
        django.http.Http404: If the specified forum does not exist.
    """

    forum_check(id_forum)

    # Check whether the user follows the forum
    try:
        follow = Follow.objects.get(iduser__exact=request.user, idforum__exact=id_forum)
        # Update database
        follow.delete()
        response = JsonResponse({'follow_status': 'UNFOLLOWED'})
    except Follow.DoesNotExist:
        # Update database
        forum = Forum.objects.get(idforum=id_forum)
        new_follow = Follow(idforum=forum, iduser=request.user, datefollowed=datetime.now())
        new_follow.save()
        response = JsonResponse({'follow_status': 'FOLLOWED'})

    return response


@login_required(login_url='sign_in')
def delete_forum(request, id_forum):
    """
    Function that allows admins to delete a forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object.
        id_forum (int): Unique forum identifier of the forum that is being deleted.

    Returns:
        django.http.HttpResponseRedirect whether the user is an admin or not, redirect to the index page.
    """

    # Check if registered user can delete a forum
    if request.user.is_authenticated and not admin_check(request.user):
        return redirect("index")

    forum_check(id_forum)
    forum = Forum.objects.get(idforum__exact=id_forum, status__exact='ACT')
    forum.status = 'DEL'
    forum.save()
    return redirect("index")


@login_required(login_url='sign_in')
def promote_moderator(request, id_forum):
    """
    Function that allows admins to grant moderator privileges to a user on the forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object.
        id_forum (int): Unique forum identifier of the forum on which user is being promoted.

    Returns:
        django.http.HttpResponseRedirect if user is not an admin, redirect to the index page.
        django.http.JsonResponse A JSON response indicating whether the promotion was successful.

        The JSON response has the following entries:

        - "message": This field contains "User has been added as a moderator to the forum" if promotion was
            successful, or the corresponding message why promotion failed

        - "status": This field contains information about promotion outcome. Possible values: 1 - successful,
            0 - not successful

    Raises:
        django.http.Http404: If the forum does not exist.
    """

    name_of_user_for_promotion = request.POST.get('name_of_user')
    if name_of_user_for_promotion == "":
        response = JsonResponse({"message": "You must specify a username", "status": 0})
        return response
    if len(name_of_user_for_promotion) > 25:
        response = JsonResponse({"message": "Username is too long", "status": 0})
        return response

    # Check if registered user can promote other users to moderators
    if request.user.is_authenticated and not admin_check(request.user):
        return redirect("index")

    admin = Admin.objects.get(idadmin__exact=request.user.iduser)

    forum_check(id_forum)
    forum = Forum.objects.get(idforum__exact=id_forum)
    try:
        user_for_promotion = RegisteredUser.objects.get(username__exact=name_of_user_for_promotion, status__exact='ACT')

        # Check if user is Admin
        check_user_is_also_admin = Admin.objects.filter(idadmin__exact=user_for_promotion.iduser).exists()
        if check_user_is_also_admin:
            response = JsonResponse({"message": "User {} is Admin".format(name_of_user_for_promotion), "status": 0})
            return response

        # Check if user is already a Moderator on this forum
        check_already_moderator_on_this_forum = Moderates.objects.filter(idforum__exact=id_forum,
                                                                         idmod__exact=user_for_promotion.iduser).exists()
        if check_already_moderator_on_this_forum:
            response = JsonResponse({"message": "User {} is already moderator on this forum".format(name_of_user_for_promotion), "status": 0})
            return response

        # Check if user is becoming Moderator for the first time
        check_create_tour_user = CreateTournamentUser.objects.filter(iduser__exact=user_for_promotion.iduser).exists()
        create_tour_user = None
        moderator = None
        if check_create_tour_user:
            create_tour_user = CreateTournamentUser.objects.get(iduser__exact=user_for_promotion.iduser)
            moderator = Moderator.objects.get(idmod__exact=user_for_promotion.iduser)
        else:
            create_tour_user = CreateTournamentUser(iduser=user_for_promotion)
            create_tour_user.save()
            moderator = Moderator(idmod=create_tour_user)
            moderator.save()

        moderates = Moderates(idforum=forum, idmod=moderator, datepromoted=date.today(), idadmin=admin)
        moderates.save()

        notf = create_notification(user_for_promotion)
        forum_notf = ForumNotification(idnot=notf, idpost=None, idforum=forum, type="MOD_ADDED")
        forum_notf.save()

    except RegisteredUser.DoesNotExist:
        response = JsonResponse({"message": "User {} doesn't exist".format(name_of_user_for_promotion), "status": 0})
        return response

    response = JsonResponse({"message": "User {} has been added as a moderator to the forum".
                            format(name_of_user_for_promotion), "status": 1})
    return response


@login_required(login_url='sign_in')
def demote_moderator(request, id_forum):
    """
    Function that allows admins to take away moderator privileges from a user on the forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object.
        id_forum (int): Unique forum identifier of the forum on which user is being demoted.

    Returns:
        django.http.HttpResponseRedirect if user is not an admin, redirect to the index page.
        django.http.JsonResponse A JSON response indicating whether the demotion was successful.

        The JSON response has the following entries:

        - "message": This field contains "User has been removed as a moderator on the forum" if demotion was
            successful, or the corresponding message why demotion failed

        - "status": This field contains information about demotion outcome. Possible values: 1 - successful,
            0 - not successful

    Raises:
        django.http.Http404: If the forum does not exist.
    """

    name_of_user_for_promotion = request.POST.get('name_of_user')
    if name_of_user_for_promotion == "":
        response = JsonResponse({"message": "You must specify a username", "status": 0})
        return response
    if len(name_of_user_for_promotion) > 25:
        response = JsonResponse({"message": "Username is too long", "status": 0})
        return response

    # Check if registered user can demote other users
    if request.user.is_authenticated and not admin_check(request.user):
        return redirect("index")

    forum_check(id_forum)
    forum = Forum.objects.get(idforum__exact=id_forum)
    try:
        user_for_demotion = RegisteredUser.objects.get(username__exact=name_of_user_for_promotion, status__exact='ACT')

        # Check if user is Admin
        check_user_is_also_admin = Admin.objects.filter(idadmin__exact=user_for_demotion.iduser).exists()
        if check_user_is_also_admin:
            response = JsonResponse({"message": "User {} is Admin".format(name_of_user_for_promotion), "status": 0})
            return response

        # Check if user is not a Moderator on this forum
        moderates = Moderates.objects.get(idforum__exact=id_forum, idmod__exact=user_for_demotion.iduser)
        moderates.delete()

        # Check if user is a Moderator on any forum, if not, delete Moderator and CreateTournamentUser for that user
        all_moderates = Moderates.objects.filter(idmod__exact=user_for_demotion.iduser).exists()
        if not all_moderates:
            moderator_for_delete = Moderator.objects.get(idmod__exact=user_for_demotion.iduser)
            moderator_for_delete.delete()
            create_tournament_for_delete = CreateTournamentUser.objects.get(iduser__exact=user_for_demotion.iduser)
            create_tournament_for_delete.delete()

        notf = create_notification(user_for_demotion)
        forum_notf = ForumNotification(idnot=notf, idpost=None, idforum=forum, type='MOD_DELETED')
        forum_notf.save()

    except RegisteredUser.DoesNotExist:
        response = JsonResponse({"message": "User {} doesn't exist".format(name_of_user_for_promotion), "status": 0})
        return response
    except Moderates.DoesNotExist:
        response = JsonResponse({"message": "User {} is not a moderator on this forum".format(name_of_user_for_promotion), "status": 0})
        return response

    response = JsonResponse({"message": "User {} has been removed as a moderator on the forum".
                            format(name_of_user_for_promotion), "status": 1})
    return response


@login_required(login_url='sign_in')
def create_post(request, id_forum):
    """
    Display create post page and allow a registered user to create a new post on the forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): The unique identifier of the forum where the current registered user
                        wants to create a post.

    Returns:
        django.http.HttpResponse if the http request is a GET request return rendered create_post.html page.
        django.http.JsonResponse if the http request is a POST request and post information is not in the correct form,
        return error information in the form of a JSON response.
        django.http.HttpResponseRedirect if the http request is a POST request and post information is in the correct
        form, redirect to the forum page where the post has been created.

    Raises:
        django.http.Http404: If the specified forum does not exist.
    """

    forum_check(id_forum)

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            forum = Forum.objects.get(idforum__exact=id_forum)
            new_post = Post(iduser=request.user, idforum=forum, title=form.cleaned_data['title'],
                            body=form.cleaned_data['body'], datecreated=datetime.now())
            new_post.save()

            # Send a notification to users following the forum
            follows_forum = Follow.objects.filter(idforum__exact=id_forum)
            users_following_forum = [follow.iduser for follow in follows_forum]

            for follower in users_following_forum:
                if follower != request.user:
                    base_notification = create_notification(follower)
                    post_new_forum_notification = ForumNotification(idnot=base_notification,
                                                                    idpost=new_post,
                                                                    idforum=forum,
                                                                    type='POST_NEW')
                    post_new_forum_notification.save()

            return redirect("forum", id_forum)

        if len(form['title'].value()) <= 0:
            return JsonResponse({"create_post_msg_type": "TITLE",
                                 "message": "Post title is required."})
        elif len(form['title'].value()) > 200:
            return JsonResponse({"create_post_msg_type": "TITLE",
                                 "message": "Post title cannot exceed 200 characters."})
        elif len(form['body'].value()) > 15000:
            return JsonResponse({"create_post_msg_type": "BODY",
                                 "message": "Post body cannot exceed 15000 characters."})
        else:
            return JsonResponse({"create_post_msg_type": "BODY",
                                 "message": "Something went wrong :("})

    context = dict()
    context["forum"] = Forum.objects.get(idforum__exact=id_forum)

    return render(request, 'GameHubApp/create_post.html', context, 'text/html', 200)


def post(request, id_forum, id_post):
    """
    Display the post page of the specified post.

    Args:
        request (django.http.HttpRequest): HttpRequest object.
        id_forum (int): The unique identifier of the forum where the post is located.
        id_post (int): The unique post identifier of the post that should be displayed.

    Returns:
        django.http.HttpResponse: Rendered post.html template.

    Raises:
        django.http.Http404: If the specified forum or post does not exist.
    """

    forum_check(id_forum)
    post_check(id_post)

    context = dict()
    # Get forum information
    context["forum"] = Forum.objects.get(idforum__exact=id_forum)
    # Get post information
    context["post"] = Post.objects.get(idpost__exact=id_post)
    # Get user information
    context["user"] = request.user
    # Is current user an admin
    context["is_admin"] = False
    # Is current user a moderator on the forum
    context["is_moderator"] = False
    # A user who is not logged in cannot be a part of a team
    context["team_member"] = False
    # Get comments on the post
    context["comments"] = Comment.objects.filter(idpost__exact=id_post, status__exact='ACT')
    # A user who is not logged in cannot like post
    context["post_liked"] = False
    # A user who is not logged in cannot like comments
    context["liked_comments"] = []

    context["has_tournaments"] = ForumNumOfPlayers.objects.filter(idforum=id_forum).exists()

    if request.user.is_authenticated:
        context["is_admin"] = admin_check(request.user)
        context["is_moderator"] = moderator_check(request.user, context["forum"])

        # Check if the user liked the post
        context["post_liked"] = LikedPost.objects.filter(idpost__exact=id_post, iduser__exact=request.user).exists()

        # Get liked comments for user
        context["liked_comments"] = [liked_comment.idcom for liked_comment in
                                     LikedComment.objects.filter(iduser__exact=request.user,
                                                                 idcom__in=context["comments"])]

        try:
            # Get user's team on the forum
            context["team"] = get_team(request.user, context["forum"])
            context["team_member"] = True
        except (TeamMember.DoesNotExist, Team.DoesNotExist):
            # User doesn't have a team on the forum
            context["team_member"] = False

    return render(request, 'GameHubApp/post.html', context, 'text/html', 200)


@login_required(login_url='sign_in')
def like_post(request, id_forum, id_post):
    """
    Allow a registered user to leave or remove a like on a post.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): The unique identifier of the forum where the post is located.
        id_post (int): The unique post identifier of the post the registered user wants to leave or remove a like on.

    Returns:
        django.http.JsonResponse: A JSON response indicating a new like status of the post for the registered user.

        - If the user successfully liked a post return {"like_status": "LIKE_ADDED"}.
        - If the user successfully removed a like from a post return {"like_status": "LIKE_REMOVED"}.

    Raises:
        django.http.Http404: If the specified forum or post does not exist.
    """

    forum_check(id_forum)
    post_check(id_post)

    # Check whether the user liked the post
    try:
        like = LikedPost.objects.get(idpost__exact=id_post, iduser__exact=request.user)
        # Update database
        like.delete()
        response = JsonResponse({"like_status": "LIKE_REMOVED"})
    except LikedPost.DoesNotExist:
        # Update database
        post_liked = Post.objects.get(idpost__exact=id_post)
        new_like = LikedPost(idpost=post_liked, iduser=request.user, dateliked=datetime.now())
        new_like.save()
        response = JsonResponse({"like_status": "LIKE_ADDED"})

    return response


@login_required(login_url='sign_in')
def delete_post(request, id_forum, id_post):
    """
    Allow a registered user to delete their own posts.
    On forums where they hold moderating privileges, moderators can delete all posts.
    An admin can delete any post from any forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): The unique identifier of the forum where the post is located.
        id_post (int): The unique identifier of the post the registered user intends to delete.

    Returns:
        django.http.JsonResponse: A JSON response indicating whether the user deleted the post successfully.

        - If the user deleted the post successfully return {"delete_status": "DELETE_SUCCESS"}.
        - If the user failed to delete the post return {"delete_status": "DELETE_FAIL"}.

    Raises:
        django.http.Http404: If the specified forum or post does not exist.
    """

    forum_check(id_forum)
    post_check(id_post)

    post_to_delete = Post.objects.get(idpost__exact=id_post)

    response = JsonResponse({"delete_status": "DELETE_FAIL"})

    # Check if the user can delete the post
    if (post_to_delete.iduser == request.user or admin_check(request.user)
        or moderator_check(request.user, post_to_delete.idforum)):
        # Set the post as deleted/inactive
        post_to_delete.status = 'DEL'
        post_to_delete.save()
        response = JsonResponse({"delete_status": "DELETE_SUCCESS"})

        # Send a notification to post's author that their post has been removed
        if post_to_delete.iduser != request.user:
            base_notification = create_notification(post_to_delete.iduser)
            post_del_forum_notification = ForumNotification(idnot=base_notification,
                                                            idpost=post_to_delete,
                                                            idforum=post_to_delete.idforum,
                                                            type='POST_DEL')
            post_del_forum_notification.save()

    else:
        raise PermissionDenied

    return response


@login_required(login_url='sign_in')
def create_comment(request, id_forum, id_post):
    """
    Allow a registered user to leave a comment on a post.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): The unique identifier of the forum where the post is located.
        id_post (int): The unique identifier of the post on which the registered user intends to leave a comment.

    Returns:
        django.http.JsonResponse if the http request is a POST request, indicating if the user successfully
        created a comment on the post. If the user successfully created a comment,
        information about the comment is returned so it can be displayed. If the user was
        unsuccessful in creating the comment, a JSON response is returned containing error
        information.
        The JSON response has the following entries:

        - "comment_status": This field indicates if the comment has been successfully created. It can
          be "SUCCESS" or "FAIL".
        - "message": This field contains "Comment created." if the comment was created, or an error message if the
          user failed to create the comment.
        - "comment_info": This field contains the comment information if the comment was created successfully,
          otherwise, it is an empty dictionary

        django.http.HttpResponseNotAllowed for http request methods other than POST.

    Raises:
        django.http.Http404: If the specified forum or post does not exist.
    """

    forum_check(id_forum)
    post_check(id_post)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment_post = Post.objects.get(idpost__exact=id_post)
            new_comment = Comment(iduser=request.user, idpost=new_comment_post,
                                  body=form.cleaned_data["body"], datecreated=datetime.now())
            new_comment.save()

            comment_info = {
                "comment_id": new_comment.idcom,
                "user_id": new_comment.iduser.iduser,
                "username": new_comment.iduser.username,
                "body": new_comment.body,
                "status": new_comment.status,
                "date_created": str(new_comment.datecreated),
                "comment_liked": False,
                "comment_owner": True,
                "like_url": reverse("like_comment", args=[id_forum, id_post, new_comment.idcom]),
                "delete_url": reverse("delete_comment", args=[id_forum, id_post, new_comment.idcom])
            }

            return JsonResponse({"comment_status": "SUCCESS",
                                 "message": "Comment created.",
                                 "comment_info": comment_info})

        if len(form["body"].value()) <= 0:
            return JsonResponse({"comment_status": "FAIL",
                                 "message": "Comment's body cannot be empty.",
                                 "comment_info": {}})
        elif len(form["body"].value()) > 15000:
            return JsonResponse({"comment_status": "FAIL",
                                 "message": "Comment's body cannot exceed 15000 characters.",
                                 "comment_info": {}})

    return HttpResponseNotAllowed("Request method not supported.")


@login_required(login_url='sign_in')
def like_comment(request, id_forum, id_post, id_comment):
    """
    Allow a registered user to leave or remove a like on a comment.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): The unique identifier of the forum where the post is located.
        id_post (int): The unique identifier of the post where the comment is located.
        id_comment (int): The unique identifier of the comment on which the registered user wants to leave or remove
                          a like.

    Returns:
        django.http.JsonResponse: A JSON response indicating a new like status of the comment for the registered user.

        - If the user successfully liked the comment, return {"like_status": "LIKE_ADDED"}.
        - If the user successfully removed a like from the comment, return {"like_status": "LIKE_REMOVED"}.

    Raises:
        django.http.Http404: If the specified forum, post or comment does not exist.
    """

    forum_check(id_forum)
    post_check(id_post)
    comment_check(id_comment)

    # Check whether the user liked the post
    try:
        like = LikedComment.objects.get(idcom__exact=id_comment, iduser__exact=request.user)
        # Update database
        like.delete()
        response = JsonResponse({"like_status": "LIKE_REMOVED"})
    except LikedComment.DoesNotExist:
        # Update database
        comment_liked = Comment.objects.get(idcom__exact=id_comment)
        new_like = LikedComment(iduser=request.user, idcom=comment_liked, dateliked=datetime.now())
        new_like.save()
        response = JsonResponse({"like_status": "LIKE_ADDED"})

    return response


@login_required(login_url='sign_in')
def delete_comment(request, id_forum, id_post, id_comment):
    """
    Allow a registered user to delete their own comments.
    Under posts on forums where they hold moderating privileges, moderators can delete all comments.
    An admin can delete any comment on any post.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): The unique identifier of the forum where the post is located.
        id_post (int): The unique identifier of the post where the comment is located.
        id_comment (int): The unique identifier of the comment the registered user intends to delete.

    Returns:
        django.http.JsonResponse: A JSON response indicating whether the user deleted the comment successfully.

        - If the user deleted the comment successfully return {"delete_status": "DELETE_SUCCESS"}.
        - If the user failed to delete the comment return {"delete_status": "DELETE_FAIL"}.

    Raises:
        django.http.Http404: If the specified forum, post or comment does not exist.
    """

    forum_check(id_forum)
    post_check(id_post)
    comment_check(id_comment)

    comment_to_delete = Comment.objects.get(idcom__exact=id_comment)

    response = JsonResponse({"delete_status": "DELETE_FAIL"})

    # Check if the user can delete the comment
    if (comment_to_delete.iduser == request.user or admin_check(request.user)
            or moderator_check(request.user, comment_to_delete.idpost.idforum)):
        # Set the comment as deleted/inactive
        comment_to_delete.status = 'DEL'
        comment_to_delete.save()
        response = JsonResponse({"delete_status": "DELETE_SUCCESS"})
    else:
        raise PermissionDenied

    return response


@login_required(login_url='sign_in')
def team(request, id_forum, id_team):
    """
    Display team page with all team members and messages of the team

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum to which the team belongs.
        id_team (int): Unique identifier of the team which registered user is a member of.

    Returns:
        django.http.HttpResponse: Rendered team.html template.

    Raises:
        django.http.Http404: If forum, team does not exist or registered user is not a member of the team.
    """

    forum_check(id_forum)
    forum = Forum.objects.get(idforum__exact=id_forum)
    team_check(id_forum, id_team)
    team = Team.objects.get(idforum__exact=id_forum, idteam__exact=id_team)

    login_user = request.user
    # Check if registered user is a member of the team
    if TeamMember.objects.filter(iduser__exact=login_user.iduser, idforum__exact=id_forum, idteam__exact=id_team).exists() == False:
        raise MyHttp404("Sorry, you are not part of this team!")

    team_members_list_for_context, messages_for_context = get_members_and_messages(id_forum, id_team, login_user.iduser)

    # room_name presents id of a room to which user connects with opening a page
    context = {
        "name_of_team": team.name,
        "name_of_forum": forum.name,
        "members": team_members_list_for_context,
        "messages": messages_for_context,
        "room_name": str(id_forum)+"t"+str(id_team),
        "id_forum": id_forum
    }
    return render(request, 'GameHubApp/team.html', context, 'text/html', 200)


def team_request(request, id_forum, id_team, id_user, id_not):
    """
    A function representing the backend for accepting or rejecting team invite requests.
    :param request: Http request
    :param id_forum: Team forum for which the request was sent.
    :param id_team: Team for which the request was sent.
    :param id_user: User who sent the request.
    :param id_not: A notification for accepting or rejecting team membership.
    :returns: JsonResponse with join status and message.
    """
    # Request status
    status = json.loads(request.body)
    # Delete the notification
    notification = Notification.objects.get(idnot=id_not)
    notification.delete()
    join_request = RequestToJoin.objects.get(iduser=id_user, idteam=id_team)
    join_request.delete()
    if status['REQUEST_STATUS'] == 'REJECT':
        # Return Fail
        return JsonResponse({'JOIN_STATUS': 'FAIL', 'message': 'Rejected!'})
    # Check if user is member of another team on the forum
    member = TeamMember.objects.filter(idteam=id_team, iduser=id_user)
    if member.exists():
        # Return fail
        return JsonResponse({'JOIN_STATUS': 'FAIL', 'message': 'The user has since joined another team!'})
    # Check to see if the team is full
    members = TeamMember.objects.filter(idteam=id_team)
    number_of_players = Team.objects.get(idteam=id_team).numberofplayers
    if len(members) >= number_of_players:
        # Return fail
        return JsonResponse({'JOIN_STATUS': 'FAIL', 'message': 'The team is full!'})
    # Accept the user's request
    user_object = RegisteredUser.objects.get(iduser=id_user)
    forum_object = Forum.objects.get(idforum=id_forum)
    team_object = Team.objects.get(idteam=id_team)
    new_team_member = TeamMember.objects.create(iduser=user_object, idforum=forum_object, datejoined=datetime.now(),
                                                isleader=0, lastmsgreaddate=datetime.now(), idteam=team_object)
    new_team_member.save()
    # Return success
    return JsonResponse({'JOIN_STATUS': 'SUCCESS', 'message': 'Success'})


def list_tournaments(request, id_forum) -> HttpResponse:
    """
    List all tournaments for a specific forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum for which will be listed tournaments.

    Returns:
        django.http.HttpResponse: Rendered list_tournaments.html template.

    Raises:
        django.http.Http404: If forum with id_forum does not exist.
    """
    forum_check(id_forum)

    forum = Forum.objects.get(idforum=id_forum)
    tours_data = get_tournaments(id_forum)
    is_privileged = check_is_user_privileged(request.user, id_forum)

    context = {
        'forum': forum,
        'tours': tours_data,
        'is_privileged': is_privileged
    }
    return render(request, 'GameHubApp/list_tournaments.html', context, 'text/html', 200)


@login_required(login_url='sign_in')
def create_tournament(request, id_forum) -> typing.Union[HttpResponse, HttpResponseRedirect]:
    """
    Creates a new tournament for a specific forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum on which will be created the tournament.

    Returns:
        django.http.HttpResponse For GET requests or for wrong data in the form with POST requests, rendered create_tournament.html template.

        django.http.HttpResponseRedirect For POST requests with correctly entered data in the form, redirect to list_tournaments.html template.

    Raises:
        django.http.Http404: If forum with id_forum does not exist.
        django.core.exceptions.PermissionDenied: If the user is not an admin or a moderator for this forum.
    """
    forum_check(id_forum)
    is_privileged = check_is_user_privileged(request.user, id_forum)
    if not is_privileged:
        raise MyPermissionDenied("You don't have permission to create tournament!")

    error_msg_name = ""
    error_msg_datetime = ""
    error_msg_format = ""
    error_msg_currency = ""
    error_msg_required_fields = ""

    if request.method == "POST":
        # Get fields from form
        name = request.POST['tour_name']
        date = request.POST['tour_date']
        time = request.POST['tour_time']
        players_per_team = str(request.POST['tour_players_per_team']).split()[0]
        num_of_places = request.POST['tour_num_of_places']
        format = request.POST['tour_format']
        value = request.POST['tour_value']
        currency = request.POST['tour_currency']

        if name != "" and date != "" and time != "" and num_of_places != "" and value != "" and currency != "":
            # Make datatime format from variables 'date' and 'time'
            date_time = str(date) + ' ' + str(time) + ':00.000000'

            if len(name) > 30:
                error_msg_name = "Tournament name is too long! (max 30 characters)"
            if len(currency) > 20:
                error_msg_currency = "Currency is too long! (max 20 characters)"

            # Check if datetime is before current datetime
            if datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S.%f") < datetime.now():
                error_msg_datetime = "Date and time cannot be in the past!"

            # Check if the tournament format is in knockout formats, and if yes, then check if a number of places is power of 2
            num_of_places = int(str(num_of_places))
            if format in get_tournament_knockout_formats():
                temp = log(num_of_places, 2)
                if 2**temp != num_of_places:
                    error_msg_format = "Number of places must be a power of 2 for knockout tournament!"

            if error_msg_name == "" and error_msg_datetime == "" and error_msg_format == "" and error_msg_currency == "":
                # Get user who created tournament and appropriate ForumNumOfPlayers
                create_tour_user = CreateTournamentUser.objects.filter(iduser=request.user.iduser).first()
                forumNumOfPlayers = ForumNumOfPlayers.objects.filter(idforum=id_forum, numberofplayers=players_per_team).first()

                # Insert into database
                new_tournament = Tournament(name=name, startdate=date_time, numberofplaces=num_of_places, format=format,
                                            idforumnumofplayers=forumNumOfPlayers, rewardvalue=value,
                                            rewardcurrency=currency, datecreated=datetime.now(), iduser=create_tour_user)
                new_tournament.save()

                return redirect('list_tournaments', id_forum)
        else:
            error_msg_required_fields = "All fields are required!"

    # Get possible numbers of players per team
    specific_forum_num_of_players = ForumNumOfPlayers.objects.filter(idforum=id_forum)
    number_of_players_per_team = [ row.numberofplayers for row in specific_forum_num_of_players ]

    # Get forum name
    forum_name = Forum.objects.filter(idforum=id_forum).first().name

    context = {
        'id_forum': id_forum,
        'forum_name': forum_name,
        'number_of_players_per_team': number_of_players_per_team,
        'formats': get_tournament_formats(),
        'error_msg_name': error_msg_name,
        'error_msg_datetime': error_msg_datetime,
        'error_msg_format': error_msg_format,
        'error_msg_currency': error_msg_currency,
        'error_msg_required_fields': error_msg_required_fields
    }
    return render(request, 'GameHubApp/create_tournament.html', context, 'text/html', 200)


def tournament(request, id_forum, id_tour) -> typing.Union[HttpResponse, HttpResponseRedirect]:
    """
    Show specified tournament on given forum.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum where the tournament is located.
        id_tour (int): Unique identifier of the tournament that will be shown.

    Returns:
        django.http.HttpResponse For GET requests, rendered tournament.html template.

        django.http.HttpResponseRedirect For POST requests which include "join tournament", "leave tournament",
        "start tournament" and "kick from tournament", redirect to tournament.html template.
        For POST requests which include "finish tournament", "delete tournament", redirect to list_tournaments.html template.

    Raises:
        django.http.Http404: If forum with id_forum does not exist or tournament with id_tour does not exist.
        django.core.exceptions.PermissionDenied: If request is POST that do "start tournament", "finish tournament",
        "delete tournament" or "kick from tournament" and the user is not an admin or a moderator for this forum.
    """
    forum_check(id_forum)
    tournament_check(id_tour)

    tour = Tournament.objects.get(idtour=id_tour)
    error_msg_join, error_msg_leave, error_msg_start, error_msg_finish, error_msg_delete, error_msg_kick = get_error_messages_tournament(request)

    if request.method == "POST":
        if "join" in request.POST:
            error_msg = join_tournament(request, id_forum, id_tour)
            request.session['error_msg_join'] = error_msg
            return redirect('tournament', id_forum, id_tour)
        elif "leave" in request.POST:
            error_msg = leave_tournament(request, id_forum, id_tour)
            request.session['error_msg_leave'] = error_msg
            return redirect('tournament', id_forum, id_tour)
        elif "start" in request.POST:
            error_msg = start_tournament(request, id_forum, id_tour)
            request.session['error_msg_start'] = error_msg
            return redirect('tournament', id_forum, id_tour)
        elif "finish" in request.POST:
            error_msg = finish_tournament(request, id_forum, id_tour)
            request.session['error_msg_finish'] = error_msg
            return redirect('list_tournaments', id_forum)
        elif "delete" in request.POST:
            error_msg = delete_tournament(request, id_forum, id_tour)
            request.session['error_msg_delete'] = error_msg
            return redirect('list_tournaments', id_forum)
        else:
            for elem in request.POST:
                if "kick_" in elem:
                    id_team = elem.split("_")[1]
                    error_msg = kick_from_tournament(request, id_forum, id_tour, id_team)
                    request.session['error_msg_kick'] = error_msg
                    return redirect('tournament', id_forum, id_tour)

    # Get status of tournament, start date and number of places
    tour_status = str(tour.status).replace("_", " ")
    start_date = str(tour.startdate)
    finer_start_date = start_date[8:10] + '.' + start_date[5:7] + '.' + start_date[0:4] + '.' + ' - ' + start_date[11:16]
    num_places = tour.numberofplaces

    # Get info is tournament knockout or not, and if yes, get how much wins is needed to promote to next round
    is_knockout, wins_to_promote = get_is_tournament_knockout(tour)

    # Find the team names, points for each team, and get number of teams participating in the tournament
    team_names, team_points = get_team_names_and_points(id_tour, is_knockout)
    number_of_joined = len(team_names)

    # Get number of <tr> tags to insert in <table> that shows teams (1 <tr> for each team)
    number_of_tr_tags = [ i for i in range(num_places) ]

    # Check if tournament has started
    tournament_started = False
    if tour.status == "IN_PROGRESS":
        tournament_started = True
        while len(team_names) < num_places:
            team_names.append("")
            team_points.append(0)

    # Check if user is admin or moderator on this forum
    is_privileged = check_is_user_privileged(request.user, id_forum)

    # Get teams for participate list
    participate = Participate.objects.filter(idtour=id_tour)
    teams = [ p.idteam for p in participate ]

    context = {
        'tour': tour,
        'error_msg_join': error_msg_join,
        'error_msg_leave': error_msg_leave,
        'error_msg_start': error_msg_start,
        'error_msg_finish': error_msg_finish,
        'error_msg_delete': error_msg_delete,
        'error_msg_kick': error_msg_kick,
        'teams': teams,
        'status': tour_status,
        'start_date': finer_start_date,
        'number_of_places': num_places,
        'number_of_joined': number_of_joined,
        'team_names': team_names,
        'team_points': team_points,
        'number_of_tr': number_of_tr_tags,
        'is_knockout': "true" if is_knockout else "false",
        'wins_to_promote': wins_to_promote,
        'tournament_started': "true" if tournament_started else "false",
        'is_privileged': "true" if is_privileged else "false"
    }
    return render(request, 'GameHubApp/tournament.html', context, 'text/html', 200)


@login_required(login_url='sign_in')
def tournament_update_points(request, id_forum, id_tour) -> JsonResponse:
    """
    Helper function for updating points of a team in the tournament.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum where the tournament is located.
        id_tour (int): Unique identifier of the tournament on which the team is participating.

    Returns:
        django.http.JsonResponse: A JSON response containing information about this tournament, so it can be shown with updated data.

    Raises:
        django.http.Http404: If forum with id_forum does not exist or tournament with id_tour does not exist.
        django.core.exceptions.PermissionDenied: If the user is not an admin or a moderator for this forum.
    """
    forum_check(id_forum)
    tournament_check(id_tour)
    is_privileged = check_is_user_privileged(request.user, id_forum)
    if not is_privileged:
        raise MyPermissionDenied("You don't have permission!")

    tour = Tournament.objects.get(idtour=id_tour)

    body = json.loads(request.body)
    team_name = body["teamName"]
    points_to_add = int(body["pointsToAdd"])

    try:
        # Get the team and update points
        team = Team.objects.get(name=team_name, idforum=id_forum, status="ACT")
        participate = Participate.objects.filter(idtour=id_tour, idteam=team.idteam).first()
        participate.points += points_to_add
        participate.save()
    except Team.DoesNotExist:
        pass

    # Get info is tournament knockout or not, and if yes, get how much wins is needed to promote to next round
    is_knockout, wins_to_promote = get_is_tournament_knockout(tour)

    # Find the team names and points for each team participating in the tournament
    team_names, team_points = get_team_names_and_points(id_tour, is_knockout)
    while len(team_names) < tour.numberofplaces:
        team_names.append("")
        team_points.append(-1)

    return JsonResponse({
        "numberOfPlaces": tour.numberofplaces,
        "teamNames": team_names,
        "teamPoints": team_points,
        "isKnockout": "true" if is_knockout else "false",
        "winsToPromote": wins_to_promote
    })


def custom_400_view(request, exception):
    """
    Custom 400 Bad Request page view.
    :param request: Http request
    :param exception: An exception object containing the appropriate error message.
    :returns: 400 Bad Request page view
    """
    context = {
        'status_code': '400',
        'status_message': 'Bad Request',
        'message': str(exception) if isinstance(exception, MySuspiciousOperation) else ''
    }
    return render(request, 'GameHubApp/error_page.html', context, 'text/html', 400)


def custom_403_view(request, exception):
    """
    Custom 403 Forbidden page view.
    :param request: Http request
    :param exception: An exception object containing the appropriate error message.
    :returns: 403 Forbidden page view
    """
    context = {
        'status_code': '403',
        'status_message': 'Forbidden',
        'message': str(exception) if isinstance(exception, MyPermissionDenied) else ''
    }
    return render(request, 'GameHubApp/error_page.html', context, 'text/html', 403)


def custom_404_view(request, exception):
    """
    Custom 404 Not Found page view.
    :param request: Http request
    :param exception: An exception object containing the appropriate error message.
    :returns: 404 Not Found page view
    """
    context = {
        'status_code': '404',
        'status_message': 'Not Found',
        'message': str(exception) if isinstance(exception, MyHttp404) else ''
    }
    return render(request, 'GameHubApp/error_page.html', context, 'text/html', 404)


def custom_500_view(request):
    """
    Custom 500 Internal Server Error page view.
    :param request: Http request
    :returns: 500 Internal Server Error page view
    """
    context = {
        'status_code': '500',
        'status_message': 'Internal Server Error',
        'message': ''
    }
    return render(request, 'GameHubApp/error_page.html', context, 'text/html', 500)
