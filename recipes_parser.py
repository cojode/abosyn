from bs4 import BeautifulSoup
import urllib3
from multiprocessing import Pool


def parse_recipes(offset):
    counter = 0
    http = urllib3.PoolManager()
    url = 'https://1000.menu/cooking/'
    with open("data/recipes.txt", "a", encoding="utf-8") as f:
        response = http.request('GET', url + str(offset))
        soup = BeautifulSoup(response.data)
        steps = soup.find_all(
            'p', {"class": "instruction"})
        if (len(steps) > 0):
            steps = list(map(lambda step: step.text, steps))
            format = "[START]" + "\n".join(steps) + "[END]\n"
            f.write(format)
            counter += 1
            print(offset)


if __name__ == '__main__':
    with Pool(16) as p:
        p.map(parse_recipes, range(10000, 20000))
