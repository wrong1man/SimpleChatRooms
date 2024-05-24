from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = get_user_model().objects.create_user('testuser111111', 'testpass')
        self.user1.set_password('testpass')
        self.user1.save()
        self.user2 = get_user_model().objects.create_user('testuser22222', 'testpass')
        self.user2.set_password('testpass')
        self.user2.save()
        # print("USERS: ",self.user1,self.user2)
    def test_login_user(self):
        response = self.client.post(reverse('login_user'), {'username': 'testuser111111', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)  # 302 means redirect, which is expected after successful login
        self.assertEqual(response.url,reverse('profile')) #should redirect to profile
    def test_register(self):
        response = self.client.post(reverse('register'), {'username': 'testuser3', 'password': 'testpass', 'email':'testemail@email.com'})
        self.assertEqual(response.status_code,
                         302)  # 302 means redirect, which is expected after successful registration  
        self.assertEqual(response.url, reverse('profile'))  # should redirect to profile

    def test_profile(self):
        self.client.login(username='testuser111111', password='testpass')  # log in before accessing profile  
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)  # 200 means OK  

    def test_get_start_Chat(self):
        self.client.login(username='testuser111111', password='testpass')  # log in before starting a chat  
        response = self.client.get(reverse('start_chat'), {'target_user': self.user2.id})
        self.assertEqual(response.status_code, 200)  # 200 means OK  
