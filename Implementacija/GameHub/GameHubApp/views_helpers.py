# Author: Nemanja Mićanović 0595/2021
# Author: Mihajlo Blagojevic 0283/2021
# Author: Viktor Mitrovic 0296/2021
# Author: Tadija Goljic 0272/2021

import base64

import GameHubApp.models as GameHubModels

from datetime import datetime, timedelta
from math import ceil
from random import shuffle
from io import BytesIO
from PIL import Image
import typing

from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Forum, Tournament, Post, LikedPost, Comment, RegisteredUser, Team, TeamMember, Message, \
    Participate, Admin, Moderates, UserParticipated, TourNotification
from .views import MyHttp404, MyPermissionDenied


def admin_check(id_user) -> bool:
    """
    Check if a registered user has administrative privileges.

    Args:
        id_user (GameHubApp.models.RegisteredUser): An instance of the RegisteredUser class.

    Returns:
        bool: True if the registered user has administrative privileges, False otherwise.
    """
    try:
        GameHubModels.Admin.objects.get(idadmin=id_user.iduser)
        return True
    except GameHubModels.Admin.DoesNotExist:
        return False


def moderator_check(id_user, id_forum) -> bool:
    """
    Check if a registered user is a moderator on the given forum.

    Args:
        id_user (GameHubApp.models.RegisteredUser): An instance of the RegisteredUser class.
        id_forum (GameHubApp.models.Forum): An instance of the Forum class.

    Returns:
        bool: True if the registered user is a moderator on the forum, False otherwise.
    """
    try:
        GameHubModels.Moderates.objects.get(idmod=id_user.iduser, idforum=id_forum.idforum)
        return True
    except GameHubModels.Moderates.DoesNotExist:
        return False


def forum_check(id_forum) -> None:
    """
    Helper function for checking if the forum exist.

    Args:
        id_forum (int): Unique identifier of the forum to be checked.

    Returns:
        None

    Raises:
        django.http.Http404: If forum with id_forum does not exist.
    """
    try:
        Forum.objects.get(pk=id_forum, status='ACT')
    except Forum.DoesNotExist:
        raise MyHttp404("Forum does not exist")


def post_check(id_post) -> None:
    """Helper function for checking if a post exists."""
    try:
        Post.objects.get(pk=id_post, status='ACT')
    except Post.DoesNotExist:
        raise MyHttp404("Post does not exist")


def comment_check(id_comment) -> None:
    """Helper function for checking if a comment exists"""
    try:
        Comment.objects.get(idcom__exact=id_comment, status='ACT')
    except Comment.DoesNotExist:
        raise MyHttp404("Comment does not exist")


def tournament_check(id_tour) -> None:
    """
    Helper function for checking if the tournament exist.

    Args:
        id_tour (int): Unique identifier of the tournament to be checked.

    Returns:
        None

    Raises:
        django.http.Http404: If the tournament with id_tour does not exist.
    """
    try:
        Tournament.objects.get(pk=id_tour)
    except Tournament.DoesNotExist:
        raise MyHttp404("Tournament does not exist")


def team_check(id_forum, id_team) -> None:
    """Helper function for checking if a team exists"""
    try:
        Team.objects.get(pk=id_team, idforum__exact=id_forum, status='ACT')
    except Team.DoesNotExist:
        raise MyHttp404("Team does not exist")


def get_team(id_user, id_forum):
    """
    This function fetches the team that the given user belongs to within a specified forum.
    If the user is not a part of any team on the forum, a TeamMember.DoesNotExist exception is raised.

    Args:
        id_user (GameHubApp.models.RegisteredUser): An instance of the RegisteredUser class representing the user.
        id_forum (GameHubApp.models.Forum): An instance of the Forum class representing the forum.

    Returns:
        GameHubApp.models.Team: An instance of the Team class representing the user's team on the forum.

    Raises:
        TeamMember.DoesNotExist: If the user is not a part of any team on the forum.
        Team.DoesNotExist: If the user is a part of a deleted (DEL) team.
    """
    team_member = GameHubModels.TeamMember.objects.get(iduser=id_user.iduser, idforum=id_forum.idforum)
    return GameHubModels.Team.objects.get(idteam__exact=team_member.idteam.idteam, status__exact='ACT')


def get_tournaments(id_forum) -> typing.List[typing.Tuple[Tournament, str, str, int]]:
    """
    Helper function for getting not finished tournaments on the given forum.

    Args:
        id_forum (int): Unique identifier of the forum from which to get the tournaments.

    Returns:
        list: List of tuples where Tournament is an instance of the Tournament class that belong to the given forum,
        first str is start date, second str is start time, int is number of joined teams in the Tournament.
    """
    tours = Tournament.objects.filter(idforumnumofplayers__idforum=id_forum)
    tours_data = []

    for tour in tours:
        if tour.status == 'FINISHED': continue

        # Gets datetime in form of 'YYYY-MM-DD hh:mm:ss', and then makes date in form of DD.MM.YYYY. and time in form of hh:mm
        date, time = str(tour.startdate).split(' ')
        date = date[8:10] + '.' + date[5:7] + '.' + date[0:4] + '.'
        time = time[0:5]

        # Get number of teams participating in the tournament
        number_of_joined = Participate.objects.filter(idtour=tour.idtour).count()

        tours_data.append((tour, date, time, number_of_joined))

    tours_data.sort(key=lambda x: x[0].startdate)
    return tours_data


def get_members_and_messages(id_forum, id_team, login_user_id):
    """
    Helper function that updates the last message date for user and returns list of team members and messages of a team.

    Args:
        id_forum: ID of forum to which the team belongs.
        id_team: ID of team which registered user is a member of.
        login_user_id: ID of registered user for which we are retrieving messages and team members.

    Returns:
        pair(team_members_list_for_context, messages_for_context)

        - team_members_list_for_context: is list of pairs(str, str) where first string is name of user, second is an id of user Ex. [('Morpheus', '1'), ('Trinity', '2'), ...].
        - messages_for_context: is list of tuples(str, int, int, int, str) where first element is name of user, second is an id of user, third is 1/0 check if message was sent by registered user, fourth is a 1/0 check if message was sent by the same user from last message, fifth is message content Ex. [("Morpheus", 1, 1, 0, "Some message"), ...], sixth is a 1/0 if profile was deleted.
    """

    teamMember = TeamMember.objects.filter(idteam__exact=id_team, idforum__exact=id_forum,
                                           iduser__exact=login_user_id).first()
    teamMember.lastmsgreaddate = datetime.now()
    teamMember.save()

    team_members_id_list = []
    team_members_query = TeamMember.objects.filter(idforum__exact=id_forum, idteam__exact=id_team)
    for team_member in team_members_query:
        team_members_id_list.append(team_member.iduser.iduser)

    team_members_list_for_context = []
    registered_user_query = RegisteredUser.objects.filter(iduser__in=team_members_id_list)
    for reg_user in registered_user_query:
        if reg_user.profilepicture is None:
            image_data = None
            profile_picture_ext = None
        else:
            image_data = base64.b64encode(reg_user.profilepicture).decode('utf-8')
            profile_picture_ext = (Image.open(BytesIO(reg_user.profilepicture))).format.lower()
        team_members_list_for_context.append((reg_user.username, reg_user.iduser, image_data, profile_picture_ext))

    messages_for_context = []
    messagesQuery = Message.objects.filter(idteam__exact=id_team)
    for message in messagesQuery:
        # Check if this message was sent by registered user
        check_message_by_login_user = 0
        if message.iduser.iduser == login_user_id:
            check_message_by_login_user = 1

        # Check if this message was sent by the same user from last message
        check_same_user_last_msg = 0
        tmp_msg_len = len(messages_for_context)
        if (check_message_by_login_user == 0 and tmp_msg_len > 0
                and messages_for_context[tmp_msg_len - 1][1] == message.iduser.iduser):
            check_same_user_last_msg = 1

        user_sent = RegisteredUser.objects.filter(iduser=message.iduser.iduser).first()
        # Check deleted profile
        check_deleted_user = 0
        if user_sent.status == 'DEL':
            check_deleted_user = 1

        messages_for_context.append((user_sent.username, message.iduser.iduser,
                                     check_message_by_login_user, check_same_user_last_msg, message.body, check_deleted_user))

    return team_members_list_for_context, messages_for_context


def create_notification(id_user):
    """
    Create a notification for the specified user.
    This function also deletes user's notifications older than 7 days.

    Args:
        id_user (GameHubApp.models.RegisteredUser): An instance of the RegisteredUser class representing the user.

    Returns:
        GameHubApp.models.Notification: A base notification that can be used to create a
                                        `GameHubApp.models.ForumNotification`,
                                        `GameHubApp.models.TeamNotification`, or a
                                        `GameHubApp.models.TourNotification`.
    """
    team_requests = GameHubModels.TeamNotification.objects.filter(type="TEAM_INVITE")
    user_notifications = GameHubModels.Notification.objects.filter(iduser__exact=id_user.iduser)
    user_notifications = user_notifications.exclude(idnot__in=team_requests)

    for user_notification in user_notifications:
        user_notification_datesent = str(user_notification.datesent.date()) \
             + " " + str(user_notification.datesent.time())
        user_notification_datesent = user_notification_datesent[0:19] + '.000000'
        if datetime.strptime(user_notification_datesent, "%Y-%m-%d %H:%M:%S.%f") < datetime.now() - timedelta(days=7):
            user_notification.delete()

    new_notification = GameHubModels.Notification(iduser=id_user, datesent=datetime.now())
    new_notification.save()
    return new_notification


def find_teams(id_forum, text=''):
    """
    A function that searches for active teams on the given forum whose name starts with a given text
    :param id_forum: Forum
    :param text: text
    """
    teams = []
    for i, forum_team in enumerate(Team.objects.filter(idforum=id_forum, name__startswith=text, status='ACT')):
        num_of_joined = len(TeamMember.objects.filter(idteam=forum_team.idteam, idforum=id_forum))
        user_leader = TeamMember.objects.get(idteam=forum_team.idteam, isleader=1)
        username_leader = RegisteredUser.objects.get(iduser=user_leader.iduser.iduser)
        id_team = forum_team.idteam
        teams.append((i, forum_team.name, username_leader.username, forum_team.numberofplayers, num_of_joined, id_team))
    return teams if teams else None


def check_is_user_privileged(user, id_forum) -> bool:
    """
    Check if the user is an admin or a moderator on the given forum.

    Args:
        user (GameHubApp.models.RegisteredUser): An instance of the RegisteredUser.
        id_forum (int): Unique identifier of the forum on which to check if the user is a moderator.

    Returns:
        bool: True if the user is an admin or a moderator on the given forum, False otherwise.
    """
    if not user.is_authenticated:
        return False
    is_admin = admin_check(user)
    is_mod_on_this_forum = moderator_check(user, Forum.objects.filter(idforum=id_forum).first())
    if is_admin or is_mod_on_this_forum:
        return True
    return False


def get_tournament_formats() -> typing.List[str]:
    """
    Get list of all tournament formats.

    Returns:
        list: List of all tournament formats.
    """
    return ['Best of 1', 'Best of 3', 'Best of 5', 'Points']


def get_tournament_knockout_formats() -> typing.List[str]:
    """
        Get list of all tournament knockout formats.

        Returns:
            list: List of all tournament knockout formats.
        """
    return ['Best of 1', 'Best of 3', 'Best of 5']


def get_is_tournament_knockout(tour) -> typing.Tuple[bool, int]:
    """
    Get if the tournament format is knockout or not and get number of wins needed to promote to next round in the tournament.

    Args:
        tour (GameHubApp.models.Tournament): An instance of the Tournament.

    Returns:
        tuple: Tuple where bool is True if the tournament format is knockout, False otherwise,
        and int is the number of wins needed to promote to next round in the tournament.
    """
    is_knockout = False
    wins_to_promote = 0
    if tour.format in get_tournament_knockout_formats():
        is_knockout = True
        wins_to_promote = ceil(int(str(tour.format)[-1]) / 2)

    return is_knockout, wins_to_promote


def get_team_names_and_points(id_tour, is_knockout) -> typing.Tuple[typing.List[str], typing.List[int]]:
    """
    Get the team names and points for each team participating in the given tournament.

    Args:
        id_tour (int): Unique identifier of the tournament from which to get team names and points.
        is_knockout: Specifies if the tournament is in knockout format or not, for sorting team names and points.

    Returns:
        tuple: Tuple where list[str] is list of team names and list[int] is list of points for each team.
    """
    if is_knockout:
        participate = Participate.objects.filter(idtour=id_tour).order_by('position')
    else:
        participate = Participate.objects.filter(idtour=id_tour).order_by('-points')
    team_names = [ p.idteam.name for p in participate ]
    team_points = [ p.points for p in participate ]

    return team_names, team_points


def get_error_messages_tournament(request) -> typing.Tuple[str, str, str, str, str, str]:
    """
    Get error messages for the tournament from the given request.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.

    Returns:
        tuple: Tuple of 6 strings, each represents the error message for different
        functionality on the tournament (join, leave, start, finish, delete, kick).
    """
    error_msg_join = ""
    error_msg_leave = ""
    error_msg_start = ""
    error_msg_finish = ""
    error_msg_delete = ""
    error_msg_kick = ""
    if 'error_msg_join' in request.session:
        error_msg_join = request.session['error_msg_join']
        del request.session['error_msg_join']
    elif 'error_msg_leave' in request.session:
        error_msg_leave = request.session['error_msg_leave']
        del request.session['error_msg_leave']
    elif 'error_msg_start' in request.session:
        error_msg_start = request.session['error_msg_start']
        del request.session['error_msg_start']
    elif 'error_msg_finish' in request.session:
        error_msg_finish = request.session['error_msg_finish']
        del request.session['error_msg_finish']
    elif 'error_msg_delete' in request.session:
        error_msg_delete = request.session['error_msg_delete']
        del request.session['error_msg_delete']
    elif 'error_msg_kick' in request.session:
        error_msg_kick = request.session['error_msg_kick']
        del request.session['error_msg_kick']

    return error_msg_join, error_msg_leave, error_msg_start, error_msg_finish, error_msg_delete, error_msg_kick


@login_required(login_url='sign_in')
def join_tournament(request, id_forum, id_tour) -> str:
    """
    Join the tournament.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum where the tournament is located.
        id_tour (int): Unique identifier of the tournament to be joined.

    Returns:
        String: Error message for joining the tournament if there is any, else empty string.
    """
    tour = Tournament.objects.get(idtour=id_tour)

    if tour.status == "IN_PROGRESS":
        return "Tournament is in progress!"
    elif tour.status == "FINISHED":
        return "Tournament has finished!"

    # Check if the user is in the team and is team leader
    team_member = TeamMember.objects.filter(iduser=request.user.iduser, idforum=id_forum).first()
    if team_member is None:
        return "You are not in a team!"
    elif team_member.isleader == 0:
        return "You are not team leader!"

    team = team_member.idteam

    # Check if the users team is already participating in the tournament
    participate = Participate.objects.filter(idteam=team.idteam, idtour=tour.idtour).first()
    if participate is not None:
        return "Your team is already participating!"

    # Check if the tournament is full
    joined_count = Participate.objects.filter(idtour=id_tour).all().count()
    if joined_count == tour.numberofplaces:
        return "Tournament is full!"

    # Check if the users team has enough players
    team_member_count = TeamMember.objects.filter(idteam=team.idteam, idforum=id_forum).all().count()
    if team_member_count != tour.idforumnumofplayers.numberofplayers:
        return "Not enough players in a team!"

    # Send notification
    team_members = TeamMember.objects.filter(idteam=team.idteam, idforum=id_forum)
    for member in team_members:
        if member.isleader == 0:
            base_notification = create_notification(member.iduser)
            tour_notification = TourNotification(idnot=base_notification, idtour=tour, type='TOUR_JOINED')
            tour_notification.save()

    participate = Participate(idteam=team, idtour=tour, position=-1, points=0)
    participate.save()
    return ""


@login_required(login_url='sign_in')
def leave_tournament(request, id_forum, id_tour) -> str:
    """
    Leave the tournament.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum where the tournament is located.
        id_tour (int): Unique identifier of the tournament to be leaved.

    Returns:
        String: Error message for leaving the tournament if there is any, else empty string.
    """
    tour = Tournament.objects.get(idtour=id_tour)

    if tour.status == "IN_PROGRESS":
        return "Tournament is in progress!"
    elif tour.status == "FINISHED":
        return "Tournament has finished!"

    participate = None
    team_member = TeamMember.objects.filter(iduser=request.user.iduser, idforum=id_forum).first()
    if team_member is not None:
        team = team_member.idteam
        participate = Participate.objects.filter(idteam=team, idtour=tour).first()

    if participate is None:
        return "You are not participating!"
    elif team_member.isleader == 0:
        return "You are not team leader!"

    participate.delete()
    return ""


@login_required(login_url='sign_in')
def start_tournament(request, id_forum, id_tour) -> str:
    """
    Start the tournament.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum where the tournament is located.
        id_tour (int): Unique identifier of the tournament to be started.

    Returns:
        String: Error message for starting the tournament if there is any, else empty string.

    Raises:
        django.core.exceptions.PermissionDenied: If the user is not an admin or a moderator for this forum.
    """
    tour = Tournament.objects.get(idtour=id_tour)

    is_privileged = check_is_user_privileged(request.user, id_forum)
    if not is_privileged:
        raise MyPermissionDenied("You don't have permission to start the tournament!")

    if tour.status == "IN_PROGRESS":
        return "Tournament is in progress!"
    elif tour.status == "FINISHED":
        return "Tournament has finished!"

    date_time = str(tour.startdate.date()) + " " + str(tour.startdate.time())
    if datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S") > datetime.now():
        return "It is not yet time to start the tournament!"

    # Find random positions for teams participating in the tournament
    participate = Participate.objects.filter(idtour=id_tour).all()
    number_of_joined = participate.count()
    positions = [i for i in range(number_of_joined)]
    shuffle(positions)
    for i, p in enumerate(participate):
        p.position = positions[i]
        p.save()

    # Send notifications
    for p in participate:
        team_members = TeamMember.objects.filter(idteam=p.idteam.idteam, idforum=id_forum)
        for member in team_members:
            base_notification = create_notification(member.iduser)
            tour_notification = TourNotification(idnot=base_notification, idtour=tour, type='TOUR_STARTED')
            tour_notification.save()

    # Update status
    tour.status = "IN_PROGRESS"
    tour.save()
    return ""


@login_required(login_url='sign_in')
def finish_tournament(request, id_forum, id_tour) -> str:
    """
    Finish the tournament.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum where the tournament is located.
        id_tour (int): Unique identifier of the tournament to be finished.

    Returns:
        String: Error message for finishing the tournament if there is any, else empty string.

    Raises:
        django.core.exceptions.PermissionDenied: If the user is not an admin or a moderator for this forum.
    """
    tour = Tournament.objects.get(idtour=id_tour)

    is_privileged = check_is_user_privileged(request.user, id_forum)
    if not is_privileged:
        raise MyPermissionDenied("You don't have permission to finish the tournament!")

    if tour.status == "NOT_STARTED":
        return "Tournament has not started!"
    elif tour.status == "FINISHED":
        return "Tournament has finished!"

    # Insert users that participated in the tournament into UserParticipated table
    participate = Participate.objects.filter(idtour=id_tour).all()
    for p in participate:
        team_members = TeamMember.objects.filter(idteam=p.idteam, idforum=id_forum)
        for team_member in team_members:
            user_participated = UserParticipated(idpar=p, iduser=team_member.iduser)
            user_participated.save()

    # Update status
    tour.status = "FINISHED"
    tour.save()
    return ""


@login_required(login_url='sign_in')
def delete_tournament(request, id_forum, id_tour) -> str:
    """
    Delete the tournament.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum where the tournament is located.
        id_tour (int): Unique identifier of the tournament to be deleted.

    Returns:
        String: Error message for deleting the tournament if there is any, else empty string.

    Raises:
        django.core.exceptions.PermissionDenied: If the user is not an admin or a moderator for this forum.
    """
    tour = Tournament.objects.get(idtour=id_tour)

    is_privileged = check_is_user_privileged(request.user, id_forum)
    if not is_privileged:
        raise MyPermissionDenied("You don't have permission to delete the tournament!")

    if tour.status == "FINISHED":
        return "Tournament has finished!"

    # Delete from Participate for this Tournament    <=== Only if on delete cascade is not set
    # participate = Participate.objects.filter(idtour=id_tour).all()
    # for p in participate:
    #     p.delete()

    tour.delete()
    return ""


@login_required(login_url='sign_in')
def kick_from_tournament(request, id_forum, id_tour, id_team) -> str:
    """
    Kick from the tournament.

    Args:
        request (django.http.HttpRequest): HttpRequest object containing information about the current user.
        id_forum (int): Unique identifier of the forum where the tournament is located.
        id_tour (int): Unique identifier of the tournament to be kicked from.
        id_team (int): Unique identifier of the team to be kicked from the tournament.

    Returns:
        String: Error message for kicking from the tournament if there is any, else empty string.

    Raises:
        django.core.exceptions.PermissionDenied: If the user is not an admin or a moderator for this forum.
    """
    tour = Tournament.objects.get(idtour=id_tour)

    is_privileged = check_is_user_privileged(request.user, id_forum)
    if not is_privileged:
        raise MyPermissionDenied("You don't have permission to kick from tournament!")

    if tour.status == "IN_PROGRESS":
        return "Tournament is in progress!"
    elif tour.status == "FINISHED":
        return "Tournament has finished!"

    # Send notification
    team_members = TeamMember.objects.filter(idteam=id_team)
    for member in team_members:
        base_notification = create_notification(member.iduser)
        tour_notification = TourNotification(idnot=base_notification, idtour=tour, type='TOUR_KICKED')
        tour_notification.save()

    # Kick team
    participate = Participate.objects.filter(idtour=id_tour, idteam=id_team).first()
    participate.delete()
    return ""


def create_a_team_base_context(id_forum):
    """
    A function that makes base context for create_a_team page
    :param id_forum: Forum where a team will be created
    :returns: create_a_team page context
    """
    context = None
    forum_info = Forum.objects.get(idforum=id_forum)
    forum_name = forum_info.name
    number_of_team_members_list = [
        row.numberofplayers for row in GameHubModels.ForumNumOfPlayers.objects.filter(idforum=id_forum)
    ]
    if len(number_of_team_members_list) > 0:
        number_of_team_members = None
        if len(number_of_team_members_list) == 1:
            number_of_team_members = number_of_team_members_list[0]
            number_of_team_members_list = None
        context = {
            'forum_name': forum_name,
            'id_forum': id_forum,
            'number_of_team_members_list': number_of_team_members_list,
            'number_of_team_members': number_of_team_members
        }
    return context


def user_profile_base_context(request, id_user):
    """
    A function that makes base context for user_profile page
    :param id_user: Profile's user
    :param request: Http request
    :returns: user_profile page context
    """
    profile_user = RegisteredUser.objects.get(iduser=id_user, is_active=1)
    profile_username = profile_user.username
    profile_about_section = profile_user.aboutsection
    # User profile picture
    profile_user_picture_b64 = None
    profile_user_picture_ext = ''
    if profile_user.profilepicture is not None:
        profile_user_picture_b64 = base64.b64encode(profile_user.profilepicture).decode('utf-8')
        profile_user_picture_ext = (Image.open(BytesIO(profile_user.profilepicture))).format.lower()
    context = {
        'profile_username': profile_username,
        'profile_about_section': profile_about_section,
        'can_delete': profile_user == request.user or Admin.objects.filter(idadmin=request.user.iduser).exists(),
        'can_edit': profile_user == request.user,
        'id_user': id_user,
        'user_profile_picture': {
            'b64': profile_user_picture_b64,
            'ext': profile_user_picture_ext
        },
        'message': '',
        'delete_message': ''
    }
    return context
