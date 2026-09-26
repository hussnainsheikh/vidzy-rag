# Email Video Previews

Vidzy generates a short animated preview and copyable HTML that links email recipients to a Vidzy video page.

## Generation

Preview generation is queued automatically when a video is created and reruns when its source URL changes. Creators can also request regeneration. The job uses the first five seconds, targets 480-pixel width at 12 frames per second, uploads the result, and records pending, processing, ready, or failed status.

## Email snippet

The generated HTML wraps the preview image in a link to the video's current embed URL. It prefers the animated GIF, falls back to the video thumbnail when no GIF exists, and includes an Outlook-specific static-image fallback when a thumbnail is available. The requested display width is constrained to 120–1200 pixels and defaults to 600.

## Operational limits

Generation depends on the source being downloadable by the server and on configured media-processing and CDN services. YouTube has a fallback that builds animation from public preview frames if video download fails. Other provider failures are reported with a failed status.

