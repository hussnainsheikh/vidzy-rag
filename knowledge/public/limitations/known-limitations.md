# Known Product Limitations

## Source hosting

Vidzy's video workflow accepts source URLs rather than uploading original video files. Direct media must remain reachable and browser-playable, and YouTube/Vimeo playback depends on those providers allowing embedding.

## Analytics semantics

The current backend does not sessionize viewers. Heatmaps count timestamped events; average watch percentage averages event timestamps against the configured duration; replay hotspots identify unusually active time buckets. These values should not be described as unique-viewer retention or exact watch time.

The dashboard's retention curve and watch-time distribution are estimates generated in the browser. They are not measured fields returned by the analytics API.

## Popup analytics

CTA clicks from the timed CTA feature are recorded. The button inside a CTA-style popup opens its URL but does not emit a dedicated click event.

## Integrations

Automatic delivery of captured leads to a CRM is not implemented. Lead data can instead be filtered and exported.

## Plan enforcement

Video-count limits and custom-domain eligibility are enforced. Monthly view figures exist in plan definitions but are not enforced by event ingestion.

## Email previews

Preview generation depends on server-side access to the source and configured processing/CDN services. A job can enter a failed state. YouTube has a preview-frame fallback; other source types do not.

