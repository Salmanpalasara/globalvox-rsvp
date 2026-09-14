from django.urls import path

from . import views


app_name = "campaigns"


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "invitees/",
        views.invitee_list,
        name="invitee_list"
    ),

    path(
        "invitees/import/",
        views.import_invitees,
        name="import_invitees"
    ),
    path(
    "campaigns/",
    views.campaign_list,
    name="campaign_list"
),

path(
    "campaigns/create/",
    views.campaign_create,
    name="campaign_create"
),

path(
    "campaigns/<int:campaign_id>/",
    views.campaign_detail,
    name="campaign_detail"
),

path(
    "campaigns/<int:campaign_id>/start/",
    views.campaign_start,
    name="campaign_start",
),

path(
    "campaigns/<int:campaign_id>/invitees/<int:campaign_invitee_id>/",
    views.campaign_invitee_detail,
    name="campaign_invitee_detail",
),

path(
    "campaigns/<int:campaign_id>/invitees/<int:campaign_invitee_id>/retry/",
    views.retry_campaign_invitee,
    name="retry_campaign_invitee",
),


]