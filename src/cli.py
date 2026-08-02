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


def reaper_cmd(args: argparse.Namespace) -> None:
    """Handle the reaper command."""
    from src.forge.reaper import run_reaper
    
    logger.info("Starting reaper...")
    try:
        count = run_reaper(DB_PATH)
        logger.info("Reaper completed. Recovered/failed %d item(s).", count)
    except Exception as e:
        logger.error("Error during reaper execution: %s", e)
        sys.exit(1)


def link_cmd(args: argparse.Namespace) -> None:
    """Handle the link command."""
    from src.forge.linker import run_linker
    
    logger.info("Starting deferred link pass...")
    try:
        run_linker(DB_PATH)
        logger.info("Deferred link pass complete.")
    except Exception as e:
        logger.error("Error during deferred link pass: %s", e)
        sys.exit(1)


def forge_cmd(args: argparse.Namespace) -> None:
    """Handle the forge command."""
    from src.forge.batcher import select_batch
    from src.forge.extractor import run_extraction
    from src.forge.clusterer import run_clustering
    from src.forge.synthesizer import run_synthesis
    
    logger.info("Starting forge pipeline...")
    try:
        batch_id, content_ids = select_batch(DB_PATH, topic=args.topic, batch_size=args.batch_size)
        logger.info("Batch %s selected with %d items.", batch_id, len(content_ids))
        
        run_extraction(batch_id, content_ids, DB_PATH)
        logger.info("Forge extraction complete for batch %s.", batch_id)
        
        run_clustering(batch_id, DB_PATH)
        logger.info("Forge clustering complete for batch %s.", batch_id)
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cluster_id FROM clusters WHERE batch_id = ?", (batch_id,))
            cluster_ids = [row[0] for row in cursor.fetchall()]
            
        logger.info("Found %d clusters for synthesis.", len(cluster_ids))
        for cid in cluster_ids:
            run_synthesis(cid, DB_PATH)
            
        logger.info("Forge synthesis complete for batch %s.", batch_id)
        
    except Exception as e:
        logger.error("Error during forge pipeline: %s", e)
        sys.exit(1)


def validate_cmd(args: argparse.Namespace) -> None:
    """Handle the validate command."""
    from src.validator.run import main as validator_main
    import sys
    
    if not getattr(args, "all", False) and not getattr(args, "skill_id", None):
        logger.error("Must specify either --all or --skill-id")
        sys.exit(1)
        
    # Patch sys.argv for the validator's argparse
    patched_argv = ["src.validator.run"]
    if getattr(args, "all", False):
        patched_argv.append("--all")
    if getattr(args, "skill_id", None):
        patched_argv.extend(["--skill-id", args.skill_id])
        
    original_argv = sys.argv.copy()
    try:
        sys.argv = patched_argv
        validator_main()
    except SystemExit as e:
        # Propagate the exit code
        sys.exit(e.code)
    except Exception as e:
        logger.error("Error during validation: %s", e)
        sys.exit(1)
    finally:
        sys.argv = original_argv


def export_cmd(args: argparse.Namespace) -> None:
    """Handle the export command."""
    from src.exporter.mcp_exporter import export_mcp, export_all_mcp
    from src.exporter.openai_exporter import export_openai, export_all_openai
    from src.exporter.hermes_exporter import export_hermes, export_all_hermes
    import os
    from pathlib import Path
    
    os.makedirs("specs/mcp", exist_ok=True)
    os.makedirs("specs/openai", exist_ok=True)
    os.makedirs("specs/hermes", exist_ok=True)
    
    if not args.all and not args.skill_id:
        logger.error("Must specify either --all or --skill-id")
        sys.exit(1)
        
    formats_to_run = ["mcp", "openai", "hermes"]
    if args.format:
        formats_to_run = [args.format]
        
    generated_count = 0
    skills_processed = set()
    
    try:
        if args.skill_id:
            # Find specific skill file
            skill_files = list(Path("skills").rglob(f"{args.skill_id}.md"))
            if not skill_files:
                logger.error("Skill %s not found in skills/ directory.", args.skill_id)
                sys.exit(1)
            skill_path = str(skill_files[0])
            
            if "mcp" in formats_to_run:
                export_mcp(skill_path)
                generated_count += 1
                skills_processed.add(skill_path)
            if "openai" in formats_to_run:
                export_openai(skill_path)
                generated_count += 1
                skills_processed.add(skill_path)
            if "hermes" in formats_to_run:
                export_hermes(skill_path)
                generated_count += 1
                skills_processed.add(skill_path)
        elif args.all:
            # Process all skills
            if "mcp" in formats_to_run:
                generated = export_all_mcp()
                generated_count += len(generated)
                skills_processed.update(generated)  # Note: this adds output paths, but we just want count of unique skills if possible. Actually, let's just count files.
            if "openai" in formats_to_run:
                generated = export_all_openai()
                generated_count += len(generated)
                skills_processed.update(generated)
            if "hermes" in formats_to_run:
                generated = export_all_hermes()
                generated_count += len(generated)
                skills_processed.update(generated)
                
            # Count distinct input skills (number of markdown files) if we did all
            md_files = list(Path("skills").rglob("*.md"))
            skills_processed = set(md_files)
                
        logger.info(
            "Export complete. Processed %d skills, generated %d spec files across: %s",
            len(skills_processed),
            generated_count,
            ", ".join([f"specs/{f}" for f in formats_to_run])
        )
    except Exception as e:
        logger.error("Error during export: %s", e)
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
    forge_parser.set_defaults(func=forge_cmd)
    
    # link
    link_parser = subparsers.add_parser("link", help="Run deferred link pass")
    link_parser.add_argument("--topic", help="Topic to scope linking")
    link_parser.set_defaults(func=link_cmd)
    
    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate skill files against the three-layer validation suite (schema, quotes, hallucination guard).")
    validate_parser.add_argument("--all", action="store_true", help="Validate all skills")
    validate_parser.add_argument("--skill-id", type=str, help="Validate a single skill by ID")
    validate_parser.set_defaults(func=validate_cmd)
    
    # export
    export_parser = subparsers.add_parser("export", help="Export specs in MCP, OpenAI, and Hermes formats")
    export_parser.add_argument("--all", action="store_true", help="Export all valid skills")
    export_parser.add_argument("--format", choices=["mcp", "openai", "hermes"], help="Export a specific format")
    export_parser.add_argument("--skill-id", type=str, help="Export a single skill by ID")
    export_parser.set_defaults(func=export_cmd)
    
    # index
    subparsers.add_parser("index", help="Generate index and similarity matrix")
    
    # reaper
    reaper_parser = subparsers.add_parser("reaper", help="Reset stale extracting items")
    reaper_parser.set_defaults(func=reaper_cmd)
    
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
