import requests
import re
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL strony z plikami JSON
BASE_URL = "https://wordlists-cdn.assetnote.io/data/"

def get_json_files():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print("Nie udało się pobrać strony.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    json_files = [urljoin(BASE_URL, a['href']) for a in soup.find_all('a', href=True) if a['href'].endswith('.json')]
    return json_files

def extract_download_links(json_url):
    response = requests.get(json_url)
    if response.status_code != 200:
        print(f"Nie udało się pobrać {json_url}")
        return []

    try:
        data = response.json()
        download_links = []
        for item in data.get("data", []):
            download_html = item.get("Download", "")
            match = re.search(r"href='(.*?)'", download_html)
            if match:
                download_links.append(urljoin(BASE_URL, match.group(1).replace("./", "")))
        return download_links
    except json.JSONDecodeError:
        print(f"Błąd parsowania JSON dla {json_url}")
        return []

def download_file(file_url, directory):
    local_filename = os.path.join(directory, file_url.split("/")[-1])
    os.makedirs(directory, exist_ok=True)
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Pobrano: {local_filename}")
    else:
        print(f"Nie udało się pobrać pliku: {file_url}")

if __name__ == "__main__":
    json_files = get_json_files()
    for json_file in json_files:
        print(f"Przetwarzanie: {json_file}")
        json_filename = os.path.basename(json_file).replace(".json", "")
        download_links = extract_download_links(json_file)
        print(download_links)
        for link in download_links:
            download_file(link, json_filename)
