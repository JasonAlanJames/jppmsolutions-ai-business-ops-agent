from app.email_ops.schemas import EmailTriageResult


IMPORTANT_SENDERS = (
    "openai.com",
    "google.com",
    "stripe.com",
    "paypal.com",
    "github.com",
    "hostinger.com",
    "namecheap.com",
    "godaddy.com",
    "cloudflare.com",
    "paidmembershipspro.com",
    "woocommerce.com",
)

AUTOMATED_SENDERS = (
    "noreply",
    "no-reply",
    "notifications@",
    "alerts@",
    "newsletter",
    "mailer",
    "marketing",
)

SPAM_TERMS = (
    "casino",
    "lottery",
    "free money",
    "crypto investment",
    "guaranteed seo",
    "seo guaranteed",
    "urgent business proposal",
    "wire transfer",
    "inheritance",
    "claim your prize",
    "adult",
    "viagra",
    "loan approval",
)

ARCHIVE_TERMS = (
    "newsletter",
    "digest",
    "weekly update",
    "tips",
    "webinar",
    "offer ends",
    "limited-time offer",
    "product update",
    "new features",
    "alert - content",
    "new ais",
    "unsubscribe",
    "promotion",
)

SENSITIVE_TERMS = (
    "api key",
    "password",
    "token",
    "secret",
    "private key",
    "oauth",
    "invoice",
    "billing",
    "payment",
    "receipt",
    "refund",
    "charge",
    "failed payment",
    "account funded",
    "legal",
    "contract",
    "tax",
    "security alert",
    "login attempt",
    "suspicious",
    "verify your account",
)

REPLY_REQUEST_TERMS = (
    "can you",
    "could you",
    "please contact",
    "please reply",
    "quote",
    "estimate",
    "pricing",
    "interested in",
    "need help",
    "looking for",
    "schedule a call",
    "consultation",
    "proposal",
    "partnership",
    "sponsorship",
    "collaboration",
    "support request",
)


def route_brand(text: str) -> str:
    if any(term in text for term in ["course", "certification", "student", "training", "ai essentials"]):
        return "AI Agent Innovation Academy"

    if any(term in text for term in ["website", "hosting", "domain", "app development", "web app", "ai agent", "chatbot", "automation", "crm"]):
        return "App & Web Developers"

    if any(term in text for term in ["printing", "flyer", "banner", "eddm", "direct mail", "postcard", "brochure", "sticker"]):
        return "MyPrintingDeals"

    if any(term in text for term in ["3d print", "3d figs", "figurine", "stl", "3mf", "bambu"]):
        return "3D Figs"

    if any(term in text for term in ["socal television", "today in socal", "restaurant review", "local media", "sponsorship", "event coverage"]):
        return "SoCal Television"

    if any(term in text for term in ["world television", "global tv", "international tv", "streaming channel"]):
        return "World Television TV"

    if any(term in text for term in ["tripping ai", "travel", "itinerary", "destination"]):
        return "Tripping AI"

    if any(term in text for term in ["tapcard", "digital business card", "qr business card", "nfc card"]):
        return "TapCard Digital Business Card"

    if any(term in text for term in ["real estate", "realtor", "listing", "property video", "property photography"]):
        return "Realty Media Expert"

    if any(term in text for term in ["marketing", "lead generation", "advertising", "promote my business"]):
        return "USA Marketing NOW"

    if any(term in text for term in ["useful ai hacks", "youtube", "sponsor video", "review my ai tool", "ai tool review"]):
        return "Useful AI Hacks"

    if any(term in text for term in ["vlogit", "video upload", "social media platform", "paid event"]):
        return "VLOGit Social Media"

    return "JPPM Solutions"


def classify_email(subject: str, sender: str, body: str) -> EmailTriageResult:
    text = f"{subject} {sender} {body}".lower()
    brand = route_brand(text)

    is_automated = any(term in sender.lower() for term in AUTOMATED_SENDERS)
    is_important_sender = any(domain in sender.lower() for domain in IMPORTANT_SENDERS)
    has_sensitive_content = any(term in text for term in SENSITIVE_TERMS)
    has_reply_request = any(term in text for term in REPLY_REQUEST_TERMS)
    has_archive_signal = any(term in text for term in ARCHIVE_TERMS)
    has_spam_signal = any(term in text for term in SPAM_TERMS)

    if has_spam_signal:
        return EmailTriageResult(
            category="spam",
            brand_route=brand,
            priority="low",
            needs_reply=False,
            human_approval_required=True,
            reason="Email contains spam-like language or irrelevant solicitation terms.",
            suggested_subject="",
            draft_reply="",
        )

    if has_sensitive_content or is_important_sender:
        needs_reply = has_reply_request and not is_automated

        return EmailTriageResult(
            category="human_review",
            brand_route=brand,
            priority="high",
            needs_reply=needs_reply,
            human_approval_required=True,
            reason=(
                "Email appears business-critical, account-related, billing-related, "
                "security-related, or from an important service provider."
            ),
            suggested_subject=f"Re: {subject}" if needs_reply else "",
            draft_reply=(
                "Thank you for your message. We received your request and will review the details carefully. "
                "A member of our team will follow up if additional action is needed."
                if needs_reply
                else ""
            ),
        )

    if is_automated or has_archive_signal:
        return EmailTriageResult(
            category="archive",
            brand_route=brand,
            priority="low",
            needs_reply=False,
            human_approval_required=True,
            reason="Email appears to be an automated notification, newsletter, product update, or marketing message.",
            suggested_subject="",
            draft_reply="",
        )

    if has_reply_request:
        return EmailTriageResult(
            category="needs_reply",
            brand_route=brand,
            priority="medium",
            needs_reply=True,
            human_approval_required=True,
            reason=f"Email appears to be a legitimate inquiry that should be routed to {brand}.",
            suggested_subject=f"Re: {subject}",
            draft_reply=(
                f"Thank you for reaching out. Based on your message, this appears to be a good fit for {brand}. "
                "We received your inquiry and would be happy to review the details. "
                "Could you please provide any additional project details, timeline, and goals so we can better assist you?"
            ),
        )

    return EmailTriageResult(
        category="archive",
        brand_route=brand,
        priority="low",
        needs_reply=False,
        human_approval_required=True,
        reason="Email does not appear to require a reply and can likely be archived after review.",
        suggested_subject="",
        draft_reply="",
    )