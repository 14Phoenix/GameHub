# Author: Tadija Goljic 0272/2021

import GameHubApp.models as GameHubModels

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from django.test import tag
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


@tag('tadija')
@tag('remove_moderator')
class RemoveModeratorTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):

        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        # User to be removed
        self.user_username = 'AquaLynx'
        self.user_password = 'P@ssw0rd1!'

        user = GameHubModels.RegisteredUser.objects.get(username=self.user_username)
        self.id_forum = GameHubModels.Moderates.objects.filter(idmod=user.iduser).first().idforum.idforum

        self.admin_username = 'tadija'
        self.admin_password = 'oracle'

    def tearDown(self):
        self.browser.close()

    def test_remove_moderator(self):

        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.user_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # check if user is a moderator
        self.browser.get(self.live_server_url + reverse('forum', args=[self.id_forum]))
        try:
            self.browser.find_element(By.ID, 'delete_button')
        except NoSuchElementException:
            self.fail()

        # sign in admin to remove moderator
        self.browser.get(self.live_server_url + reverse('logout_user'))
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.admin_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.admin_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # remove moderator
        self.browser.get(self.live_server_url + reverse('forum', args=[self.id_forum]))
        remove_moderator_button = self.browser.find_element(
            By.XPATH, '/html/body/div[7]/div/div[2]/div/div[1]/div/button[2]'
        )
        remove_moderator_button.click()
        moderator_username = self.browser.find_element(By.XPATH, '/html/body/div[4]/div/form/input[2]')
        moderator_username.send_keys(self.user_username)
        remove_moderator_button = self.browser.find_element(By.XPATH, '/html/body/div[4]/div/form/div/button[2]')
        remove_moderator_button.click()

        # sign in user to check if he is a moderator
        self.browser.get(self.live_server_url + reverse('logout_user'))
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.user_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # Test if user is not a moderator
        self.browser.get(self.live_server_url + reverse('forum', args=[self.id_forum]))
        try:
            self.browser.find_element(By.ID, 'delete_button')
            self.fail()
        except NoSuchElementException:
            pass
