from django.shortcuts import render, redirect
from .models import StudentPreferenceModel, SupportTicket
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from examProject.text_utils import normalize_title_case


def _support_role_for_user(user):
    return SupportTicket.ROLE_FACULTY if user.groups.filter(name='Professor').exists() else SupportTicket.ROLE_STUDENT


def _default_profile_redirect(user):
    return 'faculty-index' if user.groups.filter(name='Professor').exists() else 'index'

@login_required(login_url='login')
def index(request):
    exists = StudentPreferenceModel.objects.filter(user=request.user).exists()
    student_preference = None
    
    if request.method == 'GET':
        var = "On"
        if exists:
            var="Off"
            student_preference = StudentPreferenceModel.objects.get(user=request.user)
            if student_preference.sendEmailOnLogin == True:
                var = "On"
        return render(request,'studentPreferences/pref.html',{'student_preference':student_preference,'email_pref_value':var})

    if request.method == 'POST':
        if exists:
            student_preference = StudentPreferenceModel.objects.get(user=request.user)
            var = "Off"
        pref = request.POST['email_pref']
        if exists:
            student_preference.sendEmailOnLogin = pref
            student_preference.save()
        else:
            var = "On"
            StudentPreferenceModel.objects.create(user = request.user, sendEmailOnLogin=pref)

        student_preference = StudentPreferenceModel.objects.filter(user=request.user)
        if pref == 'True':
            var = "On"

        messages.success(request,"Email Notifications are turned " + var)

        return render(request,'studentPreferences/pref.html',{'student_preference':student_preference,'email_pref_value':var})

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'studentPreferences/change_password.html', {
        'form': form
    })


@login_required(login_url='login')
def contact_support(request):
    is_faculty = request.user.groups.filter(name='Professor').exists()
    role = _support_role_for_user(request.user)
    template_name = 'support/contact_support_faculty.html' if is_faculty else 'support/contact_support_student.html'
    has_registered_email = bool((request.user.email or '').strip())

    if request.method == 'POST':
        ticket_type = (request.POST.get('ticket_type') or SupportTicket.TYPE_HELP).strip()
        subject = normalize_title_case((request.POST.get('subject') or '').strip())
        message_body = (request.POST.get('message') or '').strip()
        valid_types = {choice[0] for choice in SupportTicket.TYPE_CHOICES}

        if ticket_type not in valid_types:
            ticket_type = SupportTicket.TYPE_HELP

        if not has_registered_email:
            messages.error(request, 'Add a registered email to your account before sending a support request.')
        elif not subject or not message_body:
            messages.error(request, 'Subject and message are required.')
        else:
            SupportTicket.objects.create(
                user=request.user,
                role=role,
                registered_email=request.user.email,
                ticket_type=ticket_type,
                subject=subject,
                message=message_body,
            )
            messages.success(request, 'Your message was sent to the admin support inbox.')
            return redirect('contact_support')

    context = {
        'registered_email': request.user.email,
        'has_registered_email': has_registered_email,
        'support_types': SupportTicket.TYPE_CHOICES,
    }
    return render(request, template_name, context)


@login_required(login_url='login')
def request_email_change(request):
    redirect_name = _default_profile_redirect(request.user)
    redirect_target = request.META.get('HTTP_REFERER') or redirect(redirect_name).url

    if request.method != 'POST':
        return redirect(redirect_target)

    requested_email = (request.POST.get('requested_email') or '').strip().lower()
    current_email = (request.user.email or '').strip()

    if not requested_email:
        messages.error(request, 'Enter the new email address you want the admin to approve.')
        return redirect(redirect_target)

    try:
        validate_email(requested_email)
    except ValidationError:
        messages.error(request, 'Enter a valid email address.')
        return redirect(redirect_target)

    if current_email and requested_email.lower() == current_email.lower():
        messages.error(request, 'That email is already linked to your account.')
        return redirect(redirect_target)

    if User.objects.filter(email__iexact=requested_email).exclude(pk=request.user.pk).exists():
        messages.error(request, 'That email is already in use by another account.')
        return redirect(redirect_target)

    SupportTicket.objects.create(
        user=request.user,
        role=_support_role_for_user(request.user),
        registered_email=current_email or requested_email,
        ticket_type=SupportTicket.TYPE_EMAIL_CHANGE,
        subject='Email Change Request',
        message=(
            f'Current email: {current_email or "Not set"}\n'
            f'Requested new email: {requested_email}\n'
            'Please review and approve this email change.'
        ),
    )
    messages.success(request, 'Email change request sent to admin for approval.')
    return redirect(redirect_target)
