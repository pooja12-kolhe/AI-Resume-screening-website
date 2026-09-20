import pymupdf
import pytesseract
import re

from PIL import Image

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import ResumeForm, JobDescriptionForm
from .models import Resume, JobDescription
from .matcher import calculate_match
from .skill_extractor import extract_skills
import os
from docx2pdf import convert
from django.conf import settings
from django.http import FileResponse
import os
from docx2pdf import convert
from django.conf import settings

from django.http import FileResponse

def convert_docx_to_pdf(resume):
    """
    Convert a DOCX resume to PDF and return the PDF path.
    """

    docx_path = resume.resume_file.path

    pdf_dir = os.path.join(
        settings.MEDIA_ROOT,
        "converted_resumes"
    )

    os.makedirs(pdf_dir, exist_ok=True)

    pdf_filename = os.path.splitext(
        os.path.basename(docx_path)
    )[0] + ".pdf"

    pdf_path = os.path.join(
        pdf_dir,
        pdf_filename
    )

    # Convert DOCX to PDF
    convert(docx_path, pdf_path)

    return pdf_path

def view_resume(request, resume_id):
    resume = Resume.objects.get(id=resume_id)

    file_path = resume.resume_file.path
    file_name = resume.resume_file.name.lower()

    # PDF → open directly in browser
    if file_name.endswith(".pdf"):
        return FileResponse(
            open(file_path, "rb"),
            content_type="application/pdf"
        )

    # DOCX → convert to PDF
    elif file_name.endswith(".docx"):
        pdf_path = convert_docx_to_pdf(resume)

        return FileResponse(
            open(pdf_path, "rb"),
            content_type="application/pdf"
        )

    # Other formats
    return FileResponse(
        open(file_path, "rb"),
        as_attachment=False
    )



def recruiter_required(view_func):

    @login_required
    def wrapper(request, *args, **kwargs):

        if request.user.role != "recruiter":
            return HttpResponseForbidden(
                "You do not have permission to access this page."
            )

        return view_func(request, *args, **kwargs)

    return wrapper
# Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def clean_ocr_text(text):
    # Remove unwanted OCR symbols
    
    text = re.sub(r'[¢®©«»]', '', text)

    # Replace backslash-star and similar OCR artifacts
    text = text.replace('\\*', '')
    text = text.replace('*', '')

    # Replace multiple spaces with one space
    text = re.sub(r'\s+', ' ', text)

    # Remove spaces around punctuation
    text = re.sub(r'\s+([,:;])', r'\1', text)

    return text.strip()

def extract_resume_text(pdf_path):
    """
    Extract text from a PDF.
    If the PDF contains no selectable text,
    use OCR to extract text from the PDF image.
    """
    doc = pymupdf.open(pdf_path)
    extracted_text = ""

    for page in doc:

        # First try normal PDF text extraction
        text = page.get_text()

        if text.strip():
            extracted_text += text + "\n"

        else:
            # PDF is image-based, so use OCR
            pix = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2)
            )

            img = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            ocr_text = pytesseract.image_to_string(img)
            extracted_text += ocr_text + "\n"

    doc.close()

    return extracted_text.strip()


@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)

        if form.is_valid():
            resume = form.save(commit=False)

            # Assign resume to logged-in user
            resume.user = request.user
            resume.save()

            pdf_path = resume.resume_file.path

            extracted_text = extract_resume_text(pdf_path)
            extracted_text = clean_ocr_text(extracted_text)

            detected_skills = extract_skills(extracted_text)

            resume.extracted_text = extracted_text
            resume.skills = ", ".join(detected_skills)

            resume.save()

            return redirect('upload_success')

    else:
        form = ResumeForm()

    return render(
        request,
        'resumes/upload_resume.html',
        {'form': form}
    )

def upload_success(request):

    return render(
        request,
        'resumes/upload_success.html'
    )

def resume_list(request):

    query = request.GET.get('q', '')

    resumes = Resume.objects.all().order_by('-uploaded_at')

    if query:
        resumes = resumes.filter(
            name__icontains=query
        ) | resumes.filter(
            email__icontains=query
        ) | resumes.filter(
            skills__icontains=query
        )

    for resume in resumes:
        resume.skill_list = [
            skill.strip()
            for skill in resume.skills.split(',')
            if skill.strip()
        ]

    return render(
        request,
        'resumes/resume_list.html',
        {
            'resumes': resumes,
            'query': query,
        }
    )

def create_job_description(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('job_description_success')

    else:
        form = JobDescriptionForm()

    return render(
        request,
        'resumes/job_description.html',
        {'form': form}
    )


def job_description_success(request):
    return render(
        request,
        'resumes/job_description_success.html'
    )

@recruiter_required
def match_resume(request, job_id, resume_id):
    job = JobDescription.objects.get(id=job_id)
    resume = Resume.objects.get(id=resume_id)

    result = calculate_match(
        resume.skills,
        job.description,
        resume.extracted_text
    )

    return render(
        request,
        'resumes/match_result.html',
        {
            'job': job,
            'resume': resume,
            'result': result,
        }
    )
@recruiter_required
def screening(request):
    jobs = JobDescription.objects.all().order_by('-created_at')
    resumes = Resume.objects.all().order_by('-uploaded_at')

    return render(
        request,
        'resumes/screening.html',
        {
            'jobs': jobs,
            'resumes': resumes,
        }
    )
@recruiter_required
def candidate_ranking(request, job_id):

    job = JobDescription.objects.get(id=job_id)

    query = request.GET.get("q", "").strip()
    min_score = request.GET.get("min_score", "").strip()

    resumes = Resume.objects.all()

    # Search by name, email, or skills
    if query:

        resumes = resumes.filter(
            name__icontains=query
        ) | resumes.filter(
            email__icontains=query
        ) | resumes.filter(
            skills__icontains=query
        )

    ranked_candidates = []

    for resume in resumes:

        result = calculate_match(
            resume.skills,
            job.description
        )

        # Minimum score filter
        if min_score:

            try:

                minimum = int(min_score)

                if result["score"] < minimum:
                    continue

            except ValueError:

                pass

        ranked_candidates.append({

            "resume": resume,

            "score": result["score"],

            "matched_skills": result["matched_skills"],

            "missing_skills": result["missing_skills"],

            "recommendation": result["recommendation"],

        })

    # Highest score first
    ranked_candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return render(
        request,
        "resumes/candidate_ranking.html",
        {
            "job": job,
            "ranked_candidates": ranked_candidates,
            "query": query,
            "min_score": min_score,
        }
    )
@recruiter_required
def recruiter_dashboard(request):
    total_resumes = Resume.objects.count()
    total_jobs = JobDescription.objects.count()

    recent_resumes = Resume.objects.all().order_by(
        "-uploaded_at"
    )[:5]

    recent_jobs = JobDescription.objects.all().order_by(
        "-created_at"
    )[:5]

    # Calculate average match score
    match_scores = []

    for resume in Resume.objects.all():
        for job in JobDescription.objects.all():
            result = calculate_match(
                resume.skills,
                job.description,
                resume.extracted_text
            )

            match_scores.append(result["score"])

    if match_scores:
        average_match_score = round(
            sum(match_scores) / len(match_scores)
        )
    else:
        average_match_score = 0

    context = {
        "total_resumes": total_resumes,
        "total_jobs": total_jobs,
        "recent_resumes": recent_resumes,
        "recent_jobs": recent_jobs,
        "average_match_score": average_match_score,
    }

    return render(
        request,
        "resumes/recruiter_dashboard.html",
        context
    )
@recruiter_required
def candidate_detail(request, resume_id):

    resume = Resume.objects.get(id=resume_id)

    skill_list = [
        skill.strip()
        for skill in resume.skills.split(",")
        if skill.strip()
    ]

    return render(
        request,
        "resumes/candidate_detail.html",
        {
            "resume": resume,
            "skill_list": skill_list,
        }
    )
@login_required
def candidate_dashboard(request):
    resumes = Resume.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")

    total_resumes = resumes.count()

    latest_resume = resumes.first()

    for resume in resumes:
        resume.skill_list = [
            skill.strip()
            for skill in resume.skills.split(",")
            if skill.strip()
        ]

    return render(
        request,
        "resumes/candidate_dashboard.html",
        {
            "resumes": resumes,
            "total_resumes": total_resumes,
            "latest_resume": latest_resume,
        }
    )