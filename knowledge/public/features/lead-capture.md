# Lead Capture

Vidzy can pause a video at a configured time and show a lead-capture form before playback continues.

## Configurable fields

A gate always presents an email field, which may be required or optional. The form can also show an optional name field, a phone field that may be required, and one configurable custom field that may be required.

## Presentation

Gate content includes a heading, optional subheading, and button label. Available layouts are classic, split, glass, minimal, and transparent. Creators can choose whether to dim the video, use the brand-colored button, and keep actions pinned while fields scroll in small players.

## Required and skippable gates

Playback pauses when a gate appears. If any configured field is required, the viewer must submit those required fields. If no field is required, the player shows a Skip action. A completed or skipped gate is remembered for that video in the current browser tab session.

## Lead records

Submitted fields are recorded with the video, gate, capture timestamp, and available request context. The lead dashboard supports search, video and gate filters, date filters, phone/custom-field filters, pagination, and CSV, spreadsheet-compatible HTML, and PDF exports. Existing lead records retain their video title and source URL after the original video is deleted.

## Integration limitation

The schema can store a CRM-integration configuration object, but no code delivers captured leads to a CRM. Use the dashboard exports for external processing unless another integration is added and verified.

