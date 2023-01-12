from bs4 import BeautifulSoup
import urllib3
from multiprocessing import Pool


def parse_recipes(seed) -> None:
    counter = 0
    http = urllib3.PoolManager()
    url = 'https://1000.menu/cooking/'
    with open("data/recipes.txt", "a", encoding="utf-8") as f:
        response = http.request('GET', url + str(seed))
        soup = BeautifulSoup(response.data)
        steps = soup.find_all(
            'p', {"class": "instruction"})
        if (len(steps) > 0):
            steps = list(map(lambda step: step.text, steps))
            format = f"[START] {'\n'.join(steps)} [END]\n"
            f.write(format)
            counter += 1


def mp_parsing(parse_func: function, seed_range: range, p_count: int) -> None:
    with Pool(p_count) as p:
        p.map(parse_func, seed_range)


if __name__ == '__main__':
    start_index = 10000
    end_index = 11000
    number_of_processes = 16
    mp_parsing(parse_recipes, range(
        start_index, end_index), number_of_processes)
