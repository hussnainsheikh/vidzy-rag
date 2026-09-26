# Timed Popups

Vidzy supports reusable messages that appear over video playback at selected times.

## Popup types and content

The dashboard offers CTA, announcement, and offer popup types. All can contain a heading and body. CTA popups additionally require a valid HTTP or HTTPS URL and a button label.

## Timing and assignment

Each popup has a default timestamp and can be assigned to multiple videos with a per-video timestamp override. The latest active popup is displayed at the top of the player. Viewers can close it.

## Linked popup behavior

When a popup includes both a CTA label and CTA URL, its button opens that URL in a new tab. Popup-button clicks are not recorded as the player's `cta_click` event.

