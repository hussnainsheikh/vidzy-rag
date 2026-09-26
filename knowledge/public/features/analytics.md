# Analytics

Vidzy records player interactions and provides aggregate analytics for account videos.

## Recorded events

Implemented event types include impression, view, play, pause, seek, buffer, complete, CTA click, and lead capture. An impression is sent after an unprotected video loads or a protected video is unlocked. A view is sent once when playback begins.

## Video analytics

Per-video analytics include event counts, impressions, views, completions, completion rate, total events, the furthest recorded event timestamp, and an average timestamp expressed as a percentage of configured video duration.

Timestamp activity is grouped into 10-second buckets by default. Replay hotspots are buckets whose event activity exceeds 1.5 times the average bucket activity.

## Account dashboard

The account dashboard compares impressions, views, and completions from the most recent seven days with the preceding seven days. An all-video summary supplies aggregate dashboard and video-list views.

## Interpretation limits

The heatmap counts timestamped events, not distinct viewers or continuous watched seconds. The value labeled average watch percentage is derived from all non-buffer event timestamps, not sessionized watch duration. Replay hotspots are statistical activity buckets rather than confirmed replay sessions.

