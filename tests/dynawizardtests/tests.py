from django.test import TestCase
from django.contrib.auth.models import User


class DynawizardTests(TestCase):

    def setUp(self):
        self.testuser, created = User.objects.get_or_create(username='testuser1')

    def test_foo(self):
        print("yes")
