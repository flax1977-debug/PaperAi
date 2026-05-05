import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/news_article.dart';
import '../theme/app_theme.dart';
import 'confidence_chip.dart';
import 'time_to_act_badge.dart';

class ArticleCard extends StatelessWidget {
  final NewsArticle article;
  final VoidCallback? onTap;
  const ArticleCard({super.key, required this.article, this.onTap});

  @override
  Widget build(BuildContext context) {
    final time = DateFormat('MMM d  HH:mm').format(article.publishedAt);
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  TimeToActBadge(timeToAct: article.timeToAct),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${article.source.toUpperCase()}  ·  $time',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textTertiary,
                        letterSpacing: 0.8,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                article.title,
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 10),
              Text(
                article.whatHappened,
                style: Theme.of(context).textTheme.bodySmall,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 14),
              Row(
                children: [
                  ConfidenceChip(confidence: article.confidence),
                  const Spacer(),
                  const Icon(
                    Icons.arrow_forward,
                    size: 16,
                    color: AppColors.textSecondary,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
