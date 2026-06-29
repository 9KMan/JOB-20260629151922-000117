INSERT INTO scraper_targets (name, url, selector_map, schedule)
VALUES (
  'example_directory',
  'https://example.com/listings',
  '{"row": ".item", "name": "h2", "phone": ".tel"}'::jsonb,
  '0 9 * * *'
);
