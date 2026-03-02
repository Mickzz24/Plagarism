import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

query = "natural language processing deep learning"
url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results=3"

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = response.read()
        root = ET.fromstring(data)
        
        # arXiv uses Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = root.findall('atom:entry', ns)
        print(f"Found {len(entries)} papers on arXiv:")
        for entry in entries:
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            print(f"- {title}")
except Exception as e:
    print("Error:", e)
