import requests
from bs4 import BeautifulSoup

def bing_search(query, max_results=10):
    """
    Perform a search on Bing and fetch search result titles, links, and descriptions.
    
    :param query: The search query string.
    :param max_results: The maximum number of results to fetch.
    :return: List of dictionaries containing titles, links, and descriptions.
    """
    url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    results = []

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        # Bing results typically use "li" elements with class "b_algo"
        links = soup.find_all("li", class_="b_algo")

        for link in links[:max_results]:
            title_element = link.find("a")
            description_element = link.find("p")  # Description is often in <p> tags

            if title_element:
                title = title_element.get_text()
                href = title_element["href"]
                description = description_element.get_text() if description_element else "No description available."
                results.append({"title": title, "link": href, "description": description})

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return results

def display_results(results):
    """
    Display the search results in a readable format.
    
    :param results: List of result dictionaries.
    """
    link=""
    desc=""

    if not results:
        print("No results found.")
        return

    for index, result in enumerate(results, start=1):
        print(f"Result {index}:")
        print(f"  Title: {result['title']}")
        print(f"  Link: {result['link']}")
        print(f"  Description: {result['description']}\n")
        link=result['link']
        desc=result['description']
        

    return(link,desc)


if __name__ == "__main__":
    query = "Disease caused due to Ants on Jute Crop"
    search_results = bing_search(query, max_results=1)
    [a,b]=display_results(search_results)
    print(a)
    print(b)
