# PaperAI

AI builder intelligence dashboard. Flutter v1 preview.

## Features (v1)

- Dark, professional, technical dashboard UI
- `Today` screen with a single "Today Only" priority action and ranked top signals
- Article detail view with What Happened / Why It Matters / Action / Confidence / Time-to-Act
- Saved bookmarks and Settings screens
- Hardcoded dummy data — no Firebase required to preview

## Project structure

```
lib/
  main.dart
  models/
    news_article.dart
  screens/
    home_shell.dart
    today_screen.dart
    article_detail_screen.dart
    saved_screen.dart
    settings_screen.dart
  services/
    dummy_data.dart
  theme/
    app_theme.dart
  widgets/
    article_card.dart
    confidence_chip.dart
    section_header.dart
    time_to_act_badge.dart
```

## Running

```bash
flutter create .         # generate android/ios/web platform folders
flutter pub get
flutter run
```

`flutter create .` is required once to scaffold the platform folders, which are
intentionally not committed.

## DraftMyVan (incubating, planned extraction)

The `draftmyvan/` directory contains a **separate project** that is currently
incubating in this repository. It is a manufacturing-oriented 3D campervan
configurator — manifest schema, validators, deterministic GLB fixture,
runtime reference consumer, and a CI-gated test suite. It shares **zero**
build coupling with the Flutter app under `lib/`; the two live side by side
purely for incubation convenience.

DraftMyVan will move to its own repository. See
`draftmyvan/HANDOFF.md` for the briefing and
`draftmyvan/EXTRACT_TO_REAL_REPO.md` for the step-by-step move. Until it
has moved, changes scoped to `draftmyvan/**` are gated by the
`Validate manifests & run tests` workflow and never touch the Flutter app.
