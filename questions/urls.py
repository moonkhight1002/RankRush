from django.urls import path
from . import views
urlpatterns = [
    path('prof/viewexams/',views.view_exams_prof,name="view_exams"),
    path('prof/viewpreviousexams/',views.view_previousexams_prof,name="faculty-previous"),
    path('prof/viewresults/',views.view_results_prof,name="faculty-result"),
    path('prof/viewviolations/',views.view_violation_logs_prof,name="faculty-violations"),
    path('prof/viewsessions/',views.view_active_sessions_prof,name="faculty-sessions"),
    path('prof/viewresults/<int:attempt_id>/',views.view_attempt_detail_prof,name="faculty-attempt-detail"),
    path('prof/viewresults/<int:attempt_id>/reset/',views.reset_student_attempt,name="faculty-reset-attempt"),
    path('prof/addquestions/',views.add_questions,name="faculty-addquestions"),
    path('prof/addquestions/<int:qno>/delete/',views.delete_question,name="faculty-delete-question"),
    path('prof/addnewquestionpaper/',views.add_question_paper,name="faculty-add_question_paper"),
    path('prof/addnewquestionpaper/<int:paper_id>/delete/',views.delete_question_paper,name="faculty-delete-question-paper"),
    path('prof/viewstudents/',views.view_students_prof,name="faculty-student"),
    path('student/viewexams/',views.view_exams_student,name="view_exams_student"),
    path('student/previous/',views.student_view_previous,name="student-previous"),
    path('student/appear/<int:id>',views.appear_exam,name = "appear-exam"),
    path('student/appear/<int:id>/heartbeat/',views.exam_session_heartbeat,name="exam-session-heartbeat"),
    path('student/appear/<int:id>/log-violation/',views.log_exam_violation,name="log-exam-violation"),
    path('student/result/<int:id>',views.result,name = "result"),
    path('student/attendance/',views.view_students_attendance,name="view_students_attendance")
]
