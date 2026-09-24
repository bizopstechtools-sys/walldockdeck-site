# walldockdeck.com

Static site (one `index.html`, hash routing) plus the four regional guide PDFs in `/guides`.

Every form on the site posts to Tomonagi's public intake endpoint for the **Wall Dock Deck** workspace:

`https://tomonagi.com/api/public/intake/wall-dock-deck`

- **One person = one lead.** Each post carries `external_id`, built as `wdd:{hash(address)}:{hash(email or phone)}`. The Tomonagi form's dedupe key is `external_id`, so later steps merge into the same lead rather than creating a new one.
- **`lead_source_action` records the furthest step the person reached:**
  - `guide_download`
  - `score_report`
  - `inspection_request`
- **Score fields** (`shore_score`, `shore_band`, `*_score`, `estimate_total`, …) are sent with `score_report` and with booking requests.
- **SMS consent** is sent as `consent_given`, `consent_text` and `consent_timestamp`.

Hosting: a Render Static Site with publish directory `.` and no build command. The walldockdeck.com DNS lives at GoDaddy.
