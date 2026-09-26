# Video Player

Vidzy renders YouTube, Vimeo, and direct media URLs through a shared player experience.

## Playback controls

The player provides play and pause, a seek bar, 10-second backward and forward actions, mute, volume adjustment, elapsed and total time, and fullscreen mode. Controls hide after inactivity and reappear on pointer or touch interaction.

## Playback options

Each video can enable autoplay and looping. Autoplay starts muted to follow common browser autoplay requirements. For YouTube videos, the player also attempts to suppress end-screen recommendations and restarts looping videos from the beginning.

## Thumbnail and start state

A custom thumbnail is shown before playback when autoplay is off. The configured branded play button is displayed over the start state. Direct-file playback uses the thumbnail as the native video poster as well.

## Password protection

A protected video displays an unlock form instead of media. Passwords are verified by the backend against a stored hash. The player applies a short client-side cooldown after repeated failed attempts.

## Provider constraints

The source is referenced by URL; the video itself is not uploaded through the video-creation form. Direct URLs must be playable by the viewer's browser. Provider availability, embedding permissions, and browser media rules still apply.

