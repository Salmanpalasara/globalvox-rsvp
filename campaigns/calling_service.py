import random
import time


class CallingServiceError(Exception):
    pass


def call_invitee(invitee, campaign):
    """
    Simulates the external AI calling service.

    Replace this implementation with the real assessment
    calling API once its endpoint/schema is available.
    """

    # Small delay just to simulate an external service.
    time.sleep(0.1)

    # Simulate occasional provider failure.
    if random.random() < 0.10:
        raise CallingServiceError(
            "Simulated calling provider failure."
        )

    outcomes = [
        "CONFIRMED",
        "DECLINED",
        "UNDECIDED",
    ]

    outcome = random.choice(outcomes)

    notes = {
        "CONFIRMED": (
            f"{invitee.name} confirmed attendance."
        ),
        "DECLINED": (
            f"{invitee.name} declined the invitation."
        ),
        "UNDECIDED": (
            f"{invitee.name} needs more time to decide."
        ),
    }

    return {
        "success": True,
        "rsvp_status": outcome,
        "notes": notes[outcome],
        "provider_call_id": (
            f"SIM-{campaign.id}-{invitee.id}"
        ),
    }