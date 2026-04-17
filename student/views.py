from django.shortcuts import render,redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from .forms import StudentForm, StudentInfoForm
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode 
from django.urls import reverse
try:
    from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
except ImportError:
    from django.utils.encoding import force_bytes, force_text as force_str, DjangoUnicodeDecodeError
from .utils import account_activation_token
from django.core.mail import EmailMessage
import threading
from django.contrib.auth.models import User
from studentPreferences.models import StudentPreferenceModel
from django.contrib.auth.models import Group
from django.db.models import Sum
from .models import StuExam_DB
from .models import StudentInfo
from examProject.text_utils import split_full_name
from questions.models import Exam_Model

def redirect_authenticated_user(request):
    if not request.user.is_authenticated:
        return None
    if request.user.is_superuser:
        return redirect('/admin/')
    if request.user.groups.filter(name='Professor').exists():
        return redirect('faculty-index')
    return redirect('index')

@login_required(login_url='login')
def index(request):
    ranked_scores = list(
        StuExam_DB.objects.filter(completed=1)
        .values('student')
        .annotate(total_score=Sum('score'))
        .order_by('-total_score', 'student')
    )

    student_rank = None
    total_ranked_students = len(ranked_scores)
    student_total_score = 0

    for position, item in enumerate(ranked_scores, start=1):
        if item['student'] == request.user.id:
            student_total_score = item['total_score'] or 0
            if student_total_score > 0:
                student_rank = position
            break

    exams_completed = StuExam_DB.objects.filter(student=request.user, completed=1).count()
    total_exams = Exam_Model.objects.count()
    available_exams = max(total_exams - exams_completed, 0)

    return render(request, 'student/index.html', {
        'student_rank': student_rank,
        'total_ranked_students': total_ranked_students,
        'student_total_score': student_total_score,
        'exams_completed': exams_completed,
        'available_exams': available_exams,
    })

class Register(View):
    def get(self,request):
        redirect_response = redirect_authenticated_user(request)
        if redirect_response:
            return redirect_response
        student_form = StudentForm()
        student_info_form = StudentInfoForm()
        return render(request,'student/register.html',{'student_form':student_form,'student_info_form':student_info_form})
    
    def post(self,request):
        student_form = StudentForm(data=request.POST)
        student_info_form = StudentInfoForm(data=request.POST)
        email = request.POST['email']

        if student_form.is_valid() and student_info_form.is_valid():
            student = student_form.save(commit=False)
            first_name, last_name = split_full_name(student_form.cleaned_data.get('full_name'))
            student.first_name = first_name
            student.last_name = last_name
            student.set_password(student.password)
            student.is_active = False
            my_group = Group.objects.get_or_create(name='Student')
            my_group[0].user_set.add(student)
            student.save()

            uidb64 = urlsafe_base64_encode(force_bytes(student.pk))
            domain = get_current_site(request).domain
            link = reverse('activate',kwargs={'uidb64':uidb64,'token':account_activation_token.make_token(student)})
            activate_url = 'http://' + domain +link
            email_subject = 'Activate your Exam Portal account'
            email_body = 'Hi.Please use this link to verify your account\n' + activate_url + ".\n\n You are receiving this message because you registered on " + domain +". If you didn't register please contact support team on " + domain 
            fromEmail = 'noreply@exam.com'
            email = EmailMessage(
				email_subject,
				email_body,
				fromEmail,
				[email],
            )
            student_info = student_info_form.save(commit=False)
            student_info.user = student
            if 'picture' in request.FILES:
                student_info.picture = request.FILES['picture']
            student_info.save()
            messages.success(request,"Registered Succesfully. Check Email for confirmation")
            EmailThread(email).start()
            return redirect('login')
        else:
            print(student_form.errors,student_info_form.errors)
            return render(request,'student/register.html',{'student_form':student_form,'student_info_form':student_info_form})
    
@method_decorator([never_cache, ensure_csrf_cookie], name='get')
@method_decorator(never_cache, name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(View):
	def get(self,request):
		redirect_response = redirect_authenticated_user(request)
		if redirect_response:
			return redirect_response
		get_token(request)
		response = render(request,'student\login.html')
		response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
		response['Pragma'] = 'no-cache'
		response['Expires'] = '0'
		return response
	def post(self,request):
		username = request.POST['username']
		password = request.POST['password']

		if username and password:
			exis = User.objects.filter(username=username).exists()
			user_ch = None
			if exis:
				user_ch = User.objects.get(username=username)
				if user_ch.is_superuser:
					messages.error(request,'Invalid credentials')
					return render(request,'student/login.html')
				if user_ch.groups.filter(name='Professor').exists():
					messages.error(request,'Invalid credentials')
					return render(request,'student/login.html')
			user = auth.authenticate(username=username,password=password)
			if user:
				if user.is_active:
					auth.login(request,user)
					student_pref = StudentPreferenceModel.objects.filter(user = request.user).exists()
					email = User.objects.get(username=username).email

					email_subject = 'You Logged into your Portal account'
					email_body = "If you think someone else logged in. Please contact support or reset your password.\n\nYou are receving this message because you have enabled login email notifications in portal settings. If you don't want to recieve such emails in future please turn the login email notifications off in settings."
					fromEmail = 'noreply@exam.com'
					email = EmailMessage(
						email_subject,
						email_body,
						fromEmail,
						[email],
					)
					if student_pref :
						student = StudentPreferenceModel.objects.get(user=request.user)
						sendEmail = student.sendEmailOnLogin 
					if not student_pref :
						EmailThread(email).start()
					elif sendEmail:
						EmailThread(email).start()
					display_name = user.get_full_name() or user.username
					messages.success(request,"Welcome, "+ display_name + ". You are now logged in.")

					return redirect('index')
			
			else:
				if exis and user_ch:
					if user_ch.is_active:
						messages.error(request,'Invalid credentials')	
						return render(request,'student/login.html')
					else:
						messages.error(request,'Account not Activated')
						return render(request,'student/login.html')

		messages.error(request,'Please fill all fields')
		return render(request,'student/login.html')

class LogoutView(View):
	def post(self,request):
		auth.logout(request)
		messages.success(request,'Logged Out')
		return redirect('login')


@login_required(login_url='login')
def update_profile_picture(request):
	if request.method != 'POST':
		return redirect('index')

	picture = request.FILES.get('picture')
	if not picture:
		messages.error(request, 'Select an image file to update your profile picture.')
		return redirect(request.META.get('HTTP_REFERER', 'index'))

	profile, _ = StudentInfo.objects.get_or_create(user=request.user)
	profile.picture = picture
	profile.save(update_fields=['picture'])
	messages.success(request, 'Profile picture updated successfully.')
	return redirect(request.META.get('HTTP_REFERER', 'index'))

class EmailThread(threading.Thread):
	def __init__(self,email):
		self.email = email
		threading.Thread.__init__(self)

	
	def run(self):
		self.email.send(fail_silently = False)

class VerificationView(View):
	def get(self,request,uidb64,token):
		try:
			id = force_str(urlsafe_base64_decode(uidb64))
			user = User.objects.get(pk=id)
			if not account_activation_token.check_token(user,token):
				messages.error(request,"User already Activated. Please Proceed With Login")
				return redirect("login")
			if user.is_active:
				return redirect('login')
			user.is_active = True
			user.save()
			messages.success(request,'Account activated Sucessfully')
			return redirect('login')
		except Exception as e:
			raise e
		return redirect('login')
	
