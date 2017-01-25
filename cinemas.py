import requests
from bs4 import BeautifulSoup
import time


def get_afisha_page():
    afisha_feed = 'http://www.afisha.ru/msk/schedule_cinema'
    return requests.get(afisha_feed).content


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'lxml')
    pars_divs = soup.find_all('div', {'class': 'object'})
    
    for div in pars_divs:
        title_movie = div.find('h3', {'class': 'usetags'}).a.text
        count_cinemas = len(div.find_all('td', attrs={'class': 'b-td-item'}))
        yield {'title_movie': title_movie, 'cinemas': count_cinemas}


def get_kinopoisk_page(title_movie):
    kinopoisk_url = 'https://www.kinopoisk.ru/index.php'
    payload = {'first': 'yes', 'kp_query': title_movie}
    headers = {
        'Accept-Encoding': 'UTF-8',
        'Accept-Language': 'Ru-ru',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'\
        ' (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    time.sleep(6)
    return requests.get(
        kinopoisk_url,
        params=payload,
        headers=headers,
        timeout=10
        ).content


def parse_kinopisk_page(title_movie):
    raw_html = get_kinopoisk_page(title_movie)
    soup = BeautifulSoup(raw_html, 'lxml')
    rate_movie_html = soup.find('span', {'class': 'rating_ball'})
    rate_movie = float(rate_movie_html.text) if rate_movie_html else 0
    votes_html = soup.find('span', {'class': 'ratingCount'})
    votes = int(votes_html.text.replace('\xa0', '')) if votes_html else 0
    return {'rate_movie': rate_movie, 'votes_movie': votes}


def collect_info_movies(raw_html):
    movies = list()

    for movie in parse_afisha_list(raw_html):
        rate_movie = parse_kinopisk_page(movie['title_movie'])
        movies.append({
            'title_movie': movie['title_movie'],
            'cinemas': movie['cinemas'],
            'rate_movie': rate_movie['rate_movie'],
            'votes_movie': rate_movie['votes_movie']
        })
    return movies


def output_10_movies_to_console(movies, count=10):
    best_movies = sorted(movies, key=lambda movie: movie['rate_movie'], reverse=True)

    for movie in movies[:count]:
        print('Title: {} | Rate: {} | Count votes: {} | Count cinemas: {}'.format(
            movie['title_movie'],
            movie['rate_movie'],
            movie['votes_movie'],
            movie['cinemas']
        ))


if __name__ == '__main__':
    afisha = get_afisha_page()
    movies = collect_info_movies(afisha)
    output_10_movies_to_console(movies)
