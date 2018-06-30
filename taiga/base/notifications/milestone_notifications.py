from threading import Timer
from taiga.projects.milestones.models import Milestone
from taiga.projects.models import Project, Membership, TaskStatus, UserStoryStatus
from datetime import datetime
import time
import taiga.base.notifications.notifications_settings as settings_for_push
from taiga.projects.userstories.models import UserStory
from taiga.users.models import Notification


def enable_milestone_push(project_id, sprint_id, start_date, finish_date):
    if start_date is not None and finish_date is not None:
        delta = settings_for_push.get_delta_dates(start_date, finish_date)
        secs = delta.total_seconds()

        notification = Notification.create(datetime.today().strftime('%Y-%m-%d'), project_id, settings_for_push.NotificationType.OVERDUE_SPRINT.value,
                                           "Look to Db!")
        notification.save()

        # on sprint overdue timer
        # TODO: set secs instead of 1
        Timer(1, push_on_overdue_sprint, [sprint_id, project_id]).start()
        # on sprint bad performance timer
        # TODO: remove -2 from delta
        Timer(settings_for_push.SEC_PER_DAY, check_story_points, [sprint_id, project_id, delta.days - 2]).start()

        enable_blocked_tasks_notifications(project_id)
        # check_sprint_finishing_before_deadline
        # TODO: set time correctly!!!
        check_sprint_finishing_before_deadline(project_id, sprint_id, finish_date)
        # Timer(5, check_sprint_finishing_before_deadline, [project_id, new_sprint_id, finish_date])


def push_on_overdue_sprint(new_sprint_id, project_id):
    # stories = UserStory.objects.filter(is_closed=False, milestone=new_sprint_id)
    is_milestone_closed = Milestone.objects.filter(id=new_sprint_id, project=project_id).first().closed
    # if stories.count() == 0:
    # TODO: set NOT here
    if is_milestone_closed:
        settings_for_push.push_message_to_manager(project_id,
                                                  "You have an overdue sprint, check it!",
                                                  settings_for_push.NotificationType.OVERDUE_SPRINT)


# TODO: SET time in timer correctly!
def check_story_points(sprint_id, project_id, days_until_deadline):
    new_status_id = UserStoryStatus.objects.filter(project=project_id, name="New").first().id
    all_story_points = 0
    stories = UserStory.objects.filter(is_closed=False, milestone=sprint_id)
    for story in stories:
        if story.status_id == new_status_id and story.get_total_points() is not None:
            all_story_points += story.get_total_points()
    if all_story_points > days_until_deadline:
        settings_for_push.push_message_to_manager(project_id,
                                                  "Your team doesn't have time to complete all tasks before the sprint is over!"
                                                  "You have to take actions!",
                                                  settings_for_push.NotificationType.DEADLINE_IS_CLOSE)
    days_until_deadline -= 1
    if days_until_deadline > 0:
        Timer(15, check_story_points, [sprint_id, project_id, days_until_deadline]).start()


# TODO: SET CORRECT TIME VALUES!
def check_sprint_finishing_before_deadline(project_id, sprint_id, sprint_finish_date):
    current_sprint = Milestone.objects.filter(project=project_id, id=sprint_id).first()
    # TODO: Remove not
    if not current_sprint.closed:  # check closed sprint on a deadline
        current_date = time.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
        # calculate how much time until finish
        days_until_finish = settings_for_push.get_delta_dates(current_date, sprint_finish_date).days
        #  TODO: remove +55
        if days_until_finish + 55 > 0:
            settings_for_push.push_message_to_manager(project_id, "Sprint " + current_sprint.name + " has no tasks, "
                                                      "but has already finished. You can add some new there.",
                                                      settings_for_push.NotificationType.SPRINT_FINISHED_BEFORE_DEADLINE)
            # possible case that checking was disabled before deadline
            enable_blocked_tasks_notifications(project_id)
            Timer(settings_for_push.SEC_PER_DAY, check_sprint_finishing_before_deadline,
                  [project_id, sprint_id, sprint_finish_date]).start()
    else:
        Timer(settings_for_push.SEC_PER_DAY, check_sprint_finishing_before_deadline,
              [project_id, sprint_id, sprint_finish_date]).start()


global in_progress_notification_projects
in_progress_notification_projects = []


# this method turn on notifications about user activity and blocked tasks, if opened sprints exist in project
def enable_blocked_tasks_notifications(project_id):
    global in_progress_notification_projects
    is_notification_already_enabled_for_project = False
    for notification_project_id in in_progress_notification_projects:
        if project_id == notification_project_id:
            is_notification_already_enabled_for_project = True
            break

    if is_notification_already_enabled_for_project:
        #  TODO: uncommit + set correct time (1 day delta)
        # Timer(15, send_notifications_dependent_on_sprints, [project_id, project_name]).start()
        send_notifications_dependent_on_sprints(project_id)


def send_notifications_dependent_on_sprints(project_id):
    opened_sprints = Milestone.objects.filter(project=project_id)
    if opened_sprints.count() > 0:
        in_progress_notification_projects.append(project_id)

        project_name = Project.objects.filter(id=project_id).first().name
        #   enabling notifications, if all conditions are true
        check_users_activity(project_id, project_name)
        push_on_blocked_tasks(project_id, project_name)
        #   repeat tomorrow
        Timer(settings_for_push.SEC_PER_DAY, send_notifications_dependent_on_sprints, [project_id]).start()
    else:
        # disable checking notifications depending on active sprints for this project
        in_progress_notification_projects.remove(project_id)


# check that each user has at least 1 task with status "in progress". If user has no tasks - push to manager.
def check_users_activity(project_id, project_name):
    from taiga.projects.tasks.models import Task
    global in_progress_notification_projects

    memberships = Membership.objects.filter(project=project_id)
    in_progress_status = TaskStatus.objects.filter(project=project_id, name="In progress")
    for membership in memberships:
        user = membership.user
        tasks = Task.objects.filter(project=project_id, assigned_to=user, status=in_progress_status)
        if tasks.count() == 0 and user.id != settings_for_push.get_project_manager_id(project_id):
            settings_for_push.push_message_to_manager(project_id, "User " + user.username + " doesn't have tasks in"
                                                      " project " + project_name + ". Assign some tasks to him if "
                                                      "it's possible.", settings_for_push.NotificationType.USER_WITHOUT_TASKS)


#  checking blocked tasks in project
def push_on_blocked_tasks(project_id, project_name):
    opened_sprints = Milestone.objects.filter(closed=False, project=project_id)
    # findings blocked tasks in opened sprints
    is_blocked_tasks_in_sprints = False
    for sprint in opened_sprints:
        from taiga.projects.tasks.models import Task
        tasks = Task.objects.filter(milestone=sprint.id)
        for task in tasks:
            if task.is_blocked or task.status.name == "Needs Info":
                is_blocked_tasks_in_sprints = True
                break
    if is_blocked_tasks_in_sprints:
        settings_for_push.push_message_to_manager(project_id, "You have blocked tasks in project " + project_name,
                                                  settings_for_push.NotificationType.BLOCKED_TASKS)
