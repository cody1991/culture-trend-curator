import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "publish_site_issue.py"
SPEC = importlib.util.spec_from_file_location("publish_site_issue", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


ARTICLE = """# 一次可回看的本期

*2026 年 8 月 1 日｜书影趋势周报*

第一段导语，说明本期的编辑线索。

第二段导语，补充为什么现在值得读和看。

## 书页之间：慢下来

### 1. [《一本书》](https://example.com/book)｜作者甲

这是本期最明确的“现在就读”位。它让人重新看见日常。

## 光影之中：再出发

### 1. [《一部电影》](https://example.com/film)｜导演乙

这是本期的影史补课位，适合在安静的晚上看。

## 本期观察

文化不是催促，而是给人留出停下来的位置。

## 参考来源

示例：https://example.com/source
"""


class SiteIssueBuildTests(unittest.TestCase):
    def test_build_creates_current_page_archive_and_cover(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "generated" / "20260801"
            source.mkdir(parents=True)
            article = source / "article.md"
            cover = source / "cover.png"
            article.write_text(ARTICLE, encoding="utf-8")
            cover.write_bytes(b"not-a-real-png-but-copyable")
            site = root / "site"

            files = MODULE.build_issue(article, cover, site, "20260801", dry_run=False)

            self.assertTrue((site / "index.html").is_file())
            self.assertTrue((site / "issues" / "20260801" / "index.html").is_file())
            self.assertTrue((site / "assets" / "issue-20260801-cover.png").is_file())
            self.assertEqual(len(files), 5)
            home = (site / "index.html").read_text(encoding="utf-8")
            issue_page = (site / "issues" / "20260801" / "index.html").read_text(encoding="utf-8")
            self.assertIn("一次可回看的本期", home)
            self.assertIn("《一本书》", home)
            self.assertIn("《一部电影》", issue_page)
            self.assertIn('href="https://example.com/source"', issue_page)
            archive = json.loads((site / "archive.json").read_text(encoding="utf-8"))
            self.assertEqual(archive[0]["date"], "20260801")
            self.assertEqual(archive[0]["number"], "1")

    def test_rebuilding_an_issue_replaces_its_archive_entry(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "generated" / "20260801"
            source.mkdir(parents=True)
            article = source / "article.md"
            cover = source / "cover.png"
            article.write_text(ARTICLE, encoding="utf-8")
            cover.write_bytes(b"cover")
            site = root / "site"

            MODULE.build_issue(article, cover, site, "20260801", dry_run=False)
            MODULE.build_issue(article, cover, site, "20260801", dry_run=False)

            archive = json.loads((site / "archive.json").read_text(encoding="utf-8"))
            self.assertEqual(len(archive), 1)

    def test_dry_run_does_not_write(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "generated" / "20260801"
            source.mkdir(parents=True)
            article = source / "article.md"
            cover = source / "cover.png"
            article.write_text(ARTICLE, encoding="utf-8")
            cover.write_bytes(b"cover")
            site = root / "site"

            files = MODULE.build_issue(article, cover, site, "20260801", dry_run=True)

            self.assertEqual(len(files), 5)
            self.assertFalse(site.exists())


if __name__ == "__main__":
    unittest.main()
