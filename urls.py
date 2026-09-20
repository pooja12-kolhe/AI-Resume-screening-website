from django.urls import path
from . import views


urlpatterns = [
    path(
        "upload/",
        views.upload_resume,
        name="upload_resume"
    ),

    path(
        "success/",
        views.upload_success,
        name="upload_success"
    ),

    path(
        "list/",
        views.resume_list,
        name="resume_list"
    ),

    path(
        "job-description/",
        views.create_job_description,
        name="create_job_description"
    ),

    path(
        "job-description/success/",
        views.job_description_success,
        name="job_description_success"
    ),

    path(
        "match/<int:job_id>/<int:resume_id>/",
        views.match_resume,
        name="match_resume"
    ),

    path(
        "screening/",
        views.screening,
        name="screening"
    ),

    path(
        "ranking/<int:job_id>/",
        views.candidate_ranking,
        name="candidate_ranking"
    ),

    path(
        "dashboard/",
        views.recruiter_dashboard,
        name="recruiter_dashboard"
    ),

    path(
        "candidate/<int:resume_id>/",
        views.candidate_detail,
        name="candidate_detail"
    ),

    path(
        "candidate-dashboard/",
        views.candidate_dashboard,
        name="candidate_dashboard"
    ),
    path(
    "view-resume/<int:resume_id>/",
    views.view_resume,
    name="view_resume"
),
]