# Author: Viktor Mitrovic 0296/2021
import time

from django.test import TestCase, Client, SimpleTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import GameHubApp.models as game_hub_models

from django.urls import reverse
from datetime import datetime


class CreateTournamentTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        # Test data
        forum = game_hub_models.Forum.objects.get(idforum=7)
        # self.appUrl = self.live_server_url + reverse('create_tournament', args=[self.forum_id])

        # Create user
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username='testUser',
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

        # Create moderator on forum with id=7
        create_tournament_user = game_hub_models.CreateTournamentUser(iduser=registered_user)
        create_tournament_user.save()

        moderator = game_hub_models.Moderator(idmod=create_tournament_user)
        moderator.save()

        moderates = game_hub_models.Moderates(idforum=forum, idmod=moderator, datepromoted=datetime.now(), idadmin=None)
        moderates.save()

        # Sign In
        self.browser.get(self.live_server_url + reverse('sign_in'))

        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(registered_user.username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(registered_user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

    def tearDown(self):
        self.browser.close()

    def fill_out_create_tournament_form(self,
                                        tournament_name,
                                        tournament_date,
                                        tournament_time,
                                        tournament_players_per_team,
                                        tournament_num_of_places,
                                        tournament_format,
                                        tournament_reward_value,
                                        tournament_reward_currency
                                        ):

        self.browser.get(self.live_server_url + reverse('create_tournament', args=[7]))

        tournament_name_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div/div[2]/form/table/tbody/tr[1]/td[2]/div/input')
        tournament_name_element.send_keys(tournament_name)

        tournament_date_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div/div[2]/form/table/tbody/tr[2]/td[2]/div/input[1]')
        tournament_date_element.send_keys(tournament_date)

        tournament_time_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div/div[2]/form/table/tbody/tr[2]/td[2]/div/input[2]')
        tournament_time_element.send_keys(tournament_time)

        if tournament_players_per_team:
            tournament_players_per_team_element = self.browser.find_element(
                By.XPATH, '/html/body/div[3]/div/div[2]/form/table/tbody/tr[3]/td[2]/div/select')
            tournament_players_per_team_select = Select(tournament_players_per_team_element)
            tournament_players_per_team_select.select_by_visible_text(tournament_players_per_team)

        tournament_num_of_places_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div/div[2]/form/table/tbody/tr[4]/td[2]/div/input')
        tournament_num_of_places_element.send_keys(tournament_num_of_places)

        if tournament_format:
            tournament_format_element = self.browser.find_element(
                By.XPATH, '/html/body/div[3]/div/div[2]/form/table/tbody/tr[5]/td[2]/div/select')
            tournament_format_select = Select(tournament_format_element)
            tournament_format_select.select_by_visible_text(tournament_format)

        tournament_reward_value_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div/div[2]/form/table/tbody/tr[6]/td[2]/div/input[1]')
        tournament_reward_value_element.send_keys(tournament_reward_value)

        tournament_reward_currency_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div/div[2]/form/table/tbody/tr[6]/td[2]/div/input[2]')
        tournament_reward_currency_element.send_keys(tournament_reward_currency)

    def test_create_tournament(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), True)

    def test_create_tournament_no_name(self):
        self.fill_out_create_tournament_form('',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='').exists(), False)


    def test_create_tournament_no_date(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), False)

    def test_create_tournament_no_time(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '10-12-2024',
                                             '',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), False)

    def test_create_tournament_no_players_per_team(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '10-12-2024',
                                             '12:00AM',
                                             '',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), True)

    def test_create_tournament_no_num_of_places(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), False)

    def test_create_tournament_no_format(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             '',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), True)

    def test_create_tournament_no_reward_value(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), False)

    def test_create_tournament_no_reward_currency(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), False)

    def test_create_tournament_name_29_characters(self):
        self.fill_out_create_tournament_form('29CharacterNameThatIsTooLong1',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='29CharacterNameThatIsTooLong1').exists(), True)

    def test_create_tournament_name_30_characters(self):
        self.fill_out_create_tournament_form('30CharacterNameThatIsTooLong30',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(
            name='30CharacterNameThatIsTooLong30').exists(), True)

    def test_create_tournament_name_too_long(self):
        self.fill_out_create_tournament_form('31CharacterNameThatIsTooLong123',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(
            name='31CharacterNameThatIsTooLong123').exists(), False)

    def test_create_tournament_date_and_time_in_the_past(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '10-12-2023',
                                             '11:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        submit_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/button')
        submit_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), False)

    def test_create_tournament_cancel_pressed(self):
        self.fill_out_create_tournament_form('tournamentTestSelenium',
                                             '10-12-2024',
                                             '12:00AM',
                                             '5 players',
                                             '16',
                                             'Best of 3',
                                             '100',
                                             '$')

        cancel_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/form/a/button')
        cancel_button.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(name='tournamentTestSelenium').exists(), False)


class DeleteTournamentTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        # Test data
        forum = game_hub_models.Forum.objects.get(idforum=7)

        # Create user
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username='testUser',
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

        # Create moderator on forum with id=7
        create_tournament_user = game_hub_models.CreateTournamentUser(iduser=registered_user)
        create_tournament_user.save()

        moderator = game_hub_models.Moderator(idmod=create_tournament_user)
        moderator.save()

        moderates = game_hub_models.Moderates(idforum=forum, idmod=moderator, datepromoted=datetime.now(), idadmin=None)
        moderates.save()

        # Sign In
        self.browser.get(self.live_server_url + reverse('sign_in'))

        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(registered_user.username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(registered_user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

    def tearDown(self):
        self.browser.close()

    def test_delete_tournament(self):
        self.browser.get(self.live_server_url + reverse('tournament', args=[7, 23]))

        delete_tournament_element = self.browser.find_element(By.ID, 'deleteTour')
        self.browser.execute_script("arguments[0].click()", delete_tournament_element)

        confirm_delete_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[1]')
        confirm_delete_tournament_element.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(idtour=23).exists(), False)

    def test_delete_tournament_in_progress(self):
        self.browser.get(self.live_server_url + reverse('tournament', args=[7, 21]))

        delete_tournament_element = self.browser.find_element(By.ID, 'deleteTour')
        self.browser.execute_script("arguments[0].click()", delete_tournament_element)

        confirm_delete_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[1]')
        confirm_delete_tournament_element.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(idtour=21).exists(), False)

    def test_delete_tournament_cancel_pressed(self):
        self.browser.get(self.live_server_url + reverse('tournament', args=[7, 23]))

        delete_tournament_element = self.browser.find_element(By.ID, 'deleteTour')
        self.browser.execute_script("arguments[0].click()", delete_tournament_element)

        cancel_delete_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[2]')
        cancel_delete_tournament_element.click()

        self.assertEqual(game_hub_models.Tournament.objects.filter(idtour=23).exists(), True)


class EnterTournamentTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        # Create user
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username='testUser',
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

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

        # Create team
        forum_7 = game_hub_models.Forum.objects.get(idforum=7)
        self.registered_user_team = game_hub_models.Team(name='My test team',
                                                         numberofplayers=5,
                                                         status='ACT',
                                                         description='This is my team!',
                                                         idforum=forum_7,
                                                         datecreated=datetime.now())
        self.registered_user_team.save()

        game_hub_models.TeamMember(iduser=registered_user,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=True,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_1,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_2,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_3,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_4,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        # Create team where registered user is not the leader
        forum_4 = game_hub_models.Forum.objects.get(idforum=4)
        self.member_1_team = game_hub_models.Team(name='Member 1 team',
                                                  numberofplayers=5,
                                                  status='ACT',
                                                  description='Member team.',
                                                  idforum=forum_4,
                                                  datecreated=datetime.now())
        self.member_1_team.save()

        game_hub_models.TeamMember(iduser=registered_user,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_1,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=True,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_2,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_3,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_4,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        # Create NOT_STARTED tournament of forum 7
        forum_num_of_players_f_7 = game_hub_models.ForumNumOfPlayers.objects.get(idforumnumofplayers=8)
        self.tournament_not_started_has_space = game_hub_models.Tournament(name='Selenium test tournament',
                                                                           startdate=datetime.now(),
                                                                           numberofplaces=16,
                                                                           format='Best of 1',
                                                                           idforumnumofplayers=forum_num_of_players_f_7,
                                                                           rewardvalue='100',
                                                                           rewardcurrency='$',
                                                                           datecreated=datetime.now(),
                                                                           status='NOT_STARTED',
                                                                           iduser=None)
        self.tournament_not_started_has_space.save()

        # Create NOT_STARTED tournament of forum 4
        forum_num_of_players_f_4 = game_hub_models.ForumNumOfPlayers.objects.get(idforumnumofplayers=5)
        self.tournament_not_started_has_space_not_leader = game_hub_models.Tournament(
            name='Selenium valorant tournament',
            startdate=datetime.now(),
            numberofplaces=16,
            format='Best of 1',
            idforumnumofplayers=forum_num_of_players_f_4,
            rewardvalue='100',
            rewardcurrency='$',
            datecreated=datetime.now(),
            status='NOT_STARTED',
            iduser=None
        )
        self.tournament_not_started_has_space_not_leader.save()

        # Sign In
        self.browser.get(self.live_server_url + reverse('sign_in'))

        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(registered_user.username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(registered_user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

    def tearDown(self):
        self.browser.close()

    def test_enter_tournament(self):
        tournament_path = reverse('tournament', args=[
            self.tournament_not_started_has_space.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started_has_space.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        join_tournament_element = self.browser.find_element(By.ID, 'joinTour')
        self.browser.execute_script('arguments[0].click()', join_tournament_element)

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idtour=self.tournament_not_started_has_space.idtour,
            idteam=self.registered_user_team.idteam
        ).exists(), True)

    def test_enter_tournament_not_started_no_free_places(self):
        tournament_path = reverse('tournament', args=[7, 23])
        self.browser.get(self.live_server_url + tournament_path)

        join_tournament_element = self.browser.find_element(By.ID, 'joinTour')
        self.browser.execute_script('arguments[0].click()', join_tournament_element)

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idtour=23,
            idteam=self.registered_user_team.idteam
        ).exists(), False)

    def test_enter_tournament_not_started_not_team_leader(self):
        tournament_path = reverse('tournament', args=[
            self.tournament_not_started_has_space_not_leader.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started_has_space_not_leader.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        join_tournament_element = self.browser.find_element(By.ID, 'joinTour')
        self.browser.execute_script('arguments[0].click()', join_tournament_element)

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idtour=self.tournament_not_started_has_space_not_leader.idtour,
            idteam=self.member_1_team.idteam
        ).exists(), False)

    def test_enter_tournament_user_not_in_a_team(self):
        tournament_path = reverse('tournament', args=[
            self.tournament_not_started_has_space_not_leader.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started_has_space_not_leader.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        join_tournament_element = self.browser.find_element(By.ID, 'joinTour')
        self.browser.execute_script('arguments[0].click()', join_tournament_element)

        error_msg_element = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/form/div[1]/p[1]')

        self.assertEqual(error_msg_element.text, 'You are not team leader!')


class LeaveTournamentTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        # Create user
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username='testUser',
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

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

        # Create team
        forum_7 = game_hub_models.Forum.objects.get(idforum=7)
        self.registered_user_team = game_hub_models.Team(name='My test team',
                                                         numberofplayers=5,
                                                         status='ACT',
                                                         description='This is my team!',
                                                         idforum=forum_7,
                                                         datecreated=datetime.now())
        self.registered_user_team.save()

        game_hub_models.TeamMember(iduser=registered_user,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=True,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_1,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_2,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_3,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_4,
                                   idforum=forum_7,
                                   idteam=self.registered_user_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        # Create team where registered user is not the leader
        forum_4 = game_hub_models.Forum.objects.get(idforum=4)
        self.member_1_team = game_hub_models.Team(name='Member 1 team',
                                                  numberofplayers=5,
                                                  status='ACT',
                                                  description='Member team.',
                                                  idforum=forum_4,
                                                  datecreated=datetime.now())
        self.member_1_team.save()

        game_hub_models.TeamMember(iduser=registered_user,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_1,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=True,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_2,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_3,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        game_hub_models.TeamMember(iduser=member_4,
                                   idforum=forum_4,
                                   idteam=self.member_1_team,
                                   isleader=False,
                                   datejoined=datetime.now(),
                                   lastmsgreaddate=datetime.now()).save()

        # Create NOT_STARTED tournament of forum 7
        forum_num_of_players_f_7 = game_hub_models.ForumNumOfPlayers.objects.get(idforumnumofplayers=8)
        self.tournament_not_started_has_space = game_hub_models.Tournament(name='Selenium test tournament',
                                                                           startdate=datetime.now(),
                                                                           numberofplaces=16,
                                                                           format='Best of 1',
                                                                           idforumnumofplayers=forum_num_of_players_f_7,
                                                                           rewardvalue='100',
                                                                           rewardcurrency='$',
                                                                           datecreated=datetime.now(),
                                                                           status='NOT_STARTED',
                                                                           iduser=None)
        self.tournament_not_started_has_space.save()

        # Create NOT_STARTED tournament of forum 4
        forum_num_of_players_f_4 = game_hub_models.ForumNumOfPlayers.objects.get(idforumnumofplayers=5)
        self.tournament_not_started_has_space_not_leader = game_hub_models.Tournament(
            name='Selenium valorant tournament',
            startdate=datetime.now(),
            numberofplaces=16,
            format='Best of 1',
            idforumnumofplayers=forum_num_of_players_f_4,
            rewardvalue='100',
            rewardcurrency='$',
            datecreated=datetime.now(),
            status='NOT_STARTED',
            iduser=None
        )
        self.tournament_not_started_has_space_not_leader.save()

        # Sign In
        self.browser.get(self.live_server_url + reverse('sign_in'))

        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(registered_user.username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(registered_user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

    def tearDown(self):
        self.browser.close()

    def test_leave_tournament(self):
        game_hub_models.Participate(idteam=self.registered_user_team,
                                    idtour=self.tournament_not_started_has_space,
                                    position=0,
                                    points=0).save()

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started_has_space.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started_has_space.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        join_tournament_element = self.browser.find_element(By.ID, 'leaveTour')
        self.browser.execute_script('arguments[0].click()', join_tournament_element)

        confirm_leave_element = self.browser.find_element(By.XPATH, '//*[@id="tour_event_submit_button"]')
        self.browser.execute_script('arguments[0].click()', confirm_leave_element)

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idtour=self.tournament_not_started_has_space.idtour,
            idteam=self.registered_user_team.idteam
        ).exists(), False)

    def test_leave_tournament_started(self):
        game_hub_models.Participate(idteam=self.registered_user_team,
                                    idtour=self.tournament_not_started_has_space,
                                    position=0,
                                    points=0).save()

        self.tournament_not_started_has_space.status = 'IN_PROGRESS'
        self.tournament_not_started_has_space.save()

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started_has_space.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started_has_space.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        join_tournament_element = self.browser.find_element(By.ID, 'leaveTour')
        self.browser.execute_script('arguments[0].click()', join_tournament_element)

        confirm_leave_element = self.browser.find_element(By.XPATH, '//*[@id="tour_event_submit_button"]')
        self.browser.execute_script('arguments[0].click()', confirm_leave_element)

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idtour=self.tournament_not_started_has_space.idtour,
            idteam=self.registered_user_team.idteam
        ).exists(), True)

    def test_leave_tournament_not_team_leader(self):
        game_hub_models.Participate(idteam=self.member_1_team,
                                    idtour=self.tournament_not_started_has_space_not_leader,
                                    position=0,
                                    points=0).save()

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started_has_space_not_leader.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started_has_space_not_leader.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        join_tournament_element = self.browser.find_element(By.ID, 'leaveTour')
        self.browser.execute_script('arguments[0].click()', join_tournament_element)

        confirm_leave_element = self.browser.find_element(By.XPATH, '//*[@id="tour_event_submit_button"]')
        self.browser.execute_script('arguments[0].click()', confirm_leave_element)

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idtour=self.tournament_not_started_has_space_not_leader.idtour,
            idteam=self.member_1_team.idteam
        ).exists(), True)

    def test_leave_tournament_cancel_pressed(self):
        game_hub_models.Participate(idteam=self.registered_user_team,
                                    idtour=self.tournament_not_started_has_space,
                                    position=0,
                                    points=0).save()

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started_has_space.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started_has_space.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        join_tournament_element = self.browser.find_element(By.ID, 'leaveTour')
        self.browser.execute_script('arguments[0].click()', join_tournament_element)

        cancel_leave_element = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[2]')
        self.browser.execute_script('arguments[0].click()', cancel_leave_element)

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idtour=self.tournament_not_started_has_space.idtour,
            idteam=self.registered_user_team.idteam
        ).exists(), True)


class KickTeamFromTournamentTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        self.tournament_not_started = game_hub_models.Tournament.objects.get(idtour=2)
        self.team_to_kick = game_hub_models.Team.objects.get(idteam=74)

    def tearDown(self):
        self.browser.close()

    def log_in(self, username, password):
        self.browser.get(self.live_server_url + reverse('sign_in'))

        username_element = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username_element.send_keys(username)
        password_element = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password_element.send_keys(password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

    def test_kick_team_from_tournament(self):
        registered_user_username = 'testUser'
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username=registered_user_username,
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

        create_tournament_user = game_hub_models.CreateTournamentUser(iduser=registered_user)
        create_tournament_user.save()

        admin = game_hub_models.Admin(idadmin=create_tournament_user)
        admin.save()

        self.log_in(registered_user_username, registered_user_password)

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        kick_team_element = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/form/p[4]/button')
        self.browser.execute_script('arguments[0].click()', kick_team_element)

        confirm_kick_team_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[1]')
        self.browser.execute_script('arguments[0].click()', confirm_kick_team_element)

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idteam=self.team_to_kick.idteam,
            idtour=self.tournament_not_started.idtour
        ).exists(), False)

    def test_kick_team_from_tournament_cancel_pressed(self):
        registered_user_username = 'testUser'
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username=registered_user_username,
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

        create_tournament_user = game_hub_models.CreateTournamentUser(iduser=registered_user)
        create_tournament_user.save()

        admin = game_hub_models.Admin(idadmin=create_tournament_user)
        admin.save()

        self.log_in(registered_user_username, registered_user_password)

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        kick_team_element = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/form/p[4]/button')
        self.browser.execute_script('arguments[0].click()', kick_team_element)

        cancel_kick_team_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[2]')
        self.browser.execute_script('arguments[0].click()', cancel_kick_team_element)

        self.assertEqual(game_hub_models.Participate.objects.filter(
            idteam=self.team_to_kick.idteam,
            idtour=self.tournament_not_started.idtour
        ).exists(), True)


class RunTournamentTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        self.tournament_not_started = game_hub_models.Tournament.objects.get(idtour=2)

    def tearDown(self):
        self.browser.close()

    def log_in(self, username, password):
        self.browser.get(self.live_server_url + reverse('sign_in'))

        username_element = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username_element.send_keys(username)
        password_element = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password_element.send_keys(password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

    def test_start_tournament(self):
        registered_user_username = 'testUser'
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username=registered_user_username,
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

        create_tournament_user = game_hub_models.CreateTournamentUser(iduser=registered_user)
        create_tournament_user.save()

        admin = game_hub_models.Admin(idadmin=create_tournament_user)
        admin.save()

        self.log_in(registered_user_username, registered_user_password)

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        start_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[1]/div[1]/form/div[2]/button[1]')
        self.browser.execute_script('arguments[0].click()', start_tournament_element)

        confirm_start_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[1]')
        self.browser.execute_script('arguments[0].click()', confirm_start_tournament_element)

        test_tournament = game_hub_models.Tournament.objects.get(idtour=self.tournament_not_started.idtour)
        self.assertEqual(test_tournament.status, 'IN_PROGRESS')

    def test_start_tournament_cancel_pressed(self):
        registered_user_username = 'testUser'
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username=registered_user_username,
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

        create_tournament_user = game_hub_models.CreateTournamentUser(iduser=registered_user)
        create_tournament_user.save()

        admin = game_hub_models.Admin(idadmin=create_tournament_user)
        admin.save()

        self.log_in(registered_user_username, registered_user_password)

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        start_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[1]/div[1]/form/div[2]/button[1]')
        self.browser.execute_script('arguments[0].click()', start_tournament_element)

        cancel_start_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[2]')
        self.browser.execute_script('arguments[0].click()', cancel_start_tournament_element)

        test_tournament = game_hub_models.Tournament.objects.get(idtour=self.tournament_not_started.idtour)
        self.assertEqual(test_tournament.status, 'NOT_STARTED')

    def test_end_tournament(self):
        registered_user_username = 'testUser'
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username=registered_user_username,
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

        create_tournament_user = game_hub_models.CreateTournamentUser(iduser=registered_user)
        create_tournament_user.save()

        admin = game_hub_models.Admin(idadmin=create_tournament_user)
        admin.save()

        self.log_in(registered_user_username, registered_user_password)

        self.tournament_not_started.status = "IN_PROGRESS"
        self.tournament_not_started.save()

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        end_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[1]/div[1]/form/div[2]/button[2]')
        self.browser.execute_script('arguments[0].click()', end_tournament_element)

        confirm_end_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[1]'
        )
        self.browser.execute_script('arguments[0].click()', confirm_end_tournament_element)

        test_tournament = game_hub_models.Tournament.objects.get(idtour=self.tournament_not_started.idtour)
        self.assertEqual(test_tournament.status, 'FINISHED')

    def test_end_tournament_cancel_pressed(self):
        registered_user_username = 'testUser'
        registered_user_password = 'testPassword123$'
        registered_user = game_hub_models.RegisteredUser.objects.create_user(username=registered_user_username,
                                                                             password=registered_user_password,
                                                                             email="test@email.com",
                                                                             aboutsection='Test about section.',
                                                                             status='ACT',
                                                                             dateregistered=datetime.now())

        create_tournament_user = game_hub_models.CreateTournamentUser(iduser=registered_user)
        create_tournament_user.save()

        admin = game_hub_models.Admin(idadmin=create_tournament_user)
        admin.save()

        self.log_in(registered_user_username, registered_user_password)

        self.tournament_not_started.status = "IN_PROGRESS"
        self.tournament_not_started.save()

        tournament_path = reverse('tournament', args=[
            self.tournament_not_started.idforumnumofplayers.idforum.idforum,
            self.tournament_not_started.idtour
        ])
        self.browser.get(self.live_server_url + tournament_path)

        end_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[1]/div[1]/form/div[2]/button[2]')
        self.browser.execute_script('arguments[0].click()', end_tournament_element)

        cancel_end_tournament_element = self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[3]/div/form/div/button[2]'
        )
        self.browser.execute_script('arguments[0].click()', cancel_end_tournament_element)

        test_tournament = game_hub_models.Tournament.objects.get(idtour=self.tournament_not_started.idtour)
        self.assertEqual(test_tournament.status, 'IN_PROGRESS')
