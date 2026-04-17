from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from studentPreferences.models import SupportTicket


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
