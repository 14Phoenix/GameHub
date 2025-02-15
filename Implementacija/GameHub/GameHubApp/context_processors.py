# Author: Viktor Mitrovic 0296/2021

import GameHubApp.models as GameHubModels
from django.urls import reverse
import base64
from io import BytesIO
from PIL import Image


def profile_picture_context_processor(request):
    """
    Custom Django context processor for user's profile picture.

    Args:
        request (django.http.HttpRequest): HttpRequest object.

    Returns:
        dict: A dictionary containing information about the user's profile image.
    """

    profile_picture_b64 = None
    profile_picture_ext = ""

    if request.user.is_authenticated and request.user.profilepicture is not None:
        profile_picture_b64 = base64.b64encode(request.user.profilepicture).decode('utf-8')
        profile_picture_ext = (Image.open(BytesIO(request.user.profilepicture))).format.lower()

    return {
        "gamehub_profile_picture": {
            "b64": profile_picture_b64,
            "ext": profile_picture_ext
        }
    }


def notification_context_processor(request):
    """
    Custom Django context processor for notifications.

    Args:
        request (django.http.HttpRequest): HttpRequest object.

    Returns:
        dict: A dictionary containing notification information to be added to the template context.
    """

    gamehub_notifications = []
    gamehub_team_requests = []

    if request.user.is_authenticated:
        notifications = GameHubModels.Notification.objects.filter(iduser=request.user)
        forum_notifications = GameHubModels.ForumNotification.objects.filter(idnot__in=notifications.all())
        tour_notifications = GameHubModels.TourNotification.objects.filter(idnot__in=notifications.all())
        team_notifications = GameHubModels.TeamNotification.objects.filter(idnot__in=notifications.all())

        for forum_notification in forum_notifications:
            notification = dict()

            notification["class"] = "FORUM"
            notification["object"] = forum_notification

            notification["url"] = reverse('forum', args=[forum_notification.idforum.idforum])

            if forum_notification.type == "POST_NEW":
                notification["url"] = reverse('post', args=[forum_notification.idforum.idforum,
                                                            forum_notification.idpost.idpost])

            gamehub_notifications.append(notification)

        for tour_notification in tour_notifications:
            notification = dict()

            notification["class"] = "TOURNAMENT"
            notification["object"] = tour_notification

            notification["url"] = reverse('tournament',
                                          args=[tour_notification.idtour.idforumnumofplayers.idforum.idforum,
                                                tour_notification.idtour.idtour])

            if tour_notification.type == "TOUR_KICKED":
                notification["url"] = reverse('list_tournaments',
                                              args=[tour_notification.idtour.idforumnumofplayers.idforum.idforum])

            gamehub_notifications.append(notification)

        for team_notification in team_notifications:
            notification = dict()

            notification["class"] = "TEAM"
            notification["object"] = team_notification

            notification["url"] = reverse('team',
                                          args=[team_notification.idteam.idforum.idforum,
                                                team_notification.idteam.idteam])

            if team_notification.type == "TEAM_INVITE":
                notification["team_request_url"] = reverse('team_request',
                                                           args=[team_notification.idteam.idforum.idforum,
                                                                 team_notification.idteam.idteam,
                                                                 team_notification.iduser.iduser,
                                                                 team_notification.idnot.idnot])
                gamehub_team_requests.append(notification)
            else:
                gamehub_notifications.append(notification)

    gamehub_notifications.sort(key=lambda gh_not: gh_not["object"].idnot.datesent, reverse=True)

    return {
        "gamehub_notifications": gamehub_notifications,
        "gamehub_team_requests": gamehub_team_requests
    }
