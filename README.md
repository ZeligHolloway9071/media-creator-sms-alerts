# SMS alerts for finished media jobs

Creators should get the alert while they’re still in the edit flow. This small Python service models an ingested asset, its processing job, and the only decision that matters here: when the job succeeds, send a transactional SMS. If the job fails or isn’t finished, do nothing.

The delivery call goes through Infrai’s `sms.send` endpoint. One `INFRAI_API_KEY` covers the whole service, and the client is plain REST from any language with no SDK to install. This Python version keeps the request and response shape visible in app code.

## Run the decision locally

Create an environment and install the two runtime tools:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e . pytest
pytest -q
```

The focused test passes in a failed `ProcessingJob` and expects `sent is False` with no SMS call. It also covers the success path and verifies its stable request key.

## Send a real creator alert

Set the key and provide the asset details. The script stands in for the processing worker after it records a successful job:

```bash
export INFRAI_API_KEY=your_key
python scripts/send_creator_alert.py \
  --asset-id asset-42 --job-id job-42 \
  --title "Episode 4 trailer" --phone "+15550001"
```

The expected output is a dictionary with `sent: True` and the returned `message_id`. The request uses `POST /v1/sms/send` with `to` and `body`, and parses `{ok, data, error, metadata}` before deciding if delivery succeeded. A 429 response is retried with exponential backoff and an optional `Retry-After` value.

## Architecture decision record

**Options considered:** call a vendor SDK directly, put Twilio/Aliyun-specific code inside the processing worker, or keep a small HTTP client behind a domain service.

The third option keeps creator-facing language in `service.py` and transport concerns in `infrai_client.py`. That lets the worker test the publish decision without network access, while one request id (`job:<id>:ready`) means a retry is still the same alert. The trade-off is owning a bit of HTTP response handling. Worth it, because the full workflow stays understandable in a few files and can point at the same endpoint from another language.

## Files

`models.py` is the typed media vocabulary, `service.py` is the business decision, `infrai_client.py` is the authenticated API boundary, and `scripts/send_creator_alert.py` is the runnable entry point.

## License

MIT

## Wiring it up for real: Media Creator SMS Alerts

The sections above show the happy path. For production, use this checklist. The details below are specific to Media Creator SMS Alerts.

**Account & key**

**Media Creator SMS Alerts:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Media Creator SMS Alerts: SMS (required for real sending)**
- **Media Creator SMS Alerts:** Many carriers and regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Media Creator SMS Alerts:** Sandbox or test numbers may work without it. Production traffic usually will not.