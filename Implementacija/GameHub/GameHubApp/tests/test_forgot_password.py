# Author: Mihajlo Blagojevic 0283/2021

from django.test import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

import GameHubApp.models as game_hub_models

from django.urls import reverse
from datetime import datetime

from django.contrib.auth.hashers import make_password


@tag('test_forgot_password')
class ForgotPasswordTest(StaticLiveServerTestCase):
    fixtures = ['gamehub_sample_data.json']

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)
        self.time_sleep = 4
        self.short_sleep = 1

        # Create user
        self.registered_user = game_hub_models.RegisteredUser.objects.create_user(username='testUser',
                password='testPassword123$', email="test@example.com",
                aboutsection='Test about section.', status='ACT', dateregistered=datetime.now())

    def tearDown(self):
        self.browser.close()

    def test_successful_forgot_password(self):
        # Test data
        new_password = 'new_oracle'
        new_conf_password = 'new_oracle'

        # Test execution
        # on sign in page
        self.browser.get(self.live_server_url + reverse('sign_in', args=[]))
        forgot_password_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/button')
        forgot_password_button.click()

        self.sending_email_and_inserting_data_into_form(self.registered_user.email, new_password, new_conf_password)
        self.assertEqual(game_hub_models.ForgotPassword.objects.filter(iduser=self.registered_user).exists(), False)

        new_reg_user = game_hub_models.RegisteredUser.objects.get(username=self.registered_user.username)
        salt = new_reg_user.password.split('$')[2]
        hash_pass = make_password(new_password, salt=salt)
        self.assertEqual(new_reg_user.password, hash_pass)


    def test_unsuccessful_email_not_inserted(self):
        # Test data
        new_password = 'new_oracle'

        # Test execution
        # on sign in page
        self.browser.get(self.live_server_url + reverse('sign_in', args=[]))
        forgot_password_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/button')
        forgot_password_button.click()

        # on forgot password page
        form_email = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/form/input[2]')
        form_email.send_keys('')
        send_email_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/form/input[3]')
        send_email_button.click()
        self.assertEqual(game_hub_models.ForgotPassword.objects.filter(iduser=self.registered_user).exists(), False)
        err_msg = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/p')
        self.assertEqual(err_msg.text, 'All fields must be filled out, try again!')


    def test_unsuccessful_password_and_conf_password_do_not_match(self):
        # Test data
        new_password = 'new_oracle'
        new_conf_password = 'different_pass'

        # Test execution
        # on sign in page
        self.browser.get(self.live_server_url + reverse('sign_in', args=[]))
        forgot_password_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/button')
        forgot_password_button.click()

        self.sending_email_and_inserting_data_into_form(self.registered_user.email, new_password, new_conf_password)

        self.assertEqual(game_hub_models.ForgotPassword.objects.filter(iduser=self.registered_user).exists(), True)
        err_msg = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/p')
        self.assertEqual(err_msg.text, 'Passwords don\'t match, try again!')


    def test_unsuccessful_password_not_inserted(self):
        # Test data
        new_password = ''
        new_conf_password = 'pass345654'

        # Test execution
        # on sign in page
        self.browser.get(self.live_server_url + reverse('sign_in', args=[]))
        forgot_password_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/button')
        forgot_password_button.click()

        self.sending_email_and_inserting_data_into_form(self.registered_user.email, new_password, new_conf_password)

        self.assertEqual(game_hub_models.ForgotPassword.objects.filter(iduser=self.registered_user).exists(), True)
        err_msg = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/p')
        self.assertEqual(err_msg.text, 'All fields must be filled out, try again!')


    def test_unsuccessful_conf_password_not_inserted(self):
        # Test data
        new_password = 'pass345654'
        new_conf_password = ''

        # Test execution
        # on sign in page
        self.browser.get(self.live_server_url + reverse('sign_in', args=[]))
        forgot_password_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/button')
        forgot_password_button.click()

        self.sending_email_and_inserting_data_into_form(self.registered_user.email, new_password, new_conf_password)

        self.assertEqual(game_hub_models.ForgotPassword.objects.filter(iduser=self.registered_user).exists(), True)
        err_msg = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/p')
        self.assertEqual(err_msg.text, 'All fields must be filled out, try again!')


    def login_registered_user(self, usr_username, new_usr_password):
        self.browser.get(self.live_server_url + reverse('sign_in'))
        username = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
        username.send_keys(usr_username)
        password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
        password.send_keys(new_usr_password)
        submit = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
        submit.click()


    def sending_email_and_inserting_data_into_form(self, email, user_pass, user_conf_pass):
        # on forgot password page
        form_email = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/form/input[2]')
        form_email.send_keys(email)
        send_email_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/form/input[3]')
        send_email_button.click()
        self.assertEqual(game_hub_models.ForgotPassword.objects.filter(iduser=self.registered_user).exists(), True)

        # on reset password page
        forgot_password = game_hub_models.ForgotPassword.objects.get(iduser=self.registered_user)
        self.browser.get(self.live_server_url + reverse('reset_password', args=[forgot_password.resetkey]))
        form_password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/form/input[2]')
        form_password.send_keys(user_pass)
        form_conf_password = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/form/input[3]')
        form_conf_password.send_keys(user_conf_pass)
        form_confirm_button = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/form/input[4]')
        form_confirm_button.click()