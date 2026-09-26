# Accounts and Plan-Enforced Features

Vidzy provides email/password accounts with verified email, profile management, and plan-based video and custom-domain controls.

## Account access

New registrations create an unverified account. Login requires a correct password, a verified email, and an enabled account. Authenticated users can update their full name and change their password after confirming the current password.

## Video limits

The backend enforces video-count limits when a video is created: Starter allows 50 videos, Plus 100, Premium 500, and Enterprise has no configured video-count ceiling. Deleting a video frees capacity under the implemented count check.

## Custom-domain eligibility

Custom-domain configuration is enabled for Premium and Enterprise and rejected for Starter and Plus.

## Monthly view figures

Plan definitions contain monthly view figures, but the event-ingestion path does not enforce them. They should not be interpreted as an implemented viewing cutoff.

