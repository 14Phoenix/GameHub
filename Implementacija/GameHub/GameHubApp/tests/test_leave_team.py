# Author: Viktor Mitrovic 0296/2021


from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import GameHubApp.models as game_hub_models

from django.urls import reverse
from datetime import datetime


class LeaveTeamTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        # Test data

        # Create user
        registered_user_password = 'testPassword123$'
        self.registered_user = game_hub_models.RegisteredUser.objects.create_user(username='testUser',
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

        # Create team
        self.forum_7 = game_hub_models.Forum.objects.get(idforum=7)
        self.registered_user_team = game_hub_models.Team(name='My test team',
                                                         numberofplayers=5,
                                                         status='ACT',
                                                         description='This is my team!',
                                                         idforum=self.forum_7,
                                                         datecreated=datetime.now())
        self.registered_user_team.save()

        game_hub_models.TeamMember(iduser=self.registered_user,
                                   idforum=self.forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=True,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        # Sign In
        self.browser.get(self.live_server_url + reverse('sign_in'))

        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.registered_user.username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(registered_user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

    def tearDown(self):
        self.browser.close()

    def test_leave_team(self):
        # Create team members
        member_1 = game_hub_models.RegisteredUser.objects.create_user(username='member1',
                                                                      password='Password123',
                                                                      email='member1@email.com',
                                                                      aboutsection='Member about section.',
                                                                      status='ACT',
                                                                      dateregistered=datetime.now())
        member_1.save()

        member_2 = game_hub_models.RegisteredUser.objects.create_user(username='member2',
                                                                      password='Password123',
                                                                      email='member2@email.com',
                                                                      aboutsection='Member about section.',
                                                                      status='ACT',
                                                                      dateregistered=datetime.now())
        member_2.save()

        member_3 = game_hub_models.RegisteredUser.objects.create_user(username='member3',
                                                                      password='Password123',
                                                                      email='member3@email.com',
                                                                      aboutsection='Member about section.',
                                                                      status='ACT',
                                                                      dateregistered=datetime.now())
        member_3.save()

        member_4 = game_hub_models.RegisteredUser.objects.create_user(username='member4',
                                                                      password='Password123',
                                                                      email='member4@email.com',
                                                                      aboutsection='Member about section.',
                                                                      status='ACT',
                                                                      dateregistered=datetime.now())
        member_4.save()

        game_hub_models.TeamMember(iduser=member_1,
                                   idforum=self.forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_2,
                                   idforum=self.forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_3,
                                   idforum=self.forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_4,
                                   idforum=self.forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        self.browser.get(self.live_server_url + reverse('team', args=[
            self.registered_user_team.idforum.idforum,
            self.registered_user_team.idteam
        ]))

        leave_team_element = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div/div[2]/form/button')
        self.browser.execute_script('arguments[0].click()', leave_team_element)

        self.assertEqual(game_hub_models.TeamMember.objects.filter(
            iduser=self.registered_user.iduser,
            idteam=self.registered_user_team.idteam
        ).exists(), False)

    def test_leave_team_last_member(self):
        self.browser.get(self.live_server_url + reverse('team', args=[
            self.registered_user_team.idforum.idforum,
            self.registered_user_team.idteam
        ]))

        leave_team_element = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div/div[2]/form/button')
        self.browser.execute_script('arguments[0].click()', leave_team_element)

        self.assertEqual(game_hub_models.Team.objects.get(
            idteam=self.registered_user_team.idteam
        ).status, 'DEL')
