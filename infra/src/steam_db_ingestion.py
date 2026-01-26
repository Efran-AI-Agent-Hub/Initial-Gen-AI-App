"""
Steam Games Database Ingestion Script
Normalizes CSV data into a relational SQLite database following industry best practices.
"""
import csv
import sqlite3
import pandas as pd
from typing import List, Dict, Any
from pprint import pprint
import os

DB_PATH = "data"


class SteamGamesDB:
    """Handles creation and population of normalized Steam games database."""

    def __init__(self, db_path: str = "data"):
        self.db_path = db_path

        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

        self.db_path = os.path.join(self.db_path, "steamgames.db")

        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        self.ingest_error = 0

    def create_schema(self):
        """Create normalized database schema with proper indexing."""
        cursor = self.conn.cursor()

        # Core tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                app_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                release_date TEXT,
                estimated_owners TEXT,
                peak_ccu INTEGER,
                required_age INTEGER,
                price REAL,
                discount_dlc_count INTEGER,
                about_the_game TEXT,
                reviews TEXT,
                header_image TEXT,
                website TEXT,
                support_url TEXT,
                support_email TEXT,
                windows BOOLEAN,
                mac BOOLEAN,
                linux BOOLEAN,
                metacritic_score INTEGER,
                metacritic_url TEXT,
                user_score INTEGER,
                positive_reviews INTEGER,
                negative_reviews INTEGER,
                score_rank TEXT,
                achievements INTEGER,
                recommendations INTEGER,
                notes TEXT,
                avg_playtime_forever INTEGER,
                avg_playtime_two_weeks INTEGER,
                median_playtime_forever INTEGER,
                median_playtime_two_weeks INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS developers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS publishers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS languages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Junction tables for many-to-many relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_developers (
                game_id INTEGER NOT NULL,
                developer_id INTEGER NOT NULL,
                PRIMARY KEY (game_id, developer_id),
                FOREIGN KEY (game_id) REFERENCES games(app_id) ON DELETE CASCADE,
                FOREIGN KEY (developer_id) REFERENCES developers(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_publishers (
                game_id INTEGER NOT NULL,
                publisher_id INTEGER NOT NULL,
                PRIMARY KEY (game_id, publisher_id),
                FOREIGN KEY (game_id) REFERENCES games(app_id) ON DELETE CASCADE,
                FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_categories (
                game_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                PRIMARY KEY (game_id, category_id),
                FOREIGN KEY (game_id) REFERENCES games(app_id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_genres (
                game_id INTEGER NOT NULL,
                genre_id INTEGER NOT NULL,
                PRIMARY KEY (game_id, genre_id),
                FOREIGN KEY (game_id) REFERENCES games(app_id) ON DELETE CASCADE,
                FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_tags (
                game_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (game_id, tag_id),
                FOREIGN KEY (game_id) REFERENCES games(app_id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_supported_languages (
                game_id INTEGER NOT NULL,
                language_id INTEGER NOT NULL,
                PRIMARY KEY (game_id, language_id),
                FOREIGN KEY (game_id) REFERENCES games(app_id) ON DELETE CASCADE,
                FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_audio_languages (
                game_id INTEGER NOT NULL,
                language_id INTEGER NOT NULL,
                PRIMARY KEY (game_id, language_id),
                FOREIGN KEY (game_id) REFERENCES games(app_id) ON DELETE CASCADE,
                FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE CASCADE
            )
        """)

        # Media tables for screenshots and movies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                display_order INTEGER,
                FOREIGN KEY (game_id) REFERENCES games(app_id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                display_order INTEGER,
                FOREIGN KEY (game_id) REFERENCES games(app_id) ON DELETE CASCADE
            )
        """)

        # Create indexes for better query performance
        self._create_indexes(cursor)

        self.conn.commit()
        print("✓ Database schema created successfully")

    def _create_indexes(self, cursor):
        """Create indexes on frequently queried columns."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_games_name ON games(name)",
            "CREATE INDEX IF NOT EXISTS idx_games_release_date ON games(release_date)",
            "CREATE INDEX IF NOT EXISTS idx_games_price ON games(price)",
            "CREATE INDEX IF NOT EXISTS idx_games_positive_reviews ON games(positive_reviews)",
            "CREATE INDEX IF NOT EXISTS idx_developers_name ON developers(name)",
            "CREATE INDEX IF NOT EXISTS idx_publishers_name ON publishers(name)",
            "CREATE INDEX IF NOT EXISTS idx_game_developers_game ON game_developers(game_id)",
            "CREATE INDEX IF NOT EXISTS idx_game_publishers_game ON game_publishers(game_id)",
            "CREATE INDEX IF NOT EXISTS idx_game_categories_game ON game_categories(game_id)",
            "CREATE INDEX IF NOT EXISTS idx_game_genres_game ON game_genres(game_id)",
            "CREATE INDEX IF NOT EXISTS idx_game_tags_game ON game_tags(game_id)",
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

    def _get_or_create_entity(self, table: str, name: str) -> int:
        """Get entity ID or create if doesn't exist. Returns entity ID."""
        cursor = self.conn.cursor()

        # Try to get existing
        cursor.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # Create new
        cursor.execute(f"INSERT INTO {table} (name) VALUES (?)", (name,))
        return cursor.lastrowid

    def _parse_csv_list(self, value: str) -> List[str]:
        """Parse comma-separated values from CSV, handling empty strings and NaN."""
        if pd.isna(value) or not value or value == "[]":
            return []

        # Convert to string in case it's not
        value = str(value)

        # Remove brackets and split
        cleaned = value.strip("[]")
        if not cleaned:
            return []

        return [item.strip() for item in cleaned.split(",") if item.strip()]

    def _parse_csv_array(self, value: str) -> List[str]:
        """Parse array-like strings from CSV (e.g., "['English', 'French']")."""
        if pd.isna(value) or not value or value == "[]":
            return []

        # Convert to string
        value = str(value)

        try:
            # Try to parse as Python list literal
            import ast

            return ast.literal_eval(value)
        except:
            # Fallback to simple parsing
            return self._parse_csv_list(value)

    def _parse_url_list(self, value: str) -> List[str]:
        """Parse comma-separated URLs, preserving commas in URLs."""
        if pd.isna(value) or not value:
            return []

        # Convert to string
        value = str(value)

        # Split by .jpg, .png, .mp4 etc and reconstruct
        urls = []
        for url in value.split(","):
            url = url.strip()
            if url and url.startswith("http"):
                urls.append(url)
        return urls

    def ingest_game(self, row: Dict[str, Any]):
        """Ingest a single game record into the normalized database."""
        cursor = self.conn.cursor()

        app_id = row["AppID"]

        # Note: The CSV has a column misalignment issue where Developers column contains wrong data
        # The actual mapping is: Publishers→Developers, Categories→Publishers, Genres→Categories, etc.
        actual_developers = row.get(
            "Publishers", ""
        )  # Publishers column contains developers
        actual_publishers = row.get(
            "Categories", ""
        )  # Categories column contains publishers
        actual_categories = row.get("Genres", "")
        actual_genres = row.get("Tags", "")
        actual_tags = row.get("Screenshots", "")
        actual_screenshots = row.get("Movies", "")

        # Insert main game record
        cursor.execute(
            """
            INSERT OR REPLACE INTO games (
                app_id, name, release_date, estimated_owners, peak_ccu,
                required_age, price, discount_dlc_count, about_the_game,
                reviews, header_image, website, support_url, support_email,
                windows, mac, linux, metacritic_score, metacritic_url,
                user_score, positive_reviews, negative_reviews, score_rank,
                achievements, recommendations, notes,
                avg_playtime_forever, avg_playtime_two_weeks,
                median_playtime_forever, median_playtime_two_weeks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                app_id,
                row.get("Name"),
                row.get("Release date"),
                row.get("Estimated owners"),
                row.get("Peak CCU"),
                row.get("Required age"),
                row.get("Price"),
                row.get("DiscountDLC count"),
                row.get("About the game"),
                row.get("Reviews"),
                row.get("Header image"),
                row.get("Website"),
                row.get("Support url"),
                row.get("Support email"),
                row.get("Windows") == "TRUE",
                row.get("Mac") == "TRUE",
                row.get("Linux") == "TRUE",
                row.get("Metacritic score") if row.get("Metacritic score") else None,
                row.get("Metacritic url"),
                row.get("User score"),
                row.get("Positive"),
                row.get("Negative"),
                row.get("Score rank"),
                row.get("Achievements"),
                row.get("Recommendations"),
                row.get("Notes"),
                row.get("Average playtime forever"),
                row.get("Average playtime two weeks"),
                row.get("Median playtime forever"),
                row.get("Median playtime two weeks"),
            ),
        )

        # Handle developers (from Publishers column)
        developers = self._parse_csv_list(actual_developers)
        for dev_name in developers:
            dev_id = self._get_or_create_entity("developers", dev_name)
            cursor.execute(
                "INSERT OR IGNORE INTO game_developers (game_id, developer_id) VALUES (?, ?)",
                (app_id, dev_id),
            )

        # Handle publishers (from Categories column)
        publishers = self._parse_csv_list(actual_publishers)
        for pub_name in publishers:
            pub_id = self._get_or_create_entity("publishers", pub_name)
            cursor.execute(
                "INSERT OR IGNORE INTO game_publishers (game_id, publisher_id) VALUES (?, ?)",
                (app_id, pub_id),
            )

        # Handle categories (from Genres column)
        categories = self._parse_csv_list(actual_categories)
        for cat_name in categories:
            cat_id = self._get_or_create_entity("categories", cat_name)
            cursor.execute(
                "INSERT OR IGNORE INTO game_categories (game_id, category_id) VALUES (?, ?)",
                (app_id, cat_id),
            )

        # Handle genres (from Tags column)
        genres = self._parse_csv_list(actual_genres)
        for genre_name in genres:
            genre_id = self._get_or_create_entity("genres", genre_name)
            cursor.execute(
                "INSERT OR IGNORE INTO game_genres (game_id, genre_id) VALUES (?, ?)",
                (app_id, genre_id),
            )

        # Handle tags (from Screenshots column)
        tags = self._parse_csv_list(actual_tags)
        for tag_name in tags:
            tag_id = self._get_or_create_entity("tags", tag_name)
            cursor.execute(
                "INSERT OR IGNORE INTO game_tags (game_id, tag_id) VALUES (?, ?)",
                (app_id, tag_id),
            )

        # Handle supported languages
        supported_langs = self._parse_csv_array(row.get("Supported languages", ""))
        for lang_name in supported_langs:
            lang_id = self._get_or_create_entity("languages", lang_name)
            cursor.execute(
                "INSERT OR IGNORE INTO game_supported_languages (game_id, language_id) VALUES (?, ?)",
                (app_id, lang_id),
            )

        # Handle audio languages
        audio_langs = self._parse_csv_array(row.get("Full audio languages", ""))
        for lang_name in audio_langs:
            lang_id = self._get_or_create_entity("languages", lang_name)
            cursor.execute(
                "INSERT OR IGNORE INTO game_audio_languages (game_id, language_id) VALUES (?, ?)",
                (app_id, lang_id),
            )

        # Handle screenshots (from Movies column)
        screenshots = self._parse_url_list(actual_screenshots)
        for idx, url in enumerate(screenshots):
            cursor.execute(
                "INSERT INTO game_screenshots (game_id, url, display_order) VALUES (?, ?, ?)",
                (app_id, url, idx),
            )

        # Note: No movies in this CSV due to column shift

    def ingest_csv_stream(self, csv_path: str, chunk_size: int = 50000):
        """Ingest steam review data into SQLite"""
        chunks = pd.read_csv(
            csv_path,
            chunksize=chunk_size,
            on_bad_lines='skip',
            encoding='utf-8',
            encoding_errors='replace',
            engine='python',
            index_col=False
        )

        total_attempted = 0
        total_success = 0
        errors = []

        for chunk_num, chunk_df in enumerate(chunks, 1):
            # Fill NaNs with empty strings to prevent parsing errors in _get_or_create_entity
            chunk_df = chunk_df.fillna("")

            for _, row in chunk_df.iterrows():

                total_attempted += 1
                row_dict = row.to_dict()

                try:
                    if not row_dict.get("AppID"):
                        continue
                    self.ingest_game(row_dict)
                    total_success += 1
                except Exception as e:
                    print(f"Error at AppID {row_dict.get('AppID')}: {e}")
                    errors.append({"app_id": row_dict.get("AppID"), "error": str(e)})

            self.conn.commit()
            print(f"Chunk {chunk_num} Complete: {total_success:,} successfully ingested ({len(errors)} errors)")

        return {"processed": total_success, "attempted": total_attempted, "errors": len(errors)}

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        cursor = self.conn.cursor()

        stats = {}
        tables = [
            "games",
            "developers",
            "publishers",
            "categories",
            "genres",
            "tags",
            "languages",
        ]

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]

        return stats

    def get_errors(self) -> Dict[str, int]:
        """Get database errors."""
        return {"ingest_error": self.ingest_error}

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution function."""
    import kagglehub

    # Download dataset
    print("Downloading Steam Games dataset...")
    path = kagglehub.dataset_download(
        handle="fronkongames/steam-games-dataset", force_download=False
    )
    print(f"Dataset path: {path}")
    # Initialize database
    db = SteamGamesDB("data")

    # Create schema
    db.create_schema()

    # Ingest data
    csv_path = os.path.join(path, "games.csv")
    db.ingest_csv_stream(csv_path)
    # Print statistics
    print("\n" + "=" * 50)
    print("DATABASE STATISTICS")
    print("=" * 50)
    stats = db.get_stats()

    for table, count in stats.items():
        print(f"{table:20s}: {count:,}")

    print("\n" + "=" * 50)
    print("DATABASE ERRORS")
    print("=" * 50)
    stats = db.get_errors()
    print(stats)

    db.close()
    print("\n✓ Database ingestion complete!")

if __name__ == "__main__":
    main()