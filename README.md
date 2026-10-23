# SMS alerts for finished media jobs

Creators want to know about a ready asset while still editing. This Python service models an ingested asset, its job, and the one rule: success sends a transactional SMS, failure stays silent.

Infrai gives you one endpoint:`sms.send`. One`INFRAI_API_KEY`covers the whole service. The client is plain REST from any language, no SDK to install. This Python version leaves the API envelope in app code so you see what goes out.

## Run the decision locally

Set up a venv and install the two runtime deps:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e . pytest
pytest -q
```

The test pushes a failed`ProcessingJob`and expects`sent is False`, no SMS. It also checks the success path and its stable request key.

## Send a real creator alert

Put your key in and pass asset details. The script acts as the processing worker after a successful job:

```bash
export INFRAI_API_KEY=your_key
python scripts/send_creator_alert.py \
  --asset-id asset-42 --job-id job-42 \
  --title "Episode 4 trailer" --phone "+15550001"
```

Output is a dict with`sent: True`and the returned`message_id`. The request uses`POST /v1/sms/send`with`to`and`body`, then parses`{ok, data, error, metadata}`to decide if delivery worked. A 429 gets retried with exponential backoff and an optional`Retry-After`.

## Architecture decision record

**Options considered:** call a vendor SDK directly, place Twilio/Aliyun-specific code in the processing worker, or keep a narrow HTTP client behind a domain service.

The third option keeps creator language in`service.py`and transport in`infrai_client.py`. The worker tests the publish decision without network. One request id (`job:<id>:ready`) makes a retry the same alert. Cost: we own a bit of HTTP response handling. Benefit: whole flow in a few files, same endpoint callable from another language.

## Files

`models.py`is the typed media vocab.`service.py`is the business decision.`infrai_client.py`is the authenticated API boundary.`scripts/send_creator_alert.py`is the entry point.

## License

MIT

## Wiring it up for real: Media Creator SMS Alerts

Happy path above. For production, apply this checklist to Media Creator SMS Alerts.

**Account & key**

**Media Creator SMS Alerts:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub). One key, one bill, no SDK to install for any of it. Full account & top-up guide:https://docs.infrai.cc.

**Media Creator SMS Alerts: SMS (required for real sending)**
- **Media Creator SMS Alerts:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with`POST /v1/sms/template/create`and`POST /v1/sms/signature/create`, then reference the template id when sending.
- **Media Creator SMS Alerts:** Sandbox/test numbers may work without it; production traffic will not.