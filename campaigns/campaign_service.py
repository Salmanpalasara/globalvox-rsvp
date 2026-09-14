from django.db import transaction
from django.utils import timezone

from .calling_service import (
    call_invitee,
    CallingServiceError,
)

from .models import (
    Campaign,
    CampaignInvitee,
    CallLog,
)

def process_campaign_invitee(campaign_invitee):

    campaign = campaign_invitee.campaign
    invitee = campaign_invitee.invitee

    campaign_invitee.call_status = (
        CampaignInvitee.CallStatus.PROCESSING
    )

    campaign_invitee.attempt_count += 1

    campaign_invitee.last_called_at = (
        timezone.now()
    )

    campaign_invitee.save(
        update_fields=[
            "call_status",
            "attempt_count",
            "last_called_at",
        ]
    )

    request_data = {
        "name": invitee.name,
        "phone": invitee.phone,
        "email": invitee.email,
        "campaign": campaign.name,
        "event": campaign.event_name,
        "objective": campaign.objective,
    }

    try:

        result = call_invitee(
            invitee=invitee,
            campaign=campaign,
        )

    except CallingServiceError as exc:

        campaign_invitee.call_status = (
            CampaignInvitee.CallStatus.FAILED
        )

        campaign_invitee.rsvp_status = (
            CampaignInvitee.RSVPStatus.PENDING
        )

        campaign_invitee.notes = str(exc)

        campaign_invitee.save(
            update_fields=[
                "call_status",
                "rsvp_status",
                "notes",
            ]
        )

        CallLog.objects.create(
            campaign_invitee=campaign_invitee,
            status=CallLog.Status.FAILED,
            request_data=request_data,
            error_message=str(exc),
        )

        return False


    campaign_invitee.call_status = (
        CampaignInvitee.CallStatus.COMPLETED
    )

    campaign_invitee.rsvp_status = (
        result["rsvp_status"]
    )

    campaign_invitee.notes = (
        result.get("notes", "")
    )

    campaign_invitee.save(
        update_fields=[
            "call_status",
            "rsvp_status",
            "notes",
        ]
    )

    CallLog.objects.create(
        campaign_invitee=campaign_invitee,
        status=CallLog.Status.SUCCESS,
        request_data=request_data,
        response_data=result,
    )

    return True


def process_campaign(campaign):

    campaign.status = Campaign.Status.RUNNING

    campaign.save(
        update_fields=["status"]
    )

    invitees = (
        CampaignInvitee.objects
        .filter(
            campaign=campaign,
            call_status=(
                CampaignInvitee
                .CallStatus
                .NOT_STARTED
            )
        )
        .select_related(
            "invitee",
            "campaign"
        )
    )

    processed = 0
    failed = 0

    for campaign_invitee in invitees:

        success = process_campaign_invitee(
            campaign_invitee
        )

        processed += 1

        if not success:
            failed += 1

    campaign.status = (
        Campaign.Status.COMPLETED
    )

    campaign.save(
        update_fields=["status"]
    )

    return {
        "processed": processed,
        "failed": failed,
        "successful": processed - failed,
    }