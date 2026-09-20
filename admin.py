from django.contrib import admin
from .models import Resume, JobDescription


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'phone',
        'uploaded_at',
    )

    search_fields = (
        'name',
        'email',
        'phone',
        'skills',
    )


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'created_at',
    )

    search_fields = (
        'title',
        'description',
    )