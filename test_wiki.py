import wikipedia

text = "Natural language processing (NLP) is an interdisciplinary subfield of computer science"

try:
    results = wikipedia.search(text, results=2)
    print("Search Results:", results)
    if results:
        page = wikipedia.page(results[0])
        print("Page URL:", page.url)
        print("Content Snippet:", page.content[:200])
except Exception as e:
    print("Error:", e)
