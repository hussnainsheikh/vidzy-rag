# Sharing and Embedding

Every saved Vidzy video can be opened through a direct player URL or embedded in another site with an iframe.

## Direct link

The dashboard constructs a link from the configured embed origin and video ID. When Full View is enabled, it adds `?full=true` so the embed shell expands to the viewport.

## Iframe code

The dashboard produces copyable iframe markup with a 640 by 360 default size and permissions for autoplay, fullscreen, and picture-in-picture. The embed application loads public configuration from `/videos/{videoId}/config` and renders the shared Vidzy player.

## Custom domains

Premium and Enterprise plan definitions enable custom domains. Vidzy accepts a subdomain without a protocol or `www`, verifies both a CNAME target and a Vidzy TXT token, registers the hostname with the configured CDN, and tracks pending-DNS, pending-SSL, or active status. The dashboard uses the custom domain only when its status is active.

