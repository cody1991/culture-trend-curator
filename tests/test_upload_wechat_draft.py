import importlib.util
from pathlib import Path
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "upload_wechat_draft.py"
SPEC = importlib.util.spec_from_file_location("upload_wechat_draft", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class MarkdownRenderingTests(unittest.TestCase):
    def test_title_is_removed_from_body_and_links_are_preserved(self):
        title, body = MODULE.title_and_body("# 本周书影\n\n[来源](https://example.com?a=1&b=2) 与 *强调*。")

        self.assertEqual(title, "本周书影")
        self.assertNotIn("<h1>", body)
        self.assertIn('href="https://example.com?a=1&amp;b=2"', body)
        self.assertIn('style="color:#9a5d45;text-decoration:none;', body)
        self.assertIn("<em>强调</em>", body)

    def test_raw_html_is_escaped(self):
        rendered = MODULE.markdown_to_html("<script>alert('x')</script>")

        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>", rendered)

    def test_lists_and_quotes_render(self):
        rendered = MODULE.markdown_to_html("> 一句引文\n\n- 第一项\n- 第二项\n\n1. 一个\n2. 两个")

        self.assertIn("<blockquote style=", rendered)
        self.assertIn("<ul style=", rendered)
        self.assertIn("<ol style=", rendered)

    def test_headings_and_references_receive_wechat_inline_styles(self):
        rendered = MODULE.markdown_to_html("## 第一节\n\n正文。\n\n### 1. 条目\n\n详情。\n\n## 参考来源\n\n来源：https://example.com")

        self.assertIn("border-left:4px solid #a45f4a", rendered)
        self.assertIn("border-bottom:1px solid #dcc8ba", rendered)
        self.assertIn("font-size:12px", rendered)

    def test_work_metadata_uses_a_compact_editorial_card(self):
        rendered = MODULE.markdown_to_html(
            "> 作品档案｜出版：2024｜豆瓣：8.8（32,598 人评价）｜类型：非虚构"
        )

        self.assertIn("background:#f8f4ef", rendered)
        self.assertIn("font-size:13px", rendered)
        self.assertNotIn("<blockquote", rendered)

    def test_item_titles_are_plain_but_douban_urls_remain_visible(self):
        rendered = MODULE.markdown_to_html(
            "### [《标题》](https://book.douban.com/subject/1/)｜作者\n\n"
            "豆瓣条目：https://book.douban.com/subject/1/"
        )

        self.assertIn("<h3", rendered)
        self.assertNotIn('<a href="https://book.douban.com/subject/1/"', rendered)
        self.assertIn("豆瓣条目：https://book.douban.com/subject/1/", rendered)
        self.assertIn("margin:-10px 0 20px", rendered)

    def test_article_payload_is_a_single_updateable_article(self):
        payload = MODULE.article_payload("标题", "<p>正文</p>", "cover-id", "作者", "摘要", "")

        self.assertEqual(payload["title"], "标题")
        self.assertEqual(payload["thumb_media_id"], "cover-id")
        self.assertNotIn("content_source_url", payload)


if __name__ == "__main__":
    unittest.main()
