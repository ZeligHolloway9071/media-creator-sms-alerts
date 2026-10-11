from .infrai_client import InfraiSms
from .models import AlertResult, JobState, ProcessingJob


def notify_creator(job: ProcessingJob, sms: InfraiSms) -> AlertResult:
    """Send one creator alert when media processing completes successfully."""
    if job.state is not JobState.succeeded or not job.asset.creator_phone:
        return AlertResult(sent=False)
    message = f"Your video '{job.asset.title}' is ready to publish."
    data = sms.send(job.asset.creator_phone, message, request_id=f"job:{job.job_id}:ready")
    return AlertResult(sent=True, message_id=data.get("message_id"))

