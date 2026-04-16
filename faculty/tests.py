from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class FacultyLoginTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username="student1",
            password="student-pass",
            is_active=True,
        )
        Group.objects.get_or_create(name="Student")[0].user_set.add(self.student_user)

        self.superuser = User.objects.create_superuser(
            username="admin1",
            password="admin-pass",
            email="admin@example.com",
        )
        Group.objects.get_or_create(name="Professor")[0].user_set.add(self.superuser)

    def test_superuser_cannot_log_in_through_faculty_portal(self):
        response = self.client.post(
            reverse("faculty-login"),
            {"username": "admin1", "password": "admin-pass"},
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertTrue(any(message.message == "Invalid credentials" for message in messages))

    def test_student_cannot_log_in_through_faculty_portal(self):
        response = self.client.post(
            reverse("faculty-login"),
            {"username": "student1", "password": "student-pass"},
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertTrue(any(message.message == "Invalid credentials" for message in messages))
