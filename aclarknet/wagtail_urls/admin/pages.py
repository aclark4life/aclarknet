# Copied from wagtail/admin/urls/pages.py (Wagtail 7.3.1)
# All <int: path converters replaced with <str: for Django MongoDB Backend compatibility.
# The revisions_compare re_path regex \d+ replaced with [^/.]+ to match ObjectIDs.
# Re-diff against upstream on Wagtail upgrades.
from django.urls import path, re_path

from wagtail.admin.views import page_privacy
from wagtail.admin.views.pages import (
    convert_alias,
    copy,
    create,
    delete,
    edit,
    history,
    lock,
    move,
    ordering,
    preview,
    revisions,
    search,
    unpublish,
    usage,
    workflow,
)

app_name = "wagtailadmin_pages"
urlpatterns = [
    path(
        "add/<slug:content_type_app_name>/<slug:content_type_model_name>/<str:parent_page_id>/",
        create.CreateView.as_view(),
        name="add",
    ),
    path(
        "add/<slug:content_type_app_name>/<slug:content_type_model_name>/<str:parent_page_id>/preview/",
        preview.PreviewOnCreate.as_view(),
        name="preview_on_add",
    ),
    path(
        "usage/<slug:content_type_app_name>/<slug:content_type_model_name>/",
        usage.ContentTypeUseView.as_view(),
        name="type_use",
    ),
    path(
        "usage/<slug:content_type_app_name>/<slug:content_type_model_name>/results/",
        usage.ContentTypeUseView.as_view(results_only=True),
        name="type_use_results",
    ),
    path("<str:page_id>/usage/", usage.UsageView.as_view(), name="usage"),
    path("<str:page_id>/edit/", edit.EditView.as_view(), name="edit"),
    path(
        "<str:page_id>/edit/preview/",
        preview.PreviewOnEdit.as_view(),
        name="preview_on_edit",
    ),
    path("<str:page_id>/view_draft/", preview.view_draft, name="view_draft"),
    path("<str:parent_page_id>/add_subpage/", create.add_subpage, name="add_subpage"),
    path("<str:page_id>/delete/", delete.delete, name="delete"),
    path("<str:page_id>/unpublish/", unpublish.Unpublish.as_view(), name="unpublish"),
    path(
        "<str:page_id>/convert_alias/",
        convert_alias.convert_alias,
        name="convert_alias",
    ),
    path("search/", search.SearchView.as_view(), name="search"),
    path(
        "search/results/",
        search.SearchView.as_view(results_only=True),
        name="search_results",
    ),
    path(
        "<str:page_to_move_id>/move/", move.MoveChooseDestination.as_view(), name="move"
    ),
    path(
        "<str:page_to_move_id>/move/<str:destination_id>/confirm/",
        move.move_confirm,
        name="move_confirm",
    ),
    path(
        "<str:page_to_move_id>/set_position/",
        ordering.set_page_position,
        name="set_page_position",
    ),
    path("<str:page_id>/copy/", copy.copy, name="copy"),
    path(
        "workflow/action/<str:page_id>/<slug:action_name>/<str:task_state_id>/",
        workflow.WorkflowAction.as_view(),
        name="workflow_action",
    ),
    path(
        "workflow/collect_action_data/<str:page_id>/<slug:action_name>/<str:task_state_id>/",
        workflow.CollectWorkflowActionData.as_view(),
        name="collect_workflow_action_data",
    ),
    path(
        "workflow/confirm_cancellation/<str:page_id>/",
        workflow.ConfirmWorkflowCancellation.as_view(),
        name="confirm_workflow_cancellation",
    ),
    path(
        "workflow/preview/<str:page_id>/<str:task_id>/",
        workflow.PreviewRevisionForTask.as_view(),
        name="workflow_preview",
    ),
    path("<str:page_id>/privacy/", page_privacy.set_privacy, name="set_privacy"),
    path("<str:page_id>/lock/", lock.LockView.as_view(), name="lock"),
    path("<str:page_id>/unlock/", lock.UnlockView.as_view(), name="unlock"),
    path("<str:page_id>/revisions/", revisions.revisions_index, name="revisions_index"),
    path(
        "<str:page_id>/revisions/<str:revision_id>/view/",
        revisions.RevisionsView.as_view(),
        name="revisions_view",
    ),
    path(
        "<str:page_id>/revisions/<str:revision_id>/revert/",
        revisions.RevisionsRevertView.as_view(),
        name="revisions_revert",
    ),
    path(
        "<str:page_id>/revisions/<str:revision_id>/unschedule/",
        revisions.RevisionsUnschedule.as_view(),
        name="revisions_unschedule",
    ),
    re_path(
        r"^([^/]+)/revisions/compare/(live|earliest|[^/.]+)\.\.\.(live|latest|[^/.]+)/$",
        revisions.RevisionsCompare.as_view(),
        name="revisions_compare",
    ),
    path(
        "<str:page_id>/workflow_history/",
        history.WorkflowHistoryView.as_view(),
        name="workflow_history",
    ),
    path(
        "<str:page_id>/workflow_history/detail/<str:workflow_state_id>/",
        history.WorkflowHistoryDetailView.as_view(),
        name="workflow_history_detail",
    ),
    path("<str:page_id>/history/", history.PageHistoryView.as_view(), name="history"),
    path(
        "<str:page_id>/history/results/",
        history.PageHistoryView.as_view(results_only=True),
        name="history_results",
    ),
]
