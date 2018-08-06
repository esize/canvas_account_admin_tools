from __future__ import unicode_literals

import json
import logging
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from bulk_course_settings import constants
from bulk_course_settings.models import BulkCourseSettingsJobDetails
from canvas_sdk.exceptions import CanvasAPIError
from canvas_sdk.methods.accounts import list_active_courses_in_account
from canvas_sdk.methods.courses import update_course as sdk_update_course
from canvas_sdk.utils import get_all_list_data
from icommons_common.canvas_utils import SessionInactivityExpirationRC
from icommons_common.models import Term

logger = logging.getLogger(__name__)

SDK_CONTEXT = SessionInactivityExpirationRC(**settings.CANVAS_SDK_SETTINGS)
boto3.set_stream_logger('')
AWS_REGION_NAME = settings.BULK_COURSE_SETTINGS['aws_region_name']
AWS_ACCESS_KEY_ID = settings.BULK_COURSE_SETTINGS['aws_access_key_id']
AWS_SECRET_ACCESS_KEY = settings.BULK_COURSE_SETTINGS['aws_secret_access_key']
QUEUE_NAME = settings.BULK_COURSE_SETTINGS['job_queue_name']

KW = {
    'aws_access_key_id': AWS_ACCESS_KEY_ID,
    'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
    'region_name':  AWS_REGION_NAME
}

API_MAPPING = {
    'is_public': 'course_is_public',
    'is_public_to_auth_users': 'course_is_public_to_auth_users',
    'public_syllabus': 'course_public_syllabus',
    'public_syllabus_to_auth': 'course_public_syllabus_to_auth'
}

REVERSE_API_MAPPING = {
    'course_is_public': 'is_public',
    'course_is_public_to_auth_users': 'is_public_to_auth_users',
    'course_public_syllabus': 'public_syllabus',
    'course_public_syllabus_to_auth': 'public_syllabus_to_auth'
}

try:
    SQS = boto3.resource('sqs', **KW)

except ClientError as e:
    logger.error('Error configuring sqs client: %s', e, exc_info=True)
    raise
except Exception as e:
    logger.exception('Error configuring sqs')
    raise


def get_term_data_for_school(school_sis_account_id):
    school_id = school_sis_account_id.split(':')[1]
    year_floor = datetime.now().year - 5  # Limit term query to the past 5 years
    terms = []
    query_set = Term.objects.filter(
        school=school_id,
        active=1,
        calendar_year__gt=year_floor
    ).exclude(
        start_date__isnull=True
    ).exclude(
        end_date__isnull=True
    ).order_by(
        '-end_date', 'term_code__sort_order'
    )
    for term in query_set:
        terms.append({
            'id': str(term.term_id),
            'name': term.display_name
        })
    return terms


def queue_bulk_settings_job(bulk_settings_id, school_id, term_id, setting_to_be_modified, desired_setting, queue_name=QUEUE_NAME):
    logger.debug("queue_bulk_settings_job:  bulk_settings_id=%s, school_id=%s, term_id=%s, setting_to_be_modified=%s ,"
                 "desired_setting=%s"
                 % (bulk_settings_id, school_id, term_id, setting_to_be_modified, desired_setting))
    queue = SQS.get_queue_by_name(QueueName=queue_name)
    message = queue.send_message(
        MessageBody='_'.join(['msg_body', str(bulk_settings_id)]),
        MessageAttributes={

            'bulk_settings_id': {
                'StringValue': str(bulk_settings_id),
                'DataType': 'Number'
            },
            'school_id': {
                'StringValue': school_id,
                'DataType': 'String'
            },
            'term_id': {
                'StringValue': str(term_id),
                'DataType': 'String'
            },
            'setting_to_be_modified': {
                'StringValue': setting_to_be_modified,
                'DataType': 'String'
            },
            'desired_setting': {
                'StringValue': str(desired_setting),
                'DataType': 'String'
            }
        }
    )
    logger.debug(json.dumps(message, indent=2))

    return message['MessageId']


def get_canvas_courses(account_id=None, term_id=None, search_term=None, state=None):
    try:
        canvas_courses = get_all_list_data(
            SDK_CONTEXT,
            list_active_courses_in_account,
            account_id=account_id,
            enrollment_term_id=term_id,
            search_term=search_term,
            state=state,
        )

        total_count = len(canvas_courses)
        logger.info('Found %d courses' % total_count)

    except Exception as e:
        message = 'Error listing active courses in account'
        if isinstance(e, CanvasAPIError):
            message += ', SDK error details={}'.format(e)
        logger.exception(message)
        raise e

    return canvas_courses


def check_and_update_course(course, bulk_course_settings_job):
    update_args = build_update_arg_for_course(course, bulk_course_settings_job)
    logger.debug('Update args for course {}: {}'.format(course['id'], update_args))

    # Only update the course if the arg dict is not empty
    if len(update_args):
        update_course(course, update_args, bulk_course_settings_job)
    else:
        # TODO
        # Create detail obj with skipped status
        print 'SKIPPING COURSE'
        pass


def build_update_arg_for_course(course, bulk_course_settings_job):
    # Since we only update one setting at a time, check if the given courses setting differs from the value we want
    # and if it does make it an update argument.
    update_args = {}

    setting_to_be_modified = bulk_course_settings_job.setting_to_be_modified
    desired_value = bulk_course_settings_job.desired_setting

    if course[setting_to_be_modified] is not True and desired_value is True:
        update_args[API_MAPPING[setting_to_be_modified]] = 'true'
    if course[setting_to_be_modified] is True and desired_value is False:
        update_args[API_MAPPING[setting_to_be_modified]] = 'false'

    return update_args


def update_course(course, update_args, bulk_course_settings_job):
    setting_args = update_args.copy()
    setting_to_change, desired_value = setting_args.popitem()
    bulk_setting_detail = BulkCourseSettingsJobDetails.objects.create(
        parent_job_process_id=bulk_course_settings_job,
        canvas_course_id=course['id'],
        current_setting_value=course[REVERSE_API_MAPPING[setting_to_change]],
        is_modified=True,
        prior_state=course,
        post_state=''
    )

    try:
        update_response = sdk_update_course(SDK_CONTEXT, course['id'], **update_args)

        bulk_setting_detail.workflow_status = constants.COMPLETED
        bulk_setting_detail.post_state = update_response.json()
        bulk_setting_detail.save()
    except CanvasAPIError as e:
        message = 'Error updating course {} via SDK with parameters={}, SDK error details={}'\
            .format(course['id'], update_args, e)
        logger.exception(message)

        bulk_setting_detail.workflow_status = constants.FAILED
        bulk_setting_detail.save()
