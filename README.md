# Jason D’s Vision — Ireland

AI-generated artistic interpretations of the Republic of Ireland. Free to use, no credit required. Northern Ireland belongs to the UK gallery and is not part of this territory.

Gallery canon: https://ireland.jdvision.org/

GitHub Pages may 404 on that host while TLS finishes. Until the custom domain answers over HTTPS, use https://devlij.github.io/jason-ds-vision-ireland-preview/

`CNAME` (`ireland.jdvision.org`) and `.nojekyll` stay in the repo. Do not delete or overwrite them.

All scenes ship as **Candidate** until Cosmo QC. This seed does not approve anything, and it does not invent word-of-the-day entries.

## What is here

Phase-1 gallery shell, matching the Spain / Sweden A7 page: GA4 `G-PDJ4WSS725`, canonical `https://ireland.jdvision.org/`, Open Graph, Twitter card, robots, sitemap, image sitemap, JSON-LD, Irish flag band (`#169B62` / `#ffffff` / `#FF883E`, 6px), country switcher with Ireland last and current, word-of-day band, search and region / day-night / mood filters, related scenes, copy-link, lightbox (navigation above the image, controls below, 4 second slideshow), and narration hooks.

`tools/ie.json` is an empty array. The band is structure only. Cosmo delivers the Irish entries later.

`data.json` carries IE-01-001 through IE-01-010 as Candidate stills for 30 September 2026. Masters sit under `assets/ireland/<City>/ie-01-NNN-…`. Nothing in this batch is Approved. Aerial clips are a backfill. Newgrange, the Boyne Valley, Glendalough, and the Cliffs of Moher are left for a later pass.

9:16 masters can sit on disk later. The 9:16 tab and download stay hidden until `format_9x16_approval_status` is set to `Approved` by Jason. Narration controls appear only for Aria or Warm, model `avocado_v2:MAI_01`, status Approved, and an mp3 file. There is no day/night toggle on the card. A motion control is rendered only when a motion file exists. This seed ships no audio.

## Rebuild

```bash
python3 tools/publish_gallery.py
python3 tools/qc_preflight.py
```

`tools/fetch_weather.py` has an empty pin list. Append a Republic of Ireland viewpoint, timezone `Europe/Dublin`, when a scene is published. Do not invent coordinates here.

`tools/composite_masters.py` bakes the 190px label bar and the five Art. 50 PNG text chunks from a pure pre-text under `assets/pretext/ireland/<City>/`. The Description chunk is: `AI-generated artistic interpretation from the Jason D's Vision Ireland gallery. Created with generative AI; not a photograph.`
