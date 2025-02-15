# Author: Nemanja Mićanović 0595/2021
# Author: Mihajlo Blagojevic 0283/2021
# Author: Viktor Mitrovic 0296/2021
# Author: Tadija Goljic 0272/2021

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CheckConstraint, Q


class Admin(models.Model):
    idadmin = models.OneToOneField('CreateTournamentUser', models.CASCADE, db_column='IDAdmin', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'admin'


class Comment(models.Model):
    idcom = models.AutoField(db_column='IDCom', primary_key=True)  # Field name made lowercase.
    iduser = models.ForeignKey('RegisteredUser', models.CASCADE, db_column='IDUser')  # Field name made lowercase.
    idpost = models.ForeignKey('Post', models.CASCADE, db_column='IDPost')  # Field name made lowercase.
    body = models.CharField(db_column='Body', max_length=15000)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=3, default='ACT')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'comment'
        constraints = [
            CheckConstraint(
                check=Q(status__in=['ACT', 'DEL']),
                name='comment_status_in_act_or_del'
            ),
        ]


class CreateTournamentUser(models.Model):
    iduser = models.OneToOneField('RegisteredUser', models.CASCADE, db_column='IDUser', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'create_tournament_user'


class Follow(models.Model):
    idfollow = models.AutoField(db_column='IDFollow', primary_key=True)  # Field name made lowercase.
    iduser = models.ForeignKey('RegisteredUser', models.CASCADE, db_column='IDUser')  # Field name made lowercase.
    idforum = models.ForeignKey('Forum', models.CASCADE, db_column='IDForum')  # Field name made lowercase.
    datefollowed = models.DateTimeField(db_column='DateFollowed')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'follow'
        unique_together = (('iduser', 'idforum'),)


class ForgotPassword(models.Model):
    idforgot = models.AutoField(db_column='IDForgot', primary_key=True)  # Field name made lowercase.
    resetkey = models.CharField(db_column='ResetKey', unique=True, max_length=37)  # Field name made lowercase.
    expirationdate = models.DateTimeField(db_column='ExpirationDate')  # Field name made lowercase.
    iduser = models.ForeignKey('RegisteredUser', models.CASCADE, db_column='IDUser')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'forgot_password'


class Forum(models.Model):
    idforum = models.AutoField(db_column='IDForum', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=50)  # Field name made lowercase.
    coverimage = models.BinaryField(db_column='CoverImage')  # Field name made lowercase.
    bannerimage = models.BinaryField(db_column='BannerImage')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=1000)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=3)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'forum'
        constraints = [
            CheckConstraint(
                check=Q(status__in=['ACT', 'DEL']),
                name='forum_status_in_act_or_del'
            ),
        ]


class ForumNotification(models.Model):
    idnot = models.OneToOneField('Notification', models.CASCADE, db_column='IDNot', primary_key=True)  # Field name made lowercase.
    idpost = models.ForeignKey('Post', models.CASCADE, db_column='IDPost', blank=True, null=True)  # Field name made lowercase.
    idforum = models.ForeignKey(Forum, models.CASCADE, db_column='IDForum')  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=12)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'forum_notification'
        constraints = [
            CheckConstraint(
                check=Q(type__in=['POST_DEL', 'POST_NEW', 'MOD_DELETED', 'MOD_ADDED']),
                name='forum_notification_type'
            ),
        ]


class ForumNumOfPlayers(models.Model):
    idforumnumofplayers = models.AutoField(db_column='IDForumNumOfPlayers', primary_key=True)  # Field name made lowercase.
    idforum = models.ForeignKey(Forum, models.CASCADE, db_column='IDForum')  # Field name made lowercase.
    numberofplayers = models.IntegerField(db_column='NumberOfPlayers')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'forum_num_of_players'
        unique_together = (('idforum', 'numberofplayers'),)


class LikedComment(models.Model):
    idlike = models.AutoField(db_column='IDLike', primary_key=True)  # Field name made lowercase.
    iduser = models.ForeignKey('RegisteredUser', models.CASCADE, db_column='IDUser')  # Field name made lowercase.
    idcom = models.ForeignKey(Comment, models.CASCADE, db_column='IDCom')  # Field name made lowercase.
    dateliked = models.DateTimeField(db_column='DateLiked')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'liked_comment'
        unique_together = (('iduser', 'idcom'),)


class LikedPost(models.Model):
    idlike = models.AutoField(db_column='IDLike', primary_key=True)  # Field name made lowercase.
    iduser = models.ForeignKey('RegisteredUser', models.CASCADE, db_column='IDUser')  # Field name made lowercase.
    idpost = models.ForeignKey('Post', models.CASCADE, db_column='IDPost')  # Field name made lowercase.
    dateliked = models.DateTimeField(db_column='DateLiked')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'liked_post'
        unique_together = (('iduser', 'idpost'),)


class Message(models.Model):
    body = models.CharField(db_column='Body', max_length=2000)  # Field name made lowercase.
    idmsg = models.AutoField(db_column='IDMsg', primary_key=True)  # Field name made lowercase.
    idteam = models.ForeignKey('Team', models.CASCADE, db_column='IDTeam')  # Field name made lowercase.
    iduser = models.ForeignKey('RegisteredUser', models.CASCADE, db_column='IDUser')  # Field name made lowercase.
    datesent = models.DateTimeField(db_column='DateSent')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'message'


class Moderates(models.Model):
    idmoderates = models.AutoField(db_column='IDModerates', primary_key=True)  # Field name made lowercase.
    idforum = models.ForeignKey(Forum, models.CASCADE, db_column='IDForum')  # Field name made lowercase.
    idmod = models.ForeignKey('Moderator', models.CASCADE, db_column='IDMod')  # Field name made lowercase.
    datepromoted = models.DateTimeField(db_column='DatePromoted')  # Field name made lowercase.
    idadmin = models.ForeignKey(Admin, models.SET_NULL, db_column='IDAdmin', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'moderates'
        unique_together = (('idforum', 'idmod'),)


class Moderator(models.Model):
    idmod = models.OneToOneField(CreateTournamentUser, models.CASCADE, db_column='IDMod', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'moderator'


class Notification(models.Model):
    iduser = models.ForeignKey('RegisteredUser', models.RESTRICT, db_column='IDUser')  # Field name made lowercase.
    idnot = models.AutoField(db_column='IDNot', primary_key=True)  # Field name made lowercase.
    datesent = models.DateTimeField(db_column='DateSent')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'notification'


class Participate(models.Model):
    idpar = models.AutoField(db_column='IDPar', primary_key=True)  # Field name made lowercase.
    idteam = models.ForeignKey('Team', models.CASCADE, db_column='IDTeam')  # Field name made lowercase.
    idtour = models.ForeignKey('Tournament', models.CASCADE, db_column='IDTour')  # Field name made lowercase.
    position = models.IntegerField(db_column='Position')  # Field name made lowercase.
    points = models.IntegerField(db_column='Points')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'participate'
        unique_together = (('idteam', 'idtour'),)


class Post(models.Model):
    idpost = models.AutoField(db_column='IDPost', primary_key=True)  # Field name made lowercase.
    idforum = models.ForeignKey(Forum, models.CASCADE, db_column='IDForum')  # Field name made lowercase.
    iduser = models.ForeignKey('RegisteredUser', models.CASCADE, db_column='IDUser')  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=200)  # Field name made lowercase.
    body = models.CharField(db_column='Body', max_length=15000, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=3, default='ACT')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'post'
        constraints = [
            CheckConstraint(
                check=Q(status__in=['ACT', 'DEL']),
                name='post_status_in_act_or_del'
            ),
        ]


class RegisteredUser(AbstractUser):
    iduser = models.AutoField(db_column='IDUser', primary_key=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', unique=True, max_length=254)  # Field name made lowercase.
    username = models.CharField(db_column='Username', max_length=25)  # Field name made lowercase.
    # password = models.CharField(db_column='Password', max_length=50)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=3)  # Field name made lowercase.
    dateregistered = models.DateTimeField(db_column='DateRegistered')  # Field name made lowercase.
    profilepicture = models.BinaryField(db_column='ProfilePicture', blank=True, null=True)  # Field name made lowercase.
    aboutsection = models.CharField(db_column='AboutSection', max_length=200, blank=True, null=True)  # Field name made lowercase.

    USERNAME_FIELD = "email"
    EMAIL_FIELD = None
    REQUIRED_FIELDS = []

    class Meta:
        managed = True
        db_table = 'registered_user'
        constraints = [
            CheckConstraint(
                check=Q(status__in=['ACT', 'DEL']),
                name='registered_user_status_in_act_or_del'
            ),
        ]


class RequestToJoin(models.Model):
    idreq = models.AutoField(db_column='IDReq', primary_key=True)  # Field name made lowercase.
    iduser = models.ForeignKey(RegisteredUser, models.CASCADE, db_column='IDUser')  # Field name made lowercase.
    idteam = models.ForeignKey('Team', models.CASCADE, db_column='IDTeam')  # Field name made lowercase.
    requestdate = models.DateTimeField(db_column='RequestDate')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'request_to_join'
        unique_together = (('iduser', 'idteam'),)


class Team(models.Model):
    idteam = models.AutoField(db_column='IDTeam', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=20)  # Field name made lowercase.
    numberofplayers = models.IntegerField(db_column='NumberOfPlayers')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=3)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=200)  # Field name made lowercase.
    idforum = models.ForeignKey(Forum, models.CASCADE, db_column='IDForum')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'team'
        constraints = [
            CheckConstraint(
                check=Q(status__in=['ACT', 'DEL']),
                name='team_status_in_act_or_del'
            ),
        ]


class TeamMember(models.Model):
    idmember = models.AutoField(db_column='IDMember', primary_key=True)  # Field name made lowercase.
    iduser = models.ForeignKey(RegisteredUser, models.CASCADE, db_column='IDUser')  # Field name made lowercase.
    idforum = models.ForeignKey(Forum, models.CASCADE, db_column='IDForum')  # Field name made lowercase.
    idteam = models.ForeignKey(Team, models.CASCADE, db_column='IDTeam')  # Field name made lowercase.
    isleader = models.BooleanField(db_column='IsLeader')  # Field name made lowercase. This field type is a guess.
    datejoined = models.DateTimeField(db_column='DateJoined')  # Field name made lowercase.
    lastmsgreaddate = models.DateTimeField(db_column='LastMsgReadDate')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'team_member'
        unique_together = (('iduser', 'idforum'),)


class TeamNotification(models.Model):
    idnot = models.OneToOneField(Notification, models.CASCADE, db_column='IDNot', primary_key=True)  # Field name made lowercase.
    idteam = models.ForeignKey(Team, models.CASCADE, db_column='IDTeam')  # Field name made lowercase.
    iduser = models.ForeignKey(RegisteredUser, models.CASCADE, db_column='IDUser', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=12)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'team_notification'
        constraints = [
            CheckConstraint(
                check=Q(type__in=['TEAM_INVITE', 'TEAM_LEAVE', 'TEAM_JOINED', 'NEW_MSG']),
                name='team_notification_type'
            ),
        ]


class TourNotification(models.Model):
    idnot = models.OneToOneField(Notification, models.CASCADE, db_column='IDNot', primary_key=True)  # Field name made lowercase.
    idtour = models.ForeignKey('Tournament', models.SET_NULL, db_column='IDTour', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=13)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tour_notification'
        constraints = [
            CheckConstraint(
                check=Q(type__in=['TOUR_JOINED', 'TOUR_STARTED', 'TOUR_KICKED']),
                name='tour_notification_type'
            ),
        ]


class Tournament(models.Model):
    idtour = models.AutoField(db_column='IDTour', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=30)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate')  # Field name made lowercase.
    numberofplaces = models.IntegerField(db_column='NumberOfPlaces')  # Field name made lowercase.
    format = models.CharField(db_column='Format', max_length=30)  # Field name made lowercase.
    idforumnumofplayers = models.ForeignKey(ForumNumOfPlayers, models.CASCADE, db_column='IDForumNumOfPlayers')  # Field name made lowercase.
    rewardvalue = models.IntegerField(db_column='RewardValue')  # Field name made lowercase.
    rewardcurrency = models.CharField(db_column='RewardCurrency', max_length=20)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=12, default='NOT_STARTED')  # Field name made lowercase.
    iduser = models.ForeignKey(CreateTournamentUser, models.SET_NULL, db_column='IDUser', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tournament'
        constraints = [
            CheckConstraint(
                check=Q(status__in=['NOT_STARTED', 'IN_PROGRESS', 'FINISHED']),
                name='tournament_status'
            ),
        ]


class UserParticipated(models.Model):
    iduserpar = models.AutoField(db_column='IDUserPar', primary_key=True)  # Field name made lowercase.
    idpar = models.ForeignKey(Participate, models.CASCADE, db_column='IDPar')  # Field name made lowercase.
    iduser = models.ForeignKey(RegisteredUser, models.CASCADE, db_column='IDUser')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'user_participated'
        unique_together = (('idpar', 'iduser'),)
