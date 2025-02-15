# Author: Nemanja Mićanović 0595/2021
# Author: Mihajlo Blagojevic 0283/2021
# Author: Viktor Mitrovic 0296/2021
# Author: Tadija Goljic 0272/2021

from django.urls import path
from .views import *


urlpatterns = [
    path('sign-in', sign_in, name='sign_in'),
    path('register', register, name='register'),
    path('forgot-password', forgot_password, name='forgot_password'),
    path('user-profile/<int:id_user>', user_profile, name='user_profile'),
    path('reset-password/<str:id_reset>', reset_password, name='reset_password'),
    path('delete-profile/<int:id_user>', delete_profile, name='delete_profile'),
    path('logout-user', logout_user, name='logout_user'),
    path('change-password/<int:id_user>', change_password, name='change_password'),
    path('save-profile-changes/<int:id_user>', save_profile_changes, name='save_profile_changes'),

    path('', index, name="index"),
    path('create-forum', create_forum, name="create_forum"),

    path('forum/<int:id_forum>', forum, name="forum"),
    path('forum/<int:id_forum>/follow', follow_forum, name="follow_forum"),
    path('forum/<int:id_forum>/delete-forum', delete_forum, name="delete_forum"),
    path('forum/<int:id_forum>/promote-moderator', promote_moderator, name='promote_moderator'),
    path('forum/<int:id_forum>/demote-moderator', demote_moderator, name='demote_moderator'),
    path('forum/<int:id_forum>/create-post', create_post, name='create_post'),
    path('forum/<int:id_forum>/post/<int:id_post>', post, name="post"),
    path('forum/<int:id_forum>/post/<int:id_post>/like', like_post, name='like_post'),
    path('forum/<int:id_forum>/post/<int:id_post>/delete', delete_post, name='delete_post'),
    path('forum/<int:id_forum>/post/<int:id_post>/create-comment', create_comment, name="create_comment"),

    path("forum/<int:id_forum>/post/<int:id_post>/comment/<int:id_comment>/like", like_comment, name="like_comment"),
    path("forum/<int:id_forum>/post/<int:id_post>/comment/<int:id_comment>/delete", delete_comment, name="delete_comment"),

    path('forum/<int:id_forum>/team/<int:id_team>', team, name="team"),
    path('forum/<int:id_forum>/find-a-team', find_a_team, name='find_a_team'),
    path('forum/<int:id_forum>/team/<int:id_team>/request-join', request_join, name='request_join'),
    path('forum/<int:id_forum>/create-a-team', create_a_team, name='create_a_team'),
    path('forum/<int:id_forum>/leave-a-team', leave_a_team, name='leave_a_team'),
    path('forum/<int:id_forum>/team/<int:id_team>/request/<int:id_user>/notification/<int:id_not>', team_request, name='team_request'),

    path('forum/<int:id_forum>/list-tournaments', list_tournaments, name="list_tournaments"),
    path('forum/<int:id_forum>/list-tournaments/create-tournament', create_tournament, name="create_tournament"),
    path('forum/<int:id_forum>/list-tournaments/tournament/<int:id_tour>', tournament, name="tournament"),
    path('forum/<int:id_forum>/list-tournaments/tournament/<int:id_tour>/tournament-update-points', tournament_update_points, name="tournament_update_points"),
]
