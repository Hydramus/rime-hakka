# Gboard submission workstream

> **TL;DR:** Gboard does not accept third-party IME plugins. The only
> way Huiyang Hakka can ship *inside* Gboard is for Google to add it as
> a first-class language. This folder tracks that advocacy effort. It
> produces no code artifact in this repo.

## Why this is documentation-only

Gboard is a closed-source Google app. Its language packs are curated by
Google and built in-house. Third-party developers cannot drop a `.zip`
or `.apk` plugin into Gboard the way we can into Trime or Hamster.

Attempts to ship "a Gboard plugin" are misinformed — they do not exist
as a platform feature. The correct channels are listed below.

## How to actually get Huiyang Hakka into Gboard

### 1. File a language request

- Google's official channel: **Help & feedback** inside the Gboard app
  → *Suggest a new language*. Provide:
  - Language name (English + native script): **Hakka (Huiyang)** / **客家話 (惠陽)**.
  - ISO 639-3 code: `hak` (Hakka macrolanguage). Huiyang itself has no
    dedicated ISO code; reference the macrolanguage and describe the
    variant explicitly.
  - Estimated speaker count (cite Ethnologue / regional census).

### 2. Prepare linguistic artifacts

Google's internationalization team typically asks for:

- **Phoneme inventory** — initials, finals, tones. Derivable from
  `sources/chars-hkilang.csv` + our schema's `speller.alphabet`.
- **Tone table** — six tones with contour values and checked-syllable
  rules (see `schemas/huiyang/README.md`).
- **Frequency list** — at least 1,000 most-common words with
  romanization + Hanzi. Derivable from
  `sources/flashcards-huiyang.csv` plus any corpus we add under
  `sources/phrases/`.
- **Sample sentences** — 50–100 natural sentences for keyboard
  prediction training.
- **Licensing confirmation** — explicit CC-BY-SA (or more permissive)
  attestation for the data we hand over.

All of the above can be generated from this repo's existing sources;
we just need a script to format them the way Google expects. Track
that task as an issue in this folder.

### 3. Keep Trime shipping in parallel

Because Google's language-addition process is slow and opaque, we keep
the Trime-based Android path (see `../installers/android/README.md`)
as the immediate, user-installable option. The Gboard track runs
independently.

## Issue template

When we open a tracking issue for the Gboard submission, the template
lives at `.github/ISSUE_TEMPLATE/gboard-submission.md` (to be added).

## Contacts

- Gboard feedback: in-app feedback only.
- Google i18n team: no public inbound; follow Google Search Central
  / I/O announcements about new Gboard languages.
- ISO 639-3 registrar (if we pursue a subtag for Huiyang): SIL
  International.
