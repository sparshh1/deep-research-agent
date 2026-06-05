import os
import time
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = 'http://export.arxiv.org/api/query?'
SEARCH_QUERY = '(ti:agent OR abs:agentic OR abs:"tool use" OR abs:"agent memory") AND (cat:cs.CL OR cat:cs.AI OR cat:cs.LG) AND submittedDate:[20240101 TO 20260430]'
MAX_RESULTS = 500
PDF_DIR = 'data/pdfs'
METADATA_FILE = 'data/papers.jsonl'

os.makedirs(PDF_DIR, exist_ok=True)

def fetch_metadata_with_retry(retries=5, delay=10):
    params = {
        'search_query': SEARCH_QUERY,
        'max_results': MAX_RESULTS,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    url = BASE_URL + urllib.parse.urlencode(params)
    
    for i in range(retries):
        try:
            print(f"Attempt {i+1}: Fetching metadata from arXiv...")
            with urllib.request.urlopen(url) as response:
                xml_data = response.read().decode('utf-8')
                return xml_data
        except urllib.error.HTTPError as e:
            if e.code in [429, 503]:
                wait = delay * (2 ** i) # Exponential backoff: 10s, 20s, 40s...
                print(f"Error {e.code}: Rate limited. Waiting {wait} seconds...")
                time.sleep(wait)
            else:
                raise e
    raise Exception("Failed to fetch metadata after multiple retries.")

def parse_and_download():
    try:
        xml_data = fetch_metadata_with_retry()
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            papers.append({'id': arxiv_id, 'title': title, 'abstract': summary})

        print(f"Found {len(papers)} papers. Starting downloads...")
        
        with open(METADATA_FILE, 'w') as f:
            for i, paper in enumerate(papers):
                f.write(json.dumps(paper) + '\n')
                file_path = os.path.join(PDF_DIR, f"{paper['id']}.pdf")
                
                if not os.path.exists(file_path):
                    try:
                        print(f"[{i+1}/{len(papers)}] Downloading {paper['id']}...")
                        pdf_url = f"https://arxiv.org/pdf/{paper['id']}.pdf"
                        urllib.request.urlretrieve(pdf_url, file_path)
                        time.sleep(4) 
                    except Exception as e:
                        print(f"Failed {paper['id']}: {e}")
                        time.sleep(10) 
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    parse_and_download()