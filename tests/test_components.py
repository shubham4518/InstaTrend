from pathlib import Path
import tempfile
from trendbharat.collector.pipeline import TrendsPipeline
from trendbharat.render.caption_builder import build_instagram_caption
from trendbharat.render.post_builder import RVCJPostBuilder
from trendbharat.db.manager import DatabaseManager


def test_categorization_and_blocking():
    config_dir = Path(__file__).resolve().parent.parent / "trendbharat" / "config"
    pipeline = TrendsPipeline(config_dir)

    # Test categorization
    cat, badge, hashtags = pipeline.categorize("ipl cricket match", "Rohit Sharma scores 100")
    assert cat == "Sports"
    assert "CRICKET" in badge

    # Test safety blocklist
    blocked, reason = pipeline.is_blocked("terrible suicide attempt in city")
    assert blocked is True
    assert reason == "suicide"

    safe, _ = pipeline.is_blocked("Manoj Bajpayee new thriller series")
    assert safe is False


def test_caption_builder():
    sample_story = {
        "query": "Rajinikanth",
        "category": "Entertainment",
        "badge": "CINEMA & ENTERTAINMENT",
        "headline": "Rajinikanth begins shooting for Jailer 2 in Chennai",
        "statement": "“Jailer 2 will be bigger and darker: Nelson”",
        "context": "Sun Pictures announced the sequel with music by Anirudh Ravichander.",
        "hashtags": "#rajinikanth #jailer2 #cinema",
    }
    caption = build_instagram_caption(sample_story, handle="@InstaTrend")
    assert "@InstaTrend" in caption
    assert "Rajinikanth" in caption
    assert "#jailer2" in caption


def test_database_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test.db"
        db = DatabaseManager(str(db_file))

        assert db.check_all_completed_today("2026-11-13", required_count=3) is False

        sample_story_1 = {
            "query": "Topic 1",
            "category": "Sports",
            "headline": "Headline 1",
            "hd_image_url": "https://example.com/1.jpg",
        }
        sample_story_2 = {
            "query": "Topic 2",
            "category": "Cinema",
            "headline": "Headline 2",
            "hd_image_url": "https://example.com/2.jpg",
        }
        sample_story_3 = {
            "query": "Topic 3",
            "category": "Politics",
            "headline": "Headline 3",
            "hd_image_url": "https://example.com/3.jpg",
        }

        db.record_run("2026-11-13", sample_story_1, post_index=1, status="completed")
        assert db.check_post_completed("2026-11-13", post_index=1) is True
        assert db.check_all_completed_today("2026-11-13", required_count=3) is False

        db.record_run("2026-11-13", sample_story_2, post_index=2, status="completed")
        db.record_run("2026-11-13", sample_story_3, post_index=3, status="completed")

        assert db.check_all_completed_today("2026-11-13", required_count=3) is True


def test_post_builder_text_wrapping():
    builder = RVCJPostBuilder()
    font = builder._get_font("Test", 30, bold=True)
    wrapped = builder._wrap_text("This is a long news headline for testing text wrapping", font, max_width=200)
    assert len(wrapped) > 1
