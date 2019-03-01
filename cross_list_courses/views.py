import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from django_auth_lti import const
from django_auth_lti.decorators import lti_role_required
from icommons_common.models import XlistMap
from lti_permissions.decorators import lti_permission_required

logger = logging.getLogger(__name__)


@login_required
@lti_role_required(const.ADMINISTRATOR)
@lti_permission_required(settings.PERMISSION_XLIST_TOOL)
@require_http_methods(['GET'])
def index(request):
    today = datetime.now()
    # The school that this tool is being launched in
    tool_launch_school = request.LTI['custom_canvas_account_sis_id'].split(':')[1]

    # Only get cross listings with current or future terms
    # Either the primary or secondary courses must be from the school launching the tool
    xlist_maps = XlistMap.objects.filter(Q(primary_course_instance__term__end_date__gte=today) |
                                         Q(secondary_course_instance__term__end_date__gte=today) |
                                         Q(primary_course_instance__term__end_date__isnull=True) |
                                         Q(secondary_course_instance__term__end_date__isnull=True)).filter(
                                         Q(primary_course_instance__course__school=tool_launch_school) |
                                         Q(secondary_course_instance__course__school=tool_launch_school))[:10].select_related('primary_course_instance',
                                                                                                                              'secondary_course_instance')

    context = {
        'xlist_maps': xlist_maps,
    }

    return render(request, 'list.html', context=context)
