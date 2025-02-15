# Author: Mihajlo Blagojevic 0283/2021

from django.test import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

import GameHubApp.models as game_hub_models

from django.urls import reverse
from datetime import datetime
import time


@tag('test_join_team')
class JoinTeamTest(StaticLiveServerTestCase):
    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)
        self.time_sleep = 4
        self.short_sleep = 1

        # Test data
        self.forum_id = 5
        self.forum = game_hub_models.Forum.objects.get(idforum__exact=self.forum_id)

        self.sec_username = 'testUser2'
        self.sec_password = 'testPassword123467$'

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

    def test_successful_join_team(self):
        # Test data
        team = self.create_team_and_team_member()

        # Test execution
        self.browser.get(self.live_server_url + reverse('find_a_team', args=[self.forum_id]))
        join_team_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/div/div/div[4]/button')
        join_team_button.click()

        # Changing to the leader of new team
        self.change_registered_user(self.sec_username, self.sec_password)
        self.browser.get(self.live_server_url + reverse('index', args=[]))
        self.leader_notf_acc_reg_new_member(True)

        self.assertEqual(game_hub_models.RequestToJoin.objects.filter(iduser=self.registered_user, idteam=team).exists(), False)
        self.assertEqual(game_hub_models.TeamMember.objects.filter(iduser=self.registered_user, idteam=team).exists(),True)


    def test_successful_join_team_already_member_of_other_team(self):
        # Test data
        team = self.create_team_and_team_member()

        team2 = game_hub_models.Team(name='Team123', numberofplayers=5, status='ACT', description='some text',
                                    idforum=self.forum, datecreated=datetime.now())
        team2.save()
        team_mem2 = game_hub_models.TeamMember(iduser=self.registered_user, idforum=self.forum, idteam=team2, isleader=True,
                                              datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem2.save()

        # Test execution
        self.browser.get(self.live_server_url + reverse('find_a_team', args=[self.forum_id]))
        join_team_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/div/div/div[4]/button')
        join_team_button.click()
        confirm_leave_team_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/form/div/button[2]')
        confirm_leave_team_button.click()

        self.browser.get(self.live_server_url + reverse('find_a_team', args=[self.forum_id]))
        join_team_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/div/div/div[4]/button')
        join_team_button.click()

        # Changing to the leader of new team
        self.change_registered_user(self.sec_username, self.sec_password)
        self.browser.get(self.live_server_url + reverse('index', args=[]))
        self.leader_notf_acc_reg_new_member(True)

        self.assertEqual(game_hub_models.RequestToJoin.objects.filter(iduser=self.registered_user, idteam=team).exists(), False)
        self.assertEqual(game_hub_models.TeamMember.objects.filter(iduser=self.registered_user, idteam=team).exists(),True)


    def test_cancelled_join_team_already_member_of_other_team(self):
        # Test data
        team = self.create_team_and_team_member()

        # Test execution
        team2 = game_hub_models.Team(name='Team123', numberofplayers=5, status='ACT', description='some text',
                                     idforum=self.forum, datecreated=datetime.now())
        team2.save()
        team_mem2 = game_hub_models.TeamMember(iduser=self.registered_user, idforum=self.forum, idteam=team2,
                                               isleader=True, datejoined=datetime.now(),
                                               lastmsgreaddate=datetime.now())
        team_mem2.save()

        # Test execution
        find_team_url = self.live_server_url + reverse('find_a_team', args=[self.forum_id])
        self.browser.get(find_team_url)

        join_team_button = self.browser.find_element(By.XPATH,'/html/body/div[3]/div[1]/div[1]/div/div/div[4]/button')
        join_team_button.click()
        cancel_leave_team_button = self.browser.find_element(By.XPATH,'/html/body/div[3]/div[2]/div/form/div/button[1]')
        cancel_leave_team_button.click()

        self.assertEqual(game_hub_models.RequestToJoin.objects.filter(iduser=self.registered_user, idteam=team).exists(),False)


    def test_unsuccessful_join_team_rejected_join_request(self):
        # Test data
        team = self.create_team_and_team_member()

        # Test execution
        self.browser.get(self.live_server_url + reverse('find_a_team', args=[self.forum_id]))
        join_team_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/div/div/div[4]/button')
        join_team_button.click()
        self.assertEqual(game_hub_models.RequestToJoin.objects.filter(iduser=self.registered_user, idteam=team).exists(),  True)

        # Changing to the leader of new team
        self.change_registered_user(self.sec_username, self.sec_password)
        self.browser.get(self.live_server_url + reverse('index', args=[]))

        self.leader_notf_acc_reg_new_member(False)
        self.assertEqual(game_hub_models.RequestToJoin.objects.filter(iduser=self.registered_user, idteam=team).exists(), False)
        self.assertEqual(game_hub_models.TeamMember.objects.filter(iduser=self.registered_user, idteam=team).exists(), False)


    def test_unsuccessful_join_team_too_many_members(self):
        # Test data
        team = self.create_team_and_team_member()
        new_user2 = game_hub_models.RegisteredUser.objects.create_user(username='testUser3',
            password='testPassword111$', email="test3@email.com",aboutsection='Test about section. 3',
            status='ACT', dateregistered=datetime.now())
        new_user3 = game_hub_models.RegisteredUser.objects.create_user(username='testUser4',
            password='testPassword222$', email="test4@email.com",aboutsection='Test about section. 4',
            status='ACT', dateregistered=datetime.now())
        new_user4 = game_hub_models.RegisteredUser.objects.create_user(username='testUser5',
            password='testPassword333$', email="test5@email.com", aboutsection='Test about section. 5',
            status='ACT', dateregistered=datetime.now())
        new_user5 = game_hub_models.RegisteredUser.objects.create_user(username='testUser6',
            password='testPassword444$', email="test6@email.com", aboutsection='Test about section. 6',
            status='ACT', dateregistered=datetime.now())

        team_mem2 = game_hub_models.TeamMember(iduser=new_user2, idforum=self.forum, idteam=team, isleader=False,
                                              datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem2.save()
        team_mem3 = game_hub_models.TeamMember(iduser=new_user3, idforum=self.forum, idteam=team, isleader=False,
                                               datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem3.save()
        team_mem4 = game_hub_models.TeamMember(iduser=new_user4, idforum=self.forum, idteam=team, isleader=False,
                                               datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem4.save()
        team_mem5 = game_hub_models.TeamMember(iduser=new_user5, idforum=self.forum, idteam=team, isleader=False,
                                               datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem5.save()

        # Test execution
        self.browser.get(self.live_server_url + reverse('find_a_team', args=[self.forum_id]))
        join_team_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/div/div/div[4]/button')
        join_team_button.click()

        # Changing to the leader of new team
        self.change_registered_user(self.sec_username, self.sec_password)
        self.browser.get(self.live_server_url + reverse('index', args=[]))
        self.leader_notf_acc_reg_new_member(True)

        self.assertEqual(game_hub_models.RequestToJoin.objects.filter(iduser=self.registered_user, idteam=team).exists(), False)
        self.assertEqual(game_hub_models.TeamMember.objects.filter(iduser=self.registered_user, idteam=team).exists(),False)

    def create_team_and_team_member(self):
        team = game_hub_models.Team(name='Team1', numberofplayers=5, status='ACT', description='some text',
                                    idforum=self.forum, datecreated=datetime.now())
        team.save()

        new_user = game_hub_models.RegisteredUser.objects.create_user(username=self.sec_username, password=self.sec_password,
                                                  email="test2@email.com", aboutsection='Test about section. 2',
                                                  status='ACT', dateregistered=datetime.now())

        team_mem = game_hub_models.TeamMember(iduser=new_user, idforum=self.forum, idteam=team, isleader=True,
                                              datejoined=datetime.now(), lastmsgreaddate=datetime.now())
        team_mem.save()

        return team


    def change_registered_user(self, usr_username, usr_password):
        self.browser.get(self.live_server_url + reverse('logout_user'))
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(usr_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(usr_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()


    # Leader of team accepts(True) or rejects(False) request of a new member
    def leader_notf_acc_reg_new_member(self, accept_new_mem):
        notf_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/nav/ul/li[1]/button')
        notf_button.click()
        notf_button_2 = self.browser.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/button[2]')
        notf_button_2.click()
        if accept_new_mem:
            accept_join_team = self.browser.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/button[1]')
            accept_join_team.click()
        else:
            reject_join_team = self.browser.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/button[2]')
            reject_join_team.click()
        time.sleep(self.short_sleep)