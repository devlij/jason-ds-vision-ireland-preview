# Jason D’s Vision — Ireland

AI-generated artistic interpretations of the Republic of Ireland. Free to use, no credit required. Northern Ireland belongs to the UK gallery and is not part of this site.

Gallery: https://ireland.jdvision.org/ (CNAME is `ireland.jdvision.org`; GitHub Pages may 404 until this shell is on `main`)

All scenes ship as **Candidate** until Cosmo QC. This seed does not approve anything and does not ship scene masters.

## What is here

Phase-1 gallery shell, matching the Spain / Sweden A7 page: GA4 `G-PDJ4WSS725`, canonical `https://ireland.jdvision.org/`, Open Graph, Twitter card, robots, sitemap, image sitemap, JSON-LD, Irish tricolour band (`#169B62` / `#ffffff` / `#FF883E`, 6px), country switcher with the live galleries in Sweden’s order, Sweden linked at `https://sweden.jdvision.org/`, and Ireland last and current. Search, region / day-night / mood filters, related scenes, copy-link, lightbox (navigation above the image, controls below, 4 second slideshow), and narration hooks. A listen control appears only for Aria or Warm, model `avocado_v2:MAI_01`, status Approved, and an mp3 file. There is no audio in this seed.

`tools/ie.json` is an empty array. The word-of-day band is structure only. Cosmo delivers the Irish entries later. Do not invent words.

`data.json` has an empty `scenes` array, so the page renders zero Candidate cards.

9:16 masters can sit on disk later. The 9:16 tab and download stay hidden until `format_9x16_approval_status` is set to `Approved` by Jason. There is no day/night toggle on the card. A motion control is rendered only when a motion file exists.

## Paths for later masters

Future stills land under `assets/ireland/<City>/` as `ie-01-NNN-16x9.png`, `ie-01-NNN-4x5.png`, and `ie-01-NNN-9x16.png`.

- 16:9 `1920×1270` (photo `1920×1080`)
- 4:5 `864×1270` (photo `864×1080`)
- 9:16 `1080×2110` (photo `1080×1920`)

A 190px `#0e0e12` label bar sits under the photo. The photograph itself has no scrim. EU AI Act Art. 50 Description chunk:

`AI-generated artistic interpretation from the Jason D's Vision Ireland gallery. Created with generative AI; not a photograph.`

## Rebuild

```bash
python3 tools/publish_gallery.py
python3 tools/qc_preflight.py
```

`tools/fetch_weather.py` keeps an existing weather file and fetches nothing until a scene is listed. Do not invent coordinates.

`tools/composite_masters.py` bakes the 190px label bar and the five Art. 50 PNG text chunks from a pure pre-text under `assets/pretext/ireland/<City>/`.
