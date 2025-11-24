# 表说明: `cs2_items`

这个表用于存储每个饰品的基础信息（中文名、Steam 市场 Hash 名称、以及各平台对应的 itemId）。设计如下：

字段（与 `create_items_table.py` 保持一致）:

- `id` INT AUTO_INCREMENT 主键
- `name` VARCHAR(255) 中文名称（`name`）
- `market_hash_name` VARCHAR(255) Steam 市场 Hash 名称（`marketHashName`） — 唯一索引
- `buff_id` VARCHAR(50) BUFF 平台的 itemId
- `c5_id` VARCHAR(50) C5 平台的 itemId
- `youpin_id` VARCHAR(50) YOUPIN 平台的 itemId
- `haloskins_id` VARCHAR(50) HALOSKINS 平台的 itemId
- `created_at` TIMESTAMP 默认 CURRENT_TIMESTAMP
- `updated_at` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

索引:

- `idx_market_hash_name` (market_hash_name) — 用于基于 marketHashName 的查找
- `idx_name` (name) — 中文名称查找
- `idx_buff_id`, `idx_c5_id` — 以便通过平台的 itemId 找到饰品

