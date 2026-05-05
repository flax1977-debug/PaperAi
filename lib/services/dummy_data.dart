import '../models/news_article.dart';

class TodayAction {
  final String headline;
  final String rationale;
  final String cta;
  final Duration estimatedTime;

  const TodayAction({
    required this.headline,
    required this.rationale,
    required this.cta,
    required this.estimatedTime,
  });
}

class DummyData {
  static final TodayAction todayOnlyAction = const TodayAction(
    headline: 'Ship a Claude Sonnet 4.6 prompt-caching prototype',
    rationale:
        'Anthropic shipped 1M-token caching this week. Teams adopting it in 48h are reporting 3-5x cost reductions on agent workloads. The window before competitors close the gap is narrow.',
    cta: 'Spike a 2-hour proof of concept',
    estimatedTime: Duration(hours: 2),
  );

  static final List<NewsArticle> topSignals = [
    NewsArticle(
      id: 'sig-001',
      title: 'Claude Opus 4.7 lands with 1M-token context window',
      source: 'Anthropic',
      publishedAt: DateTime(2026, 5, 5, 8, 15),
      whatHappened:
          'Anthropic released Opus 4.7 with a 1M-token context window, native tool use improvements, and a 40% reduction in output latency for agent loops.',
      whyItMatters:
          'Long-context retrieval pipelines you built around 200k tokens can be simplified. Multi-document reasoning that required chunking is now a single call.',
      action:
          'Audit one RAG pipeline today. If chunking exists purely to fit context, plan a migration spike this week.',
      confidence: ArticleConfidence.high,
      timeToAct: TimeToAct.today,
      tags: ['LLM', 'Context', 'Anthropic'],
    ),
    NewsArticle(
      id: 'sig-002',
      title: 'OpenAI ships native agent memory primitives',
      source: 'OpenAI',
      publishedAt: DateTime(2026, 5, 4, 17, 42),
      whatHappened:
          'A new memory API exposes per-user persistent memory with automatic summarization, retrieval, and TTL controls.',
      whyItMatters:
          'Custom vector-store + summarizer stacks lose their moat. If your product differentiates on "remembering the user", reassess what is now table stakes.',
      action:
          'Map your memory stack to the new primitives. Identify what becomes commodity vs. what stays proprietary.',
      confidence: ArticleConfidence.high,
      timeToAct: TimeToAct.thisWeek,
      tags: ['Agents', 'Memory', 'OpenAI'],
    ),
    NewsArticle(
      id: 'sig-003',
      title: 'EU AI Act Article 50 enforcement begins',
      source: 'European Commission',
      publishedAt: DateTime(2026, 5, 4, 9, 30),
      whatHappened:
          'Transparency obligations for AI-generated content take effect. Providers must disclose synthetic outputs in machine-readable form.',
      whyItMatters:
          'If you ship to EU users, missing disclosure metadata is now a compliance gap with material fines.',
      action:
          'Add C2PA or equivalent provenance tags to AI outputs. Coordinate with legal this week.',
      confidence: ArticleConfidence.medium,
      timeToAct: TimeToAct.now,
      tags: ['Regulation', 'Compliance', 'EU'],
    ),
    NewsArticle(
      id: 'sig-004',
      title: 'Mistral open-sources 70B reasoning model',
      source: 'Mistral AI',
      publishedAt: DateTime(2026, 5, 3, 14, 0),
      whatHappened:
          'A 70B-parameter reasoning model with permissive licensing now matches GPT-4o on MATH and HumanEval benchmarks.',
      whyItMatters:
          'Self-hosted reasoning is viable for cost-sensitive workloads. The build-vs-buy tradeoff shifts for high-volume inference.',
      action:
          'Benchmark on your top-3 prompts. Decide whether to keep a self-host track on the roadmap.',
      confidence: ArticleConfidence.medium,
      timeToAct: TimeToAct.thisWeek,
      tags: ['Open Source', 'Reasoning', 'Inference'],
    ),
    NewsArticle(
      id: 'sig-005',
      title: 'NVIDIA H300 sampling to hyperscalers',
      source: 'NVIDIA',
      publishedAt: DateTime(2026, 5, 2, 11, 15),
      whatHappened:
          'H300 silicon ships to AWS, Azure, and GCP with a 2.4x training throughput uplift over H200.',
      whyItMatters:
          'Inference pricing pressure expected within two quarters. Long-term GPU commitments should be reviewed.',
      action:
          'Hold off on multi-year capacity contracts. Track spot pricing on H200 for a possible dip.',
      confidence: ArticleConfidence.low,
      timeToAct: TimeToAct.watch,
      tags: ['Hardware', 'Pricing', 'NVIDIA'],
    ),
  ];

  static final List<NewsArticle> savedArticles = [
    topSignals[0],
    topSignals[2],
  ];

  static NewsArticle byId(String id) =>
      topSignals.firstWhere((a) => a.id == id);
}
