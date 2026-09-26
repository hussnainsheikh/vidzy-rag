# Timed Calls-to-Action

Vidzy supports reusable calls-to-action that appear over selected videos at configured playback times.

## CTA types

The dashboard offers button, text-link, and image CTA types. Button and link CTAs use a label and destination URL. An image CTA uses an uploaded image as the clickable surface.

## Timing and assignment

Each CTA has a default timestamp. It can be assigned to multiple videos, and each assignment can override that timestamp. A CTA fires when playback reaches its scheduled time; seeking backward resets its trigger so it may appear again.

## Viewer behavior

Viewers may dismiss a CTA. Clicking it records a `cta_click` event, opens its configured URL in a new tab with opener isolation, and dismisses the CTA. Although the dashboard stores a link-target choice, the current player always opens CTA links in a new tab.

## Images

CTA image uploads accept JPEG, PNG, WebP, or GIF through the backend and are limited to 5 MB. The full displayed image is clickable.

