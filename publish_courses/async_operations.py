# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.conf import settings
from rq import get_current_job

from async.models import Process
from bulk_utilities.bulk_course_settings import BulkCourseSettingsOperation
from icommons_common.canvas_utils import SessionInactivityExpirationRC

SDK_CONTEXT = SessionInactivityExpirationRC(**settings.CANVAS_SDK_SETTINGS)

logger = logging.getLogger(__name__)


def bulk_publish_canvas_sites(process_id, account=None, course_list=None,
                              term=None, published=True, dry_run=False):
    logger.info("Starting bulk_publish_canvas_sites job {}".format(process_id))

    try:
        job = get_current_job()
        logger.debug("RQ job details: {}".format(job.to_dict()))
    except Exception as e:
        logger.exception(
            "Failed to get current job information from RQ for process_id: {}. "
            "(Possibly running bulk_publish_canvas_sites() outside of an RQ "
            "worker?)".format(process_id))

    try:
        process = Process.objects.get(id=process_id)
    except Process.DoesNotExist:
        logger.exception(
            "Failed to find Process with id {}".format(process_id))
        raise

    op_config = {
        'published': 'true' if published else None,
        'account': account,
        'courses': course_list,
        'term': term,
        'dry_run': dry_run
    }
    process.state = Process.ACTIVE
    process.details['op_config'] = op_config
    process.save(update_fields=['state', 'details'])

    op = BulkCourseSettingsOperation(op_config)
    try:
        op.execute()
    except Exception as e:
        logger.exception("bulk_publish_canvas_sites job {} "
                         "failed".format(process_id))
        process.status = 'failed'
        process.details['error'] = str(e)

    process.details['stats'] = op.get_stats_dict()
    process.state = Process.COMPLETE
    process.save(update_fields=['state', 'status', 'details'])

    logger.info("Finished bulk_publish_canvas_sites job {}".format(process_id))
    return process
