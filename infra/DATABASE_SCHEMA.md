# Steam Games Database Schema

This document describes the relational database schema for the Steam Games application. The schema is designed following database normalization principles to minimize redundancy and ensure data integrity.

## Overview

The database uses **SQLite** with the following characteristics:
- Foreign key constraints enabled
- Normalized structure (avoiding data duplication)
- Many-to-many relationships via junction tables
- Automatic timestamps for audit trails
- Indexes for frequently queried columns

## Database Creation

To create the database schema, use the `SteamGamesDB` class from `steam_db_ingestion.py`:

```python
from steam_db_ingestion import SteamGamesDB

# Initialize database
db = SteamGamesDB("data")

# Create schema
db.create_schema()
```

This will create a SQLite database at `data/steamgames.db` with all tables, indexes, and constraints.

## Core Tables

### games

Primary table storing core game information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| app_id | INTEGER | PRIMARY KEY | Unique Steam App ID |
| name | TEXT | NOT NULL | Game title |
| release_date | TEXT | | Release date |
| estimated_owners | TEXT | | Estimated ownership range |
| peak_ccu | INTEGER | | Peak concurrent users |
| required_age | INTEGER | | Minimum age requirement |
| price | REAL | | Current price |
| discount_dlc_count | INTEGER | | Number of DLCs/discounts |
| about_the_game | TEXT | | Game description |
| reviews | TEXT | | Review summary |
| header_image | TEXT | | Header image URL |
| website | TEXT | | Official website URL |
| support_url | TEXT | | Support page URL |
| support_email | TEXT | | Support email |
| windows | BOOLEAN | | Windows support |
| mac | BOOLEAN | | macOS support |
| linux | BOOLEAN | | Linux support |
| metacritic_score | INTEGER | | Metacritic score (0-100) |
| metacritic_url | TEXT | | Metacritic review URL |
| user_score | INTEGER | | User score |
| positive_reviews | INTEGER | | Positive review count |
| negative_reviews | INTEGER | | Negative review count |
| score_rank | TEXT | | Score ranking |
| achievements | INTEGER | | Number of achievements |
| recommendations | INTEGER | | Recommendation count |
| notes | TEXT | | Additional notes |
| avg_playtime_forever | INTEGER | | Average total playtime (minutes) |
| avg_playtime_two_weeks | INTEGER | | Average 2-week playtime (minutes) |
| median_playtime_forever | INTEGER | | Median total playtime (minutes) |
| median_playtime_two_weeks | INTEGER | | Median 2-week playtime (minutes) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- `idx_games_name` on `name`
- `idx_games_release_date` on `release_date`
- `idx_games_price` on `price`
- `idx_games_positive_reviews` on `positive_reviews`

## Entity Tables

These tables store unique entities that can be associated with multiple games.

### developers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Developer ID |
| name | TEXT | UNIQUE NOT NULL | Developer name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Indexes:**
- `idx_developers_name` on `name`

### publishers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Publisher ID |
| name | TEXT | UNIQUE NOT NULL | Publisher name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Indexes:**
- `idx_publishers_name` on `name`

### categories

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Category ID |
| name | TEXT | UNIQUE NOT NULL | Category name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

### genres

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Genre ID |
| name | TEXT | UNIQUE NOT NULL | Genre name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

### tags

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Tag ID |
| name | TEXT | UNIQUE NOT NULL | Tag name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

### languages

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Language ID |
| name | TEXT | UNIQUE NOT NULL | Language name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

## Junction Tables (Many-to-Many Relationships)

### game_developers

Links games to their developers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| game_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References games(app_id) |
| developer_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References developers(id) |

**Foreign Keys:**
- `game_id` → `games(app_id)` ON DELETE CASCADE
- `developer_id` → `developers(id)` ON DELETE CASCADE

**Indexes:**
- `idx_game_developers_game` on `game_id`

### game_publishers

Links games to their publishers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| game_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References games(app_id) |
| publisher_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References publishers(id) |

**Foreign Keys:**
- `game_id` → `games(app_id)` ON DELETE CASCADE
- `publisher_id` → `publishers(id)` ON DELETE CASCADE

**Indexes:**
- `idx_game_publishers_game` on `game_id`

### game_categories

Links games to their categories.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| game_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References games(app_id) |
| category_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References categories(id) |

**Foreign Keys:**
- `game_id` → `games(app_id)` ON DELETE CASCADE
- `category_id` → `categories(id)` ON DELETE CASCADE

**Indexes:**
- `idx_game_categories_game` on `game_id`

### game_genres

Links games to their genres.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| game_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References games(app_id) |
| genre_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References genres(id) |

**Foreign Keys:**
- `game_id` → `games(app_id)` ON DELETE CASCADE
- `genre_id` → `genres(id)` ON DELETE CASCADE

**Indexes:**
- `idx_game_genres_game` on `game_id`

### game_tags

Links games to their tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| game_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References games(app_id) |
| tag_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References tags(id) |

**Foreign Keys:**
- `game_id` → `games(app_id)` ON DELETE CASCADE
- `tag_id` → `tags(id)` ON DELETE CASCADE

**Indexes:**
- `idx_game_tags_game` on `game_id`

### game_supported_languages

Links games to languages they support.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| game_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References games(app_id) |
| language_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References languages(id) |

**Foreign Keys:**
- `game_id` → `games(app_id)` ON DELETE CASCADE
- `language_id` → `languages(id)` ON DELETE CASCADE

### game_audio_languages

Links games to languages with full audio support.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| game_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References games(app_id) |
| language_id | INTEGER | PRIMARY KEY, FOREIGN KEY | References languages(id) |

**Foreign Keys:**
- `game_id` → `games(app_id)` ON DELETE CASCADE
- `language_id` → `languages(id)` ON DELETE CASCADE

## Media Tables

### game_screenshots

Stores game screenshots with display ordering.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Screenshot ID |
| game_id | INTEGER | NOT NULL, FOREIGN KEY | References games(app_id) |
| url | TEXT | NOT NULL | Screenshot URL |
| display_order | INTEGER | | Display order |

**Foreign Keys:**
- `game_id` → `games(app_id)` ON DELETE CASCADE

### game_movies

Stores game trailer/movie URLs with display ordering.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Movie ID |
| game_id | INTEGER | NOT NULL, FOREIGN KEY | References games(app_id) |
| url | TEXT | NOT NULL | Movie URL |
| display_order | INTEGER | | Display order |

**Foreign Keys:**
- `game_id` → `games(app_id)` ON DELETE CASCADE

## Entity-Relationship Diagram

```
┌─────────────┐
│    games    │──┐
└─────────────┘  │
                 │ 1:N
                 │
         ┌───────┴────────┬────────────┬─────────────┬──────────┬─────────────┐
         │                │            │             │          │             │
         ▼                ▼            ▼             ▼          ▼             ▼
┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌───────┐  ┌──────┐  ┌──────────┐
│game_devs     │  │game_pubs     │  │game_cats │  │game_  │  │game_ │  │game_     │
│              │  │              │  │          │  │genres │  │tags  │  │supported │
│              │  │              │  │          │  │       │  │      │  │languages │
└──────┬───────┘  └──────┬───────┘  └────┬─────┘  └───┬───┘  └──┬───┘  └────┬─────┘
       │                 │               │            │         │           │
       │ N:1             │ N:1           │ N:1        │ N:1     │ N:1       │ N:1
       │                 │               │            │         │           │
       ▼                 ▼               ▼            ▼         ▼           ▼
┌──────────┐      ┌───────────┐   ┌──────────┐ ┌────────┐ ┌──────┐ ┌──────────┐
│developers│      │publishers │   │categories│ │genres  │ │tags  │ │languages │
└──────────┘      └───────────┘   └──────────┘ └────────┘ └──────┘ └──────────┘

                        ┌─────────────┐
                        │    games    │
                        └─────────────┘
                               │ 1:N
                     ┌─────────┴──────────┐
                     │                    │
                     ▼                    ▼
              ┌─────────────┐      ┌────────────┐
              │game_        │      │game_movies │
              │screenshots  │      │            │
              └─────────────┘      └────────────┘
```

## SQL Schema Generation

To generate the complete SQL schema, run:

```bash
python src/steam_db_ingestion.py
```

Or programmatically:

```python
from steam_db_ingestion import SteamGamesDB

db = SteamGamesDB("data")
db.create_schema()
db.close()
```

## Query Examples

### Get all games with their developers

```sql
SELECT g.name, d.name as developer
FROM games g
JOIN game_developers gd ON g.app_id = gd.game_id
JOIN developers d ON gd.developer_id = d.id;
```

### Find games by genre

```sql
SELECT g.name, g.price
FROM games g
JOIN game_genres gg ON g.app_id = gg.game_id
JOIN genres ge ON gg.genre_id = ge.id
WHERE ge.name = 'Action';
```

### Get top-rated games

```sql
SELECT name, positive_reviews, negative_reviews,
       (positive_reviews * 100.0 / (positive_reviews + negative_reviews)) as rating
FROM games
WHERE (positive_reviews + negative_reviews) > 100
ORDER BY rating DESC
LIMIT 10;
```

### Games by platform

```sql
SELECT name, price
FROM games
WHERE windows = 1 AND mac = 1 AND linux = 1
ORDER BY positive_reviews DESC;
```

## Data Integrity

- **Foreign key constraints** are enabled to ensure referential integrity
- **CASCADE DELETE** ensures orphaned records are automatically removed
- **UNIQUE constraints** on entity names prevent duplicates
- **NOT NULL constraints** ensure required fields are populated
- **Composite primary keys** on junction tables prevent duplicate relationships

## Performance Considerations

The schema includes indexes on:
- Game names (for search)
- Release dates (for filtering)
- Prices (for sorting/filtering)
- Review counts (for ranking)
- All junction table game_id foreign keys (for join performance)

These indexes significantly improve query performance for common operations.
