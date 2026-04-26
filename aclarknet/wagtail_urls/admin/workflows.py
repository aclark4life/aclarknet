# Copied from wagtail/admin/urls/workflows.py (Wagtail 7.3.1)
# All <int: path converters replaced with <str: for Django MongoDB Backend compatibility.
# Re-diff against upstream on Wagtail upgrades.
from django.urls import path

from wagtail.admin.views import workflows

app_name = "wagtailadmin_workflows"
urlpatterns = [
    path("list/", workflows.Index.as_view(), name="index"),
    path(
        "list/results/",
        workflows.Index.as_view(results_only=True),
        name="index_results",
    ),
    path("add/", workflows.Create.as_view(), name="add"),
    path("enable/<str:pk>/", workflows.enable_workflow, name="enable"),
    path("disable/<str:pk>/", workflows.Disable.as_view(), name="disable"),
    path("edit/<str:pk>/", workflows.Edit.as_view(), name="edit"),
    path("usage/<str:pk>/", workflows.WorkflowUsageView.as_view(), name="usage"),
    path(
        "usage/<str:pk>/results/",
        workflows.WorkflowUsageView.as_view(results_only=True),
        name="usage_results",
    ),
    path("remove/<str:page_pk>/", workflows.remove_workflow, name="remove"),
    path(
        "remove/<str:page_pk>/<str:workflow_pk>/",
        workflows.remove_workflow,
        name="remove",
    ),
    path(
        "tasks/add/<str:app_label>/<str:model_name>/",
        workflows.CreateTask.as_view(),
        name="add_task",
    ),
    path("tasks/select_type/", workflows.select_task_type, name="select_task_type"),
    path("tasks/index/", workflows.TaskIndex.as_view(), name="task_index"),
    path(
        "tasks/index/results/",
        workflows.TaskIndex.as_view(results_only=True),
        name="task_index_results",
    ),
    path("tasks/edit/<str:pk>/", workflows.EditTask.as_view(), name="edit_task"),
    path(
        "tasks/disable/<str:pk>/", workflows.DisableTask.as_view(), name="disable_task"
    ),
    path("tasks/enable/<str:pk>/", workflows.enable_task, name="enable_task"),
    path("task_chooser/", workflows.TaskChooserView.as_view(), name="task_chooser"),
    path(
        "task_chooser/results/",
        workflows.TaskChooserResultsView.as_view(),
        name="task_chooser_results",
    ),
    path(
        "task_chooser/create/",
        workflows.TaskChooserCreateView.as_view(),
        name="task_chooser_create",
    ),
    path("task_chooser/<str:task_id>/", workflows.task_chosen, name="task_chosen"),
]
