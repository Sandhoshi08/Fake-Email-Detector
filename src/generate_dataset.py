"""
generate_dataset.py
--------------------
Creates a synthetic but realistic dataset of phishing (fake) and legitimate
emails so the project runs end-to-end without needing an external download.

You can later REPLACE data/emails.csv with a real dataset (e.g. from Kaggle's
"Phishing Email Dataset" or "Enron-Spam") as long as it has two columns:
    text,label      (label = 1 for phishing/fake, 0 for legitimate)
"""

import csv
import random

random.seed(42)

# ---------------------------------------------------------------------
# Building blocks used to generate many varied phishing emails
# ---------------------------------------------------------------------
PHISHING_SUBJECTS = [
    "Urgent: Your Account Will Be Suspended",
    "Action Required: Verify Your Identity Now",
    "You Have Won a Prize! Claim Now",
    "Security Alert: Unusual Sign-in Activity Detected",
    "Your Payment Failed - Update Billing Info",
    "Final Notice: Your Package Could Not Be Delivered",
    "Confirm Your Bank Details Immediately",
    "Your Account Has Been Locked",
    "Congratulations! You've Been Selected",
    "Update Your Password to Avoid Suspension",
]

PHISHING_BODIES = [
    "Dear Customer, we detected suspicious activity on your account. "
    "Click the link below within 24 hours to verify your identity or your "
    "account will be permanently suspended. {link}",

    "Congratulations! You have been selected to receive a ${amount} gift card. "
    "To claim your prize, please confirm your personal details here: {link}",

    "Your recent payment of ${amount} could not be processed. Please update "
    "your billing information immediately by clicking here: {link} to avoid "
    "service interruption.",

    "We noticed a login attempt from a new device. If this wasn't you, "
    "secure your account now by verifying your password at {link}. "
    "Failure to act within 12 hours will result in account lock.",

    "Your package could not be delivered due to an incomplete address. "
    "Please confirm your shipping details and pay a small redelivery fee "
    "of ${amount} at {link} to receive your item.",

    "This is your final notice. Your account will be closed permanently "
    "unless you verify your information within 24 hours: {link}. "
    "Failure to comply may result in legal action.",

    "Dear user, our records show your subscription has expired. "
    "Renew now at {link} using your card details to avoid losing access "
    "to all your saved files.",

    "IT Support: Your mailbox has exceeded its storage limit. Click {link} "
    "and log in with your current password to increase your quota "
    "immediately or your emails will be deleted.",

    "Congratulations! You have won a ${amount} cash prize in our monthly "
    "giveaway. To claim your reward, simply confirm your details at {link} "
    "before the offer expires.",

    "We could not verify your recent transaction of ${amount}. To avoid "
    "having your card suspended, please log in and confirm your identity "
    "at {link} within 24 hours.",

    "Your cloud storage account is almost full. Upgrade now at {link} and "
    "enter your login credentials to avoid losing access to your files "
    "permanently.",

    "Attention: unusual activity has been detected on your account from a "
    "new location. Please act now and confirm it was you at {link}, or "
    "your account access will be restricted.",
]

LINKS = [
    "http://secure-update-account.com/verify",
    "http://bank-security-check.net/login",
    "http://claim-your-prize-now.info/redeem",
    "http://paypal-account-verify.support/confirm",
    "http://appleid-locked-support.com/unlock",
    "http://amaz0n-delivery-issue.com/track",
    "http://192.168.44.21/login.php",
    "http://bit.ly/3xUrgentVerify",
]

URGENT_PHRASES = [
    "act now", "immediate action required", "your account will be suspended",
    "verify your identity", "click here immediately", "limited time offer",
    "failure to respond will result in", "final warning", "confirm your details",
    "unusual activity detected",
]

# ---------------------------------------------------------------------
# Building blocks for legitimate emails
# ---------------------------------------------------------------------
LEGIT_SUBJECTS = [
    "Team Meeting Rescheduled to 3 PM",
    "Your Order Has Shipped",
    "Monthly Newsletter - July Edition",
    "Invoice #4521 for Your Records",
    "Reminder: Project Deadline Next Friday",
    "Welcome to the Team!",
    "Weekly Progress Report",
    "Your Flight Itinerary",
    "Notes from Yesterday's Call",
    "Lunch Plans This Week?",
]

LEGIT_BODIES = [
    "Hi {name}, just a reminder that our meeting has been moved to 3 PM "
    "today in the main conference room. Let me know if that doesn't work "
    "for you. Thanks, {sender}",

    "Hello {name}, your order #{order} has shipped and should arrive within "
    "3-5 business days. You can track it from your account dashboard. "
    "Thanks for shopping with us!",

    "Hi {name}, attached is the monthly newsletter with updates from the "
    "team, upcoming events, and a few articles we thought you'd enjoy. "
    "Have a great read!",

    "Hi {name}, please find attached invoice #{order} for last month's "
    "services. Let us know if you have any questions about the charges. "
    "Best regards, {sender}",

    "Hey {name}, quick reminder that the project deliverables are due next "
    "Friday. Let me know if you need any help wrapping things up. "
    "Cheers, {sender}",

    "Welcome aboard, {name}! We're excited to have you join the team. "
    "Your manager {sender} will reach out shortly to set up your onboarding "
    "schedule.",

    "Hi {name}, here's the weekly progress report. Overall things are on "
    "track, with two minor blockers noted in the doc. Let's discuss in "
    "standup tomorrow.",

    "Hi {name}, attached is your flight itinerary for the trip on the "
    "15th. Departure is at 9:40 AM. Let me know if you need the hotel "
    "confirmation as well.",

    "Hi {name}, thanks for jumping on the call yesterday. I've summarized "
    "the key decisions in the shared doc. Let me know if I missed anything.",

    "Hey {name}, want to grab lunch on Thursday? There's a new place near "
    "the office I've been wanting to try. Let me know!",

    "Hi {name}, thanks for your patience while we looked into this. The "
    "issue has been resolved and everything should be working normally "
    "now. Reach out if you notice anything else.",

    "Hi {name}, sharing the slides from today's presentation in case you "
    "want to review them again. Happy to answer any questions before the "
    "next session.",

    "Hi {name}, just confirming our call is still on for tomorrow at 10 "
    "AM. I'll send over the agenda beforehand so we can make the most of "
    "the time.",

    "Hi {name}, congrats on finishing the certification! Let {sender} know "
    "if you'd like to add it to your internal profile.",
]

NAMES = ["Alex", "Priya", "John", "Maria", "Wei", "Sam", "Fatima", "Chris", "Anika", "David"]
SENDERS = ["Sarah", "the HR team", "Michael", "Support Team", "Lisa", "the Ops team"]


def make_phishing_email():
    subject = random.choice(PHISHING_SUBJECTS)
    body_template = random.choice(PHISHING_BODIES)
    body = body_template.format(
        link=random.choice(LINKS),
        amount=random.choice([49, 99, 199, 250, 500, 1000]),
    )
    if random.random() < 0.5:
        body += " " + random.choice(URGENT_PHRASES).capitalize() + "."
    # Randomize whether a "Subject:" line is present so the model can't just
    # learn "has a Subject: line" as a proxy for the class.
    if random.random() < 0.5:
        return f"Subject: {subject}\n{body}"
    return body


def make_legit_email():
    subject = random.choice(LEGIT_SUBJECTS)
    body_template = random.choice(LEGIT_BODIES)
    body = body_template.format(
        name=random.choice(NAMES),
        sender=random.choice(SENDERS),
        order=random.randint(1000, 9999),
    )
    if random.random() < 0.5:
        return f"Subject: {subject}\n{body}"
    return body


def generate_dataset(n_per_class=400, out_path="data/emails.csv"):
    rows = []
    for _ in range(n_per_class):
        rows.append((make_phishing_email(), 1))
    for _ in range(n_per_class):
        rows.append((make_legit_email(), 0))
    random.shuffle(rows)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} emails to {out_path}")


if __name__ == "__main__":
    generate_dataset()
