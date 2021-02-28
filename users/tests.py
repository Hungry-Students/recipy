# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelsManagersTests(TestCase):
    def test_create_user(self):
        user_model = get_user_model()
        user = user_model.objects.create_user("normal", "normal@user.com", "foo")
        self.assertEqual(user.username, "normal")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user_model = get_user_model()
        admin_user = user_model.objects.create_superuser(
            "super", "super@user.com", "foo"
        )
        self.assertEqual(admin_user.username, "super")
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
