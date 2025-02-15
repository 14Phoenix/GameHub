# Author: Mihajlo Blagojevic 0283/2021
# Author: Tadija Goljic 0272/2021
# Author: Viktor Mitrovic 0296/2021
# Author: Nemanja Micanovic 0595/2021

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, tag

import GameHubApp.models as game_hub_models

from django.urls import reverse
from datetime import datetime
import json
from django.contrib.auth.hashers import make_password


@tag('test_views')
class UnitTest(TestCase):
    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        self.client = Client()

        self.admin = game_hub_models.RegisteredUser.objects.get(username='tadija')
        self.admin_password = 'oracle'

        self.reg_user = game_hub_models.RegisteredUser.objects.get(username='AquaLynx')
        self.reg_user_password = 'P@ssw0rd1!'

        self.forum = game_hub_models.Forum.objects.get(idforum=5)

    def test_sign_in_GET(self):
        response = self.client.get(reverse('sign_in'))
        self.assertEquals(response.status_code, 200)

    def test_register_GET(self):
        response = self.client.get(reverse('register'))
        self.assertEquals(response.status_code, 200)

    def test_forgot_password_GET(self):
        response = self.client.get(reverse('forgot_password'))
        self.assertEquals(response.status_code, 200)

    def test_user_profile_GET(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})

        response = self.client.get(reverse('user_profile', args=[self.admin.iduser]))
        self.assertEquals(response.status_code, 200)

    def test_reset_password_GET(self):
        response = self.client.get(reverse('reset_password', args=[1]))
        self.assertEquals(response.status_code, 200)

    def test_change_password_GET(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})

        response = self.client.get(reverse('change_password', args=[self.admin.iduser]))
        self.assertEquals(response.status_code, 200)

    def test_find_a_team_GET(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})

        response = self.client.get(reverse('find_a_team', args=[self.forum.idforum]))
        self.assertEquals(response.status_code, 200)

    def test_create_a_team_GET(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})

        response = self.client.get(reverse('create_a_team', args=[self.forum.idforum]))
        self.assertEquals(response.status_code, 200)

    def test_index_GET(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)

    def test_create_forum_GET(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})
        response = self.client.get(reverse('create_forum'))
        self.assertEquals(response.status_code, 200)

    def test_sign_in_POST1(self):
        data = {
            'username-field': self.admin.username,
            'password-field': self.admin_password
        }
        response = self.client.post(reverse('sign_in'), data=data)
        self.assertEquals(response.status_code, 302)

    def test_sign_in_POST2(self):
        data = {
            'username-field': self.admin.username,
            'password-field': ''
        }
        response = self.client.post(reverse('sign_in'), data=data)
        self.assertEquals(response.status_code, 200)

    def test_register_POST1(self):
        username_field = 'testUser378'
        data = {
            'email-field': 'test@example.net',
            'username-field': username_field,
            'password-field': 'testPassword167$',
            'password-again-field': 'testPassword167$',
            'description-field': 'some text'
        }
        response = self.client.post(reverse('register'), data=data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(game_hub_models.RegisteredUser.objects.filter(username=username_field).exists(), True)

    def test_register_POST2(self):
        username_field = 'testUser378565'
        data = {
            'email-field': 'test@example.net',
            'username-field': username_field,
            'password-field': '',
            'password-again-field': 'testPassword14523$',
            'description-field': 'some text'
        }
        response = self.client.post(reverse('register'), data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(game_hub_models.RegisteredUser.objects.filter(username=username_field).exists(), False)

    def test_forgot_password_POST(self):
        new_admin = game_hub_models.RegisteredUser.objects.create_user(username='testNewNewUser',
            password='testPassword6565$', email='test@example.com', aboutsection='Test about section.',
            status='ACT', dateregistered=datetime.now())
        new_admin_password = 'testPassword6565$'
        create_tour = game_hub_models.CreateTournamentUser(iduser=new_admin)
        create_tour.save()
        admin_user = game_hub_models.Admin(idadmin=create_tour)
        admin_user.save()

        data = {
            'email-field': new_admin.email,
        }
        response = self.client.post(reverse('forgot_password'), data=data)
        self.assertEquals(game_hub_models.ForgotPassword.objects.filter(iduser=new_admin.iduser).exists(), True)
        self.assertEquals(response.status_code, 302)

    def test_reset_password_POST(self):
        new_admin = game_hub_models.RegisteredUser.objects.create_user(username='testNewNewUser',
            password='testPassword6565$', email='test@example.com', aboutsection='Test about section.',
            status='ACT', dateregistered=datetime.now())
        new_admin_password = 'testPassword6565$'
        create_tour = game_hub_models.CreateTournamentUser(iduser=new_admin)
        create_tour.save()
        admin_user = game_hub_models.Admin(idadmin=create_tour)
        admin_user.save()

        new_user_pass = 'newOracle'
        data = {
            'password-field': new_user_pass,
            'password-again-field': new_user_pass
        }
        responseForgotPass = self.client.post(reverse('forgot_password'), data={'email-field': new_admin.email})
        forgot_password = game_hub_models.ForgotPassword.objects.get(iduser__exact=new_admin.iduser)
        response = self.client.post(reverse('reset_password', args=[forgot_password.resetkey]), data=data)
        self.assertEquals(response.status_code, 302)
        new_reg_user = game_hub_models.RegisteredUser.objects.get(username=new_admin.username)
        salt = new_reg_user.password.split('$')[2]
        hash_pass = make_password(new_user_pass, salt=salt)
        self.assertEqual(new_reg_user.password, hash_pass)

    def test_logout_user_POST(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})
        response = self.client.post(reverse('logout_user'))
        self.assertEquals(response.status_code, 302)

    def test_change_password_POST1(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})
        new_user_pass = '123'
        data = {
            'old-password-field': self.admin_password,
            'new-password-field': new_user_pass,
            'new-password-again-field': new_user_pass
        }
        response = self.client.post(reverse('change_password', args=[self.admin.iduser]), data=data)
        self.assertEquals(response.status_code, 302)
        new_reg_user = game_hub_models.RegisteredUser.objects.get(username=self.admin.username)
        salt = new_reg_user.password.split('$')[2]
        hash_pass = make_password(new_user_pass, salt=salt)
        self.assertEqual(new_reg_user.password, hash_pass)

    def test_change_password_POST2(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})
        data = {
            'old-password-field': self.admin_password,
            'new-password-field': '123',
            'new-password-again-field': '455'
        }
        response = self.client.post(reverse('change_password', args=[self.admin.iduser]), data=data)
        self.assertEquals(response.status_code, 200)

    def test_save_profile_changes_POST(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})
        new_section = 'new section'
        data = {
            'profile_picture': '',
            'profile_about_section': new_section,
        }
        response = self.client.post(reverse('save_profile_changes', args=[self.admin.iduser]), data=data)
        new_reg_user = game_hub_models.RegisteredUser.objects.get(username=self.admin.username)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(new_reg_user.aboutsection, new_section)

    def test_request_join_POST(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})

        team = game_hub_models.Team(name='Team1', numberofplayers=5, status='ACT', description='some text',
                                    idforum=self.forum, datecreated=datetime.now())
        team.save()

        new_user = game_hub_models.RegisteredUser.objects.get(username__exact='viktor')
        team_mem = game_hub_models.TeamMember(iduser=new_user, idforum=self.forum, idteam=team, isleader=True,
                                              datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem.save()

        response = self.client.post(reverse('request_join', args=[self.forum.idforum, team.idteam]))
        self.assertEquals(response.status_code, 302)
        self.assertEqual(game_hub_models.RequestToJoin.objects.filter(iduser=self.admin, idteam=team).exists(), True)

    def test_create_a_team_POST1(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})
        data = {
            'team-name-field': 'Team1',
            'team-description-field': 'some text',
            'team-num-of-players-field': '5'

        }
        response = self.client.post(reverse('create_a_team', args=[self.forum.idforum]), data=data)
        self.assertEquals(response.status_code, 302)

    def test_create_a_team_POST2(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})
        data = {
            'team-name-field': '',
            'team-description-field': 'some text',
            'team-num-of-players-field': '5'
        }
        response = self.client.post(reverse('create_a_team', args=[self.forum.idforum]), data=data)
        self.assertEquals(response.status_code, 200)

    def test_team_accept_join_team_through_notification(self):
        self.client.post(reverse('sign_in'),
                         data={'username-field': self.admin.username, 'password-field': self.admin_password})

        team = game_hub_models.Team(name='Team1', numberofplayers=5, status='ACT', description='some text',
                                    idforum=self.forum, datecreated=datetime.now())
        team.save()

        new_user = game_hub_models.RegisteredUser.objects.get(username__exact='viktor')
        new_user_pass = 'morpheus'
        team_mem = game_hub_models.TeamMember(iduser=new_user, idforum=self.forum, idteam=team, isleader=True,
                                              datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem.save()

        response = self.client.post(reverse('request_join', args=[self.forum.idforum, team.idteam]))
        team_notification = game_hub_models.TeamNotification.objects.get(idteam=team, iduser=self.admin)

        # changing to new_user
        self.client.post(reverse('logout_user'))
        self.client.post(reverse('sign_in'),
                         data={'username-field': new_user.username, 'password-field': new_user_pass})

        data = {
            "REQUEST_STATUS": 'ACCEPT'
        }
        json_data = json.dumps(data)

        response = self.client.post(reverse('team_request', args=[self.forum.idforum, team.idteam,
                                                                  self.admin.iduser, team_notification.idnot.idnot]),
                                    data=json_data, content_type='application/json')
        self.assertEquals(response.status_code, 200)
        json_response = response.json()
        self.assertEquals(json_response['JOIN_STATUS'], 'SUCCESS')
        self.assertEquals(game_hub_models.TeamMember.objects.filter(idteam=team,
                                                                    iduser=self.admin, idforum=self.forum).exists(),
                          True)

    def test_create_forum_POST1(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.reg_user.username,
                'password-field': self.reg_user_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': '',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1',

            }
        )
        self.assertEqual(response.status_code, 302)

    def test_create_forum_POST2(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': '',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1',

            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST3(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': '12',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST4(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': '',
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST5(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': '',
                'description': 'testtest',
                'possible_number_of_players': '1'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST6(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': '',
                'possible_number_of_players': '1'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST7(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': ''
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST8(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': 'kbdh'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST9(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'testtesttesttesttesttesttesttesttesttesttesttesttest',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1,3'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST10(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': '''100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001
                    01000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010
                    00100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001
                    00010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000
                    10001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100
                    01000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010
                    00100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001
                    00010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000
                    100010001000100010001000100010001000100010001000100010001000100''',
                'possible_number_of_players': '1,3'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST11(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'Fortnite',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1,3'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST12(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.webp',
                    content=open('../../Test/images/test.webp', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1,3'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST13(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.webp',
                    content=open('../../Test/images/test.webp', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1,3'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST14(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1,3,3'
            }
        )
        self.assertEquals(response.status_code, 200)

    def test_create_forum_POST15(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('create_forum'),
            data={
                'forum_name': 'test',
                'cover_image': SimpleUploadedFile(
                    name='cover_image.jpeg',
                    content=open('../../Test/images/test_forum_cover_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'banner_image': SimpleUploadedFile(
                    name='banner_image.jpeg',
                    content=open('../../Test/images/test_forum_banner_image.jpg', 'rb').read(),
                    content_type='image/jpg'
                ),
                'description': 'testtest',
                'possible_number_of_players': '1,3'
            }
        )
        self.assertEquals(response.status_code, 302)

    def test_delete_forum_POST1(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.reg_user.username,
                'password-field': self.reg_user_password
            }
        )
        response = self.client.post(
            reverse('delete_forum', args=[1])
        )
        self.assertEquals(response.status_code, 302)

    def test_delete_forum_POST2(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('delete_forum', args=[1])
        )
        self.assertEquals(response.status_code, 302)

    def test_promote_moderator_POST1(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.reg_user.username,
                'password-field': self.reg_user_password
            }
        )
        response = self.client.post(
            reverse('promote_moderator', args=[1]),
            data={
                'name_of_user': 'AquaLynx'
            }
        )
        self.assertEquals(response.status_code, 302)

    def test_promote_moderator_POST2(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.reg_user.username,
                'password-field': self.reg_user_password
            }
        )
        response = self.client.post(
            reverse('promote_moderator', args=[1]),
            data={
                'name_of_user': ''
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), 'You must specify a username')
        self.assertEquals(json_response.get('status'), 0)

    def test_promote_moderator_POST3(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.reg_user.username,
                'password-field': self.reg_user_password
            }
        )
        response = self.client.post(
            reverse('promote_moderator', args=[1]),
            data={
                'name_of_user': 'hellohellohellohellohello1'
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), 'Username is too long')
        self.assertEquals(json_response.get('status'), 0)

    def test_promote_moderator_POST4(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('promote_moderator', args=[1]),
            data={
                'name_of_user': 'viktor'
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), 'User viktor is Admin')
        self.assertEquals(json_response.get('status'), 0)

    def test_promote_moderator_POST5(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('promote_moderator', args=[7]),
            data={
                'name_of_user': self.reg_user.username
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), f'User {self.reg_user.username} is already moderator on this forum')
        self.assertEquals(json_response.get('status'), 0)

    def test_promote_moderator_POST6(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('promote_moderator', args=[7]),
            data={
                'name_of_user': 'fsbfbsbofiabof'
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), 'User fsbfbsbofiabof doesn\'t exist')
        self.assertEquals(json_response.get('status'), 0)

    def test_promote_moderator_POST7(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('promote_moderator', args=[1]),
            data={
                'name_of_user': self.reg_user.username
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), f'User {self.reg_user.username} has been added as a moderator to the forum')
        self.assertEquals(json_response.get('status'), 1)

    def test_remove_moderator_POST1(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.reg_user.username,
                'password-field': self.reg_user_password
            }
        )
        response = self.client.post(
            reverse('demote_moderator', args=[7]),
            data={
                'name_of_user': 'AquaLynx'
            }
        )
        self.assertEquals(response.status_code, 302)

    def test_remove_moderator_POST2(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('demote_moderator', args=[7]),
            data={
                'name_of_user': ''
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), 'You must specify a username')
        self.assertEquals(json_response.get('status'), 0)

    def test_remove_moderator_POST3(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('demote_moderator', args=[7]),
            data={
                'name_of_user': 'hellohellohellohellohello1'
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), 'Username is too long')
        self.assertEquals(json_response.get('status'), 0)

    def test_remove_moderator_POST4(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('demote_moderator', args=[7]),
            data={
                'name_of_user': 'viktor'
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), 'User viktor is Admin')
        self.assertEquals(json_response.get('status'), 0)

    def test_remove_moderator_POST5(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('demote_moderator', args=[7]),
            data={
                'name_of_user': 'sfjbsfgjkbfgj'
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), 'User sfjbsfgjkbfgj doesn\'t exist')
        self.assertEquals(json_response.get('status'), 0)

    def test_remove_moderator_POST6(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('demote_moderator', args=[1]),
            data={
                'name_of_user': self.reg_user.username
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), f'User {self.reg_user.username} is not a moderator on this forum')
        self.assertEquals(json_response.get('status'), 0)

    def test_remove_moderator_POST7(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('demote_moderator', args=[7]),
            data={
                'name_of_user': self.reg_user.username
            }
        )
        json_response = response.json()
        self.assertEquals(json_response.get('message'), f'User {self.reg_user.username} has been removed as a moderator on the forum')
        self.assertEquals(json_response.get('status'), 1)

    def test_team_GET1(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('team', args=[1, 1]),
        )
        self.assertEquals(response.status_code, 404)

    def test_team_GET2(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': self.admin.username,
                'password-field': self.admin_password
            }
        )
        response = self.client.post(
            reverse('team', args=[7, 1]),
        )
        self.assertEquals(response.status_code, 200)

    def test_list_tournaments_GET(self):
        response = self.client.get(reverse('list_tournaments', args=[7]))
        self.assertEqual(response.status_code, 200)

    def test_create_tournament_GET(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

        response = self.client.get(reverse('create_tournament', args=[7]))
        self.assertEqual(response.status_code, 200)

    def test_create_tournament_POST(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

        response = self.client.post(
            reverse('create_tournament', args=[7]),
            data={
                'tour_name': 'Unit Test Tournament',
                'tour_date': '2024-06-20',
                'tour_time': '12:00',
                'tour_players_per_team': '5 players',
                'tour_num_of_places': '16',
                'tour_format': 'Best of 3',
                'tour_value': '100',
                'tour_currency': '$'
            }
        )
        self.assertEqual(game_hub_models.Tournament.objects.filter(name='Unit Test Tournament').exists(), True)

    def test_tournament_GET(self):
        response = self.client.post(
            reverse('tournament', args=[7, 21])
        )
        self.assertEqual(response.status_code, 200)

    def test_tournament_join_POST(self):
        # Create a new tournament on forum idforum = 7
        forum_num_of_players_f_7 = game_hub_models.ForumNumOfPlayers.objects.get(idforumnumofplayers=8)

        tournament = game_hub_models.Tournament(
            name='Unit test tournament',
            startdate=datetime.now(),
            numberofplaces=16,
            format='Best of 1',
            idforumnumofplayers=forum_num_of_players_f_7,
            rewardvalue='100',
            rewardcurrency='$',
            datecreated=datetime.now(),
            status='NOT_STARTED',
            iduser=None
        )
        tournament.save()

        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

        self.client.post(
            reverse('tournament', args=[7, tournament.idtour]),
            data={
                'join': ''
            }
        )

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idteam=1,
            idtour=tournament.idtour
        ).exists(), True)

    def test_tournament_leave_POST(self):
        # Create a new tournament on forum idforum = 7
        forum_num_of_players_f_7 = game_hub_models.ForumNumOfPlayers.objects.get(idforumnumofplayers=8)

        tournament = game_hub_models.Tournament(
            name='Unit test tournament',
            startdate=datetime.now(),
            numberofplaces=16,
            format='Best of 1',
            idforumnumofplayers=forum_num_of_players_f_7,
            rewardvalue='100',
            rewardcurrency='$',
            datecreated=datetime.now(),
            status='NOT_STARTED',
            iduser=None
        )
        tournament.save()

        team = game_hub_models.Team.objects.get(idteam=1)
        game_hub_models.Participate(
            idteam=team,
            idtour=tournament,
            position=0,
            points=0
        ).save()

        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

        self.client.post(
            reverse('tournament', args=[7, tournament.idtour]),
            data={
                'leave': ''
            }
        )

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idteam=1,
            idtour=tournament.idtour
        ).exists(), False)

    def test_tournament_start_POST(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

        self.client.post(
            reverse('tournament', args=[7, 23]),
            data={
                'start': ''
            }
        )

        self.assertEqual(game_hub_models.Tournament.objects.get(idtour=23).status, 'IN_PROGRESS')

    def test_tournament_finish_POST(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

        self.client.post(
            reverse('tournament', args=[1, 1]),
            data={
                'finish': ''
            }
        )

        self.assertEqual(game_hub_models.Tournament.objects.get(idtour=1).status, 'FINISHED')

    def test_tournament_delete_POST(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

        self.client.post(
            reverse('tournament', args=[1, 1]),
            data={
                'delete': ''
            }
        )

        self.assertEqual(game_hub_models.Tournament.objects.filter(idtour=1).exists(), False)

    def test_tournament_kick_POST(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

        self.client.post(
            reverse('tournament', args=[1, 2]),
            data={
                'kick_74': ''
            }
        )

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idteam=74,
            idtour=2
        ).exists(), False)

    def test_tournament_update_points_POST(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

        response = self.client.post(
            reverse('tournament_update_points', args=[1, 1]),
            data={
                'teamName': 'Matrix',
                'pointsToAdd': 50
            },
            content_type='application/json'
        )

        json_response = response.json()

        for team_name, team_points in zip(json_response.get('teamNames'), json_response.get('teamPoints')):
            if team_name == 'Matrix':
                self.assertEqual(team_points, 50)

    def test_leave_a_team_POST(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'viktor',
                'password-field': 'morpheus'
            }
        )

        self.client.post(
            reverse('leave_a_team', args=[7])
        )

        self.assertEqual(game_hub_models.TeamMember.objects.filter(
            iduser=1,
            idforum=7
        ).exists(), False)

    def login_for_test(self):
        self.client.post(
            reverse('sign_in'),
            data={
                'username-field': 'nemanja',
                'password-field': 'trinity'
            }
        )

    def test_forum_GET(self):
        response = self.client.get(reverse('forum', args=[7]))
        self.assertEqual(response.status_code, 200)

    def test_follow_forum_POST(self):
        self.login_for_test()

        self.client.post(reverse('follow_forum', args=[1]))

        self.assertEqual(game_hub_models.Follow.objects.filter(iduser=3, idforum=1).exists(), True)

    def test_create_post_GET(self):
        self.login_for_test()
        response = self.client.get(reverse('create_post', args=[7]))
        self.assertEqual(response.status_code, 200)

    def test_create_post_POST(self):
        self.login_for_test()

        self.client.post(
            reverse('create_post', args=[7]),
            data={
                'title': 'Test post',
                'body': 'some body'
            }
        )

        self.assertEqual(game_hub_models.Post.objects.filter(title='Test post', body='some body', idforum=7, status='ACT').exists(), True)

    def test_post_GET(self):
        response = self.client.get(reverse('post', args=[7, 16]))
        self.assertEqual(response.status_code, 200)

    def test_like_post_POST(self):
        self.login_for_test()

        self.client.post(reverse('like_post', args=[7, 16]))

        self.assertEqual(game_hub_models.LikedPost.objects.filter(iduser=3, idpost=16).exists(), True)

    def test_delete_post_POST(self):
        self.login_for_test()

        self.client.post(reverse('delete_post', args=[7, 16]))

        self.assertEqual(game_hub_models.Post.objects.filter(idpost=16).first().status == 'DEL', True)

    def test_create_comment_POST(self):
        self.login_for_test()

        self.client.post(
            reverse('create_comment', args=[7, 16]),
            data={
                'body': 'Test comment'
            }
        )

        self.assertEqual(game_hub_models.Comment.objects.filter(body='Test comment', idpost=16, status='ACT').exists(), True)

    def test_like_comment_POST(self):
        self.login_for_test()

        self.client.post(reverse('like_comment', args=[7, 16, 16]))

        self.assertEqual(game_hub_models.LikedComment.objects.filter(iduser=3, idcom=16).exists(), True)

    def test_delete_comment_POST(self):
        self.login_for_test()

        self.client.post(reverse('delete_comment', args=[7, 16, 16]))

        self.assertEqual(game_hub_models.Comment.objects.filter(idcom=16).first().status == 'DEL', True)
