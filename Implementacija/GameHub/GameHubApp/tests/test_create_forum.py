# Author: Tadija Goljic 0272/2021

import GameHubApp
import GameHubApp.models as GameHubModels
from os.path import abspath

from selenium import webdriver
from selenium.webdriver.common.by import By

from django.test import tag
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


@tag('tadija')
@tag('create_forum')
class CreateForumTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):

        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        self.admin_username = 'tadija'
        self.admin_password = 'oracle'

        self.forum_name = 'TestForum'
        self.forum_cover_image = abspath('../../Test/images/test_forum_cover_image.jpg')
        self.forum_banner_image = abspath('../../Test/images/test_forum_banner_image.jpg')
        self.forum_description = 'TestDescription'
        self.forum_num_of_players = '1,2,4,8'

        self.forums_before = [forum for forum in GameHubModels.Forum.objects.all()]

    def tearDown(self):
        self.browser.close()

    def test_create_forum(self):

        # sign in as admin
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.admin_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.admin_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # create forum
        self.browser.get(self.live_server_url + reverse('create_forum'))
        forum_name_field = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/form/input[2]')
        forum_name_field.send_keys(self.forum_name)
        forum_cover_image = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/form/input[3]')
        forum_cover_image.send_keys(self.forum_cover_image)
        forum_banner_image = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/form/input[4]')
        forum_banner_image.send_keys(self.forum_banner_image)
        forum_description = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/form/input[5]')
        forum_description.send_keys(self.forum_description)
        forum_num_of_players = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/form/input[6]')
        forum_num_of_players.send_keys(self.forum_num_of_players)
        create_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/form/input[7]')
        #create_button.click()
        self.browser.execute_script('arguments[0].click();', create_button)

        # check if forum is created
        try:
            forums_after = [forum for forum in GameHubModels.Forum.objects.all()]
            new_forum = [forum for forum in forums_after if forum not in self.forums_before][0]
            self.browser.get(self.live_server_url + reverse('forum', args=[new_forum.idforum]))
        except NoReverseMatch:
            self.fail()
