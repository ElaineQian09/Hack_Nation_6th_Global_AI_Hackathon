# Facility Trust Desk Design Direction

## 1. Visual Direction

Facility Trust Desk should feel like a healthcare-provider inspired facility intelligence workspace. The interface should use a clean white background, calm typography, generous spacing, and evidence-focused sections that feel trustworthy and clinical.

The target tone is:

- healthcare-provider inspired
- clean white background
- professional clinical workspace
- evidence-focused
- calm, trustworthy, and spacious
- not cartoonish
- not overly dashboard-like
- not AI-generated looking

The product should feel closer to a hospital location and capability review page than a generic SaaS analytics dashboard.

## 2. Reference Inspiration

The uploaded reference screenshots are only a style direction. They suggest:

- a large healthcare-style header
- a clean search/filter section
- large white content areas
- strong black headings
- thin vertical dividers
- address/contact/location-style sections
- clear primary actions
- generous spacing
- simple green link/action accents

The reference must not be copied exactly. Do not copy the exact brand, logo, colors, layout, or text.

## 3. Color Direction

Use a mostly white visual system:

- Page background: `#FFFFFF`
- Section background: `#FFFFFF`
- Very light neutral background when needed: `#F8FAF8` or `#F7F9F7`
- Deep green primary: `#0F5F4A`
- Dark text: `#101A16` or `#14201B`
- Muted text: `#5F6B64`
- Border: `#D9E1DC`
- Divider: `#E6ECE8`
- Soft green active: `#E7F5EF`
- Warning amber: `#B7791F`
- Weak red: `#B42318`

The overall pale green page wash should be removed. Green should be used for brand, selected states, links, and primary actions.

## 4. Typography Direction

Use a clean modern sans-serif stack:

```css
Inter, Avenir Next, Helvetica Neue, Arial, ui-sans-serif, system-ui, sans-serif
```

Typography goals:

- headings bold and clear, but not cartoonishly heavy
- body text readable and calm
- labels smaller but crisp
- avoid too many all-caps labels
- reduce overly thick badge text
- make information hierarchy more like a clinic website

## 5. Hero Background Direction

Use the existing asset `frontend/public/background.webp` as a cropped background band between the top header and the capability/location selector.

Important behavior:

- do not show the full image as a huge banner
- use it as a partial cropped strip
- keep it subtle
- use `background-size: cover`
- use `background-position: center`
- add a white or light gradient overlay for readability
- desktop height should be roughly 180px to 260px
- mobile height should be roughly 120px to 160px

The hero band should create a healthcare-site feel without becoming a marketing poster.

## 6. Header Direction

The header should feel like a healthcare website header:

- left logo lockup
- Facility Trust Desk name
- optional tagline: Evidence-led care insights
- right simple nav text links:
  - Evidence Search
  - Review Queue
  - About

The header background should be white with a subtle bottom border. It should not look like an admin app topbar.

## 7. Capability Selector Direction

The ICU / NICU / Emergency options should feel like healthcare service cards.

Each card should include:

- icon
- title
- subtitle
- short description
- selected state

Cards:

- ICU — Intensive Care Unit — Critical care, equipment, and staffing evidence.
- NICU — Neonatal Intensive Care Unit — Newborn critical-care and neonatal support signals.
- Emergency — Emergency / Trauma Care — 24/7 emergency, ambulance, and urgent-care signals.

Style:

- white cards
- thin borders
- spacious padding
- simple line icons
- green selected border
- subtle active background
- no emoji icons
- no external icon library required

## 8. Search / Region Section

Below the capability cards, keep State / City / Search Facilities.

This area should feel like a healthcare search bar:

- large inputs
- clear labels
- white background
- thin border
- strong green search button
- clean spacing
- no technical copy

State and City should use custom searchable combobox controls instead of visible browser-native selects. The controls should look like large healthcare search inputs with a left icon, typed filtering, a floating white option panel, keyboard support, and subtle green focus/selected states. Hidden form values may be kept for JavaScript compatibility, but the visible UI should not expose default select dropdown styling.

## 9. Lower Content Redesign

The lower dashboard should feel like a healthcare location/detail page instead of an AI dashboard.

Use:

- large white sections
- strong section headings
- clean rows
- subtle dividers
- fewer heavy cards
- clear address/location/evidence sections
- left side as search results
- right side as facility review detail

The right Evidence Review should include a three-column information section similar to healthcare location pages:

1. Location
   - city, state, pincode when available
   - facility type
2. Evidence Summary
   - trust score
   - confidence
   - claim present
3. Source / Context
   - beds
   - doctors
   - website/source availability

Use vertical dividers between columns on desktop and stack on mobile.

## 10. Facility Results Redesign

Facility result rows should feel like clean healthcare search results:

- facility name
- city/state
- doctors/beds
- short reason summary
- trust score displayed calmly on the right
- small evidence/warning metadata
- selected row with green left border or very light green background

Reduce badge clutter. Keep only essential chips:

- Trust label
- Confidence
- Evidence count
- Warning count

## 11. Remove Technical User-Facing Text

Do not show:

- API running status
- loaded facility debug count
- backend limit wording
- implementation details
- overly explanatory AI-style copy

User-facing copy should stay simple:

- Choose care capability and location
- Facility matches
- Top results
- Evidence Review
- Facility Location
- Evidence receipts
- Missing context
- Review notes

## 12. Scrolling Direction

Use normal page scrolling. Avoid nested scrollbars unless absolutely necessary.

The right panel may be sticky on desktop if useful, but it should not trap scroll internally. On mobile, the layout should stack naturally.

## 13. Implementation Boundaries

- No backend changes
- No API changes
- No database changes
- No new framework
- No image generation
- No new external icon library
- Keep existing vanilla HTML/CSS/JS structure
- Preserve existing data flow and Mapbox behavior

## 14. Accessibility

- capability cards must be keyboard focusable
- selected state must be visible beyond color alone
- focus states must be visible
- buttons must have clear labels
- text contrast must remain strong
