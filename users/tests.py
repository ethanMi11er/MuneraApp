from django.test import TestCase
from django.urls import reverse

from users.models import User


class UserSignupTests(TestCase):
    def test_get_create_account_renders(self):
        url = reverse('create_account')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Create Account')

    def test_post_create_account_success(self):
        url = reverse('create_account')
        payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'alias': 'JD',
            'username': 'jdoe',
            'email': 'jdoe@example.com',
            'password': 'Password123',
            'password_confirm': 'Password123',
        }
        resp = self.client.post(url, data=payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Account created! Please log in.')
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.username, 'jdoe')
        self.assertNotEqual(user.password, 'Password123')
        self.assertTrue(user.check_password('Password123'))

    def test_post_create_account_password_mismatch(self):
        url = reverse('create_account')
        payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'jdoe',
            'email': 'jdoe@example.com',
            'password': 'Password123',
            'password_confirm': 'Mismatch',
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Please correct the errors below')
        self.assertContains(resp, 'Passwords do not match')
        self.assertEqual(User.objects.count(), 0)

    def test_post_create_account_short_password(self):
        url = reverse('create_account')
        payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'jdoe',
            'email': 'jdoe@example.com',
            'password': 'short',
            'password_confirm': 'short',
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Please correct the errors below')
        self.assertContains(resp, 'at least 8 characters')

    def test_post_create_account_duplicate_username_email(self):
        User.objects.create(
            first_name='Jane', last_name='Roe', email='jane@example.com', username='jdoe', password='x'
        )
        url = reverse('create_account')
        payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'jdoe', 
            'email': 'jdoe@example.com',
            'password': 'Password123',
            'password_confirm': 'Password123',
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Please correct the errors below')
        self.assertContains(resp, 'Username is already taken')

        payload['username'] = 'johnny'
        payload['email'] = 'jane@example.com'
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Please correct the errors below')
        self.assertContains(resp, 'Email is already registered')


class UserLoginTests(TestCase):
    def setUp(self):
        self.user = User(
            first_name='John', last_name='Doe', alias='JD', email='john@example.com', username='jdoe'
        )
        self.user.set_password('Password123')
        self.user.save()

    def test_get_login_renders(self):
        url = reverse('login')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Login')

    def test_post_login_success(self):
        url = reverse('login')
        resp = self.client.post(url, data={'username': 'jdoe', 'password': 'Password123'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Welcome back!')
        self.assertEqual(self.client.session.get('id'), self.user.pk)

    def test_post_login_invalid_credentials(self):
        url = reverse('login')
        resp = self.client.post(url, data={'username': 'jdoe', 'password': 'wrong'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Invalid username or password')
