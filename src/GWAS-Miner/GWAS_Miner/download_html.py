import os
import sys
import time
import requests
from requests_html import HTMLSession
from requests.exceptions import ConnectionError

def download_pmc_articles(pmcs, save_dir, file_format='html'):
    start_time = time.time()
    s = HTMLSession()
    headers = {'user-agent': 'Mozilla/5.0'}
	
    for id in pmcs:
        url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{id}/"
        try:
            response = s.get(url, headers=headers)
            response.raise_for_status()
        except ConnectionError as e:
            print(f"Failed to connect to {url}: {e}")
            continue

        if response.status_code == 200:
            content = response.text
            if file_format == 'html':
                filename = os.path.join(save_dir, f"{id}.html")
                with open(filename, "w", encoding='utf-8') as f:
                    f.write(content)
                print(f"Article with ID {id} downloaded and saved as HTML.")
            else:
                print(f"Invalid file format: {file_format} for article with ID {id}")
        else:
            print(f"Failed to download article with ID: {id}")

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken to download {len(pmcs)} articles: {total_time} seconds")
  
if __name__ == "__main__":
    pmcs = sys.argv[1:]
    save_dir = os.getcwd() + "/Auto-CORPus/html_files"
    download_pmc_articles(pmcs, save_dir)
