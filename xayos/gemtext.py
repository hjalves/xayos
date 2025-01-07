import io
from dataclasses import dataclass


@dataclass
class GemtextToken:
    """
    In Gemtext, a token is generally a single line of text. One exception is the
    preformatted block, which consists of multiple lines of text.

    The attribute type can be one of: 'text' (the default), 'list', 'link', 'quote',
    'pre' for preformatted block, and 'head1', 'head2', 'head3' for headings.
    The text attribute contains the text content of the token, without the line break.
    The meta attribute is used for link labels and preformatted block alt text.
    """

    type: str = "text"  # text, head1, head2, head3, list, link, quote, pre
    text: str = ""  # content of the token, without the line break (except for pre)
    meta: str = ""  # for links and preformatted blocks


class GemtextParser:
    """
    A parser for the Gemtext markup language, a lightweight alternative to Markdown.

    See https://geminiprotocol.net/docs/gemtext.gmi for the specification.
    """

    def parse(self, gemtext):
        """
        Parse the given Gemtext string into a list of tokens.
        """
        stream = io.StringIO(gemtext)
        return list(self.parse_stream(stream))

    def parse_stream(self, stream):
        """
        Parse the given stream of Gemtext and yield tokens.
        """
        in_pre = False
        pre_alt = ""
        pre_lines = []
        for line in stream:
            if line.startswith("```"):
                in_pre = not in_pre
                if in_pre:
                    pre_alt = line[3:].rstrip("\n")
                    continue
            if in_pre:
                pre_lines.append(line)
            elif pre_lines:
                yield GemtextToken(type="pre", text="".join(pre_lines), meta=pre_alt)
                pre_lines = []
            else:
                yield self.parse_single_line(line)

    def parse_single_line(self, line):
        """
        Parse a single line of Gemtext into a token.
        Does not handle preformatted blocks.
        """
        line = line.rstrip("\n")
        if line.startswith("# "):
            return GemtextToken(type="head1", text=line[2:].lstrip())
        elif line.startswith("## "):
            return GemtextToken(type="head2", text=line[3:].lstrip())
        elif line.startswith("### "):
            return GemtextToken(type="head3", text=line[4:].lstrip())
        elif line.startswith("* "):
            return GemtextToken(type="list", text=line[2:].lstrip())
        elif line.startswith(">"):
            return GemtextToken(type="quote", text=line[1:].lstrip())
        elif line.startswith("=>"):
            url, *label = line[2:].strip().split(maxsplit=1)
            return GemtextToken(type="link", text=url, meta="".join(label))
        return GemtextToken(type="text", text=line)
