import 'package:flutter/material.dart';
import '../models/news_article.dart';

class TimeToActBadge extends StatelessWidget {
  final TimeToAct timeToAct;
  const TimeToActBadge({super.key, required this.timeToAct});

  @override
  Widget build(BuildContext context) {
    final color = timeToAct.accent;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.14),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        timeToAct.label.toUpperCase(),
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: color,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}
