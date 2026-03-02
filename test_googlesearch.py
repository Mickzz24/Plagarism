from googlesearch import search

text = "Natural language processing (NLP) is an interdisciplinary subfield of computer science and information retrieval."

try:
    results = list(search(f'"{text}"', num_results=3))
    print("Results:", results)
except Exception as e:
    print("Error:", e)
