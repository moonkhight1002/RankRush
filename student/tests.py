from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class AdminAccessTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username="student1",
            password="student-pass",
            is_active=True,
        )
        Group.objects.get_or_create(name="Student")[0].user_set.add(self.student_user)

        self.faculty_user = User.objects.create_user(
            username="faculty1",
            password="faculty-pass",
            is_active=True,
            is_staff=True,
        )
        Group.objects.get_or_create(name="Professor")[0].user_set.add(self.faculty_user)

        self.superuser = User.objects.create_superuser(
            username="admin1",
            password="admin-pass",
            email="admin@example.com",
        )

    def test_student_cannot_access_admin_index(self):
        self.client.login(username="student1", password="student-pass")
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_faculty_staff_cannot_access_admin_index(self):
        self.client.login(username="faculty1", password="faculty-pass")
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_faculty_staff_cannot_access_proctor_ml_test(self):
        self.client.login(username="faculty1", password="faculty-pass")
        response = self.client.get(reverse("admin:proctor-ml-test"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_superuser_can_access_admin_and_ml_test(self):
        self.client.login(username="admin1", password="admin-pass")
        admin_response = self.client.get("/admin/")
        ml_response = self.client.get(reverse("admin:proctor-ml-test"))
        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(ml_response.status_code, 200)

    def test_superuser_cannot_log_in_through_student_portal(self):
        response = self.client.post(
            reverse("login"),
            {"username": "admin1", "password": "admin-pass"},
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertTrue(any(message.message == "Invalid credentials" for message in messages))

    def test_faculty_cannot_log_in_through_student_portal(self):
        response = self.client.post(
            reverse("login"),
            {"username": "faculty1", "password": "faculty-pass"},
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertTrue(any(message.message == "Invalid credentials" for message in messages))
