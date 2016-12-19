# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.conf import settings

from async.models import Process
from bulk_utilities.bulk_course_settings import BulkCourseSettingsOperation
from icommons_common.canvas_utils import SessionInactivityExpirationRC

SDK_CONTEXT = SessionInactivityExpirationRC(**settings.CANVAS_SDK_SETTINGS)

logger = logging.getLogger(__name__)


def bulk_publish_canvas_sites(process_id, account=None, course_list=None, term=None, published=True):
    logger.info("Starting bulk_publish_canvas_sites job")  # todo: more info

    # todo: validate input

    try:
        process = Process.objects.get(id=process_id)
    except Process.DoesNotExist:
        logger.exception(
            "Failed to find Process with id {}".format(process_id))
        raise

    process.update_state(Process.ACTIVE)

    # todo: put options (e.g. published, dry-run, etc) into the details section of process as well
    op_config = {
        'published': 'true' if published else None,
        'account': account,
        'courses': course_list,
        'term': term,
        # todo: remove after debugging
        'dry_run': True
    }
    op = BulkCourseSettingsOperation(op_config)
    try:
        op.execute()
    except Exception as e:
        # todo: examine possible error conditions and how to know if we've accomplished what we want
        process.state = Process.COMPLETE
        process.status = 'failed'
        process.details['error'] = str(e)
        process.details['stats'] = op.get_stats_dict()
        process.save()
        raise

    process.details['stats'] = op.get_stats_dict()
    process.update_state(Process.COMPLETE)

    logger.info("Finished bulk_publish_canvas_sites job")  # todo: more info
    return process
