# load and saves wiki info from danbooru
import os, json
from resources import parameters
import cloudscraper
from tqdm import tqdm


wiki_filename = "wiki_info.json"

def load_wiki_info():
    try:
        with open(os.path.join(parameters.MAIN_FOLDER, "resources", wiki_filename), 'r') as f:
            wiki_info = json.load(f)
    except FileNotFoundError:
        # save an empty file
        wiki_info = {}
        save_wiki_info(wiki_info)
    return wiki_info

def save_wiki_info(wiki_info):
    with open(os.path.join(parameters.MAIN_FOLDER, "resources", wiki_filename), 'w') as f:
        json.dump(wiki_info, f)


failed_wiki_response = []
       
def get_wiki_page(tag):
    wiki_page = ""
    api_url = "https://danbooru.donmai.us/wiki_pages.json"
    USER_AGENT = "HaW Tagger"
    HTTP_HEADERS = {'User-Agent': USER_AGENT}
    
    if tag in failed_wiki_response:
        parameters.log.info(f"Skipping getting wiki page for {tag}")
        return wiki_page
    
    scraper = cloudscraper.create_scraper()
    url = f'{api_url}?search[title]={tag.replace(" ", "_")}'
    response = scraper.get(url=url, headers=HTTP_HEADERS)

    if response.status_code == 200:
        data = response.json()
        try:
            wiki_page = data[0]["body"]
            if "h4" in wiki_page and "[Expand=" in wiki_page:
                wiki_page = wiki_page[:min(wiki_page.index("h4"),wiki_page.index("[Expand="))].strip()
            elif "h4" in wiki_page:
                wiki_page = wiki_page[:wiki_page.index("h4")].strip()
            elif "[Expand=" in wiki_page:
                wiki_page = wiki_page[:wiki_page.index("[Expand=")].strip()
            else:
                wiki_page = wiki_page[:500].strip()
            return wiki_page
        except (IndexError, KeyError):
            return wiki_page
    else:
        failed_wiki_response.append(tag)
    return wiki_page

def add_wiki_info(tags, wiki_info, force_update=False):
    # add new entries to wiki_info for all tags in a list
    counter = 0
    for tag in tqdm(tags):
        if tag not in wiki_info or force_update:
            tag_wiki = get_wiki_page(tag)
            if tag_wiki:
                counter += 1
                wiki_info[tag] = tag_wiki
    parameters.log.info(f"Added {counter} new wiki entries")
    return wiki_info
        
