from threading import Timer
import taiga.base.notifications.notifications_settings as settings_for_push
from taiga.projects.issues.models import Issue

global notification_projects
notification_projects = []


def enable_notifications_on_high_priority_issues(project_id):
    global notification_projects
    is_notification_already_enabled_in_project = False
    for notification_project_id in notification_projects:
        if project_id == notification_project_id:
            is_notification_already_enabled_in_project = True
    if not is_notification_already_enabled_in_project:
        notification_projects.append(project_id)
        #  TODO: set 1 day time
        Timer(5, push_on_high_priority, [project_id]).start()


def push_on_high_priority(project_id):
    issues = Issue.objects.filter(project=project_id, assigned_to=None)
    unassigned_high_issues = 0
    for issue in issues:
        if issue.priority.name == "High":
            unassigned_high_issues = unassigned_high_issues + 1
    if unassigned_high_issues > 0:
        settings_for_push.push_message_to_manager(project_id, "You have " + str(unassigned_high_issues)
                                                  + " unassigned issues with high priority."
                                                    " Don't forget to assign it to somebody.",
                                                  settings_for_push.NotificationType.HIGH_PRIORITY_ISSUE_WITHOUT_EXECUTOR)
    if issues.count() > 0:
        Timer(settings_for_push.SEC_PER_DAY, push_on_high_priority).start()
    else:
        notification_projects.remove(project_id)
