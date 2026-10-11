import argparse

from media_sms.infrai_client import InfraiSms
from media_sms.models import Asset, JobState, ProcessingJob
from media_sms.service import notify_creator


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a media-ready SMS to its creator")
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--phone", required=True)
    parser.add_argument("--job-id", required=True)
    args = parser.parse_args()
    job = ProcessingJob(args.job_id, Asset(args.asset_id, args.title, args.phone), JobState.succeeded)
    result = notify_creator(job, InfraiSms())
    print({"sent": result.sent, "message_id": result.message_id})


if __name__ == "__main__":
    main()

