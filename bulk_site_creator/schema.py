import datetime
from enum import Enum
from typing import Optional

from ulid import ULID

"""
Defines the schema of the dynamodb table.
"""


class JobRecord:
    def __init__(
        self,
        school: str,
        sis_account_id: str,
        term_id: str,
        term_name: Optional[str],
        department_id: Optional[str],
        department_name: Optional[str],
        course_group_id: Optional[str],
        course_group_name: Optional[str],
        template_id: Optional[str],
        user_id: str,
        user_full_name: str,
        user_email: str,
        workflow_state: str,
    ):
        self.pk = f"SCHOOL#{school.upper()}"
        self.sk = f"JOB#{str(ULID())}"
        self.sis_account_id = sis_account_id
        self.term_id = term_id
        self.term_name = term_name
        self.department_id = department_id
        self.department_name = department_name
        self.course_group_id = course_group_id
        self.course_group_name = course_group_name
        self.template_id = template_id
        self.user_id = user_id
        self.user_full_name = user_full_name
        self.user_email = user_email
        self.school = school
        self.created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if not is_valid_state(workflow_state):
            raise ValueError(f"Invalid workflow state: {workflow_state}")
        self.workflow_state = workflow_state.lower()

    def __getitem__(self, key):
        return self.__dict__[key]

    def to_dict(self):
        return {
            "pk": self.pk,
            "sk": self.sk,
            "sis_account_id": self.sis_account_id,
            "term_id": self.term_id,
            "term_name": self.term_name,
            "department_id": self.department_id,
            "department_name": self.department_name,
            "course_group_id": self.course_group_id,
            "course_group_name": self.course_group_name,
            "template_id": self.template_id,
            "user_id": self.user_id,
            "user_full_name": self.user_full_name,
            "workflow_state": self.workflow_state,
            "user_email": self.user_email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "school": self.school
        }


class TaskRecord:
    def __init__(
        self,
        job_record: JobRecord,
        course_instance_id: str,
        workflow_state: str,
        canvas_course_id: str,
        course_code: str,
        course_title: str,
        section: str,
        department_id: str
    ):
        self.pk = job_record.sk
        self.sk = f"TASK#{str(ULID())}"
        self.course_instance_id = course_instance_id
        self.canvas_course_id = canvas_course_id
        self.course_code = course_code
        self.course_title = course_title
        self.section = section
        self.department_id = department_id
        self.created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if not is_valid_state(workflow_state):
            raise ValueError(f"Invalid workflow state: {workflow_state}")
        self.workflow_state = workflow_state.lower()

    def to_dict(self):
        return {
            "pk": self.pk,
            "sk": self.sk,
            "workflow_state": self.workflow_state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "course_instance_id": self.course_instance_id,
            "canvas_course_id": self.canvas_course_id,
            "course_code": self.course_code,
            "course_title": self.course_title,
            "section": self.section,
            "department_id": self.department_id
        }


class States(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


def is_valid_state(workflow_state: str):
    return workflow_state.lower() in [state.value for state in States]
