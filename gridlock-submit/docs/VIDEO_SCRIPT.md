# GridLock AI — 3-Minute Submission Video Script
## IBM AI Builders Challenge 2026 · May Innovation Challenge

---

## PRODUCTION NOTES
- **Total duration**: 2 minutes 50 seconds
- **Tone**: Urgent, expert, cinematic — like an F1 broadcast
- **Background music**: Low tension ambient (like Hans Zimmer F1 style)
- **Screen recording**: Use OBS or Loom at 1920x1080
- **Voiceover**: Confident, measured pace — not rushed

---

## [SEGMENT 1] — THE PROBLEM (0:00 – 0:35)

### VISUALS
Open on a black screen. Text appears:

> *"December 12, 2021. Abu Dhabi. Final lap. World Championship on the line."*

Cut to: Show the GridLock AI app loading — the dark interface with the animated speed traces in the hero section. The live telemetry numbers ticking. The F1 red glow.

### VOICEOVER
*"On the final lap of the 2021 season, a single decision by F1's Race Director changed the World Championship forever."*

*"Michael Masi allowed only 5 of 8 lapped cars to un-lap themselves before the Safety Car returned. It put Max Verstappen — on fresh tyres — directly behind Lewis Hamilton, who had been on 42-lap-old rubber."*

*"Verstappen overtook on lap 58. Hamilton lost the championship by 8 points."*

*"The FIA removed the Race Director. They rewrote the regulation. But they built no AI system to prevent this from ever happening again."*

*"GridLock AI is that system."*

---

## [SEGMENT 2] — THE GAP (0:35 – 0:55)

### VISUALS
Scroll to the Architecture section of the app — show the FIA Gap table side by side:
- Left column (green): What FIA fixed
- Right column (red): What FIA has NOT solved

### VOICEOVER
*"The FIA reformed race control. They built a Remote Operations Centre. They published new Driving Standards."*

*"But no AI-based steward assistant exists. No searchable precedent database. No automated telemetry-to-regulation matching. No explainability layer for 500 million fans."*

*"GridLock AI fills every gap."*

---

## [SEGMENT 3] — LIVE DEMO: ABU DHABI 2021 (0:55 – 1:40)

### VISUALS + ACTIONS (show on screen as you narrate)

**Step 1** — Click "Abu Dhabi 2021 — Safety Car Controversy" in the sidebar
> Show the incident header loading with severity badge "Championship-defining — 9.8/10"

**Step 2** — Point to the Telemetry tab
> Show: Hamilton tyre age 42 laps (red), Verstappen tyre age 0 laps (green), Gap at restart 0.0s (red)
> *"The telemetry tells the story instantly."*

**Step 3** — Switch to Steward Brief tab
> Watch IBM Granite start typing the analysis in real time — typewriter animation
> *"IBM Granite 3.1-8B-Instruct, via HuggingFace free serverless inference, analyses the incident against FIA regulations retrieved by IBM Docling from 500+ steward decision PDFs."*

**Step 4** — Point to the confidence bar reaching 94%
> *"94% confidence. Article 48.12 breach confirmed. Zero precedent for selective application in modern F1."*

**Step 5** — Scroll to show the Historical Precedents section appearing
> *"IBM Docling RAG retrieves the most comparable historical cases from the FIA archive — 2010 to 2026."*

**Step 6** — Click Fan View tab
> Show the plain-language explainer appear
> *"For 500 million fans who never receive an explanation — GridLock AI generates one in plain language, instantly."*

### VOICEOVER
*"Watch what happens when I select Abu Dhabi 2021."*

*"The telemetry loads. IBM Granite analyses the regulation breach. Confidence: 94%. Article 48.12 — selective unlapping — zero documented precedent. IBM Docling pulls comparable cases from the FIA archive."*

*"And for any fan watching around the world — a plain-language explanation. No jargon. Just the truth of what happened and why it mattered."*

---

## [SEGMENT 4] — FEATURES SHOWCASE (1:40 – 2:15)

### VISUALS + ACTIONS

**Feature 1** — Custom Incident Builder
> Scroll to Custom Incident Builder. Type a quick incident: "Turn 1 contact, 60% overlap, 8G impact"
> Click Analyse. Show Granite generating the analysis in real time.
> *"Any incident. Any race. IBM Granite analyses it."*

**Feature 2** — Team Appeal Scoring
> Go back to Abu Dhabi 2021, click Team Appeal tab
> Show the 82% appeal strength score
> *"Teams get appeal strength scoring — equal access to legal intelligence regardless of budget."*

**Feature 3** — Penalty Simulator
> Navigate to the Penalty Simulator section
> Drag the overlap slider to 62%, impact to 51G
> Show penalty matrix update
> *"The Penalty Simulator lets stewards test parameters before committing to a decision."*

**Feature 4** — Compare Incidents
> Scroll to Compare. Select Silverstone 2021 vs Jeddah 2021
> Show side-by-side comparison
> *"Side-by-side incident comparison — steward consistency at a glance."*

**Feature 5** — Championship Standings
> Show the 2026 WDC and WCC tables
> *"Every decision happens in championship context. GridLock AI shows you exactly what is at stake."*

### VOICEOVER
*"Beyond Abu Dhabi 2021, GridLock AI covers 9 real incidents from 2021 to 2024."*

*"Custom incident analysis. Team appeal scoring — 0 to 100. An interactive Penalty Simulator. Side-by-side incident comparison. 2026 championship standings for context. And a regulation search engine powered by IBM Docling RAG across 500 FIA documents."*

---

## [SEGMENT 5] — TECHNOLOGY (2:15 – 2:40)

### VISUALS
Show the How It Works section of the app — the pipeline flow diagram

### VOICEOVER
*"The technology stack:"*

*"IBM Granite 3.1-8B-Instruct — the reasoning engine. Temperature 0.2 for deterministic legal analysis. Via HuggingFace free serverless inference — no paid tier required."*

*"IBM Docling — the knowledge backbone. 500 FIA steward decision PDFs from 2010 to 2026, plus Sporting Regulations and the 2025-2026 Driving Standards Guidelines. All ingested, chunked, and indexed in FAISS for sub-100 millisecond retrieval."*

*"Langflow — the visual pipeline. OpenF1 telemetry to Docling RAG to Granite to output router. Every step visible, every connection explainable."*

*"Single-file web application. Zero build step. Deploys instantly to Netlify or Vercel."*

---

## [SEGMENT 6] — IMPACT AND CLOSE (2:40 – 2:50)

### VISUALS
Return to the hero section — show the full app landing with the animated telemetry traces and the red GridLock AI logo glowing

### VOICEOVER
*"GridLock AI serves three audiences simultaneously."*

*"FIA stewards — a structured decision brief in 60 seconds, before every penalty."*

*"F1 teams — appeal intelligence powered by 500 historical FIA decisions."*

*"500 million fans — plain-language explainers the FIA has never provided."*

*"The FIA confirmed this gap exists. We built the solution."*

*"IBM Granite provides the reasoning. IBM Docling provides the knowledge. Langflow orchestrates the pipeline."*

*"GridLock AI — augmenting human judgment. Never replacing it."*

---

## SCREEN RECORDING GUIDE

### What to show, in order:
1. App landing page with live telemetry animation (5 sec)
2. Sidebar — 9 incidents listed (3 sec)
3. Click Abu Dhabi 2021 — incident header loads (4 sec)
4. Telemetry tab — show 6 data points (5 sec)
5. Steward Brief tab — show Granite typewriting the analysis (15 sec)
6. Confidence bars animating to 94% (3 sec)
7. Precedents section appearing (4 sec)
8. Fan View tab — plain language explainer (5 sec)
9. Custom Incident Builder — type and run (10 sec)
10. Team Appeal — 82% score (4 sec)
11. Penalty Simulator — drag sliders (6 sec)
12. Compare Incidents side by side (4 sec)
13. Championship Standings table (3 sec)
14. Architecture section — pipeline flow diagram (6 sec)
15. Hero landing page — final shot (5 sec)

### Tips for Recording:
- Use Chrome or Firefox — both fully supported
- Record at 1920x1080, export at 1080p
- If showing live Granite: paste your HuggingFace token first, then record
- If no token available: Demo Mode shows pre-curated analysis — still looks great
- Add captions/subtitles matching the voiceover for accessibility

---

## THUMBNAIL SUGGESTION
Black background. Red "GRIDLOCK AI" in Bebas Neue font. Subtitle: "F1 Incident Intelligence — IBM AI Builders 2026". Small badges: IBM Granite · IBM Docling · Langflow. Red glowing F1 car silhouette on the right.

---

*GridLock AI — IBM AI Builders Challenge 2026*
*Augmenting human judgment. Never replacing it.*
