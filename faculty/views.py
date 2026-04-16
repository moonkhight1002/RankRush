from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

from questions.views import has_group
from student.views import EmailThread
from student.models import ActiveExamSession, ExamViolationLog
from django.utils import timezone
from datetime import timedelta

from .forms import FacultyForm, FacultyInfoForm
from .models import FacultyInfo
from examProject.text_utils import split_full_name

def redirect_authenticated_user(request):
    if not request.user.is_authenticated:
        return None
    if request.user.is_superuser:
        return redirect('/admin/')
    if has_group(request.user, "Professor"):
        return redirect('faculty-index')
    return redirect('index')


@login_required(login_url='faculty-login')
def index(request):
    if not has_group(request.user, "Professor"):
        return redirect('view_exams_student')

    ActiveExamSession.objects.filter(
        professor=request.user,
        status=ActiveExamSession.STATUS_ACTIVE,
        last_seen_at__lt=timezone.now() - timedelta(seconds=45)
    ).update(status=ActiveExamSession.STATUS_STALE)

    sessions = ActiveExamSession.objects.filter(professor=request.user)
    logs = ExamViolationLog.objects.filter(professor=request.user)
    context = {
        'monitor_summary': {
            'active_sessions': sessions.filter(status=ActiveExamSession.STATUS_ACTIVE).count(),
            'stale_sessions': sessions.filter(status=ActiveExamSession.STATUS_STALE).count(),
            'violation_events': logs.count(),
            'high_risk_signals': logs.filter(violation_type='fast_submit').count(),
        }
    }
    return render(request, 'faculty/index.html', context)


class Register(View):
    def get(self, request):
        redirect_response = redirect_authenticated_user(request)
        if redirect_response:
            return redirect_response
        faculty_form = FacultyForm()
        faculty_info_form = FacultyInfoForm()
        return render(request, 'faculty/register.html', {
            'faculty_form': faculty_form,
            'faculty_info_form': faculty_info_form,
        })

    def post(self, request):
        faculty_form = FacultyForm(request.POST)
        faculty_info_form = FacultyInfoForm(request.POST, request.FILES)
        email = request.POST.get('email')

        if faculty_form.is_valid() and faculty_info_form.is_valid():
            faculty = faculty_form.save(commit=False)
            first_name, last_name = split_full_name(faculty_form.cleaned_data.get('full_name'))
            faculty.first_name = first_name
            faculty.last_name = last_name
            faculty.set_password(faculty_form.cleaned_data['password'])
            faculty.is_active = False
            faculty.is_staff = False
            faculty.save()

            faculty_info = faculty_info_form.save(commit=False)
            faculty_info.user = faculty
            if 'picture' in request.FILES:
                faculty_info.picture = request.FILES['picture']
            faculty_info.save()

            domain = get_current_site(request).domain
            email_subject = 'Faculty Registration Submitted'
            email_body = (
                f"Hi. Your faculty registration on {domain} has been received and is waiting for admin approval.\n\n"
                f"You will be able to log in after an admin activates your account and grants faculty access.\n\n"
                f"If you did not register, please contact support."
            )
            from_email = 'noreply@exam.com'

            email_message = EmailMessage(
                email_subject,
                email_body,
                from_email,
                [email],
            )
            EmailThread(email_message).start()

            messages.success(request, 'Registration submitted. Your account is waiting for admin approval.')
            return redirect('faculty-login')

        print(faculty_form.errors, faculty_info_form.errors)
        return render(request, 'faculty/register.html', {
            'faculty_form': faculty_form,
            'faculty_info_form': faculty_info_form,
        })


@method_decorator([never_cache, ensure_csrf_cookie], name='get')
@method_decorator(never_cache, name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(View):
    def get(self, request):
        redirect_response = redirect_authenticated_user(request)
        if redirect_response:
            return redirect_response
        get_token(request)
        response = render(request, 'faculty/login.html')
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        has_grp = False
        user_check = None

        if username and password:
            exists = User.objects.filter(username=username).exists()
            if exists:
                user_check = User.objects.get(username=username)
                has_grp = has_group(user_check, "Professor")
                if user_check.is_superuser or not has_grp:
                    messages.error(request, 'Invalid credentials')
                    return render(request, 'faculty/login.html')
                if not user_check.is_active:
                    messages.error(request, 'Your faculty account is waiting for admin approval.')
                    return render(request, 'faculty/login.html')

            user = auth.authenticate(username=username, password=password)
            if user and user.is_superuser:
                messages.error(request, 'Invalid credentials')
                return render(request, 'faculty/login.html')
            if user and user.is_active and exists and has_grp:
                auth.login(request, user)
                display_name = user.get_full_name() or user.username
                messages.success(request, "Welcome, " + display_name + ". You are now logged in.")
                return redirect('faculty-index')

            messages.error(request, 'Invalid credentials')
            return render(request, 'faculty/login.html')

        messages.error(request, 'Please fill all fields')
        return render(request, 'faculty/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'Logged Out')
        return redirect('faculty-login')
