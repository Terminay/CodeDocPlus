import json
import tempfile
import unittest
from pathlib import Path

from web import create_app


class DocumentationSiteTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        self.app = create_app(docs_dir=self.docs)
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_library_lists_markdown_documents_and_ignores_hidden_paths(self):
        (self.docs / "guide.md").write_text("# Guide", encoding="utf-8")
        hidden = self.docs / ".private"
        hidden.mkdir()
        (hidden / "notes.md").write_text("# Private", encoding="utf-8")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Guide", response.data)
        self.assertNotIn(b"Private", response.data)
        self.assertIn(b"/docs/guide.md", response.data)

    def test_document_renders_markdown_toc_code_and_escapes_raw_html(self):
        (self.docs / "guide.md").write_text(
            "# Guide\n\n## Setup\n\n```py\nprint('ready')\n```\n\n<script>alert(1)</script>",
            encoding="utf-8",
        )

        response = self.client.get("/docs/guide.md")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="#setup"', response.data)
        self.assertIn(b'<h2 id="setup">Setup</h2>', response.data)
        self.assertIn(b'<code class="language-py">print(', response.data)
        self.assertNotIn(b"<script>alert(1)</script>", response.data)
        self.assertIn(b"&lt;script&gt;", response.data)

    def test_local_markdown_links_and_assets_are_routed_inside_docs(self):
        (self.docs / "index.md").write_text(
            "[Next](nested/next.md#details)\n\n![Diagram](images/map.svg)",
            encoding="utf-8",
        )
        nested = self.docs / "nested"
        nested.mkdir()
        (nested / "next.md").write_text("# Next\n\n## Details", encoding="utf-8")
        images = self.docs / "images"
        images.mkdir()
        (images / "map.svg").write_text("<svg></svg>", encoding="utf-8")

        response = self.client.get("/docs/index.md")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="/docs/nested/next.md#details"', response.data)
        self.assertIn(b'src="/files/images/map.svg"', response.data)
        asset_response = self.client.get("/files/images/map.svg")
        self.assertEqual(asset_response.status_code, 200)
        asset_response.close()

    def test_missing_documents_and_paths_outside_docs_return_not_found(self):
        self.assertEqual(self.client.get("/docs/missing.md").status_code, 404)
        self.assertEqual(self.client.get("/files/../README.md").status_code, 404)

    def test_site_configuration_applies_branding_and_rejects_invalid_colors(self):
        config = self.root / "site.json"
        config.write_text(
            json.dumps(
                {
                    "title": "Field Manual",
                    "tagline": "Project notes",
                    "docs_dir": "docs",
                    "theme": {"accent": "#123456"},
                }
            ),
            encoding="utf-8",
        )
        configured_app = create_app(config_path=config)
        configured_app.config.update(TESTING=True)
        response = configured_app.test_client().get("/")
        self.assertIn(b"Field Manual", response.data)
        self.assertIn(b"#123456", response.data)

        config.write_text(
            json.dumps({"docs_dir": "docs", "theme": {"accent": "red; color: blue"}}),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "3- or 6-digit hex color"):
            create_app(config_path=config)
        with self.assertRaisesRegex(ValueError, "site config file does not exist"):
            create_app(config_path=self.root / "missing.json")


if __name__ == "__main__":
    unittest.main()
