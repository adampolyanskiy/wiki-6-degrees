import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from urllib.request import urlopen

import numpy as np
from bs4 import BeautifulSoup

# Так как urlopen при вызове открывает каждый раз отдельной соединение
# то rate_limit я интерперитурую как количество потоков, которое
# "параллельно" делает запросы и получает ссылки в теле статьи на другие статьи
# программа будет работать, пока каждый поток не найдет первую попавшуюся цепчоку из ссылок
# решение не будет оптимальным
# ведущих от from_url -> to_url

wiki_url = "https://en.wikipedia.org"

def main():
    argv = sys.argv[1:]

    if (len(argv) > 2):
        from_url = argv[0]
        to_url = argv[1]

    if (len(argv) >= 3):
        rate_limit = int(argv[2])
    else:
        rate_limit = 3

    # from_url = "https://en.wikipedia.org/wiki/Six_degrees_of_separation"
    # to_url = "https://en.wikipedia.org/wiki/American_Broadcasting_Company"

    links = list(getArticleLinks(from_url))

    splitted_links = np.array_split(links, rate_limit)
    
    args = [[from_url, to_url, 3, [], chunk] for chunk in splitted_links]

    with ThreadPoolExecutor() as executor:
        executor.map(lambda args: searchLink(*args), args)

            
def searchLink(current, dest, depth, path = [], links = []):
    if (depth == 0):
        return

    path.append(current)
    
    links = list(getArticleLinks(current)) if links == [] else links

    for link in links:
        if link == dest:
            path.append(link)
            print(" => ".join([p.split("/wiki/")[1] for p in path]))
            raise Exception("Found")
        elif (link not in path):
            searchLink(link, dest, depth - 1, path.copy())

def getArticleLinks(url):
    html = urlopen(url)
    bs = BeautifulSoup(html, 'html.parser')
    links = (wiki_url + link["href"] for link in bs.select('#bodyContent a[href^="/wiki/"]'))
    return links

if __name__ == "__main__":
    main()