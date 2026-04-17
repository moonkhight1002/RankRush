import shutil
import tempfile

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from faculty.models import FacultyInfo


FACULTY_TEST_MEDIA_ROOT = tempfile.mkdtemp()


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


@override_settings(MEDIA_ROOT=FACULTY_TEST_MEDIA_ROOT)
class FacultyProfilePictureTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(FACULTY_TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.faculty_user = User.objects.create_user(
            username="facultypic",
            password="faculty-pass",
            is_active=True,
        )
        Group.objects.get_or_create(name="Professor")[0].user_set.add(self.faculty_user)
        FacultyInfo.objects.create(user=self.faculty_user)
        self.client.login(username="facultypic", password="faculty-pass")

    def test_faculty_profile_picture_upload_updates_saved_image(self):
        upload = SimpleUploadedFile(
            "faculty-avatar.png",
            b"\x89PNG\r\n\x1a\nfaculty-avatar",
            content_type="image/png",
        )
        response = self.client.post(
            reverse("faculty-profile-picture"),
            {"picture": upload},
            HTTP_REFERER=reverse("faculty-index"),
        )
        self.assertEqual(response.status_code, 302)
        self.faculty_user.facultyinfo.refresh_from_db()
        self.assertTrue(self.faculty_user.facultyinfo.picture.name.endswith("faculty-avatar.png"))
