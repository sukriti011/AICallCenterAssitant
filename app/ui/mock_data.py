from __future__ import annotations
from typing import Any

SAMPLE_TRANSCRIPTS = {
    "Billing Dispute": "Agent: Hello, thanks for calling support. Customer: I was charged twice for last month and need a refund. Agent: I can help with that. Let me verify your order number and email.",
    "Technical Support": "Agent: Thank you for calling support. Customer: The app crashes after login on iOS. Agent: I understand, let us gather device details and escalate to Tier 2 if needed.",
    "Escalation": "Agent: Hello, how may I help? Customer: This is my third call and my issue is still unresolved. Agent: I apologize and will arrange manager follow-up today.",
    "Sentiment Demo (Audio-style)": (
        "Agent: Hello, thank you for calling support. "
        "Customer: [annoyed] This is the third time I'm calling and my issue is still not fixed! "
        "Agent: [apologetic] I sincerely apologize for the inconvenience. Let me help resolve this for you. "
        "Customer: My refund has not been processed yet. "
        "Agent: [understanding] I understand your frustration. Let me check the status immediately. "
        "Customer: [frustrated] This is very frustrating. "
        "Agent: [reassuring] I will escalate this to our senior support team and ensure it is handled as a priority. "
        "Customer: It better be resolved soon. "
        "Agent: [calmly] I assure you we will follow up within 24 hours."
    ),
}

DEMO_RESULT = {
    "transcript": (
        "Agent: Hello, thank you for calling. "
        "Customer: I am calling about a refund for a canceled order. "
        "Agent: Absolutely, I can help with that request today. "
        "Customer: Please verify when the refund will be processed. "
        "Agent: I will confirm status and send a follow-up email."
    ),
    "summary": {
        "summary": (
            "Customer requested a refund for a canceled order. Agent gathered required details, "
            "confirmed next steps, and committed to email follow-up within processing window."
        ),
        "key_points": [
            "Customer issue: Refund for canceled order",
            "Resolution: Refund request initiated",
            "Next step: Follow up in 5-7 days",
        ],
        "action_items": [
            "Confirm refund processing timeline",
            "Send confirmation email to customer",
            "Escalate to Tier 2 if processing is delayed",
        ],
        "tags": ["Refund", "Escalation", "Billing", "Compliance", "Customer Service"],
    },
    "quality_score": {
        "tone_score": 0.75,
        "empathy_score": 0.8,
        "professionalism_score": 0.85,
        "resolution_score": 0.8,
        "overall_score": 0.82,
        "compliance_flags": [],
    },
    "routing": {
        "route": "standard_complete",
        "used_fallback": False,
        "reason": "Quality checks passed",
    },
    "pipeline_trace": [
        {"step": "Intake Agent", "status": "ok", "detail": "1.2s"},
        {"step": "Transcription Agent", "status": "ok", "detail": "3.5s"},
        {"step": "Summarization Agent", "status": "ok", "detail": "2.8s"},
        {"step": "QA Scoring Agent", "status": "ok", "detail": "1.1s"},
        {"step": "Routing Agent", "status": "ok", "detail": "0.4s"},
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# Per-call analysis data
# Each entry mirrors the shape of DEMO_RESULT so render_call_detail_view works
# without any changes.  Swap this dict for a real DB / API lookup later.
# ─────────────────────────────────────────────────────────────────────────────
_MOCK_CALL_ANALYSIS: dict[str, dict] = {
    "CALL-001": {
        "transcript": (
            "Agent: Hello, thank you for calling. "
            "Customer: I am calling about a refund for a canceled order. "
            "Agent: Absolutely, I can help with that request today. "
            "Customer: Please verify when the refund will be processed. "
            "Agent: I will confirm status and send a follow-up email."
        ),
        "summary": {
            "summary": (
                "Customer requested a refund for a canceled order. Agent gathered required details, "
                "confirmed next steps, and committed to email follow-up within the processing window."
            ),
            "key_points": [
                "Customer issue: Refund for canceled order",
                "Resolution: Refund request initiated",
                "Next step: Follow up in 5–7 business days",
            ],
            "action_items": [
                "Confirm refund processing timeline in billing system",
                "Send confirmation email to customer",
                "Escalate to Tier 2 if processing is delayed beyond 7 days",
            ],
            "tags": ["Refund", "Billing", "Order Cancellation", "Compliance", "Customer Service"],
        },
        "quality_score": {
            "tone_score": 0.80, "empathy_score": 0.82, "professionalism_score": 0.85,
            "resolution_score": 0.82, "overall_score": 0.82, "compliance_flags": [],
        },
        "routing": {"route": "standard_complete", "used_fallback": False, "reason": "Quality checks passed"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "1.2s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "3.5s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "2.8s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "1.1s"},
            {"step": "Routing Agent", "status": "ok", "detail": "0.4s"},
        ],
    },
    "CALL-002": {
        "transcript": (
            "Agent: Thank you for calling, how can I help? "
            "Customer: [angry] I have been waiting three weeks for my refund and nobody has helped me! "
            "Agent: [apologetic] I sincerely apologize for the delay. Let me pull up your account right now. "
            "Customer: [frustrated] This is completely unacceptable. I want to speak to a manager. "
            "Agent: I completely understand. I am escalating this to a senior specialist immediately. "
            "Customer: [frustrated] I expect a call back within the hour."
        ),
        "summary": {
            "summary": (
                "Customer called in an escalated state regarding a three-week delayed refund. "
                "Agent acknowledged the issue, apologized, and escalated to a senior specialist. "
                "Customer demanded a callback within one hour."
            ),
            "key_points": [
                "Customer issue: 3-week delayed refund with no resolution",
                "Resolution: Escalated to senior specialist",
                "Next step: Manager callback within 1 hour",
            ],
            "action_items": [
                "Escalate ticket to senior billing specialist",
                "Arrange manager callback within 60 minutes",
                "Issue expedited refund credit if not processed within 24 hours",
            ],
            "tags": ["Escalation", "Refund Delay", "Angry Customer", "Compliance", "Priority"],
        },
        "quality_score": {
            "tone_score": 0.65, "empathy_score": 0.72, "professionalism_score": 0.60,
            "resolution_score": 0.48, "overall_score": 0.61, "compliance_flags": ["escalation_required"],
        },
        "routing": {"route": "escalation_required", "used_fallback": True, "reason": "Customer demanded manager; refund delay exceeds SLA"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "1.4s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "4.2s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "3.1s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "1.3s"},
            {"step": "Routing Agent", "status": "escalated", "detail": "0.6s"},
        ],
    },
    "CALL-003": {
        "transcript": (
            "Agent: Hello, thank you for calling. How can I assist you today? "
            "Customer: [happy] Hi! I just wanted to upgrade my plan to the premium tier. "
            "Agent: That is wonderful, I would be happy to help you with that upgrade. "
            "Customer: [pleased] Great, I have been really happy with the service so far. "
            "Agent: I am glad to hear that. I will process the upgrade now and email you the confirmation. "
            "Customer: [grateful] Perfect, thank you so much!"
        ),
        "summary": {
            "summary": (
                "Customer called to upgrade their subscription to the premium tier. "
                "Agent processed the upgrade smoothly and sent a confirmation email. "
                "Customer expressed satisfaction with service throughout the call."
            ),
            "key_points": [
                "Customer issue: Subscription upgrade request",
                "Resolution: Premium tier upgrade processed successfully",
                "Next step: Confirmation email sent; new tier active immediately",
            ],
            "action_items": [
                "Confirm premium upgrade is reflected in billing system",
                "Send welcome email with premium feature guide",
                "Schedule 30-day check-in to ensure customer satisfaction",
            ],
            "tags": ["Upgrade", "Subscription", "Happy Customer", "Upsell", "Retention"],
        },
        "quality_score": {
            "tone_score": 0.95, "empathy_score": 0.94, "professionalism_score": 0.93,
            "resolution_score": 0.92, "overall_score": 0.93, "compliance_flags": [],
        },
        "routing": {"route": "standard_complete", "used_fallback": False, "reason": "All quality checks passed with high scores"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "0.9s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "2.7s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "2.1s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "0.8s"},
            {"step": "Routing Agent", "status": "ok", "detail": "0.3s"},
        ],
    },
    "CALL-004": {
        "transcript": (
            "Agent: Thank you for calling, how can I help today? "
            "Customer: [annoyed] My package was supposed to arrive five days ago and it still hasn't shown up. "
            "Agent: I am sorry to hear that. Let me check the tracking information for your order. "
            "Customer: [frustrated] I have already checked online and it just says in transit. I need answers. "
            "Agent: I understand your frustration. The shipment appears to be delayed at a regional hub. "
            "Customer: [frustrated] I need this escalated. Can you issue a partial refund while we wait? "
            "Agent: I can initiate a partial refund and flag this for logistics follow-up right away."
        ),
        "summary": {
            "summary": (
                "Customer contacted support about a package delayed five days past the expected delivery date. "
                "Agent located the shipment stuck at a regional hub and initiated a partial refund. "
                "Call escalated to logistics team for delivery resolution."
            ),
            "key_points": [
                "Customer issue: Package delayed 5 days past expected delivery",
                "Resolution: Partial refund initiated; logistics team flagged",
                "Next step: Logistics follow-up within 24 hours",
            ],
            "action_items": [
                "Process partial refund for shipping delay",
                "Escalate shipment case to logistics team",
                "Notify customer by email once package is out for delivery",
            ],
            "tags": ["Shipping Delay", "Partial Refund", "Logistics", "Escalation", "Customer Service"],
        },
        "quality_score": {
            "tone_score": 0.76, "empathy_score": 0.78, "professionalism_score": 0.74,
            "resolution_score": 0.68, "overall_score": 0.74, "compliance_flags": ["partial_refund_issued"],
        },
        "routing": {"route": "escalation_logistics", "used_fallback": True, "reason": "Shipping delay exceeds threshold; logistics escalation required"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "1.3s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "3.9s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "2.9s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "1.2s"},
            {"step": "Routing Agent", "status": "escalated", "detail": "0.5s"},
        ],
    },
    "CALL-005": {
        "transcript": (
            "Agent: Hello, technical support. How can I help you today? "
            "Customer: Hi, I am locked out of my account. I have been trying to reset my password but the link never arrives. "
            "Agent: I can help you with that. Let me verify your account email first. "
            "Customer: Sure, it is the email I signed up with. "
            "Agent: I found the account. The reset emails were going to your spam folder. I will send a new one now and whitelist your address. "
            "Customer: Oh, I see it now. Thank you, that worked!"
        ),
        "summary": {
            "summary": (
                "Customer was locked out of their account because password reset emails were being filtered to spam. "
                "Agent identified the root cause, sent a new reset link, and whitelisted the email address. "
                "Issue resolved within the call with no escalation needed."
            ),
            "key_points": [
                "Customer issue: Account lockout due to missing password reset emails",
                "Resolution: Reset email resent; spam filter issue resolved",
                "Next step: Customer to update spam settings; no follow-up required",
            ],
            "action_items": [
                "Whitelist customer email address in the mail delivery system",
                "Send new password reset link",
                "Log spam filter issue for the platform team to investigate",
            ],
            "tags": ["Account Access", "Password Reset", "Technical Support", "Email Delivery", "Resolved"],
        },
        "quality_score": {
            "tone_score": 0.88, "empathy_score": 0.86, "professionalism_score": 0.90,
            "resolution_score": 0.90, "overall_score": 0.88, "compliance_flags": [],
        },
        "routing": {"route": "standard_complete", "used_fallback": False, "reason": "Technical issue resolved within call"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "1.0s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "3.0s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "2.3s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "0.9s"},
            {"step": "Routing Agent", "status": "ok", "detail": "0.3s"},
        ],
    },
    "CALL-006": {
        "transcript": (
            "Agent: Hello, how may I assist you today? "
            "Customer: [angry] I want to cancel my account immediately. You have been charging me for a plan I downgraded months ago. "
            "Agent: I am very sorry about that. Let me review your billing history right away. "
            "Customer: [frustrated] I have called about this twice already and nothing has been done. I have been overcharged for four months. "
            "Agent: I can see the billing discrepancy on my screen. I will escalate this to our billing compliance team. "
            "Customer: [frustrated] I am not satisfied with just an escalation. I want a full refund for four months. "
            "Agent: I completely understand. I am opening a formal billing dispute ticket now and flagging it as high priority."
        ),
        "summary": {
            "summary": (
                "Customer called to cancel their account after being overcharged for four months following a plan downgrade. "
                "This was the customer's third contact about the same issue. Agent identified the billing error and opened a "
                "formal compliance dispute ticket. Customer is at high churn risk."
            ),
            "key_points": [
                "Customer issue: 4-month overcharge after plan downgrade",
                "Resolution: Formal billing dispute ticket opened; escalated to compliance",
                "Next step: Billing compliance review within 48 hours; full refund decision pending",
            ],
            "action_items": [
                "Open formal billing dispute ticket — high priority",
                "Escalate to billing compliance team within 4 hours",
                "Review all charges from the downgrade date and calculate refund amount",
                "Flag customer account for churn risk follow-up",
            ],
            "tags": ["Billing Dispute", "Overcharge", "Account Cancellation", "Compliance", "Churn Risk"],
        },
        "quality_score": {
            "tone_score": 0.58, "empathy_score": 0.62, "professionalism_score": 0.55,
            "resolution_score": 0.44, "overall_score": 0.55, "compliance_flags": ["billing_dispute", "repeat_contact", "compliance_review_required"],
        },
        "routing": {"route": "compliance_escalation", "used_fallback": True, "reason": "Repeat billing complaint; compliance review required"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "1.6s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "4.8s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "3.4s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "1.5s"},
            {"step": "Routing Agent", "status": "escalated", "detail": "0.7s"},
        ],
    },
    "CALL-007": {
        "transcript": (
            "Agent: Hello, thank you for calling. How can I help? "
            "Customer: I am looking to change from the annual plan to a monthly plan. Is that possible? "
            "Agent: Yes, absolutely. I can process that change for you. The new rate would apply at your next billing cycle. "
            "Customer: And will I lose any features by switching? "
            "Agent: No, all features remain the same. The only difference is the billing frequency and the per-month rate. "
            "Customer: Perfect, let us go ahead and switch to monthly."
        ),
        "summary": {
            "summary": (
                "Customer requested a plan change from annual to monthly billing. "
                "Agent confirmed the change is possible, explained there are no feature changes, "
                "and processed the switch effective at the next billing cycle."
            ),
            "key_points": [
                "Customer issue: Request to switch from annual to monthly billing",
                "Resolution: Plan change processed; effective next billing cycle",
                "Next step: Confirmation email with new billing date",
            ],
            "action_items": [
                "Process plan change to monthly billing in the system",
                "Send confirmation email with updated billing schedule",
                "Add a note to the account about the pricing change reason",
            ],
            "tags": ["Plan Change", "Billing", "Subscription", "Account Management", "Resolved"],
        },
        "quality_score": {
            "tone_score": 0.82, "empathy_score": 0.78, "professionalism_score": 0.80,
            "resolution_score": 0.78, "overall_score": 0.79, "compliance_flags": [],
        },
        "routing": {"route": "standard_complete", "used_fallback": False, "reason": "Plan change completed; no compliance flags"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "1.1s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "3.2s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "2.4s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "1.0s"},
            {"step": "Routing Agent", "status": "ok", "detail": "0.4s"},
        ],
    },
    "CALL-008": {
        "transcript": (
            "Agent: Thank you for calling, how can I help today? "
            "Customer: [frustrated] This is the fourth time I am calling about the same problem. My invoice is still wrong. "
            "Agent: I apologize for the repeated inconvenience. Let me review the full history of your case. "
            "Customer: [frustrated] Every time I call, someone says it will be fixed and it never is. "
            "Agent: I can see four prior contacts on this account. I am going to personally own this case and ensure it is resolved today. "
            "Customer: [frustrated] I have heard that before. I need this fixed now or I am disputing the charge with my bank."
        ),
        "summary": {
            "summary": (
                "Customer contacted support for the fourth time about an incorrect invoice that has not been resolved. "
                "Agent acknowledged the repeated failure, reviewed the full case history, and committed to personally "
                "owning the resolution. Customer threatened a bank dispute if not resolved immediately."
            ),
            "key_points": [
                "Customer issue: Incorrect invoice — 4th contact, still unresolved",
                "Resolution: Agent escalated and committed to personal case ownership",
                "Next step: Resolve invoice error within 24 hours; contact customer directly",
            ],
            "action_items": [
                "Correct the invoice error in the billing system today",
                "Call customer back within 2 hours with confirmation",
                "File an internal complaint about repeated failed resolutions",
                "Flag account to prevent bank dispute charge-back",
            ],
            "tags": ["Invoice Error", "Repeat Contact", "Escalation", "Billing", "Churn Risk"],
        },
        "quality_score": {
            "tone_score": 0.70, "empathy_score": 0.74, "professionalism_score": 0.68,
            "resolution_score": 0.55, "overall_score": 0.67, "compliance_flags": ["repeat_contact", "chargeback_risk"],
        },
        "routing": {"route": "escalation_required", "used_fallback": True, "reason": "4th contact; chargeback risk; personal escalation committed"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "1.4s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "4.1s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "3.0s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "1.2s"},
            {"step": "Routing Agent", "status": "escalated", "detail": "0.5s"},
        ],
    },
    "CALL-009": {
        "transcript": (
            "Agent: Hello, thank you for calling returns and exchanges. How can I help? "
            "Customer: [happy] Hi! I bought a jacket last week but I ordered the wrong size. Can I do an exchange? "
            "Agent: Of course, exchanges are easy. I will generate a free return label for you right now. "
            "Customer: [pleased] Oh that is so convenient, thank you. How long will the exchange take? "
            "Agent: Once we receive the return, the new size ships within one business day. "
            "Customer: [grateful] Perfect! I really appreciate the quick help."
        ),
        "summary": {
            "summary": (
                "Customer requested an exchange for a jacket purchased in the wrong size. "
                "Agent quickly issued a free return label and explained the one-business-day turnaround. "
                "Customer was highly satisfied with the experience."
            ),
            "key_points": [
                "Customer issue: Wrong size jacket — exchange requested",
                "Resolution: Free return label issued; exchange approved",
                "Next step: New size ships within 1 business day of return receipt",
            ],
            "action_items": [
                "Generate and email prepaid return label",
                "Reserve correct size in warehouse",
                "Confirm exchange shipment when return is received",
            ],
            "tags": ["Returns", "Exchange", "Happy Customer", "Order Management", "Resolved"],
        },
        "quality_score": {
            "tone_score": 0.93, "empathy_score": 0.91, "professionalism_score": 0.92,
            "resolution_score": 0.90, "overall_score": 0.91, "compliance_flags": [],
        },
        "routing": {"route": "standard_complete", "used_fallback": False, "reason": "Exchange processed; no compliance flags"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "0.8s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "2.6s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "1.9s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "0.7s"},
            {"step": "Routing Agent", "status": "ok", "detail": "0.3s"},
        ],
    },
    "CALL-010": {
        "transcript": (
            "Agent: Thank you for calling, how can I assist today? "
            "Customer: I am trying to use the platform but it seems like everything is down. Is there an outage? "
            "Agent: Yes, we are currently experiencing a partial service disruption affecting some regions. Our team is actively working on it. "
            "Customer: Any idea when it will be resolved? I have a deadline in two hours. "
            "Agent: Our engineering team expects full restoration within 90 minutes. I am noting your account for priority access once service resumes. "
            "Customer: Okay, I will wait. Can you send me an update by email once it is resolved? "
            "Agent: Absolutely, I will add you to our outage notification list right now."
        ),
        "summary": {
            "summary": (
                "Customer contacted support during an active partial service outage affecting their region. "
                "Agent communicated the 90-minute restoration estimate, added the customer to outage notifications, "
                "and flagged the account for priority access. Customer accepted the resolution with some urgency."
            ),
            "key_points": [
                "Customer issue: Service outage preventing platform access",
                "Resolution: Outage confirmed; 90-minute ETA communicated; notification registered",
                "Next step: Email notification on service restoration",
            ],
            "action_items": [
                "Add customer to outage notification list",
                "Flag account for priority access post-restoration",
                "Send resolution email within 10 minutes of service restoration",
            ],
            "tags": ["Service Outage", "Incident", "Technical Support", "Customer Communication", "SLA"],
        },
        "quality_score": {
            "tone_score": 0.74, "empathy_score": 0.72, "professionalism_score": 0.73,
            "resolution_score": 0.65, "overall_score": 0.71, "compliance_flags": ["incident_logged"],
        },
        "routing": {"route": "incident_track", "used_fallback": False, "reason": "Known outage incident; no agent escalation needed"},
        "pipeline_trace": [
            {"step": "Intake Agent", "status": "ok", "detail": "1.2s"},
            {"step": "Transcription Agent", "status": "ok", "detail": "3.6s"},
            {"step": "Summarization Agent", "status": "ok", "detail": "2.7s"},
            {"step": "QA Scoring Agent", "status": "ok", "detail": "1.0s"},
            {"step": "Routing Agent", "status": "ok", "detail": "0.4s"},
        ],
    },
}


def get_mock_call_records() -> list[dict]:
    """Return mock call records for the Manager Dashboard.

    Replace this function body with a real DB query to go live.
    Each record's call_id maps to a full analysis result in _MOCK_CALL_ANALYSIS.
    """
    return [
        {
            "call_id": "CALL-001",
            "agent_name": "Sarah Mitchell",
            "customer_id": "CUST-4821",
            "datetime": "2026-04-29 09:14",
            "duration": "8m 32s",
            "qa_score": 0.82,
            "sentiment": "Neutral",
            "status": "Completed",
            "escalation_flag": False,
            "guardrail_risk": "Low",
            # ── Future Guardrails placeholders ─────────────────────────────
            "pii_detected": False,
            "hallucination_risk": "Low",
            "compliance_risk": "Low",
            "confidence_score": 0.91,
            "requires_human_review": False,
            # ── Future MCP tool action placeholders ────────────────────────
            "customer_profile_checked": False,
            "refund_policy_checked": False,
            "ticket_created": False,
            "manager_notified": False,
        },
        {
            "call_id": "CALL-002",
            "agent_name": "James Okonkwo",
            "customer_id": "CUST-3302",
            "datetime": "2026-04-29 09:41",
            "duration": "12m 07s",
            "qa_score": 0.61,
            "sentiment": "Frustrated",
            "status": "Escalated",
            "escalation_flag": True,
            "guardrail_risk": "High",
            "pii_detected": True,
            "hallucination_risk": "Medium",
            "compliance_risk": "High",
            "confidence_score": 0.54,
            "requires_human_review": True,
            "customer_profile_checked": True,
            "refund_policy_checked": False,
            "ticket_created": True,
            "manager_notified": True,
        },
        {
            "call_id": "CALL-003",
            "agent_name": "Priya Nair",
            "customer_id": "CUST-7710",
            "datetime": "2026-04-29 10:05",
            "duration": "5m 49s",
            "qa_score": 0.93,
            "sentiment": "Happy",
            "status": "Completed",
            "escalation_flag": False,
            "guardrail_risk": "Low",
            "pii_detected": False,
            "hallucination_risk": "Low",
            "compliance_risk": "Low",
            "confidence_score": 0.97,
            "requires_human_review": False,
            "customer_profile_checked": True,
            "refund_policy_checked": False,
            "ticket_created": False,
            "manager_notified": False,
        },
        {
            "call_id": "CALL-004",
            "agent_name": "Sarah Mitchell",
            "customer_id": "CUST-5509",
            "datetime": "2026-04-29 10:28",
            "duration": "9m 15s",
            "qa_score": 0.74,
            "sentiment": "Frustrated",
            "status": "Escalated",
            "escalation_flag": True,
            "guardrail_risk": "Medium",
            "pii_detected": False,
            "hallucination_risk": "Low",
            "compliance_risk": "Medium",
            "confidence_score": 0.72,
            "requires_human_review": True,
            "customer_profile_checked": True,
            "refund_policy_checked": True,
            "ticket_created": True,
            "manager_notified": False,
        },
        {
            "call_id": "CALL-005",
            "agent_name": "Daniel Reyes",
            "customer_id": "CUST-9983",
            "datetime": "2026-04-29 11:02",
            "duration": "6m 00s",
            "qa_score": 0.88,
            "sentiment": "Neutral",
            "status": "Completed",
            "escalation_flag": False,
            "guardrail_risk": "Low",
            "pii_detected": False,
            "hallucination_risk": "Low",
            "compliance_risk": "Low",
            "confidence_score": 0.89,
            "requires_human_review": False,
            "customer_profile_checked": False,
            "refund_policy_checked": False,
            "ticket_created": False,
            "manager_notified": False,
        },
        {
            "call_id": "CALL-006",
            "agent_name": "James Okonkwo",
            "customer_id": "CUST-1147",
            "datetime": "2026-04-29 11:35",
            "duration": "14m 52s",
            "qa_score": 0.55,
            "sentiment": "Frustrated",
            "status": "In Progress",
            "escalation_flag": True,
            "guardrail_risk": "High",
            "pii_detected": True,
            "hallucination_risk": "High",
            "compliance_risk": "High",
            "confidence_score": 0.41,
            "requires_human_review": True,
            "customer_profile_checked": True,
            "refund_policy_checked": True,
            "ticket_created": False,
            "manager_notified": True,
        },
        {
            "call_id": "CALL-007",
            "agent_name": "Priya Nair",
            "customer_id": "CUST-2268",
            "datetime": "2026-04-29 13:10",
            "duration": "7m 22s",
            "qa_score": 0.79,
            "sentiment": "Neutral",
            "status": "Completed",
            "escalation_flag": False,
            "guardrail_risk": "Low",
            "pii_detected": False,
            "hallucination_risk": "Low",
            "compliance_risk": "Low",
            "confidence_score": 0.84,
            "requires_human_review": False,
            "customer_profile_checked": False,
            "refund_policy_checked": False,
            "ticket_created": False,
            "manager_notified": False,
        },
        {
            "call_id": "CALL-008",
            "agent_name": "Daniel Reyes",
            "customer_id": "CUST-6634",
            "datetime": "2026-04-29 14:03",
            "duration": "11m 40s",
            "qa_score": 0.67,
            "sentiment": "Frustrated",
            "status": "Escalated",
            "escalation_flag": True,
            "guardrail_risk": "Medium",
            "pii_detected": False,
            "hallucination_risk": "Medium",
            "compliance_risk": "Medium",
            "confidence_score": 0.63,
            "requires_human_review": True,
            "customer_profile_checked": True,
            "refund_policy_checked": True,
            "ticket_created": True,
            "manager_notified": True,
        },
        {
            "call_id": "CALL-009",
            "agent_name": "Ava Chen",
            "customer_id": "CUST-8801",
            "datetime": "2026-04-29 14:55",
            "duration": "4m 18s",
            "qa_score": 0.91,
            "sentiment": "Happy",
            "status": "Completed",
            "escalation_flag": False,
            "guardrail_risk": "Low",
            "pii_detected": False,
            "hallucination_risk": "Low",
            "compliance_risk": "Low",
            "confidence_score": 0.95,
            "requires_human_review": False,
            "customer_profile_checked": True,
            "refund_policy_checked": False,
            "ticket_created": False,
            "manager_notified": False,
        },
        {
            "call_id": "CALL-010",
            "agent_name": "Marcus Webb",
            "customer_id": "CUST-3371",
            "datetime": "2026-04-29 15:30",
            "duration": "10m 05s",
            "qa_score": 0.71,
            "sentiment": "Neutral",
            "status": "In Progress",
            "escalation_flag": False,
            "guardrail_risk": "Medium",
            "pii_detected": False,
            "hallucination_risk": "Low",
            "compliance_risk": "Medium",
            "confidence_score": 0.76,
            "requires_human_review": False,
            "customer_profile_checked": False,
            "refund_policy_checked": False,
            "ticket_created": False,
            "manager_notified": False,
        },
    ]
