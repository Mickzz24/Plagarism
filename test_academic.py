import urllib.request
import json
import urllib.parse

# Test Crossref metadata
query = "machine learning natural language processing"
url = f"https://api.crossref.org/works?query={urllib.parse.quote(query)}&select=title,abstract&rows=3"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'mailto:test@example.com'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        items = data['message']['items']
        print(f"Found {len(items)} academic papers from Crossref:")
        for item in items:
            title = item.get('title', ['Unnamed'])[0]
            print(f"- {title}")
except Exception as e:
    print("Error:", e)
