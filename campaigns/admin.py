from django.contrib import admin

from .models import (
    Invitee,
    Campaign,
    CampaignInvitee,
    CallLog
)


@admin.register(Invitee)
class InviteeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "phone",
        "email",
        "created_at"
    )

    search_fields = (
        "name",
        "phone",
        "email"
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "event_name",
        "event_date",
        "status"
    )

    list_filter = (
        "status",
        "event_date"
    )


@admin.register(CampaignInvitee)
class CampaignInviteeAdmin(admin.ModelAdmin):

    list_display = (
        "invitee",
        "campaign",
        "rsvp_status",
        "call_status",
        "attempt_count"
    )

    list_filter = (
        "rsvp_status",
        "call_status"
    )


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):

    list_display = (
        "campaign_invitee",
        "status",
        "created_at"
    )

    list_filter = (
        "status",
    )