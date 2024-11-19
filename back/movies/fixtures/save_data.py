from django.conf import settings
import requests
import os
import django
import sys
import json

'''
- 프로젝트 루트 경로에 있는 상태에서 실행해야 db.json 파일 생성 시 경로를 찾아갈 수 있음
- settings.py를 찾지 못하는 문제로 인해 경로 지정 
- 에러 확인을 위해 json 파일을 분리하여 데이터를 저장했으며 최종적으로 로드하여 사용하는 파일은 db.json

python manage.py loaddata db.json 
'''
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()  

API_KEY = settings.TMDB_API_KEY
base_url = 'https://api.themoviedb.org/3/'
genre_db = []
actor_db = []
director_db = []
provider_db = []
movie_db = []
video_db = []

# JSON 파일 생성 ----------------------------------------------------------------------------------------------------------
def save_to_json(data, filename):
    # JSON 파일 경로 설정
    json_file_path = os.path.join(os.path.dirname(__file__), f'{filename}.json')   
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)  


# API 요청 ----------------------------------------------------------------------------------------------------------------
def save_data():

    # 배급사
    provider_url = 'watch/providers/movie'
    params = {
        'language':'ko-KR',
        'api_key':API_KEY
    }
    providers = requests.get(base_url+provider_url, params=params).json()

    for provider in providers['results']:
        data = {
            "model": "movies.provider",
            "pk": provider.get('provider_id'),
            "fields": {
                "name": provider.get('provider_name'),
                "logo_path": provider.get('logo_path')
            }
        }
        provider_db.append(data)
    #--------------------------------------------------------------------------- 배급사 DB 완성 ------------------
    # 장르 
    genre_url = 'genre/movie/list'
    params = {
        'language':'ko-KR',
        'api_key':API_KEY
    }
    genres = requests.get(base_url+genre_url, params=params).json()

    for genre in genres['genres']:
        data = {
            "model": "movies.genre",
            "pk": genre.get('id'),
            "fields": {
                "name": genre.get('name')
            }
        }
        genre_db.append(data)
    
    #--------------------------------------------------------------------------- 장르 DB 완성 --------------------
    
    # 영화 리스트 조회 + 영화 디테일 + 배우 + 감독 + 배급사 + 장르 
    movie_list_url = 'movie/popular'

    for i in range(1, 71):
        movie_list_params = {
            'language':'ko-KR',
            'region': 'KR',
            'page': i,
            'api_key':API_KEY
        }

        # 영화 전체 조회
        movies = requests.get(base_url+movie_list_url, params=movie_list_params).json()

        for movie in movies['results']:
            id = movie.get('id')
            title = movie.get('title')
            original_title = movie.get('original_title')
            overview = movie.get('overview')
            release_date = movie.get('release_date')
            popularity = movie.get('popularity')
            poster_path = movie.get('poster_path')
            backdrop_path = movie.get('backdrop_path')

            # 전체 영화 리스트 조회 시 각 영화의 필수 필드 데이터 존재 여부 확인
            if not all([id, title, original_title, overview, release_date, popularity, poster_path, backdrop_path]):
                print('영화 전체 조회 : movie 데이터 없음')
                continue

            # 전체 영화 리스트 조회 시 각 영화의 장르 데이터 저장
            genres = []
            for genre_id in movie.get('genre_ids'):
                genres.append(genre_id)
            
            # 장르 데이터 존재 여부 확인
            if genres == []:
                print('영화 전체 조회 : genre 데이터 없음')
                continue
            #---------------------------------------------------------------------------------------------------
            # 각 영화의 상세 정보를 API를 통해 한번 더 조회 [1] : 상영시간, 태그라인, 국가
            movie_detail_url = 'movie/' + str(id)
            movie_detail_params = {
                'language':'ko-KR',
                'api_key':API_KEY
            }
            movie_detail = requests.get(base_url+movie_detail_url, params=movie_detail_params).json()

            runtime = movie_detail.get('runtime')
            tagline = movie_detail.get('tagline', '')

            # 각 영화의 상세 정보 중 필수 필드 데이터 존재 여부 확인
            if not all([runtime, tagline]):
                print('영화 상세 조회 : runtime, tagline 데이터 없음')
                continue

            countries = []
            
            for country in movie_detail.get('origin_country'):
                if country == 'US':
                    countries.append(1)
                elif country == 'KR':
                    countries.append(2)
                elif country == 'GB':
                    countries.append(3)
                elif country == 'JP':
                    countries.append(4)
                elif country == 'CN':
                    countries.append(5)
                elif country == 'FR':
                    countries.append(6)
                else:
                    countries.append(7)
            
            # 장르 데이터 존재 여부 확인
            if countries == []:
                print('영화 전체 조회 : countries 데이터 없음')
                continue
            else:
                countries = list(set(countries))

            # 각 영화의 상세 정보를 API를 통해 한번 더 조회 [2] : 배우 및 감독
            credit_url = 'movie/' + str(id) + '/credits'
            credit_params = {
                'language':'ko-KR',
                'api_key':API_KEY
            }
            credits = requests.get(base_url+credit_url, params=credit_params).json()
            
            actors = []
            for credit in credits['cast'][:5]:
                if credit.get('known_for_department') == 'Acting':
                    actor_id = credit.get('id')
                    actor_name = credit.get('name')
                    actor_popularity = credit.get('popularity')
                    actor_profile_path = credit.get('profile_path')

                    # 배우 데이터 존재 여부 확인
                    if not all([actor_id, actor_name, actor_popularity, actor_profile_path]):
                        print('영화 상세 조회 : actors 데이터 없음')
                        continue

                    actors.append(actor_id)
                    data = {
                        "model": "movies.actor",
                        "pk": actor_id,
                        "fields": {
                            "name": actor_name,
                            "popularity": actor_popularity,
                            'profile_path': actor_profile_path
                        }
                    }
                    actor_db.append(data)
            
            directors = []
            for credit in credits['crew']:
                if credit.get('job') == 'Director':
                    director_id = credit.get('id')
                    director_name = credit.get('name')
                    director_profile_path = credit.get('profile_path')

                    # 감독 데이터 존재 여부 확인
                    if not all([director_id, director_name, director_profile_path]):
                        print('영화 상세 조회 : directors 데이터 없음')
                        continue

                    directors.append(director_id)
                    data = {
                        "model": "movies.director",
                        "pk": director_id,
                        "fields": {
                            "name": director_name,
                            'profile_path': director_profile_path
                        }
                    }
                    director_db.append(data)
            
            #---------------------------------------------------------------------------------------------------
            # 각 영화의 상세 정보를 API를 통해 한번 더 조회 [3] : 개별 영화의 배급사 조회 
            provider_for_movie_url = 'movie/' + str(id) + '/watch/providers'
            providers_for_movie_list = []
            provider_for_movie_params = {
                'api_key':API_KEY
            }
            providers_for_movie = requests.get(base_url+provider_for_movie_url, params=provider_for_movie_params).json()
            if providers_for_movie == []:
                print('영화 상세 조회 : 배급사 데이터 없음')
                continue

            if "KR" in providers_for_movie['results']:
                if "flatrate" in providers_for_movie['results'].get('KR'):
                    for provider in providers_for_movie['results'].get('KR').get('flatrate'):
                        providers_for_movie_list.append(provider.get('provider_id'))
                else:
                    continue
            else:
                continue

            # 개별 영화의 관련 영상 조회
            video_url = 'movie/' + str(id) + '/videos'
            video_params = {
                'language': 'ko-KR',
                'api_key': API_KEY
            }
            videos = requests.get(base_url + video_url, params=video_params).json()

            # 비디오 데이터 존재 여부 확인
            if videos['results'] == []:
                print(f"비디오 데이터 없음: {title} (ID: {id})")
                continue

            # JSON 파일 생성 전 영화 데이터 존재 여부 확인 (비디오 데이터 조건 포함)
            if all([id, title, original_title, overview, release_date, popularity, poster_path, backdrop_path, runtime, genres, actors, directors, providers_for_movie_list, countries]):
                # 영화 데이터를 한 번만 저장
                movie_data = {
                    "model": "movies.movie",
                    "pk": id,
                    "fields": {
                        "title": title,
                        "original_title": original_title,
                        "overview": overview,
                        "release_date": release_date,
                        "popularity": popularity,
                        "poster_path": poster_path,
                        "backdrop_path": backdrop_path,
                        "runtime": runtime,
                        "tagline": tagline,
                        "genres": genres,
                        "actors": actors,
                        "directors": directors,
                        "providers": providers_for_movie_list,
                        "countries": countries
                    }
                }
                movie_db.append(movie_data)  # 영화 데이터 저장

                # 비디오 데이터 반복 저장 (외래키 관련 에러를 피하기 위해 영화가 저장된 이후에 저장해야 함)
                for video in videos['results']:
                    video_id = video.get('id')
                    video_movie_id = id
                    key = video.get('key')

                    if not all([video_id, video_movie_id, key]):
                        print(f"비디오 데이터 유효하지 않음: {title} (Video ID: {video_id})")
                        continue

                    # 영화 데이터가 저장된 이후 비디오 데이터 저장
                    video_data = {
                        "model": "movies.video",
                        "pk": video_id,
                        "fields": {
                            "movie": video_movie_id,
                            "key": key
                        }
                    }
                    video_db.append(video_data)  # 비디오 데이터 저장
            else:
                print('영화 데이터 저장 조건 불만족')
                continue



            
            
            

    save_to_json(genre_db, 'genre_db')
    save_to_json(actor_db, 'actor_db')
    save_to_json(director_db, 'director_db')
    save_to_json(provider_db, 'provider_db')
    save_to_json(movie_db, 'movie_db')
    save_to_json(video_db, 'video_db')

save_data()


# 파일 경로 설정
fixture_dir = os.path.abspath('back/movies/fixtures/')

# 파일 목록
files = [
    'actor_db.json',
    'director_db.json',
    'genre_db.json',
    'movie_db.json',
    'provider_db.json',
    'video_db.json',
    'country_db.json'
]

# 모든 데이터를 담을 리스트
combined_data = []

# 각 JSON 파일 읽어서 데이터를 하나로 합치기
for file in files:
    file_path = os.path.join(fixture_dir, file)
    
    # 파일이 존재하는지 확인
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            combined_data.extend(data)  # 파일에서 읽은 데이터를 리스트에 추가

# 합쳐진 데이터를 새로운 JSON 파일로 저장
combined_file_path = os.path.join(fixture_dir, 'db.json')
with open(combined_file_path, 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, ensure_ascii=False, indent=4)

print(f"파일이 성공적으로 합쳐졌습니다: {combined_file_path}")