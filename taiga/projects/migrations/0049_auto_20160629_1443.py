# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-29 14:43
from __future__ import unicode_literals

import taiga.base.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0048_auto_20160615_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='EpicStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('slug', models.SlugField(blank=True, max_length=255, verbose_name='slug')),
                ('order', models.IntegerField(default=10, verbose_name='order')),
                ('is_closed', models.BooleanField(default=False, verbose_name='is closed')),
                ('color', models.CharField(default='#999999', max_length=20, verbose_name='color')),
            ],
            options={
                'verbose_name_plural': 'epic statuses',
                'ordering': ['project', 'order', 'name'],
                'verbose_name': 'epic status',
            },
        ),
        migrations.AlterModelOptions(
            name='issuestatus',
            options={'ordering': ['project', 'order', 'name'], 'verbose_name': 'issue status', 'verbose_name_plural': 'issue statuses'},
        ),
        migrations.AlterModelOptions(
            name='issuetype',
            options={'ordering': ['project', 'order', 'name'], 'verbose_name': 'issue type', 'verbose_name_plural': 'issue types'},
        ),
        migrations.AlterModelOptions(
            name='membership',
            options={'ordering': ['project', 'user__full_name', 'user__username', 'user__email', 'email'], 'verbose_name': 'membership', 'verbose_name_plural': 'memberships'},
        ),
        migrations.AlterModelOptions(
            name='points',
            options={'ordering': ['project', 'order', 'name'], 'verbose_name': 'points', 'verbose_name_plural': 'points'},
        ),
        migrations.AlterModelOptions(
            name='priority',
            options={'ordering': ['project', 'order', 'name'], 'verbose_name': 'priority', 'verbose_name_plural': 'priorities'},
        ),
        migrations.AlterModelOptions(
            name='severity',
            options={'ordering': ['project', 'order', 'name'], 'verbose_name': 'severity', 'verbose_name_plural': 'severities'},
        ),
        migrations.AlterModelOptions(
            name='taskstatus',
            options={'ordering': ['project', 'order', 'name'], 'verbose_name': 'task status', 'verbose_name_plural': 'task statuses'},
        ),
        migrations.AlterModelOptions(
            name='userstorystatus',
            options={'ordering': ['project', 'order', 'name'], 'verbose_name': 'user story status', 'verbose_name_plural': 'user story statuses'},
        ),
        migrations.AddField(
            model_name='project',
            name='is_epics_activated',
            field=models.BooleanField(default=False, verbose_name='active epics panel'),
        ),
        migrations.AddField(
            model_name='projecttemplate',
            name='epic_statuses',
            field=taiga.base.db.models.fields.JSONField(blank=True, null=True, verbose_name='epic statuses'),
        ),
        migrations.AddField(
            model_name='projecttemplate',
            name='is_epics_activated',
            field=models.BooleanField(default=False, verbose_name='active epics panel'),
        ),
        migrations.AlterField(
            model_name='project',
            name='anon_permissions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(choices=[('view_project', 'View project'), ('view_milestones', 'View milestones'), ('view_epics', 'View epic'), ('view_us', 'View user stories'), ('view_tasks', 'View tasks'), ('view_issues', 'View issues'), ('view_wiki_pages', 'View wiki pages'), ('view_wiki_links', 'View wiki links')]), blank=True, default=[], null=True, size=None, verbose_name='anonymous permissions'),
        ),
        migrations.AlterField(
            model_name='project',
            name='public_permissions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(choices=[('view_project', 'View project'), ('view_milestones', 'View milestones'), ('add_milestone', 'Add milestone'), ('modify_milestone', 'Modify milestone'), ('delete_milestone', 'Delete milestone'), ('view_epics', 'View epic'), ('add_epic', 'Add epic'), ('modify_epic', 'Modify epic'), ('comment_epic', 'Comment epic'), ('delete_epic', 'Delete epic'), ('view_us', 'View user story'), ('add_us', 'Add user story'), ('modify_us', 'Modify user story'), ('comment_us', 'Comment user story'), ('delete_us', 'Delete user story'), ('view_tasks', 'View tasks'), ('add_task', 'Add task'), ('modify_task', 'Modify task'), ('comment_task', 'Comment task'), ('delete_task', 'Delete task'), ('view_issues', 'View issues'), ('add_issue', 'Add issue'), ('modify_issue', 'Modify issue'), ('comment_issue', 'Comment issue'), ('delete_issue', 'Delete issue'), ('view_wiki_pages', 'View wiki pages'), ('add_wiki_page', 'Add wiki page'), ('modify_wiki_page', 'Modify wiki page'), ('comment_wiki_page', 'Comment wiki page'), ('delete_wiki_page', 'Delete wiki page'), ('view_wiki_links', 'View wiki links'), ('add_wiki_link', 'Add wiki link'), ('modify_wiki_link', 'Modify wiki link'), ('delete_wiki_link', 'Delete wiki link')]), blank=True, default=[], null=True, size=None, verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='epicstatus',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='epic_statuses', to='projects.Project', verbose_name='project'),
        ),
        migrations.AddField(
            model_name='project',
            name='default_epic_status',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='projects.EpicStatus', verbose_name='default epic status'),
        ),
        migrations.AlterUniqueTogether(
            name='epicstatus',
            unique_together=set([('project', 'slug'), ('project', 'name')]),
        ),
    ]