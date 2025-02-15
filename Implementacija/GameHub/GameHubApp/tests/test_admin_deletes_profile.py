# Author: Tadija Goljic 0272/2021

import GameHubApp.models as GameHubModels

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By

from django.test import tag
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


@tag('tadija')
@tag('admin_deletes_profile')
class AdminDeletesProfileTest(StaticLiveServerTestCase):
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

    def test_admin_deletes_profile(self):
        # sign in user to check ih his account exists
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.user_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # sign out user, sign in admin
        self.browser.get(self.live_server_url + reverse('logout_user'))
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.admin_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.admin_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        # delete user's profile
        self.browser.get(self.live_server_url + reverse('user_profile', args=[self.user.iduser]))
        delete_account_button = self.browser.find_element(By.XPATH, '/html/body/form/div/div[2]/div/button')
        delete_account_button.click()
        password_field = self.browser.find_element(By.XPATH, '/html/body/div[5]/div/form/input[2]')
        password_field.send_keys(self.admin_password)
        delete_button = self.browser.find_element(By.XPATH, '/html/body/div[5]/div/form/div/button[2]')
        delete_button.click()

        # sign out admin, try to sign in user
        self.browser.get(self.live_server_url + reverse('logout_user'))
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(self.user_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(self.user_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()

        error_message = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/p')
        self.assertEqual(error_message.text, 'Wrong credentials, try again!')
