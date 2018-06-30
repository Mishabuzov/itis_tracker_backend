from threading import Timer

import taiga.base.notifications.notifications_settings as settings_for_push
from taiga.base.notifications.notifications_settings import NotificationType
from taiga.projects.milestones.models import Milestone


def enable_notifications_after_adding_member(username, project):
    project_id = project.id
    notification_type = NotificationType.ADDING_MEMBER_WITHOUT_MENTOR
    closed_milestones = Milestone.objects.filter(project=project_id, closed=True)
    if closed_milestones.count() > 0:
        notification_type = NotificationType.ADDING_MEMBER_WITH_MENTOR
        #  TODO: change time to 1 day in secs
        Timer(10, send_new_member_interview_notification, [project_id, 0]).start()
    settings_for_push.send_quantity_notification(project_id, project.get_users().count(),
                                                 "New Member " + username + "was added to the " + project.name
                                                 + " project",
                                                 notification_type)


def send_new_member_interview_notification(self, project_id, times):
    from threading import Timer
    settings_for_push.push_message_to_manager(project_id, "Your team has new members. Don't forget to ask them about"
                                                          "progress in project at daily scrum meeting.",
                                              NotificationType.REVIEW_NEWCOMER)
    if times < settings_for_push.ADAPTATION_PERIOD_FOR_NEW_MEMBERS:
        Timer(settings_for_push.SEC_PER_DAY, self.send_new_member_interview_notification, [project_id, times + 1])\
            .start()


def notificate_after_leaving(user, project):
    settings_for_push.send_quantity_notification(project.id, project.get_users().count,
                                                 "User " + user.username + " has left " + project.name + " project. ",
                                                 NotificationType.TEAM_MEMBER_HAS_LEFT_PROJECT)


def notificate_after_deleting_member(username, project):
    settings_for_push.send_quantity_notification(project.id, project.get_users().count(),
                                        "Member " + username + "was kicked from " + project.name + " project",
                                        NotificationType.DELETING_TEAM_MEMBER)
