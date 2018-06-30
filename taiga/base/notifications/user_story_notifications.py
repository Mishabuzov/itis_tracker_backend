import taiga.base.notifications.notifications_settings as settings_for_push
from taiga.projects.models import Project


def notificate_after_creating(project_id, owner_id):
    manager_id = settings_for_push.get_project_manager_id(project_id)

    # You don't need to get notification from yourself)
    if owner_id != manager_id:
        from taiga.users.models import User
        owner_name = User.objects.filter(id=owner_id).first().username
        project_name = Project.objects.filter(id=project_id).first().name
        settings_for_push.push_message_to_manager(project_id, "New user story was added to the project \""
                                                  + project_name + "\" by " + owner_name + ". Review it.",
                                                  settings_for_push.NotificationType.NEW_USER_STORY_CREATED)
