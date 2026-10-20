import MarkdownIt from "markdown-it";

const parser = new MarkdownIt("commonmark", { html: false });
parser.enable("table").enable("strikethrough");

function slugify(text) {
  const slug = text
    .toLowerCase()
    .replace(/[^\w-]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "section";
}

export function renderMarkdown(source) {
  const tokens = parser.parse(source, {});
  const toc = [];
  const slugCounts = {};

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (token.type === "heading_open") {
      const inline = tokens[i + 1];
      const base = slugify(inline.content || "");
      const count = slugCounts[base] || 0;
      slugCounts[base] = count + 1;
      const slug = count === 0 ? base : `${base}-${count + 1}`;
      token.attrSet("id", slug);
      toc.push({
        level: parseInt(token.tag.slice(1), 10),
        title: inline.content || "",
        id: slug,
      });
    }
  }

  const html = parser.renderer.render(tokens, parser.options, {});
  return { html, toc };
}
