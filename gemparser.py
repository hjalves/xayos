from xayos.gemtext import GemtextParser

parser = GemtextParser()

with open("faq.gmi") as f:
    gemtext = f.read()

tokens = parser.parse(gemtext)
for token in tokens:
    print(token)
