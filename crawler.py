import wikipediaapi
from pyquery import PyQuery as pq
from urllib.parse import urljoin

wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='YourAppName/1.0'
)

wiki_wiki.user_agent = 'YourAppName/1.0'

def fetch_and_parse_url(url):
    try:
        response = pq(url=url)
        return response
    except Exception as e:
        print(f"An error occurred while fetching {url}: {e}")
    return None

def extract_and_store_child_links(base_url, pq_doc):
    """
    Extracts child URLs from a webpage and counts occurrences of the last part of the base URL in each child URL.

    Args:
        base_url (str): The base URL from which child URLs are extracted.
        pq_doc: PyQuery object representing the parsed webpage.

    Returns:
        list: A list of tuples containing child URLs and their keyword counts.
    """
    links = []
    keyword = base_url.split('/')[-1]
    for link in pq_doc('a[href]'):
        href = pq(link).attr('href')
        if href and not href.startswith('#'):
            absolute_url = urljoin(base_url, href)
            if absolute_url not in links:
                links.append((absolute_url, count_keyword_occurrences(absolute_url, keyword)))
    return links

def count_keyword_occurrences(url, keyword):
    """
    Counts occurrences of a keyword in a URL.

    Args:
        url (str): The URL in which occurrences of the keyword are counted.
        keyword (str): The keyword to be counted.

    Returns:
        int: Number of occurrences of the keyword in the URL.
    """
    return url.lower().count(keyword.lower())

def find_nearest_wikipedia_page(keyword):
    """
    Finds the nearest Wikipedia page URL for the entered keyword.

    Args:
        keyword (str): The keyword for which the nearest Wikipedia page is found.

    Returns:
        str: URL of the nearest Wikipedia page.
    """
    seed_page = wiki_wiki.page(keyword)
    if seed_page.exists():
        return seed_page.fullurl
    else:
        print(f"No Wikipedia page found for '{keyword}'")
    return None

title = input("Enter a Wikipedia title: ")

seed_url = find_nearest_wikipedia_page(title)

if seed_url:
    print(f"Seed URL based on '{title}': {seed_url}")

    visited_urls = []
    queue = [(seed_url, 0)]

    max_child_urls_to_crawl = 10 # Can be Customized

    while queue and len(visited_urls) < max_child_urls_to_crawl:
        url, keyword_count = max(queue, key=lambda x: x[1])
        queue.remove((url, keyword_count))
        
        pq_doc = fetch_and_parse_url(url)
        if pq_doc:
            visited_urls.append((url, keyword_count))
            child_links = extract_and_store_child_links(url, pq_doc)
            
            for child_url, child_keyword_count in child_links:
                queue.append((child_url, child_keyword_count))
    
    print("Crawling completed. Visited Child URLs are:")
    for url, keyword_count in visited_urls:
        print(f"URL: {url}")
