import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from student.forms import StudentForm
from student.models import StudentInfo
from studentPreferences.models import AuthIdentifierSettings


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


class StudentRegistrationFormTests(TestCase):
    def test_student_registration_can_use_email_prefix_mode(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_mode = AuthIdentifierSettings.MODE_EMAIL_PREFIX
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        form = StudentForm(
            data={
                "full_name": "new student",
                "email": "newstudent@example.com",
                "password": "Abc!12",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "newstudent@xyz.ac.in")

    def test_student_registration_applies_configured_username_affix(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        form = StudentForm(
            data={
                "username": "newstudent",
                "full_name": "new student",
                "email": "student@example.com",
                "password": "Abc!12",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "newstudent@xyz.ac.in")

    def test_student_registration_rejects_weak_password(self):
        form = StudentForm(
            data={
                "username": "newstudent",
                "full_name": "new student",
                "email": "student@example.com",
                "password": "abc12!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_student_registration_accepts_strong_password(self):
        form = StudentForm(
            data={
                "username": "newstudent",
                "full_name": "new student",
                "email": "student@example.com",
                "password": "Abc!12",
            }
        )

        self.assertTrue(form.is_valid())


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class StudentRegistrationViewTests(TestCase):
    @patch("student.views.EmailThread")
    def test_student_registration_creates_inactive_student_and_assigns_group(self, email_thread):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newstudent",
                "full_name": "new student",
                "email": "newstudent@example.com",
                "password": "Abc!12",
                "address": "Bhubaneswar",
                "stream": "Computer Science",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

        student = User.objects.get(username="newstudent")
        self.assertFalse(student.is_active)
        self.assertTrue(student.groups.filter(name="Student").exists())
        self.assertTrue(StudentInfo.objects.filter(user=student, stream="Computer Science").exists())
        email_thread.return_value.start.assert_called_once()


class StudentAffixLoginTests(TestCase):
    def setUp(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        self.student_user = User.objects.create_user(
            username="student1@xyz.ac.in",
            password="student-pass",
            is_active=True,
        )
        Group.objects.get_or_create(name="Student")[0].user_set.add(self.student_user)

    def test_student_can_log_in_with_local_username_when_affix_is_enabled(self):
        response = self.client.post(
            reverse("login"),
            {"username": "student1", "password": "student-pass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("index"))

    def test_legacy_student_without_suffix_can_still_log_in_after_affix_is_enabled(self):
        legacy_user = User.objects.create_user(
            username="legacyuser",
            password="student-pass",
            is_active=True,
        )
        Group.objects.get_or_create(name="Student")[0].user_set.add(legacy_user)

        response = self.client.post(
            reverse("login"),
            {"username": "legacyuser", "password": "student-pass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("index"))

    def test_student_email_prefix_mode_login_accepts_email_prefix(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_mode = AuthIdentifierSettings.MODE_EMAIL_PREFIX
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        email_prefix_user = User.objects.create_user(
            username="mailstudent@xyz.ac.in",
            password="student-pass",
            is_active=True,
            email="mailstudent@example.com",
        )
        Group.objects.get_or_create(name="Student")[0].user_set.add(email_prefix_user)

        response = self.client.post(
            reverse("login"),
            {"username": "mailstudent", "password": "student-pass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("index"))
