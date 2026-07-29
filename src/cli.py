import argparse
import logging
import sqlite3
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data/registry.db"
MIGRATION_PATH = "src/migrations/001_init.sql"

def init_db(args: argparse.Namespace) -> None:
    """Initialize the SQLite database."""
    logger.info("Initializing database...")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.dirname(DB_PATH)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Created directory: {data_dir}")
    
    # Check if DB already has tables
    db_exists = os.path.exists(DB_PATH)
    if db_exists:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='content';")
                if cursor.fetchone() is not None:
                    logger.info("Database already initialized (tables exist). Idempotent exit.")
                    return
        except sqlite3.Error as e:
            logger.error("Error checking existing database: %s", e)
            sys.exit(1)
            
    # Read and execute migration script
    if not os.path.exists(MIGRATION_PATH):
        logger.error("Migration file not found: %s", MIGRATION_PATH)
        sys.exit(1)
        
    try:
        with open(MIGRATION_PATH, "r", encoding="utf-8") as f:
            sql_script = f.read()
            
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(sql_script)
            logger.info("Database initialized successfully with schema from 001_init.sql.")
    except sqlite3.Error as e:
        logger.error("Database error during initialization: %s", e)
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        logger.error("Unexpected error: %s", e)
        sys.exit(1)

def ingest_library_cmd(args: argparse.Namespace) -> None:
    """Handle the ingest-library command."""
    from src.ingest.library_scraper import process_urls
    
    urls = []
    if args.url:
        urls.append(args.url)
    if args.urls:
        urls.extend(args.urls)
        
    logger.info("Starting ingest-library for %d URL(s)...", len(urls))
    try:
        process_urls(urls, DB_PATH)
        logger.info("ingest-library complete.")
    except Exception as e:
        logger.error("Error during ingest-library: %s", e)
        sys.exit(1)


def ingest_youtube_cmd(args: argparse.Namespace) -> None:
    """Handle the ingest-youtube command."""
    from src.ingest.youtube_downloader import process_urls
    
    urls = []
    if args.url:
        urls.append(args.url)
    if args.urls:
        urls.extend(args.urls)
        
    logger.info("Starting ingest-youtube for %d URL(s)...", len(urls))
    try:
        process_urls(urls, DB_PATH)
        logger.info("ingest-youtube complete.")
    except Exception as e:
        logger.error("Error during ingest-youtube: %s", e)
        sys.exit(1)


def chunk_cmd(args: argparse.Namespace) -> None:
    """Handle the chunk command."""
    if not args.all:
        logger.error("Currently only --all is supported for the chunk command.")
        sys.exit(1)
        
    from src.chunker.essay_chunker import chunk_essay
    from src.chunker.transcript_chunker import chunk_transcript
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content_id, source_type, file_path, speaker FROM content WHERE state = 'downloaded'")
            records = cursor.fetchall()
            
        if not records:
            logger.info("No downloaded content found to chunk.")
            return
            
        logger.info("Found %d downloaded items to chunk.", len(records))
        
        success_count = 0
        for record in records:
            content_id, source_type, file_path, speaker = record
            
            try:
                if source_type == 'library':
                    with open(file_path, "r", encoding="utf-8") as f:
                        markdown_text = f.read()
                    chunk_essay(content_id, markdown_text, speaker, DB_PATH)
                elif source_type == 'youtube':
                    chunk_transcript(content_id, file_path, speaker, DB_PATH)
                else:
                    logger.warning("Unknown source_type %s for %s", source_type, content_id)
                    continue
                success_count += 1
            except Exception as e:
                logger.error("Failed to chunk %s: %s", content_id, e)
                
        logger.info("Chunking complete. Successfully chunked %d/%d items.", success_count, len(records))
    except sqlite3.Error as e:
        logger.error("Database error during chunking: %s", e)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="YC Skills Forge CLI")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
    
    # init-db
    init_parser = subparsers.add_parser("init-db", help="Initialize the SQLite database")
    init_parser.set_defaults(func=init_db)
    
    # Stubs for future commands
    # ingest-library
    ingest_lib_parser = subparsers.add_parser("ingest-library", help="Ingest YC Library essay")
    lib_group = ingest_lib_parser.add_mutually_exclusive_group(required=True)
    lib_group.add_argument("--url", help="URL of the essay")
    lib_group.add_argument("--urls", nargs="+", help="Multiple URLs of the essays")
    ingest_lib_parser.set_defaults(func=ingest_library_cmd)
    
    # ingest-youtube
    ingest_yt_parser = subparsers.add_parser("ingest-youtube", help="Ingest YouTube video")
    yt_group = ingest_yt_parser.add_mutually_exclusive_group(required=True)
    yt_group.add_argument("--url", help="URL of the video")
    yt_group.add_argument("--urls", nargs="+", help="Multiple URLs of the videos")
    ingest_yt_parser.set_defaults(func=ingest_youtube_cmd)
    
    # chunk
    chunk_parser = subparsers.add_parser("chunk", help="Chunk downloaded content")
    chunk_parser.add_argument("--all", action="store_true", help="Chunk all unchunked content")
    chunk_parser.set_defaults(func=chunk_cmd)
    
    # forge
    forge_parser = subparsers.add_parser("forge", help="Run core forge pipeline")
    forge_parser.add_argument("--topic", help="Topic to scope extraction")
    forge_parser.add_argument("--batch-size", type=int, default=15, help="Batch size")
    
    # link
    link_parser = subparsers.add_parser("link", help="Run deferred link pass")
    link_parser.add_argument("--topic", help="Topic to scope linking")
    
    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate generated skills")
    validate_parser.add_argument("--all", action="store_true", help="Validate all skills")
    
    # export
    export_parser = subparsers.add_parser("export", help="Export specs")
    export_parser.add_argument("--all", action="store_true", help="Export all valid skills")
    
    # index
    subparsers.add_parser("index", help="Generate index and similarity matrix")
    
    # reaper
    subparsers.add_parser("reaper", help="Reset stale extracting items")
    
    # quota
    subparsers.add_parser("quota", help="Check provider quota usage")
    
    # backfill
    backfill_parser = subparsers.add_parser("backfill", help="Historical content ingestion")
    backfill_parser.add_argument("--start-date", help="Start date for backfill")

    args = parser.parse_args()
    
    if hasattr(args, "func"):
        args.func(args)
    else:
        logger.warning("Command '%s' is registered but not implemented yet.", args.command)

if __name__ == "__main__":
    main()
