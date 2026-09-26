# Vidzy Product Overview

Vidzy is a video engagement product for configuring externally hosted videos, publishing them through a Vidzy player, and measuring viewer interactions. The implemented dashboard manages videos, reusable engagement elements, branding, leads, and analytics.

## Video sources and publishing

Users create a Vidzy video from a YouTube URL, Vimeo URL, or direct media URL. The dashboard auto-detects the provider from the URL, while the backend stores the title, source, provider, duration, player configuration, and optional thumbnail.

Each saved video receives a direct Vidzy URL and copyable iframe markup. A video can also use a custom domain after that domain is configured, verified, and active on an eligible plan.

## Engagement and conversion

Vidzy supports reusable calls-to-action, popups, and lead-capture gates. Each item has a default playback timestamp and can be assigned to multiple videos with a per-video timestamp override.

Calls-to-action can open a destination URL. Popups can show announcements, offers, or a CTA. Lead gates can pause playback, collect configured fields, and resume after completion.

## Appearance and access

Branding presets control player colors, play-button design, control-bar styling, and CTA treatment. Individual videos can also use a custom thumbnail, logo watermark, and scheduled or always-visible image overlays.

Videos can be password protected. The public player requests and verifies the password before rendering the media.

## Measurement

The player records impressions, views, plays, pauses, seeks, buffering, completions, CTA clicks, and lead-capture activity where the relevant provider emits those events. The dashboard provides per-video and account-level summaries, timestamp-bucket heatmaps, replay-hotspot calculations, and lead management.

