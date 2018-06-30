from taiga.users.models import Role
from taiga.projects.models import Membership
from taiga.users.models import User
from push_notifications.models import GCMDevice
from enum import Enum

SEC_PER_DAY = 86400

ADAPTATION_PERIOD_FOR_NEW_MEMBERS = 7


def send_quantity_notification(project_id, team_size, message, notification_type):
    if team_size < 3 or team_size > 9:
        if team_size < 3:
            message += "Your team is very small now. Add more people for more productive results."
        elif team_size > 9:
            message += "Your team is large now. "
            message += "Reduce the number of members to avoid communication problems and improve team productivity."
        push_message_to_manager(project_id, notification_type, message)


def get_project_manager_id(project_id):
    manager_id = None
    role_id = Role.objects\
        .filter(project=project_id, name="Project manager")\
        .first().id
    if role_id is not None:
        manager_id = Membership.objects\
            .filter(project=project_id, role=role_id)\
            .first().user_id
    return manager_id


def push_message_to_manager(project_id, message, notification_type):
    manager_id = get_project_manager_id(project_id)
    if manager_id is not None:
        push_id = User.objects\
            .filter(id=manager_id).first().push_id
        if push_id is not None:
            send_message(project_id,
                         push_id,
                         notification_type,
                         message)


def send_message(project_id, push_id, notification_type, message):
    fcm_device = GCMDevice.objects\
        .filter(registration_id=push_id, cloud_message_type="FCM")\
        .first()
    if fcm_device is None:
        fcm_device = GCMDevice.objects\
            .create(registration_id=push_id,
                    cloud_message_type="FCM")
    fcm_device.send_message(message,
                            tag=notification_type.value,
                            extra={"project_id": project_id})


def get_delta_dates(start_date, finish_date):
    import datetime
    s_date = datetime.datetime(start_date.tm_year, start_date.tm_mon, start_date.tm_mday)
    f_date = datetime.datetime(finish_date.tm_year, finish_date.tm_mon, finish_date.tm_mday)

    return f_date - s_date


class NotificationType(Enum):

    OVERDUE_SPRINT = "overdue_sprint"

    ADDING_MEMBER_WITH_MENTOR = "adding_team_member"    # If project has closed sprints.

    ADDING_MEMBER_WITHOUT_MENTOR = "adding_member_without_mentor"  # If project doesn't have closed sprints.

    DELETING_TEAM_MEMBER = "deleting_team_member"

    TEAM_MEMBER_HAS_LEFT_PROJECT = "team_member_has_left_project"

    REVIEW_NEWCOMER = "review_newcomer"  # If project has closed sprints.

    HIGH_PRIORITY_ISSUE_WITHOUT_EXECUTOR = "high_priority_issue_without_executor"

    DEADLINE_IS_CLOSE = "deadline_is_closed"

    BLOCKED_TASKS = "blocked_tasks"  # Only if project has opened sprints

    USER_WITHOUT_TASKS = "user_without_tasks"   # Only if project has opened sprints

    SPRINT_FINISHED_BEFORE_DEADLINE = "sprint_finished_before_deadline"

    NEW_USER_STORY_CREATED = "new_user_story_created"
