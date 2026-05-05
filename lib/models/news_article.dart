import 'package:flutter/material.dart';

enum ArticleConfidence { low, medium, high }

extension ArticleConfidenceX on ArticleConfidence {
  String get label {
    switch (this) {
      case ArticleConfidence.low:
        return 'Low';
      case ArticleConfidence.medium:
        return 'Medium';
      case ArticleConfidence.high:
        return 'High';
    }
  }

  Color get color {
    switch (this) {
      case ArticleConfidence.low:
        return const Color(0xFFE57373);
      case ArticleConfidence.medium:
        return const Color(0xFFFFB74D);
      case ArticleConfidence.high:
        return const Color(0xFF4DD0A0);
    }
  }
}

enum TimeToAct { now, today, thisWeek, watch }

extension TimeToActX on TimeToAct {
  String get label {
    switch (this) {
      case TimeToAct.now:
        return 'Act Now';
      case TimeToAct.today:
        return 'Today';
      case TimeToAct.thisWeek:
        return 'This Week';
      case TimeToAct.watch:
        return 'Monitor';
    }
  }

  Color get accent {
    switch (this) {
      case TimeToAct.now:
        return const Color(0xFFFF6B6B);
      case TimeToAct.today:
        return const Color(0xFF4DA3FF);
      case TimeToAct.thisWeek:
        return const Color(0xFFB18CFF);
      case TimeToAct.watch:
        return const Color(0xFF7A8699);
    }
  }
}

class NewsArticle {
  final String id;
  final String title;
  final String source;
  final DateTime publishedAt;
  final String whatHappened;
  final String whyItMatters;
  final String action;
  final ArticleConfidence confidence;
  final TimeToAct timeToAct;
  final List<String> tags;

  const NewsArticle({
    required this.id,
    required this.title,
    required this.source,
    required this.publishedAt,
    required this.whatHappened,
    required this.whyItMatters,
    required this.action,
    required this.confidence,
    required this.timeToAct,
    this.tags = const [],
  });
}
