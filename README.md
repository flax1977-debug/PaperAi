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
