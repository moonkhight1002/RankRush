from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.urls import path
from .models import *


def proctor_ml_test_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only superusers can access the proctoring ML test.")

    settings_obj = ProctoringSettings.get_solo()
    if request.method == "POST":
        idle_baseline = float(request.POST.get("idle_baseline", settings_obj.idle_baseline) or settings_obj.idle_baseline)
        speech_threshold = float(request.POST.get("speech_threshold", settings_obj.speech_threshold) or settings_obj.speech_threshold)
        ambient_threshold = float(request.POST.get("ambient_threshold", settings_obj.ambient_threshold) or settings_obj.ambient_threshold)
        voice_match_threshold = float(request.POST.get("voice_match_threshold", settings_obj.voice_match_threshold) or settings_obj.voice_match_threshold)

        settings_obj.idle_baseline = min(max(idle_baseline, 0.005), 0.100)
        settings_obj.speech_threshold = min(max(speech_threshold, 0.050), 0.300)
        settings_obj.ambient_threshold = min(max(ambient_threshold, 0.080), 0.800)
        settings_obj.voice_match_threshold = min(max(voice_match_threshold, 0.200), 8.000)
        settings_obj.quiet_range_summary = (request.POST.get("quiet_range_summary", settings_obj.quiet_range_summary) or "").strip()[:255]
        settings_obj.ambient_range_summary = (request.POST.get("ambient_range_summary", settings_obj.ambient_range_summary) or "").strip()[:255]
        settings_obj.speech_range_summary = (request.POST.get("speech_range_summary", settings_obj.speech_range_summary) or "").strip()[:255]
        settings_obj.precheck_ms = min(max(int(request.POST.get("precheck_ms", settings_obj.precheck_ms) or settings_obj.precheck_ms), 500), 8000)
        settings_obj.no_face_ms = min(max(int(request.POST.get("no_face_ms", settings_obj.no_face_ms) or settings_obj.no_face_ms), 500), 15000)
        settings_obj.multi_face_ms = min(max(int(request.POST.get("multi_face_ms", settings_obj.multi_face_ms) or settings_obj.multi_face_ms), 500), 15000)
        settings_obj.gaze_away_ms = min(max(int(request.POST.get("gaze_away_ms", settings_obj.gaze_away_ms) or settings_obj.gaze_away_ms), 500), 15000)
        settings_obj.save()
        messages.success(request, "Proctoring settings and calibration data saved.")
    context = {
        **admin.site.each_context(request),
        "title": "Proctoring ML Test",
        "proctoring_settings": settings_obj,
    }
    return TemplateResponse(request, "admin/proctor_ml_test.html", context)


_original_get_urls = admin.site.get_urls


def _custom_admin_urls():
    custom_urls = [
        path(
            "proctor-ml-test/",
            admin.site.admin_view(proctor_ml_test_view),
            name="proctor-ml-test",
        ),
    ]
    return custom_urls + _original_get_urls()


admin.site.get_urls = _custom_admin_urls

admin.site.register(StudentInfo)
admin.site.register(Stu_Question)
admin.site.register(StuExam_DB)
admin.site.register(StuResults_DB)
admin.site.register(ExamViolationLog)
admin.site.register(ActiveExamSession)
admin.site.register(ProctoringSettings)
