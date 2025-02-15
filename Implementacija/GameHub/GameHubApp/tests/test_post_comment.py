# Author: Nemanja Mićanović 0595/2021

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

import GameHubApp.models as GameHubModels

from django.urls import reverse
from datetime import datetime
import time


def sign_in_for_test(browser, live_server_url, username, password):
    browser.get(live_server_url + reverse('sign_in'))

    username_field = browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[2]')
    username_field.send_keys(username)

    password_field = browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[3]')
    password_field.send_keys(password)

    submit = browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/form/input[4]')
    time.sleep(1)
    submit.click()


class AdminDeleteCommentOnPostTest(StaticLiveServerTestCase):
    fixtures = ['gamehub_sample_data.json']
    admin_id = 3
    admin_password = 'trinity'
    forum_id = 7
    post_id = 16
    comment_id = 16

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        admin = GameHubModels.Admin.objects.get(idadmin=self.admin_id)

        sign_in_for_test(self.browser, self.live_server_url, admin.idadmin.iduser.username, self.admin_password)

    def tearDown(self):
        self.browser.close()

    def test_delete_comment(self):
        self.browser.get(self.live_server_url + reverse('post', args=[self.forum_id, self.post_id]))
        time.sleep(2)

        delete_comment_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div[3]/div[2]/button[2]')
        delete_comment_button.click()
        time.sleep(2)

        self.assertEqual(GameHubModels.Comment.objects.filter(idcom=self.comment_id).first().status == "DEL", True)


class UserDeleteCommentOnPostTest(StaticLiveServerTestCase):
    fixtures = ['gamehub_sample_data.json']
    forum_id = 7
    post_id = 16

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        # Create user
        registered_user_password = 'testPassword123'
        registered_user = GameHubModels.RegisteredUser.objects.create_user(username='testUser',
                                                                           password=registered_user_password,
                                                                           email="testUser@email.com",
                                                                           aboutsection='Test about section.',
                                                                           status='ACT',
                                                                           dateregistered=datetime.now())

        # Get post
        post = GameHubModels.Post.objects.get(idpost=self.post_id)

        # Create comment
        comment = GameHubModels.Comment(iduser=registered_user, idpost=post, body="Test comment.", datecreated=datetime.now())
        comment.save()
        self.comment_id = comment.idcom

        sign_in_for_test(self.browser, self.live_server_url, registered_user.username, registered_user_password)

    def tearDown(self):
        self.browser.close()

    def test_delete_comment(self):
        self.browser.get(self.live_server_url + reverse('post', args=[self.forum_id, self.post_id]))
        time.sleep(2)

        delete_comment_button = self.browser.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div[3]/div[4]/button[2]')
        delete_comment_button.click()
        time.sleep(2)

        self.assertEqual(GameHubModels.Comment.objects.filter(idcom=self.comment_id).first().status == "DEL", True)


class LikeUnlikePostAndCommentTest(StaticLiveServerTestCase):
    fixtures = ['gamehub_sample_data.json']
    admin_id = 3
    admin_password = 'trinity'

    forum_id = 7
    forum_id_2 = 6

    post_id_for_like = 16
    post_id_for_unlike = 18

    comment_id_for_like = 16
    comment_id_for_unlike = 49

    def setUp(self):
        service = webdriver.ChromeService(executable_path='../../Test/chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)

        admin = GameHubModels.Admin.objects.get(idadmin=self.admin_id)

        sign_in_for_test(self.browser, self.live_server_url, admin.idadmin.iduser.username, self.admin_password)

    def tearDown(self):
        self.browser.close()

    def check_is_liked(self, type):
        if type == "post_like":
            return GameHubModels.LikedPost.objects.filter(iduser=self.admin_id, idpost=self.post_id_for_like).exists()
        elif type == "comment_like":
            return GameHubModels.LikedComment.objects.filter(iduser=self.admin_id, idcom=self.comment_id_for_like).exists()
        elif type == "post_unlike":
            return GameHubModels.LikedPost.objects.filter(iduser=self.admin_id, idpost=self.post_id_for_unlike).exists()
        elif type == "comment_unlike":
            return GameHubModels.LikedComment.objects.filter(iduser=self.admin_id, idcom=self.comment_id_for_unlike).exists()

    def click_like_button(self, reverse_object, path, type):
        self.browser.get(self.live_server_url + reverse_object)
        time.sleep(2)

        liked_before = self.check_is_liked(type)

        like_button = self.browser.find_element(By.XPATH, path)
        like_button.click()
        time.sleep(2)

        liked_after = self.check_is_liked(type)

        if type.split("_")[1] == "like":
            self.assertEqual(not liked_before and liked_after, True)
        elif type.split("_")[1] == "unlike":
            self.assertEqual(liked_before and not liked_after, True)

    def test_like_post_from_forum(self):
        self.click_like_button(reverse('forum', args=[self.forum_id]),
                               '/html/body/div[7]/div/div[2]/div/div[2]/button[1]', "post_like")

    def test_like_post_from_post(self):
        self.click_like_button(reverse('post', args=[self.forum_id, self.post_id_for_like]),
                               '/html/body/div[3]/div/div[1]/div[1]/div/button[1]', "post_like")

    def test_like_comment(self):
        self.click_like_button(reverse('post', args=[self.forum_id, self.post_id_for_like]),
                               '/html/body/div[3]/div/div[1]/div[3]/div[2]/button[1]', "comment_like")

    def test_unlike_post_from_forum(self):
        self.click_like_button(reverse('forum', args=[self.forum_id_2]),
                               '/html/body/div[6]/div/div[2]/div/div[2]/button[1]', "post_unlike")

    def test_unlike_post_from_post(self):
        self.click_like_button(reverse('post', args=[self.forum_id_2, self.post_id_for_unlike]),
                               '/html/body/div[3]/div/div[1]/div[1]/div/button[1]', "post_unlike")

    def test_unlike_comment(self):
        self.click_like_button(reverse('post', args=[self.forum_id, self.post_id_for_like]),
                               '/html/body/div[3]/div/div[1]/div[3]/div[3]/button[1]', "comment_unlike")
