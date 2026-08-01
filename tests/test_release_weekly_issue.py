import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "release_weekly_issue.py"
SPEC = importlib.util.spec_from_file_location("release_weekly_issue", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ReleaseCommandTests(unittest.TestCase):
    def test_release_commands_publish_wechat_then_push_site(self):
        args = type(
            "Args",
            (),
            {
                "article": Path("/tmp/article.md"),
                "cover": Path("/tmp/cover.png"),
                "author": "书影趋势",
                "digest": "本周推荐",
                "source_url": "",
            },
        )()

        wechat = MODULE.build_wechat_command(args)
        site = MODULE.build_site_command(args)

        self.assertIn("--publish", wechat)
        self.assertIn("--author", wechat)
        self.assertNotIn("--source-url", wechat)
        self.assertEqual(site[-2:], ["--commit", "--push"])


if __name__ == "__main__":
    unittest.main()
