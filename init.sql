
-- AI Intelligence Hub 新闻来源初始化数据
-- SQLite

INSERT INTO news_sources
(name, url, source_type, category, weight, enabled, created_at)
VALUES
(
    'TechCrunch',
    'https://techcrunch.com/',
    'auto',
    '科技',
    5,
    1,
    CURRENT_TIMESTAMP
),
(
    '量子位',
    'https://www.qbitai.com/feed',
    'rss',
    'AI',
    5,
    1,
    CURRENT_TIMESTAMP
);
