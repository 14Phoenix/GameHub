# Author: Mihajlo Blagojevic 0283/2021

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Message, RegisteredUser, TeamMember, TeamNotification, Notification
from datetime import datetime
from django.urls import reverse

from .views_helpers import create_notification


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        self.user = self.scope["user"]

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        # Check if user is member of the team is already tested in function team
        if self.user.is_authenticated:
            self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        """
            Function that is called when sending the message, thought channels is distributed to all connected team members
        """

        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        room_name = text_data_json["room_name"]
        id_team = room_name.split('t')[1]
        id_forum = room_name.split('t')[0]

        id_user_sent_msg = self.user.iduser
        username_user_sent_msg = self.user.username
        # Link to the profile of user
        link_user = reverse("user_profile", args=[id_user_sent_msg])

        # Check if any messages exist in the team
        check_if_any_messages = Message.objects.filter(idteam__exact=id_team).exists()
        # Variable same_user_as_prev_mess tells us if same user sent 2 or more consecutive messages
        # if so, we show link to a profile page only in first message
        same_user_as_prev_mess = False

        if check_if_any_messages:
            last_message_before_this = Message.objects.filter(idteam__exact=id_team).order_by('idmsg').last()
            if last_message_before_this.iduser.iduser == id_user_sent_msg:
                same_user_as_prev_mess = True

        new_message = Message(body=message, idteam_id=id_team, iduser_id=id_user_sent_msg, datesent=datetime.now())
        new_message.save()

        team_members_query = TeamMember.objects.filter(idforum__exact=id_forum, idteam__exact=id_team)
        for team_member in team_members_query:
            if team_member.iduser.iduser != id_user_sent_msg:
                for team_notification in TeamNotification.objects.filter(idteam=id_team, idnot__iduser=team_member.iduser, type='NEW_MSG'):
                    base_notification = team_notification.idnot
                    team_notification.delete()
                    base_notification.delete()

                notf = create_notification(team_member.iduser)
                team_notf = TeamNotification(idnot=notf, idteam_id=id_team, iduser=None, type='NEW_MSG')
                team_notf.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message, "id_user_sent_msg": id_user_sent_msg,
                                   "username_user_sent_msg": username_user_sent_msg, "link_user": link_user,
                                   "same_user_as_prev_mess": same_user_as_prev_mess, "id_team": id_team,
                                   "id_forum": id_forum}
        )

    # Receive message from room group
    def chat_message(self, event):
        """
        Function that is called for each connected team member, receiving all necessary information about new message
        and updating the last message date

        Returns:
            dict

            - message: message text.
            - id_user_sent_msg: ID of user that sent the message.
            - username_user_sent_msg: username of user that sent the message.
            - link_user: link to profile of user that sent the message.
            - same_user_as_prev_mess: check if same user sent 2 or more consecutive messages.
            - is_my_message: check whether user that sent this message is same as one receiving.
        """

        message = event["message"]
        id_user_sent_msg = event["id_user_sent_msg"]
        username_user_sent_msg = event["username_user_sent_msg"]
        link_user = event["link_user"]
        same_user_as_prev_mess = event["same_user_as_prev_mess"]

        id_team = int(event["id_team"])
        id_forum = int(event["id_forum"])

        id_user_logged_in = self.user.iduser
        is_my_message = False
        if id_user_sent_msg == id_user_logged_in:
            is_my_message = True

        teamMember = TeamMember.objects.filter(idteam__exact=id_team, idforum__exact=id_forum,
                                               iduser__exact=id_user_logged_in).first()
        teamMember.lastmsgreaddate = datetime.now()
        teamMember.save()

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message, "id_user_sent_msg": id_user_sent_msg,
                                        "username_user_sent_msg": username_user_sent_msg, "link_user": link_user,
                                        "same_user_as_prev_mess": same_user_as_prev_mess,
                                        "is_my_message": is_my_message}))
