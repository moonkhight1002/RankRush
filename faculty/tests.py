import shutil
import tempfile

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from faculty.forms import FacultyForm
from faculty.models import FacultyInfo
from studentPreferences.models import AuthIdentifierSettings


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


class FacultyRegistrationFormTests(TestCase):
    def test_faculty_registration_can_use_email_prefix_mode(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_mode = AuthIdentifierSettings.MODE_EMAIL_PREFIX
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        form = FacultyForm(
            data={
                "full_name": "new faculty",
                "email": "newfaculty@example.com",
                "password": "Abc!12",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "newfaculty@xyz.ac.in")

    def test_faculty_registration_applies_configured_username_affix(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_affix = "inst-"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_PREFIX
        settings_obj.save()

        form = FacultyForm(
            data={
                "username": "newfaculty",
                "full_name": "new faculty",
                "email": "faculty@example.com",
                "password": "Abc!12",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "inst-newfaculty")

    def test_faculty_registration_rejects_weak_password(self):
        form = FacultyForm(
            data={
                "username": "newfaculty",
                "full_name": "new faculty",
                "email": "faculty@example.com",
                "password": "abc12!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_faculty_registration_accepts_strong_password(self):
        form = FacultyForm(
            data={
                "username": "newfaculty",
                "full_name": "new faculty",
                "email": "faculty@example.com",
                "password": "Abc!12",
            }
        )

        self.assertTrue(form.is_valid())


class FacultyAffixLoginTests(TestCase):
    def setUp(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        self.faculty_user = User.objects.create_user(
            username="faculty1@xyz.ac.in",
            password="faculty-pass",
            is_active=True,
        )
        Group.objects.get_or_create(name="Professor")[0].user_set.add(self.faculty_user)

    def test_faculty_can_log_in_with_local_username_when_affix_is_enabled(self):
        response = self.client.post(
            reverse("faculty-login"),
            {"username": "faculty1", "password": "faculty-pass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("faculty-index"))

    def test_legacy_faculty_without_suffix_can_still_log_in_after_affix_is_enabled(self):
        legacy_faculty = User.objects.create_user(
            username="legacyfaculty",
            password="faculty-pass",
            is_active=True,
        )
        Group.objects.get_or_create(name="Professor")[0].user_set.add(legacy_faculty)

        response = self.client.post(
            reverse("faculty-login"),
            {"username": "legacyfaculty", "password": "faculty-pass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("faculty-index"))

    def test_faculty_email_prefix_mode_login_accepts_email_prefix(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_mode = AuthIdentifierSettings.MODE_EMAIL_PREFIX
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        email_prefix_user = User.objects.create_user(
            username="mailfaculty@xyz.ac.in",
            password="faculty-pass",
            is_active=True,
            email="mailfaculty@example.com",
        )
        Group.objects.get_or_create(name="Professor")[0].user_set.add(email_prefix_user)

        response = self.client.post(
            reverse("faculty-login"),
            {"username": "mailfaculty", "password": "faculty-pass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("faculty-index"))
