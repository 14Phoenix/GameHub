# Author: Mihajlo Blagojevic 0283/2021

from django.test import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

import GameHubApp.models as game_hub_models

from django.urls import reverse
from datetime import datetime


@tag('test_create_team')
class CreateTeamTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)
        self.time_sleep = 3

        # Test data
        self.forum_id = 5
        self.forum = game_hub_models.Forum.objects.get(idforum__exact=self.forum_id)

        # Create user
        self.registered_user_password = 'testPassword123$'
        self.registered_user = game_hub_models.RegisteredUser.objects.create_user(username='testUser',
            password=self.registered_user_password, email="test@email.com",
            aboutsection='Test about section.', status='ACT', dateregistered=datetime.now())

        # Sign In
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.registered_user.username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.registered_user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

    def tearDown(self):
        self.browser.close()

    def test_unsuccessful_create_team_name_not_inserted(self):
        # Test data
        team_name = ''
        team_description = 'some text about team'

        # Test execution
        self.browser.get(self.live_server_url + reverse('create_a_team', args=[self.forum_id]))

        self.insertDataIntoForm(team_name, team_description)
        form_create_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div[4]/button[1]')
        form_create_button.click()

        self.assertEqual(game_hub_models.Team.objects.filter(name=team_name).exists(), False)


    def test_unsuccessful_create_team_description_not_inserted(self):
        # Test data
        team_name = 'Team1'
        team_description = ''

        # Test execution
        self.browser.get(self.live_server_url + reverse('create_a_team', args=[self.forum_id]))

        self.insertDataIntoForm(team_name, team_description)
        form_create_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div[4]/button[1]')
        form_create_button.click()

        self.assertEqual(game_hub_models.Team.objects.filter(name=team_name).exists(), False)


    def test_cancelled_create_team(self):
        # Test data
        team_name = 'Team1'
        team_description = 'some text about team 65465'

        # Test execution
        self.browser.get(self.live_server_url + reverse('create_a_team', args=[self.forum_id]))

        self.insertDataIntoForm(team_name, team_description)
        form_cancel_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div[4]/button[2]')
        form_cancel_button.click()

        self.assertEqual(game_hub_models.Team.objects.filter(name=team_name).exists(), False)


    def test_successful_create_team(self):
        # Test data
        team_name = 'Team1'
        team_description = 'some text about team'

        # Test execution
        self.browser.get(self.live_server_url + reverse('create_a_team', args=[self.forum_id]))

        self.insertDataIntoForm(team_name, team_description)
        form_create_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div[4]/button[1]')
        form_create_button.click()

        self.assertEqual(game_hub_models.Team.objects.filter(name=team_name).exists(), True)


    def test_unsuccessful_create_team_already_exist_with_same_name(self):
        # Test data
        team_name = 'Team1'
        team_description = 'some text about team 65465'

        self.create_team_and_team_member()

        # Test execution
        self.browser.get(self.live_server_url + reverse('create_a_team', args=[self.forum_id]))

        self.insertDataIntoForm(team_name, team_description)
        form_create_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div[4]/button[1]')
        form_create_button.click()

        err_msg = self.browser.find_element(By.XPATH, '/html/body/div[3]/p')
        self.assertEqual(err_msg.text, 'There is a team with name "' + team_name + '" on this forum, try again!')


    def test_successful_create_team_with_leaving_old_team(self):
        # Test data
        team_name = 'Team321'
        team_description = 'some text about team 232'

        team2 = game_hub_models.Team(name='Team7676', numberofplayers=5, status='ACT', description='some text',
                                     idforum=self.forum, datecreated=datetime.now())
        team2.save()
        team_mem2 = game_hub_models.TeamMember(iduser=self.registered_user, idforum=self.forum, idteam=team2,
                                               isleader=True,
                                               datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem2.save()

        # Test execution
        # on forum page
        self.browser.get(self.live_server_url + reverse('forum', args=[self.forum_id]))

        create_team_button = self.browser.find_element(By.ID, 'create_team_button')
        self.browser.execute_script("arguments[0].click()", create_team_button)
        confirm_leave_team_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div/button[2]')
        confirm_leave_team_button.click()

        # on create team page
        self.browser.get(self.live_server_url + reverse('create_a_team', args=[self.forum_id]))
        self.insertDataIntoForm(team_name, team_description)
        form_create_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div[4]/button[1]')
        form_create_button.click()

        self.assertEqual(game_hub_models.Team.objects.filter(name=team_name).exists(), True)


    def test_cancelled_create_team_leaving_old_team(self):
        # Test data
        team_name = 'Team3214565'
        team_description = 'some text about team 232'

        team2 = game_hub_models.Team(name='Team7676', numberofplayers=5, status='ACT', description='some text',
                                     idforum=self.forum, datecreated=datetime.now())
        team2.save()
        team_mem2 = game_hub_models.TeamMember(iduser=self.registered_user, idforum=self.forum, idteam=team2,
                                               isleader=True,
                                               datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem2.save()

        # Test execution
        # on forum page
        forum_url = self.live_server_url + reverse('forum', args=[self.forum_id])
        self.browser.get(forum_url)

        create_team_button = self.browser.find_element(By.ID, 'create_team_button')
        self.browser.execute_script("arguments[0].click()", create_team_button)
        cancel_leave_team_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div/button[1]')
        cancel_leave_team_button.click()

        self.assertEqual(self.live_server_url + reverse('forum', args=[self.forum_id]), forum_url)
        self.assertEqual(game_hub_models.Team.objects.filter(name=team_name).exists(), False)


    def insertDataIntoForm(self, team_name, team_description):
        form_team_name = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div[1]/input')
        form_team_name.send_keys(team_name)
        form_team_description = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div[3]/textarea')
        form_team_description.send_keys(team_description)


    def create_team_and_team_member(self):
        team = game_hub_models.Team(name='Team1', numberofplayers=5, status='ACT', description='some text',
                                  idforum=self.forum, datecreated=datetime.now())
        team.save()

        new_user = game_hub_models.RegisteredUser(username='testUser2', password='testPassword123467$',
                                                email="test2@email.com", aboutsection='Test about section. 2',
                                                status='ACT', dateregistered=datetime.now())
        new_user.save()

        team_mem = game_hub_models.TeamMember(iduser=new_user, idforum=self.forum, idteam=team, isleader=True,
                                            datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem.save()

