from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from studentPreferences.auth_identifier import build_auth_identifier_username, get_auth_identifier_username_candidates
from studentPreferences.models import AuthIdentifierSettings, SupportTicket


class EmailChangeRequestTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username="student1",
            password="student-pass",
            email="student@example.com",
            is_active=True,
        )
        Group.objects.get_or_create(name="Student")[0].user_set.add(self.student_user)

        self.faculty_user = User.objects.create_user(
            username="faculty1",
            password="faculty-pass",
            email="faculty@example.com",
            is_active=True,
        )
        Group.objects.get_or_create(name="Professor")[0].user_set.add(self.faculty_user)

    def test_student_email_change_creates_admin_review_ticket(self):
        self.client.login(username="student1", password="student-pass")
        response = self.client.post(
            reverse("request_email_change"),
            {"requested_email": "student-new@example.com"},
            HTTP_REFERER=reverse("index"),
        )
        self.assertEqual(response.status_code, 302)
        ticket = SupportTicket.objects.get(user=self.student_user)
        self.assertEqual(ticket.role, SupportTicket.ROLE_STUDENT)
        self.assertEqual(ticket.ticket_type, SupportTicket.TYPE_EMAIL_CHANGE)
        self.assertIn("student-new@example.com", ticket.message)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.email, "student@example.com")

    def test_faculty_email_change_creates_admin_review_ticket(self):
        self.client.login(username="faculty1", password="faculty-pass")
        response = self.client.post(
            reverse("request_email_change"),
            {"requested_email": "faculty-new@example.com"},
            HTTP_REFERER=reverse("faculty-index"),
        )
        self.assertEqual(response.status_code, 302)
        ticket = SupportTicket.objects.get(user=self.faculty_user)
        self.assertEqual(ticket.role, SupportTicket.ROLE_FACULTY)
        self.assertEqual(ticket.ticket_type, SupportTicket.TYPE_EMAIL_CHANGE)
        self.assertIn("faculty-new@example.com", ticket.message)
        self.faculty_user.refresh_from_db()
        self.assertEqual(self.faculty_user.email, "faculty@example.com")


class AuthIdentifierHelperTests(TestCase):
    def test_blank_settings_keep_plain_username(self):
        self.assertEqual(build_auth_identifier_username("student1"), "student1")

    def test_suffix_settings_append_affix(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        self.assertEqual(build_auth_identifier_username("student1"), "student1@xyz.ac.in")

    def test_username_candidates_keep_legacy_plain_username_as_fallback(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        self.assertEqual(
            get_auth_identifier_username_candidates("student1"),
            ["student1@xyz.ac.in", "student1"],
        )

    def test_email_prefix_mode_uses_email_local_part(self):
        settings_obj = AuthIdentifierSettings.get_solo()
        settings_obj.username_mode = AuthIdentifierSettings.MODE_EMAIL_PREFIX
        settings_obj.username_affix = "@xyz.ac.in"
        settings_obj.affix_position = AuthIdentifierSettings.POSITION_SUFFIX
        settings_obj.save()

        self.assertEqual(
            build_auth_identifier_username("", email="student1@example.com"),
            "student1@xyz.ac.in",
        )
