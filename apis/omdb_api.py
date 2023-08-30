import requests
import pycountry


class MovieAPIConnection:
    """Movie API request class, gets movie from the API request
    and handles any errors."""
    def __init__(self):
        self._api_key = '292ab885'
        self._api_ep = f'http://www.omdbapi.com/?apikey={self._api_key}&type=movie&t='

    def get_movie_data(self, title: str, year) -> dict:
        """Gets a movie title and tries to fetch movie data from api.
        Returns a dict of extracted data, if there is an error the function
        returns a dict with "error" as key and the error as it's value"""
        try:
            data = self.get_request_from_api(title, year)
        except requests.exceptions.ConnectionError:
            return {'error': 'Connection error'}

        if 'Error' in data:
            return {'error': 'Movie not found!'}

        return {
            'name': data.get('Title'),
            'rating': data.get('imdbRating'),
            'year': int(data.get('Year')),
            'genre': data.get('Genre'),
            'img': data.get('Poster'),
            'director': data.get('Director'),
            'country': data.get('Country'),
            'alpha_2': self.get_country_alpha_2(data.get('Country')),
            'imdbID': data.get('imdbID')
        }

    def get_request_from_api(self, title: str, year):
        """Send a GET requests to API and returns response in json format"""
        url = self._api_ep + title
        if year:
            url += f"&y={year}"
        response = requests.get(url, timeout=3)
        return response.json()

    @staticmethod
    def get_country_alpha_2(country_name: str) -> str:
        """Takes countries names from api response, and returns
        the 2-letter code of the first country
        """
        if ',' in country_name:
            countries_list = country_name.split(',')
            country_name = countries_list[0].strip()
        country = pycountry.countries.search_fuzzy(country_name)
        return country[0].alpha_2
