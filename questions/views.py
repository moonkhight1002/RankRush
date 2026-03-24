from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.models import Group
from student.models import *
from django.utils import timezone
from student.models import StuExam_DB,StuResults_DB
from questions.questionpaper_models import QPForm
from questions.question_models import QForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.utils.dateparse import parse_datetime
import random
import uuid
import json
from datetime import timedelta
from django.db.models import Sum

def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@login_required(login_url='faculty-login')
def view_exams_prof(request):
    prof = request.user
    prof_user = User.objects.get(username=prof)
    permissions = False
    if prof:
        permissions = has_group(prof,"Professor")
    if permissions:
        new_Form = ExamForm(prof_user)
        if request.method == 'POST' and permissions:
            form = ExamForm(prof_user,request.POST)
            if form.is_valid():
                exam = form.save(commit=False)
                exam.professor = prof
                exam.save()
                form.save_m2m()
                return redirect('view_exams')

        exams = Exam_Model.objects.filter(professor=prof)
        return render(request, 'exam/mainexam.html', {
            'exams': exams, 'examform': new_Form, 'prof': prof,
        })
    else:
        return redirect('view_exams_student')

@login_required(login_url='faculty-login')
def add_question_paper(request):
    prof = request.user
    prof_user = User.objects.get(username=prof)
    permissions = False
    if prof:
        permissions = has_group(prof,"Professor")
    if permissions:
        new_Form = QPForm(prof_user)
        if request.method == 'POST' and permissions:
            form = QPForm(prof_user,request.POST)
            if form.is_valid():
                exam = form.save(commit=False)
                exam.professor = prof_user
                exam.save()
                form.save_m2m()
                messages.success(request, f'Question paper "{exam.qPaperTitle}" saved successfully.')
                return redirect('faculty-add_question_paper')
            new_Form = form
            messages.error(request, 'Question paper could not be saved. Please fix the form errors below.')

        exams = Exam_Model.objects.filter(professor=prof)
        question_papers = Question_Paper.objects.filter(professor=prof_user).order_by('-id')
        return render(request, 'exam/addquestionpaper.html', {
            'exams': exams, 'examform': new_Form, 'prof': prof, 'question_papers': question_papers,
        })
    else:
        return redirect('view_exams_student')

@login_required(login_url='faculty-login')
def add_questions(request):
    prof = request.user
    prof_user = User.objects.get(username=prof)
    permissions = False
    if prof:
        permissions = has_group(prof,"Professor")
    if permissions:
        new_Form = QForm()
        if request.method == 'POST' and permissions:
            form = QForm(request.POST, request.FILES)
            if form.is_valid():
                exam = form.save(commit=False)
                exam.professor = prof_user
                exam.save()
                form.save_m2m()
                messages.success(request, 'Question saved successfully.')
                return redirect('faculty-addquestions')
            new_Form = form
            messages.error(request, 'Question could not be saved. Please fix the form errors below.')

        exams = Exam_Model.objects.filter(professor=prof)
        saved_questions = Question_DB.objects.filter(professor=prof_user).order_by('-qno')
        return render(request, 'exam/addquestions.html', {
            'exams': exams, 'examform': new_Form, 'prof': prof, 'saved_questions': saved_questions,
        })
    else:
        return redirect('view_exams_student')

@login_required(login_url='faculty-login')
def delete_question(request, qno):
    prof = request.user
    permissions = False
    if prof:
        permissions = has_group(prof, "Professor")
    if not permissions:
        return redirect('view_exams_student')
    if request.method != 'POST':
        return redirect('faculty-addquestions')

    question = Question_DB.objects.filter(qno=qno, professor=prof).first()
    if not question:
        messages.error(request, 'Question not found or you do not have permission to delete it.')
        return redirect('faculty-addquestions')

    question_text = question.question
    question.delete()
    messages.success(request, f'Question "{question_text}" deleted successfully.')
    return redirect('faculty-addquestions')

@login_required(login_url='faculty-login')
def delete_question_paper(request, paper_id):
    prof = request.user
    permissions = False
    if prof:
        permissions = has_group(prof, "Professor")
    if not permissions:
        return redirect('view_exams_student')
    if request.method != 'POST':
        return redirect('faculty-add_question_paper')

    question_paper = Question_Paper.objects.filter(id=paper_id, professor=prof).first()
    if not question_paper:
        messages.error(request, 'Question paper not found or you do not have permission to delete it.')
        return redirect('faculty-add_question_paper')

    if question_paper.exams.exists():
        messages.error(request, 'This question paper is already used in a scheduled exam and cannot be deleted.')
        return redirect('faculty-add_question_paper')

    paper_title = question_paper.qPaperTitle
    question_paper.delete()
    messages.success(request, f'Question paper "{paper_title}" deleted successfully.')
    return redirect('faculty-add_question_paper')

@login_required(login_url='faculty-login')
def view_previousexams_prof(request):
    prof = request.user
    student = 0
    exams = Exam_Model.objects.filter(professor=prof)
    return render(request, 'exam/previousexam.html', {
        'exams': exams,'prof': prof
    })

@login_required(login_url='login')
def student_view_previous(request):
    exams = Exam_Model.objects.all()
    list_of_completed = []
    for exam in exams:
        stu_exam = StuExam_DB.objects.filter(
            examname=exam.name,
            qpaper=exam.question_paper,
            student=request.user,
        ).order_by('-id').first()
        if stu_exam and stu_exam.completed == 1:
            list_of_completed.append(exam)

    return render(request,'exam/previousstudent.html',{
        'completed':list_of_completed
    })

@login_required(login_url='faculty-login')
def view_students_prof(request):
    students = User.objects.filter(groups__name = "Student")
    student_name = []
    student_completed = []
    count = 0
    dicts = {}
    examn = Exam_Model.objects.filter(professor=request.user)
    for student in students:
        student_name.append(student.username)
        count = 0
        for exam in examn:
            if StuExam_DB.objects.filter(student=student,examname=exam.name,completed=1).exists():
                count += 1
            else:
                count += 0
        student_completed.append(count)
    i = 0
    for x in student_name:
        dicts[x] = student_completed[i]
        i+=1
    return render(request, 'exam/viewstudents.html', {
        'students':dicts
    })

@login_required(login_url='faculty-login')
def view_results_prof(request):
    prof = request.user
    professor = User.objects.get(username=prof.username)
    examn = Exam_Model.objects.filter(professor=professor)
    attempts = []
    for exam in examn:
        completed_attempts = StuExam_DB.objects.filter(
            examname=exam.name,
            qpaper=exam.question_paper,
            completed=1
        ).select_related('student', 'qpaper')
        attempts.extend(completed_attempts)

    attempts.sort(key=lambda attempt: (attempt.examname.lower(), attempt.student.username.lower()))
    attach_attempt_risk(attempts)
    return render(request, 'exam/resultsstudent.html', {
        'attempts': attempts
    })

@login_required(login_url='faculty-login')
def view_violation_logs_prof(request):
    prof = request.user
    permissions = False
    if prof:
        permissions = has_group(prof, "Professor")
    if not permissions:
        return redirect('view_exams_student')

    current_exam_ids = set(
        Exam_Model.objects.filter(professor=request.user).values_list('id', flat=True)
    )
    logs_queryset = ExamViolationLog.objects.filter(professor=request.user).select_related('student', 'qpaper')
    logs = [log for log in logs_queryset if log.exam_id in current_exam_ids or log.exam_id is None]
    webcam_types = {'no_face', 'multi_face', 'gaze_away', 'camera_permission', 'camera_error', 'camera_disconnected', 'model_error'}
    audio_types = {'audio_activity', 'mic_disconnected'}
    summary = {
        'total_logs': len(logs),
        'warning_logs': sum(log.violation_count for log in logs if log.violation_type == 'warning'),
        'fast_submit_logs': sum(1 for log in logs if log.violation_type == 'fast_submit'),
        'students_flagged': len({log.student_id for log in logs}),
        'webcam_logs': sum(1 for log in logs if log.violation_type in webcam_types),
        'audio_logs': sum(1 for log in logs if log.violation_type in audio_types),
        'general_logs': sum(1 for log in logs if log.violation_type not in webcam_types and log.violation_type not in audio_types),
    }
    return render(request, 'exam/violationlogs.html', {
        'logs': logs,
        'summary': summary,
        'webcam_types': webcam_types,
        'audio_types': audio_types,
    })

@login_required(login_url='faculty-login')
def view_attempt_detail_prof(request, attempt_id):
    prof = request.user
    permissions = False
    if prof:
        permissions = has_group(prof, "Professor")
    if not permissions:
        return redirect('view_exams_student')

    attempt = get_object_or_404(
        StuExam_DB.objects.select_related('student', 'qpaper'),
        pk=attempt_id
    )
    owns_exam = Exam_Model.objects.filter(
        professor=request.user,
        name=attempt.examname,
        question_paper=attempt.qpaper,
    ).exists()
    if not owns_exam:
        messages.error(request, 'You do not have permission to view this attempt.')
        return redirect('faculty-result')

    attempt.risk_level = compute_attempt_risk(attempt)
    logs = ExamViolationLog.objects.filter(
        student=attempt.student,
        exam_name=attempt.examname,
        qpaper=attempt.qpaper,
    )
    return render(request, 'exam/attemptdetail.html', {
        'attempt': attempt,
        'questions': attempt.questions.all().order_by('qno'),
        'logs': logs,
    })

@login_required(login_url='faculty-login')
def reset_student_attempt(request, attempt_id):
    prof = request.user
    permissions = False
    if prof:
        permissions = has_group(prof, "Professor")
    if not permissions:
        return redirect('view_exams_student')
    if request.method != 'POST':
        return redirect('faculty-result')

    attempt = StuExam_DB.objects.filter(pk=attempt_id, completed=1).select_related('student', 'qpaper').first()
    if not attempt:
        messages.error(request, 'Student attempt not found.')
        return redirect('faculty-result')

    owns_exam = Exam_Model.objects.filter(
        professor=request.user,
        name=attempt.examname,
        question_paper=attempt.qpaper,
    ).exists()
    if not owns_exam:
        messages.error(request, 'You do not have permission to reset this attempt.')
        return redirect('faculty-result')

    results_qs = StuResults_DB.objects.filter(student=attempt.student, exams=attempt)
    for result in results_qs:
        result.exams.remove(attempt)

    if attempt.questions.exists():
        attempt.questions.all().delete()
        attempt.questions.clear()

    attempt.score = 0
    attempt.completed = 0
    attempt.save()

    messages.success(request, f'Attempt for {attempt.student.username} on "{attempt.examname}" was reset to pending.')
    return redirect('faculty-result')

@login_required(login_url='login')
def view_exams_student(request):
    exams = Exam_Model.objects.all()
    list_of_completed = []
    list_un = []
    for exam in exams:
        stu_exam = StuExam_DB.objects.filter(
            examname=exam.name,
            qpaper=exam.question_paper,
            student=request.user,
        ).order_by('-id').first()
        if stu_exam:
            if stu_exam.completed == 1:
                list_of_completed.append(exam)
            else:
                list_un.append(exam)
        else:
            list_un.append(exam)

    return render(request,'exam/mainexamstudent.html',{
        'exams':list_un,
        'completed':list_of_completed
    })

@login_required(login_url='login')
def view_students_attendance(request):
    exams = Exam_Model.objects.all()
    list_of_completed = []
    for exam in exams:
        stu_exam = StuExam_DB.objects.filter(
            examname=exam.name,
            qpaper=exam.question_paper,
            student=request.user,
        ).order_by('-id').first()
        if stu_exam and stu_exam.completed == 1:
            list_of_completed.append(exam)

    return render(request,'exam/attendance.html',{
        'completed':list_of_completed
    })

def convert(seconds): 
    min, sec = divmod(seconds, 60) 
    hour, min = divmod(min, 60) 
    min += hour*60
    return "%02d:%02d" % (min, sec) 

def normalize_answer_choice(question, answer_value):
    answer = (answer_value or "").strip()
    option_map = {
        'A': (question.optionA or '').strip(),
        'B': (question.optionB or '').strip(),
        'C': (question.optionC or '').strip(),
        'D': (question.optionD or '').strip(),
    }
    answer_upper = answer.upper()
    if answer_upper in option_map:
        return answer_upper
    answer_lower = answer.lower()
    for choice, option_text in option_map.items():
        if answer_lower == option_text.lower():
            return choice
    return answer_upper


def exam_lock_cache_key(student_id, exam_id):
    return f"exam-lock:{student_id}:{exam_id}"


def exam_session_token_key(exam_id):
    return f"exam_session_token_{exam_id}"


def exam_started_at_key(exam_id):
    return f"exam_started_at_{exam_id}"


def exam_last_seen_key(student_id, exam_id):
    return f"exam-last-seen:{student_id}:{exam_id}"


def get_exam_lock_timeout(exam):
    remaining = int((exam.end_time - timezone.now()).total_seconds())
    return max(300, remaining + 300)


def get_session_stale_cutoff():
    return timezone.now() - timedelta(seconds=45)


def mark_stale_sessions(professor=None):
    sessions = ActiveExamSession.objects.filter(
        status=ActiveExamSession.STATUS_ACTIVE,
        last_seen_at__lt=get_session_stale_cutoff()
    )
    if professor is not None:
        sessions = sessions.filter(professor=professor)
    sessions.update(status=ActiveExamSession.STATUS_STALE)


def compute_attempt_risk(attempt):
    logs = ExamViolationLog.objects.filter(
        student=attempt.student,
        exam_name=attempt.examname,
        qpaper=attempt.qpaper,
    )
    warning_total = logs.filter(violation_type='warning').aggregate(total=Sum('violation_count'))['total'] or 0
    fast_submit_count = logs.filter(violation_type='fast_submit').count()
    risk_score = warning_total + (fast_submit_count * 3)
    if risk_score >= 6:
        return 'High'
    if risk_score >= 3:
        return 'Medium'
    return 'Low'


def attach_attempt_risk(attempts):
    for attempt in attempts:
        attempt.risk_level = compute_attempt_risk(attempt)
    return attempts


def exam_window_status(exam):
    now = timezone.now()
    if now < exam.start_time:
        return 'before'
    if now > exam.end_time:
        return 'after'
    return 'open'


def log_violation(student, exam, violation_type, detail="", violation_count=1, session_token=""):
    professor = None
    if exam.professor_id:
        professor = exam.professor
    return ExamViolationLog.objects.create(
        student=student,
        professor=professor,
        exam_id=exam.id,
        exam_name=exam.name,
        qpaper=exam.question_paper,
        violation_type=violation_type,
        detail=detail,
        violation_count=violation_count,
        session_token=session_token or "",
    )


def sync_active_exam_session(student, exam, session_token, status=ActiveExamSession.STATUS_ACTIVE, completed=False):
    professor = exam.professor if exam.professor_id else None
    session, _ = ActiveExamSession.objects.get_or_create(
        session_token=session_token,
        defaults={
            'student': student,
            'professor': professor,
            'exam_id': exam.id,
            'exam_name': exam.name,
            'qpaper': exam.question_paper,
            'status': status,
            'started_at': timezone.now(),
            'last_seen_at': timezone.now(),
        }
    )
    session.student = student
    session.professor = professor
    session.exam_id = exam.id
    session.exam_name = exam.name
    session.qpaper = exam.question_paper
    session.status = status
    session.last_seen_at = timezone.now()
    if completed:
        session.completed_at = timezone.now()
    session.save()
    return session


@login_required(login_url='login')
@require_POST
def log_exam_violation(request, id):
    exam = get_object_or_404(Exam_Model, pk=id)
    lock_key = exam_lock_cache_key(request.user.id, exam.id)
    session_token = request.session.get(exam_session_token_key(exam.id))
    active_token = cache.get(lock_key)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    submitted_token = payload.get("session_token", "")
    if not submitted_token or submitted_token != session_token or (active_token and submitted_token != active_token):
        return JsonResponse({"logged": False, "reason": "inactive_session"}, status=409)

    violation_type = (payload.get("violation_type") or "warning").strip()[:50]
    detail = (payload.get("detail") or "").strip()[:255]
    violation_count = int(payload.get("violation_count") or 1)
    log_violation(
        request.user,
        exam,
        violation_type=violation_type,
        detail=detail,
        violation_count=violation_count,
        session_token=submitted_token,
    )
    return JsonResponse({"logged": True})


@login_required(login_url='login')
@require_POST
def exam_session_heartbeat(request, id):
    exam = get_object_or_404(Exam_Model, pk=id)
    lock_key = exam_lock_cache_key(request.user.id, exam.id)
    last_seen_key = exam_last_seen_key(request.user.id, exam.id)
    session_token = request.session.get(exam_session_token_key(exam.id))
    active_token = cache.get(lock_key)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    submitted_token = payload.get("session_token", "")
    if not submitted_token or submitted_token != session_token or (active_token and submitted_token != active_token):
        return JsonResponse({"ok": False, "reason": "inactive_session"}, status=409)

    timeout = get_exam_lock_timeout(exam)
    cache.set(lock_key, submitted_token, timeout=timeout)
    cache.set(last_seen_key, timezone.now().isoformat(), timeout=timeout)
    sync_active_exam_session(request.user, exam, submitted_token, status=ActiveExamSession.STATUS_ACTIVE)
    return JsonResponse({"ok": True, "heartbeat_at": timezone.now().isoformat()})

@login_required(login_url='login')
def appear_exam(request,id):
    student = request.user
    if request.method == 'GET':
        proctoring_settings = ProctoringSettings.get_solo()
        exam = get_object_or_404(Exam_Model, pk=id)
        window_state = exam_window_status(exam)
        if window_state == 'before':
            messages.error(request, f'This exam has not started yet. It opens at {exam.start_time}.')
            return redirect('view_exams_student')
        if window_state == 'after':
            messages.error(request, 'This exam window has already ended.')
            return redirect('view_exams_student')

        lock_key = exam_lock_cache_key(student.id, exam.id)
        session_token_key = exam_session_token_key(exam.id)
        started_at_session_key = exam_started_at_key(exam.id)
        current_session_token = request.session.get(session_token_key)
        active_lock_token = cache.get(lock_key)

        if active_lock_token:
            active_session = ActiveExamSession.objects.filter(
                session_token=active_lock_token,
                student=student,
                exam_id=exam.id
            ).first()
            if active_session and active_session.status == ActiveExamSession.STATUS_ACTIVE and active_session.last_seen_at < get_session_stale_cutoff():
                active_session.status = ActiveExamSession.STATUS_STALE
                active_session.save(update_fields=['status'])
                cache.delete(lock_key)
                active_lock_token = None

        if active_lock_token and current_session_token != active_lock_token:
            messages.error(request, 'This exam is already active in another session. Finish it there or wait for it to expire.')
            return redirect('view_exams_student')

        if not current_session_token:
            current_session_token = uuid.uuid4().hex
            request.session[session_token_key] = current_session_token

        if not request.session.get(started_at_session_key):
            request.session[started_at_session_key] = timezone.now().isoformat()

        request.session.modified = True
        timeout = get_exam_lock_timeout(exam)
        cache.set(lock_key, current_session_token, timeout=timeout)
        cache.set(exam_last_seen_key(student.id, exam.id), timezone.now().isoformat(), timeout=timeout)
        sync_active_exam_session(student, exam, current_session_token, status=ActiveExamSession.STATUS_ACTIVE)

        time_delta = exam.end_time - exam.start_time
        time = convert(time_delta.seconds)
        time = time.split(":")
        mins = time[0]
        secs = time[1]

        questions = list(exam.question_paper.questions.all())
        random.shuffle(questions)
        question_cards = []
        for question in questions:
            options = [
                {'value': 'A', 'text': question.optionA, 'image_url': question.optionA_image.url if question.optionA_image else ''},
                {'value': 'B', 'text': question.optionB, 'image_url': question.optionB_image.url if question.optionB_image else ''},
                {'value': 'C', 'text': question.optionC, 'image_url': question.optionC_image.url if question.optionC_image else ''},
                {'value': 'D', 'text': question.optionD, 'image_url': question.optionD_image.url if question.optionD_image else ''},
            ]
            random.shuffle(options)
            display_labels = ['A', 'B', 'C', 'D']
            for index, option in enumerate(options):
                option['display_value'] = display_labels[index]
            question_cards.append({
                'qno': question.qno,
                'question': question.question,
                'question_image_url': question.question_image.url if getattr(question, 'question_image', None) else '',
                'options': options,
            })

        context = {
            "exam":exam,
            "question_cards":question_cards,
            "secs":secs,
            "mins":mins,
            "exam_session_token": current_session_token,
            "proctoring_settings": proctoring_settings,
        }
        return render(request,'exam/giveExam.html',context)
    if request.method == 'POST' :
        student = User.objects.get(username=request.user.username)
        exam_id = request.POST.get('exam_id')
        if exam_id:
            examMain = get_object_or_404(Exam_Model, pk=exam_id)
            paper = examMain.name
        else:
            paper = request.POST['paper']
            examMain = get_object_or_404(Exam_Model, name=paper)

        if exam_window_status(examMain) != 'open':
            messages.error(request, 'This exam can no longer be submitted because the exam window is closed.')
            return redirect('view_exams_student')

        lock_key = exam_lock_cache_key(student.id, examMain.id)
        session_token_key = exam_session_token_key(examMain.id)
        started_at_session_key = exam_started_at_key(examMain.id)
        submitted_session_token = request.POST.get('exam_token', '')
        current_session_token = request.session.get(session_token_key)
        active_lock_token = cache.get(lock_key)

        if not submitted_session_token or submitted_session_token != current_session_token or (active_lock_token and submitted_session_token != active_lock_token):
            messages.error(request, 'This exam session is no longer active. Reopen the exam and try again.')
            return redirect('view_exams_student')

        stuExam = StuExam_DB.objects.filter(
            examname=paper,
            student=student,
            qpaper=examMain.question_paper,
            completed=0,
        ).order_by('-id').first()
        if not stuExam:
            stuExam = StuExam_DB.objects.create(
                examname=paper,
                student=student,
                qpaper=examMain.question_paper,
            )

        qPaper = examMain.question_paper
        stuExam.qpaper = qPaper

        if stuExam.questions.exists():
            stuExam.questions.all().delete()
            stuExam.questions.clear()

        examScore = 0
        qPaperQuestionsList = examMain.question_paper.questions.all()
        for original_question in qPaperQuestionsList:
            ans = request.POST.get(f'question_{original_question.qno}', 'E')
            student_question = Stu_Question(
                student=student,
                question=original_question.question,
                question_image=original_question.question_image,
                optionA=original_question.optionA,
                optionA_image=original_question.optionA_image,
                optionB=original_question.optionB,
                optionB_image=original_question.optionB_image,
                optionC=original_question.optionC,
                optionC_image=original_question.optionC_image,
                optionD=original_question.optionD,
                optionD_image=original_question.optionD_image,
                answer=original_question.answer,
                choice=ans,
                max_marks=original_question.max_marks,
            )
            student_question.save()
            stuExam.questions.add(student_question)

            correct_choice = normalize_answer_choice(original_question, original_question.answer)
            if ans.upper() == correct_choice:
                examScore += original_question.max_marks

        started_at_raw = request.session.get(started_at_session_key)
        started_at = parse_datetime(started_at_raw) if started_at_raw else None
        if started_at and timezone.is_naive(started_at):
            started_at = timezone.make_aware(started_at, timezone.get_current_timezone())
        elapsed_seconds = None
        if started_at:
            elapsed_seconds = max(0, int((timezone.now() - started_at).total_seconds()))
            suspicious_threshold = max(30, min(len(qPaperQuestionsList) * 12, 120))
            if elapsed_seconds < suspicious_threshold:
                log_violation(
                    student,
                    examMain,
                    violation_type='fast_submit',
                    detail=f'Submitted in {elapsed_seconds} seconds.',
                    session_token=submitted_session_token,
                )

        stuExam.completed = 1
        stuExam.score = examScore
        stuExam.save()
        results = StuResults_DB.objects.get_or_create(student=request.user)[0]
        results.exams.add(stuExam)
        results.save()

        sync_active_exam_session(student, examMain, submitted_session_token, status=ActiveExamSession.STATUS_COMPLETED, completed=True)
        cache.delete(lock_key)
        cache.delete(exam_last_seen_key(student.id, examMain.id))
        request.session.pop(session_token_key, None)
        request.session.pop(started_at_session_key, None)
        return redirect('view_exams_student')

@login_required(login_url='faculty-login')
def view_active_sessions_prof(request):
    prof = request.user
    permissions = False
    if prof:
        permissions = has_group(prof, "Professor")
    if not permissions:
        return redirect('view_exams_student')

    mark_stale_sessions(request.user)
    sessions = ActiveExamSession.objects.filter(professor=request.user).select_related('student', 'qpaper')
    summary = {
        'active': sessions.filter(status=ActiveExamSession.STATUS_ACTIVE).count(),
        'stale': sessions.filter(status=ActiveExamSession.STATUS_STALE).count(),
        'completed': sessions.filter(status=ActiveExamSession.STATUS_COMPLETED).count(),
    }
    return render(request, 'exam/activesessions.html', {
        'sessions': sessions,
        'summary': summary,
    })

@login_required(login_url='login')
def result(request,id):
    student = request.user
    exam = Exam_Model.objects.get(pk=id)
    score = StuExam_DB.objects.get(student=student,examname=exam.name,qpaper=exam.question_paper).score
    return render(request,'exam/result.html',{'exam':exam,"score":score})
