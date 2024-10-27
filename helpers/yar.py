from bs4 import BeautifulSoup as bs
import httpx

def scrape_btsearch(q):
    url = f"https://bitsearch.to/search?q={q.replace(' ', '+')}&sort=seeders"

    with httpx.Client() as client:
        response = client.get(url, timeout=60)

    soup = bs(response.text, "html.parser")
    results = []
    for item in soup.select('.card.search-result.my-2'):
        # Failsafe for magnet link
        magnet_link_element = item.select_one('.dl-magnet')
        if not magnet_link_element:
            continue
        magnet_link = magnet_link_element['href']

        # Failsafe for title
        title_element = item.select_one('.title a')
        title = title_element.text.strip() if title_element else "Title not found"

        # Failsafe for link
        link = title_element['href'] if title_element else "Link not found"

        # Failsafe for category
        category_element = item.select_one('.category')
        category = category_element.text.strip() if category_element else "Category not found"

        # Failsafe for size
        size_element = item.select_one('.stats img[alt="Size"]')
        size = size_element.parent.text.strip() if size_element and size_element.parent else "Size not found"

        # Failsafe for seeders
        seeders_element = item.select_one('.stats img[alt="Seeder"]')
        seeders = seeders_element.parent.text.strip() if seeders_element and seeders_element.parent else "Seeders not found"

        # Failsafe for leechers
        leechers_element = item.select_one('.stats img[alt="Leecher"]')
        leechers = leechers_element.parent.text.strip() if leechers_element and leechers_element.parent else "Leechers not found"

        # Failsafe for date
        date_element = item.select_one('.stats img[alt="Date"]')
        date = date_element.parent.text.strip() if date_element and date_element.parent else "Date not found"

        results.append({
            'title': title,
            'link': link,
            'category': category,
            'size': size,
            'seeders': seeders,
            'leechers': leechers,
            'date': date,
            'magnet_link': magnet_link
        })

        if len(results) >= 10:
            break

    return results
