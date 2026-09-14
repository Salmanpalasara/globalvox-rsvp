from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .campaign_service import (
    process_campaign,
    process_campaign_invitee
)
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .forms import (
    InviteeCSVUploadForm,
    CampaignCreateForm
)

from .models import (
    Invitee,
    Campaign,
    CampaignInvitee
)

def home(request):

    return render(
        request,
        "home.html"
    )

def import_invitees(request):

    if request.method == "POST":

        form = InviteeCSVUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            result = import_invitees_from_csv(
                form.cleaned_data["csv_file"]
            )

            if not result["success"]:

                messages.error(
                    request,
                    result["message"]
                )

            else:

                messages.success(
                    request,
                    (
                        f'{result["created"]} invitees imported. '
                        f'{result["duplicates"]} duplicates skipped. '
                        f'{len(result["errors"])} invalid rows skipped.'
                    )
                )

                request.session[
                    "import_errors"
                ] = result["errors"]

                return redirect(
                    "campaigns:invitee_list"
                )

    else:

        form = InviteeCSVUploadForm()

    return render(
        request,
        "invitees/import.html",
        {
            "form": form
        }
    )

def invitee_list(request):

    invitees = Invitee.objects.all().order_by(
        "-created_at"
    )

    paginator = Paginator(
        invitees,
        25
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    import_errors = request.session.pop(
        "import_errors",
        []
    )

    return render(
        request,
        "invitees/list.html",
        {
            "page_obj": page_obj,
            "import_errors": import_errors
        }
    )



def campaign_create(request):

    if request.method == "POST":

        form = CampaignCreateForm(
            request.POST
        )

        if form.is_valid():

            campaign = form.save()

            select_all = form.cleaned_data.get(
                "select_all"
            )

            if select_all:

                selected_invitees = (
                    Invitee.objects.all()
                )

            else:

                selected_invitees = (
                    form.cleaned_data["invitees"]
                )

            campaign_invitees = [

                CampaignInvitee(
                    campaign=campaign,
                    invitee=invitee
                )

                for invitee in selected_invitees
            ]

            CampaignInvitee.objects.bulk_create(
                campaign_invitees,
                batch_size=1000
            )

            messages.success(
                request,
                (
                    f"Campaign created successfully "
                    f"with {len(campaign_invitees)} invitees."
                )
            )

            return redirect(
                "campaigns:campaign_detail",
                campaign_id=campaign.id
            )

    else:

        form = CampaignCreateForm()

    return render(
        request,
        "campaigns/create.html",
        {
            "form": form
        }
    )

def campaign_list(request):

    campaigns = (
        Campaign.objects
        .all()
        .order_by("-created_at")
    )

    paginator = Paginator(
        campaigns,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        "campaigns/list.html",
        {
            "page_obj": page_obj
        }
    )


# def campaign_detail(
#     request,
#     campaign_id
# ):

#     campaign = get_object_or_404(
#         Campaign,
#         id=campaign_id
#     )

#     base_queryset = (
#         CampaignInvitee.objects
#         .filter(campaign=campaign)
#     )

#     stats = base_queryset.aggregate(

#         total=Count("id"),

#         confirmed=Count(
#             "id",
#             filter=Q(
#                 rsvp_status=(
#                     CampaignInvitee
#                     .RSVPStatus
#                     .CONFIRMED
#                 )
#             )
#         ),

#         declined=Count(
#             "id",
#             filter=Q(
#                 rsvp_status=(
#                     CampaignInvitee
#                     .RSVPStatus
#                     .DECLINED
#                 )
#             )
#         ),

#         undecided=Count(
#             "id",
#             filter=Q(
#                 rsvp_status=(
#                     CampaignInvitee
#                     .RSVPStatus
#                     .UNDECIDED
#                 )
#             )
#         ),

#         pending=Count(
#             "id",
#             filter=Q(
#                 rsvp_status=(
#                     CampaignInvitee
#                     .RSVPStatus
#                     .PENDING
#                 )
#             )
#         ),

#         failed=Count(
#             "id",
#             filter=Q(
#                 call_status=(
#                     CampaignInvitee
#                     .CallStatus
#                     .FAILED
#                 )
#             )
#         ),
#     )

#     campaign_invitees = (
#         base_queryset
#         .select_related("invitee")
#         .order_by("invitee__name")
#     )

#     paginator = Paginator(
#         campaign_invitees,
#         25
#     )

#     page_obj = paginator.get_page(
#         request.GET.get("page")
#     )

#     return render(
#         request,
#         "campaigns/detail.html",
#         {
#             "campaign": campaign,
#             "page_obj": page_obj,
#             "stats": stats,
#         }
#     )

def campaign_detail(request, campaign_id):

    campaign = get_object_or_404(
        Campaign,
        id=campaign_id
    )

    base_queryset = (
        CampaignInvitee.objects
        .filter(campaign=campaign)
        .select_related("invitee")
    )

    # Dashboard statistics
    stats = base_queryset.aggregate(

        total=Count("id"),

        confirmed=Count(
            "id",
            filter=Q(
                rsvp_status=CampaignInvitee.RSVPStatus.CONFIRMED
            )
        ),

        declined=Count(
            "id",
            filter=Q(
                rsvp_status=CampaignInvitee.RSVPStatus.DECLINED
            )
        ),

        undecided=Count(
            "id",
            filter=Q(
                rsvp_status=CampaignInvitee.RSVPStatus.UNDECIDED
            )
        ),

        pending=Count(
            "id",
            filter=Q(
                rsvp_status=CampaignInvitee.RSVPStatus.PENDING
            )
        ),

        failed=Count(
            "id",
            filter=Q(
                call_status=CampaignInvitee.CallStatus.FAILED
            )
        ),
    )

    # -----------------------
    # Search
    # -----------------------

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        base_queryset = base_queryset.filter(

            Q(
                invitee__name__icontains=search
            )
            |
            Q(
                invitee__phone__icontains=search
            )
            |
            Q(
                invitee__email__icontains=search
            )
        )


    # -----------------------
    # RSVP Filter
    # -----------------------

    rsvp_status = request.GET.get(
        "rsvp_status",
        ""
    ).strip()

    valid_rsvp_statuses = {
        CampaignInvitee.RSVPStatus.PENDING,
        CampaignInvitee.RSVPStatus.CONFIRMED,
        CampaignInvitee.RSVPStatus.DECLINED,
        CampaignInvitee.RSVPStatus.UNDECIDED,
    }

    if rsvp_status in valid_rsvp_statuses:

        base_queryset = base_queryset.filter(
            rsvp_status=rsvp_status
        )


    # -----------------------
    # Call Status Filter
    # -----------------------

    call_status = request.GET.get(
        "call_status",
        ""
    ).strip()

    valid_call_statuses = {
        CampaignInvitee.CallStatus.NOT_STARTED,
        CampaignInvitee.CallStatus.PROCESSING,
        CampaignInvitee.CallStatus.COMPLETED,
        CampaignInvitee.CallStatus.FAILED,
    }

    if call_status in valid_call_statuses:

        base_queryset = base_queryset.filter(
            call_status=call_status
        )


    # -----------------------
    # Ordering
    # -----------------------

    campaign_invitees = (
        base_queryset
        .order_by("invitee__name")
    )


    # -----------------------
    # Pagination
    # -----------------------

    paginator = Paginator(
        campaign_invitees,
        25
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    return render(
        request,
        "campaigns/detail.html",
        {
            "campaign": campaign,
            "page_obj": page_obj,
            "stats": stats,

            "search": search,
            "selected_rsvp_status": rsvp_status,
            "selected_call_status": call_status,

            "filtered_count": paginator.count,
        }
    )


# @require_POST
# def campaign_start(request, campaign_id):

#     campaign = get_object_or_404(
#         Campaign,
#         id=campaign_id
#     )

#     if campaign.status != Campaign.Status.DRAFT:

#         messages.warning(
#             request,
#             "This campaign has already been started."
#         )

#         return redirect(
#             "campaigns:campaign_detail",
#             campaign_id=campaign.id
#         )

#     if not campaign.campaign_invitees.exists():

#         messages.error(
#             request,
#             "Cannot start a campaign without invitees."
#         )

#         return redirect(
#             "campaigns:campaign_detail",
#             campaign_id=campaign.id
#         )

#     result = process_campaign(campaign)

#     messages.success(
#         request,
#         (
#             f"Campaign processed. "
#             f"{result['successful']} successful calls, "
#             f"{result['failed']} failed calls."
#         )
#     )

#     return redirect(
#         "campaigns:campaign_detail",
#         campaign_id=campaign.id
#     )

@require_POST
def campaign_start(
    request,
    campaign_id
):

    campaign = get_object_or_404(
        Campaign,
        id=campaign_id
    )

    if campaign.status != Campaign.Status.DRAFT:

        messages.warning(
            request,
            "This campaign has already been started."
        )

        return redirect(
            "campaigns:campaign_detail",
            campaign_id=campaign.id
        )


    if not campaign.campaign_invitees.exists():

        messages.error(
            request,
            "Cannot start a campaign without invitees."
        )

        return redirect(
            "campaigns:campaign_detail",
            campaign_id=campaign.id
        )


    try:

        result = process_campaign(
            campaign
        )

    except Exception:

        campaign.status = Campaign.Status.DRAFT

        campaign.save(
            update_fields=[
                "status"
            ]
        )

        messages.error(
            request,
            (
                "Campaign could not be processed "
                "because of an unexpected error."
            )
        )

        return redirect(
            "campaigns:campaign_detail",
            campaign_id=campaign.id
        )


    messages.success(
        request,
        (
            f"Campaign processed. "
            f"{result['successful']} successful calls, "
            f"{result['failed']} failed calls."
        )
    )


    return redirect(
        "campaigns:campaign_detail",
        campaign_id=campaign.id
    )

def campaign_invitee_detail(
    request,
    campaign_id,
    campaign_invitee_id
):

    campaign = get_object_or_404(
        Campaign,
        id=campaign_id
    )

    campaign_invitee = get_object_or_404(
        CampaignInvitee.objects.select_related(
            "invitee",
            "campaign"
        ),
        id=campaign_invitee_id,
        campaign=campaign
    )

    call_logs = (
        campaign_invitee
        .call_logs
        .all()
        .order_by("-created_at")
    )

    return render(
        request,
        "campaigns/invitee_detail.html",
        {
            "campaign": campaign,
            "campaign_invitee": campaign_invitee,
            "invitee": campaign_invitee.invitee,
            "call_logs": call_logs,
        }
    )

@require_POST
def retry_campaign_invitee(
    request,
    campaign_id,
    campaign_invitee_id
):

    campaign_invitee = get_object_or_404(
        CampaignInvitee.objects.select_related(
            "campaign",
            "invitee"
        ),
        id=campaign_invitee_id,
        campaign_id=campaign_id
    )

    if (
        campaign_invitee.call_status
        != CampaignInvitee.CallStatus.FAILED
    ):

        messages.warning(
            request,
            "Only failed calls can be retried."
        )

        return redirect(
            "campaigns:campaign_invitee_detail",
            campaign_id=campaign_id,
            campaign_invitee_id=campaign_invitee.id
        )

    success = process_campaign_invitee(
        campaign_invitee
    )

    if success:

        messages.success(
            request,
            "Call retried successfully."
        )

    else:

        messages.error(
            request,
            "Retry failed. Please try again later."
        )

    return redirect(
        "campaigns:campaign_invitee_detail",
        campaign_id=campaign_id,
        campaign_invitee_id=campaign_invitee.id
    )