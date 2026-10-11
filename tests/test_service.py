from media_sms.models import Asset, JobState, ProcessingJob
from media_sms.service import notify_creator
from media_sms.infrai_client import InfraiSms
from unittest.mock import Mock


class FakeSms:
    def __init__(self):
        self.calls = []

    def send(self, to, message, request_id):
        self.calls.append((to, message, request_id))
        return {"message_id": "msg_123"}


def test_failed_processing_job_does_not_alert_creator():
    sms = FakeSms()
    job = ProcessingJob("job-7", Asset("asset-2", "Trailer", "+15550001"), JobState.failed)
    result = notify_creator(job, sms)
    assert result.sent is False
    assert sms.calls == []


def test_successful_job_alerts_once_with_stable_request_id():
    sms = FakeSms()
    job = ProcessingJob("job-7", Asset("asset-2", "Trailer", "+15550001"), JobState.succeeded)
    result = notify_creator(job, sms)
    assert result == type(result)(sent=True, message_id="msg_123")
    assert sms.calls == [("+15550001", "Your video 'Trailer' is ready to publish.", "job:job-7:ready")]


def test_http_request_uses_sms_body_field():
    session = Mock()
    session.request.return_value.json.return_value = {"ok": True, "data": {"message_id": "msg_123"}}

    InfraiSms(key="test-key", session=session).send("+15550001", "Ready", "job:job-7:ready")

    assert session.request.call_args.kwargs["json"] == {"to": "+15550001", "body": "Ready"}
