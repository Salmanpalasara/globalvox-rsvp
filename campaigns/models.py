from django.db import models


class Invitee(models.Model):

    name = models.CharField(max_length=150)

    phone = models.CharField(
        max_length=20,
        unique=True
    )

    email = models.EmailField(
        max_length=255,
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} - {self.phone}"


class Campaign(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        RUNNING = "RUNNING", "Running"
        COMPLETED = "COMPLETED", "Completed"

    name = models.CharField(max_length=200)
    event_name = models.CharField(max_length=200)
    event_date = models.DateField()
    event_location = models.CharField(max_length=200)
    objective = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CampaignInvitee(models.Model):

    class RSVPStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        DECLINED = "DECLINED", "Declined"
        UNDECIDED = "UNDECIDED", "Undecided"

    class CallStatus(models.TextChoices):
        NOT_STARTED = "NOT_STARTED", "Not Started"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="campaign_invitees"
    )

    invitee = models.ForeignKey(
        Invitee,
        on_delete=models.CASCADE,
        related_name="campaigns"
    )

    rsvp_status = models.CharField(
        max_length=20,
        choices=RSVPStatus.choices,
        default=RSVPStatus.PENDING,
        db_index=True
    )

    call_status = models.CharField(
        max_length=20,
        choices=CallStatus.choices,
        default=CallStatus.NOT_STARTED,
        db_index=True
    )

    notes = models.TextField(blank=True)

    attempt_count = models.PositiveIntegerField(default=0)

    last_called_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["campaign", "invitee"],
                name="unique_campaign_invitee"
            )
        ]

    def __str__(self):
        return f"{self.invitee.name} - {self.campaign.name}"


class CallLog(models.Model):

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    campaign_invitee = models.ForeignKey(
        CampaignInvitee,
        on_delete=models.CASCADE,
        related_name="call_logs"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices
    )

    request_data = models.JSONField(
        null=True,
        blank=True
    )

    response_data = models.JSONField(
        null=True,
        blank=True
    )

    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.campaign_invitee.invitee.name} - {self.status}"