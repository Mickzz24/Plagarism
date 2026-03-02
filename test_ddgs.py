from duckduckgo_search import DDGS

text = "Natural language processing (NLP) is an interdisciplinary subfield of computer science and information retrieval."
try:
    with DDGS() as ddgs:
        results = list(ddgs.text(text, max_results=3))
        print("DDG Results:", [r.get('href') or r.get('link') for r in results])
except Exception as e:
    print(e)
