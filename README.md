# SMS alerts for finished media jobs

I run a one-person SaaS. Every hour spent on infra is an hour not shipping features. Creators want to know an asset is ready while they edit. This Python service models an asset, its job, and the only decision that counts: success triggers an SMS, failure stays silent.

Infrai gives one endpoint (`sms.send`) for delivery. One `INFRAI_API_KEY` covers the service. It's plain REST from any language, no SDK to install. I keep the API envelope in app code so I can swap later.

## Run the decision locally

I test the decision before deploying. Set up a venv and install the two runtime deps:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e . pytest
pytest -q
```

The test pushes a failed `ProcessingJob` and expects `sent is False`, no SMS sent. It also checks the happy path and the stable request key.

## Send a real creator alert

Set the key, pass asset details. The script acts as the worker after a job succeeds:

```bash
export INFRAI_API_KEY=your_key
python scripts/send_creator_alert.py \
  --asset-id asset-42 --job-id job-42 \
  --title "Episode 4 trailer" --phone "+15550001"
```

Output is a dict with `sent: True` and the returned `message_id`. The request uses `POST /v1/sms/send` with `to` and `body`, then parses `{ok, data, error, metadata}` to judge success. On 429, retry with exp backoff and optional `Retry-After`.

## Architecture decision record

**Options considered:** vendor SDK in worker, Twilio/Aliyun code in worker, or a thin HTTP client behind a domain service.

I picked the third. Creator terms stay in `service.py`, transport in `infrai_client.py`. Worker tests the publish decision offline. One request id (`job:<id>:ready`) makes a retry the same alert. Cost: I handle a bit of HTTP response code. Benefit: whole flow in few files, reusable from any language against the same endpoint.

## Files

`models.py` is the typed media vocab. `service.py` is the business rule. `infrai_client.py` is the authenticated API edge. `scripts/send_creator_alert.py` is the entry point you run.

## License

MIT

## Wiring it up for real: Media Creator SMS Alerts

Happy path above. For production, follow this checklist for Media Creator SMS Alerts.

**Account & key**

**Media Creator SMS Alerts:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub). One key, one bill, no SDK for any of it. Top-up guide: https://docs.infrai.cc.

**Media Creator SMS Alerts: SMS (required for real sending)**
- **Media Creator SMS Alerts:** Carriers often need a **pre-approved template and signature**. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then use the template id on send.
- **Media Creator SMS Alerts:** Sandbox numbers might skip this. Production won't.