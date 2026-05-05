import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/news_article.dart';
import '../theme/app_theme.dart';
import '../widgets/confidence_chip.dart';
import '../widgets/time_to_act_badge.dart';

class ArticleDetailScreen extends StatelessWidget {
  final NewsArticle article;
  const ArticleDetailScreen({super.key, required this.article});

  @override
  Widget build(BuildContext context) {
    final time = DateFormat('EEE, MMM d · HH:mm').format(article.publishedAt);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Signal'),
        actions: [
          IconButton(
            icon: const Icon(Icons.bookmark_border),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.share_outlined),
            onPressed: () {},
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
        children: [
          Row(
            children: [
              TimeToActBadge(timeToAct: article.timeToAct),
              const SizedBox(width: 8),
              ConfidenceChip(confidence: article.confidence),
            ],
          ),
          const SizedBox(height: 18),
          Text(
            article.title,
            style: Theme.of(context).textTheme.headlineLarge,
          ),
          const SizedBox(height: 10),
          Text(
            '${article.source.toUpperCase()}  ·  $time',
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
              color: AppColors.textTertiary,
            ),
          ),
          const SizedBox(height: 24),
          if (article.tags.isNotEmpty) ...[
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final tag in article.tags) _Tag(label: tag),
              ],
            ),
            const SizedBox(height: 24),
          ],
          _DetailBlock(
            label: 'What Happened',
            body: article.whatHappened,
            icon: Icons.bolt_outlined,
          ),
          const SizedBox(height: 14),
          _DetailBlock(
            label: 'Why It Matters',
            body: article.whyItMatters,
            icon: Icons.insights_outlined,
          ),
          const SizedBox(height: 14),
          _DetailBlock(
            label: 'Action',
            body: article.action,
            icon: Icons.task_alt_outlined,
            accent: true,
          ),
          const SizedBox(height: 28),
          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.check_rounded, size: 18),
                  label: const Text('Mark Done'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.bookmark_outline, size: 18),
                  label: const Text('Save'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _DetailBlock extends StatelessWidget {
  final String label;
  final String body;
  final IconData icon;
  final bool accent;
  const _DetailBlock({
    required this.label,
    required this.body,
    required this.icon,
    this.accent = false,
  });

  @override
  Widget build(BuildContext context) {
    final color = accent ? AppColors.accent : AppColors.textSecondary;
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: accent ? AppColors.accent.withOpacity(0.4) : AppColors.border,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 8),
              Text(
                label.toUpperCase(),
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.4,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            body,
            style: const TextStyle(
              fontSize: 14,
              height: 1.55,
              color: AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}

class _Tag extends StatelessWidget {
  final String label;
  const _Tag({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: AppColors.surfaceElevated,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: AppColors.border),
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: AppColors.textSecondary,
          letterSpacing: 0.3,
        ),
      ),
    );
  }
}
