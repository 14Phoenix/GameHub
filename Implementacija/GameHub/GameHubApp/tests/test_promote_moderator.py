# Author: Tadija Goljic 0272/2021

import GameHubApp.models as GameHubModels

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from django.test import tag
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


@tag('tadija')
@tag('promote_moderator')
class PromoteModeratorTest(StaticLiveServerTestCase):

    fixtures = ['gamehub_sample_data.json']

    def setUp(self):

        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        # Test to be moderator
        self.user_username = 'Agent'
        self.user_password = 'Smith'
        self.user = GameHubModels.RegisteredUser.objects.create_user(
            username=self.user_username, password=self.user_password, email="test@email.com",
            aboutsection='Test about section.', status='ACT', dateregistered=datetime.now()
        )

        self.admin_username = 'tadija'
        self.admin_password = 'oracle'

    def tearDown(self):
        self.browser.close()

    def test_promote_moderator(self):

        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.user_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # Test if user is already a moderator
        self.browser.get(self.live_server_url + reverse('forum', args=[5]))
        try:
            self.browser.find_element(By.ID, 'delete_button')
            self.fail()
        except NoSuchElementException:
            pass

        # sign in admin to promote user
        self.browser.get(self.live_server_url + reverse('logout_user'))
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.admin_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.admin_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # promote a moderator
        self.browser.get(self.live_server_url + reverse('forum', args=[5]))
        promote_button = self.browser.find_element(By.XPATH, '/html/body/div[6]/div/div[2]/div/div[1]/div/button[1]')
        promote_button.click()
        moderator_username = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/input[2]')
        moderator_username.send_keys(self.user_username)
        add_moderator_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/form/div/button[2]')
        add_moderator_button.click()

        # sign in user to check if he is a moderator
        self.browser.get(self.live_server_url + reverse('logout_user'))
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.user_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # Test if user is a moderator
        self.browser.get(self.live_server_url + reverse('forum', args=[5]))
        try:
            self.browser.find_element(By.ID, 'delete_button')
        except NoSuchElementException:
            self.fail()
