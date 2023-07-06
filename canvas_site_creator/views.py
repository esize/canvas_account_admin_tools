import logging

from canvas_api.helpers import accounts as canvas_api_accounts
from common.utils import get_canvas_site_templates_for_school, get_term_data_for_school
from coursemanager.models import CourseInstance, Course, Department, Term
from coursemanager.models import School
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from lti_school_permissions.decorators import lti_permission_required
from django.contrib import messages

from .utils import create_canvas_course_and_section

logger = logging.getLogger(__name__)


@login_required
@lti_permission_required(canvas_api_accounts.ACCOUNT_PERMISSION_MANAGE_COURSES)
@require_http_methods(['GET', 'POST'])
def create_new_course(request):
    sis_account_id = request.LTI['custom_canvas_account_sis_id']

    try:
        school_id = sis_account_id.split(':')[1]
        school = School.objects.get(school_id=school_id)
    except School.objects.DoesNotExist as e:
        logger.exception(f"School does not exist for given sis_account_id: {sis_account_id}")
        raise Exception
    if not school:
        return render(request, 'canvas_site_creator/restricted_access.html', status=403)

    canvas_site_templates = get_canvas_site_templates_for_school(school_id)
    terms, _current_term_id = get_term_data_for_school(sis_account_id)

    if request.method == 'POST':
        post_data = request.POST.dict()

        is_blueprint = post_data.get('is_blueprint', False)
        department = Department.objects.get(school=school_id, short_name=post_data["course-code-type"])
        term = Term.objects.get(term_id=post_data['course-term'])
        course_code_type = 'BLU' if is_blueprint else post_data["course-code-type"]

        logger.info(f'Creating Course and CourseInstance records from the posted site creator info: {post_data}')

        course = Course.objects.create(
            registrar_code=f'{course_code_type}-{post_data["course-code"]}',
            registrar_code_display=f'{course_code_type}-{post_data["course-code"]}',
            school=school,
            department=department
        )

        course_instance = CourseInstance.objects.create(
            course=course,
            section='001',
            exclude_from_catalog=1,
            short_title=post_data['course-short-title'],
            title=post_data['course-title'],
            sync_to_canvas=0,
            term=term
        )

        course_data = {
            'sis_account_id': sis_account_id,
            'course': course,
            'course_instance': course_instance,
            'is_blueprint': is_blueprint
        }

        canvas_course = create_canvas_course_and_section(course_data)

        if canvas_course:
            course_instance.update(sync_to_canvas=1,
                                   canvas_course_id=canvas_course['id'],
                                   parent_course_instance=None)

            messages.add_message(request, messages.SUCCESS, 'Course successfully created')
        else:
            messages.add_message(request, messages.ERROR, 'The course could not successfully be created. '
                                                          'Please try again or contact support if the issue persists.')

    context = {'school_id': school_id,
               'school_name': school.title_short,
               'canvas_site_templates': canvas_site_templates,
               'terms': terms}

    return render(request, 'canvas_site_creator/index.html', context)
