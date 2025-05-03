from pprint import pprint
import requests
import csv
from datetime import datetime, timedelta

url = "https://api.themoviedb.org/3/genre/movie/list?language=en"

#title for http requests.
headers = {
    "accept": "application/json", #we want some json
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8"
} #Autification, gives dostup to database

class MovieData:
    def __init__(self, pages):
        self.pages = pages
        self.data = [] #if we are asking for 10 pages, so this will have info about all films in these pages

    def getFilm(self):
        for page in range(1, self.pages + 1): #lookong for all pages. FE self.pages = 3, so it will contine 1, 2, 3
            url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&sort_by=popularity.desc&page={page}"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                self.data.extend(data["results"]) #adding all films in self.data
            else:
                print(f"Error {page}: {response.status_code}")
                break

    def getAllData(self):
        return self.data

    def getFilmByIndex(self, index):
        needed_films = []

        for indexes in index:
            if 0 <= indexes < len(self.data):
                needed_films.append(self.data[indexes])
        return needed_films

    def getFilmByPopularity(self):
        popular_film = self.data[0]
        for film in self.data:
            if film["popularity"] > popular_film["popularity"]:
                popular_film = film
            else:
                continue

        return popular_film

    def getFilmByOverview(self, keyword):
        filmList = []
        for film in self.data:
            if keyword in film["overview"]:
                filmList.append(film)

        return filmList

    def getFilmByUniqueGenres(self):
        uniqGenres = set()
        for film in self.data:
            uniqGenres.update(film["genre_ids"])

        return uniqGenres

    def deleteFilmByGenres(self, genre):
        new_data = []
        for film in self.data:
            if genre not in film["genre_ids"]:
                new_data.append(film)

        self.data = new_data

    def countFilmsGenresAndPop(self):
        genre_popular = {}

        for film in self.data:
            genres = film["genre_ids"]
            popularity = film["popularity"]

            for genre in genres:
                if genre not in genre_popular:
                    genre_popular[genre] = {"count": 0, "popularity": 0}

                genre_popular[genre]["count"] += 1
                genre_popular[genre]["popularity"] += popularity

        return genre_popular

    def groupFilmsByGenres(self):
        groupGenre = {}
        for film in self.data:
            genreFrozenset = frozenset(film["genre_ids"])

            if genreFrozenset not in groupGenre:
                groupGenre[genreFrozenset] = []

            groupGenre[genreFrozenset].append(film)

        return groupGenre

    def firstGenre22(self):
        copyData = []

        for film in self.data:
            modGenres = film["genre_ids"].copy()

            if modGenres:
                modGenres[0] = 22

            modFilm = film.copy()
            modFilm["genre_ids"] = modGenres

            copyData.append(modFilm)

        return copyData

    def createListFilm(self):
        filmList = []

        for film in self.data:
            title = film["title"]
            popularity = round(film["popularity"], 1)
            vote = round(film["vote_average"])
            releaseDate = datetime.strptime(film["release_date"], "%Y-%m-%d")

            newDate = releaseDate + timedelta(weeks=2)
            newDate = newDate + timedelta(days=60)

            filmInfo = {
                "title": title,
                "popularity":popularity,
                "vote_average": vote,
                "release_date": newDate.strftime("%Y-%m-%d")
            }

            filmList.append(filmInfo)

        sortedFilms = sorted(filmList, key=lambda x: (x["vote_average"], x["popularity"]), reverse=True)

        filePath = input("Enter the path where you want to save CSV: ")

        with open(filePath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["title", "popularity", "vote_average", "release_date"])

            writer.writeheader()

            for film in sortedFilms:
                writer.writerow(film)

        print(f"Data has been written to {filePath}")

        return sortedFilms



def main():
    test = MovieData(1)
    test.getFilm()

    while True:
        print("\nChose the option:")
        print("1 All films")
        print("2 Get films by indexes 3, 7, 11, 15, 19")
        print("3 Popular films")
        print("4 Keyword search")
        print("5 Unique genres")
        print("6 Delete films by genre")
        print("7 Count genre and popularity")
        print("8 Group films by genre")
        print("9 Copy by first genre = 22")
        print("10 Create films list with csv")
        print("0 Exit")

        choice = input("Enter number: ")

        match choice:
            case "1":
                pprint(test.getAllData())
            case "2":
                neededIndexFilm = test.getFilmByIndex([3, 7, 11, 15, 19])
                pprint(neededIndexFilm)
            case "3":
                pprint(test.getFilmByPopularity())
            case "4":
                keyword = input("Enter key word: ")
                pprint(test.getFilmByOverview(keyword))
            case "5":
                pprint(test.getFilmByUniqueGenres())
            case "6":
                genre = int(input("Enter genre to delete: "))
                test.deleteFilmByGenres(genre)
                pprint(test.getAllData())
            case "7":
                pprint(test.countFilmsGenresAndPop())
            case "8":
                pprint(test.groupFilmsByGenres())
            case "9":
                pprint(test.firstGenre22())
            case "10":
                sorted_films = test.createListFilm()
                pprint(sorted_films)
            case "0":
                print("End of program.")
                break
            case _:
                print("Error.")

main()