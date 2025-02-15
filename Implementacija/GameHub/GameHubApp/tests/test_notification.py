# Author: Nemanja Mićanović 0595/2021

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

import GameHubApp.models as GameHubModels
from GameHubApp.tests.test_post_comment import sign_in_for_test

from django.urls import reverse
import time


class NotificationTest(StaticLiveServerTestCase):
    fixtures = ['gamehub_sample_data.json']
    admin_id = 1
    admin_password = 'morpheus'
    forum_id = 1
    post_id = 29

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        admin = GameHubModels.Admin.objects.get(idadmin=self.admin_id)

        sign_in_for_test(self.browser, self.live_server_url, admin.idadmin.iduser.username, self.admin_password)

    def tearDown(self):
        self.browser.close()

    def check_is_displayed(self, notification_div):
        if notification_div.is_displayed():
            return True
        return False

    def click_notification_button(self):
        notification_button = self.browser.find_element(By.ID, 'notification_bell_button')
        notification_button.click()
        time.sleep(2)

    def test_notification_show(self):
        self.browser.get(self.live_server_url + reverse('index', args=[]))
        time.sleep(2)

        notification_div = self.browser.find_element(By.ID, 'notification_container')

        displayed_before = self.check_is_displayed(notification_div)
        self.click_notification_button()
        displayed_after = self.check_is_displayed(notification_div)

        self.assertEqual(not displayed_before and displayed_after, True)

    def test_notification_press(self):
        self.browser.get(self.live_server_url + reverse('index', args=[]))
        time.sleep(2)

        self.click_notification_button()
        notification = self.browser.find_element(By.XPATH, '/html/body/div[1]/div[2]/a')
        notification.click()
        time.sleep(2)

        current_url = self.browser.current_url
        post_url = self.live_server_url + reverse('post', args=[self.forum_id, self.post_id])
        self.assertEqual(current_url == post_url, True)
