import shutil
import tempfile

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from student.models import StudentInfo


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


STUDENT_TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=STUDENT_TEST_MEDIA_ROOT)
class StudentProfilePictureTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(STUDENT_TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.student_user = User.objects.create_user(
            username="studentpic",
            password="student-pass",
            is_active=True,
        )
        Group.objects.get_or_create(name="Student")[0].user_set.add(self.student_user)
        StudentInfo.objects.create(user=self.student_user)
        self.client.login(username="studentpic", password="student-pass")

    def test_student_profile_picture_upload_updates_saved_image(self):
        upload = SimpleUploadedFile(
            "avatar.png",
            b"\x89PNG\r\n\x1a\nstudent-avatar",
            content_type="image/png",
        )
        response = self.client.post(
            reverse("student-profile-picture"),
            {"picture": upload},
            HTTP_REFERER=reverse("index"),
        )
        self.assertEqual(response.status_code, 302)
        self.student_user.studentinfo.refresh_from_db()
        self.assertTrue(self.student_user.studentinfo.picture.name.endswith("avatar.png"))
