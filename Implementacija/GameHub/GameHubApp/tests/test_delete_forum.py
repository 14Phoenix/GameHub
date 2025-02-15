# Author: Tadija Goljic 0272/2021

import GameHubApp
import GameHubApp.models as GameHubModels

from selenium import webdriver
from selenium.webdriver.common.by import By

from django.test import tag
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


@tag('tadija')
@tag('delete_forum')
class DeleteForumTest(StaticLiveServerTestCase):
    fixtures = ['gamehub_sample_data.json']

    def setUp(self):

        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        self.admin_username = 'tadija'
        self.admin_password = 'oracle'

        self.id_forum = GameHubModels.Forum.objects.all().first().idforum

    def tearDown(self):
        self.browser.close()

    def test_delete_forum(self):

        # sign in as admin
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.admin_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.admin_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # delete forum
        self.browser.get(self.live_server_url + reverse('forum', args=[self.id_forum]))
        delete_forum_button = self.browser.find_element(
            By.XPATH, '/html/body/div[7]/div/div[2]/div/div[1]/div/button[3]'
        )
        delete_forum_button.click()
        delete_button = self.browser.find_element(By.XPATH, '/html/body/div[5]/div/form/div/button[2]')
        delete_button.click()

        # try if the forum exists
        try:
            GameHubModels.Forum.objects.get(idforum=self.id_forum, status='ACT')
            self.fail()
        except GameHubApp.models.Forum.DoesNotExist:
            pass
