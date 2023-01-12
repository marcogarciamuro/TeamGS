from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from soccer.models import Team, Player, TeamArticle, League, LeagueArticle
from soccer.forms import TeamSearch
import http.client
import json
from datetime import datetime, date, timedelta
import environ
import re
from dal import autocomplete
from django.utils.html import format_html
from django.utils import timezone
from unidecode import unidecode

env = environ.Env()
environ.Env.read_env()

cur_date = date.today()
cur_datetime = timezone.now()
# cur_season = (cur_date - timedelta(days=365)).year
cur_season = 2022
PREMIER_LEAGUE_ID = 39
LA_LIGA_ID = 140
SERIE_A_ID = 135
BUNDESLIGA_ID = 78
LIGUE_1_ID = 61

LEAGUES = [
    {
        "name": 'La Liga',
        "formatted_name": 'la%20liga',
        "id": LA_LIGA_ID
    },
    {
        "name": 'Premier League',
        "formatted_name": 'premier%20league',
        "id": PREMIER_LEAGUE_ID
    },
    {
        "name": "Serie A",
        "formatted_name": 'serie%20a',
        "id": SERIE_A_ID
    },
    {
        "name": "Bundesliga",
        "formatted_name": 'bundesliga',
        "id": BUNDESLIGA_ID
    },
    {
        "name": "Ligue 1",
        "formatted_name": 'ligue%201',
        "id": LIGUE_1_ID
    },
]

SOCCER_API_HEADERS = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': env("SOCCER_API_KEY")
}

NEWS_API_HEADERS = {
    'User-agent': 'Mozilla/5.0'
}

COUNTRIES = [
    'AFGHANISTAN', 'ALAND ISLANDS', 'ALBANIA', 'ALGERIA', 'AMERICAN SAMOA', 'ANDORRA', 'ANGOLA', 'ANGUILLA', 'ANTARCTICA', 'ANTIGUA AND BARBUDA', 'ARGENTINA', 'ARMENIA', 'ARUBA', 'AUSTRALIA', 'AUSTRIA', 'AZERBAIJAN', 'BAHAMAS', 'BAHRAIN', 'BANGLADESH', 'BARBADOS', 'BELARUS', 'BELGIUM', 'BELIZE', 'BENIN', 'BERMUDA', 'BHUTAN', 'BOLIVIA, PLURINATIONAL STATE OF', 'BONAIRE, SINT EUSTATIUS AND SABA', 'BOSNIA AND HERZEGOVINA', 'BOTSWANA', 'BOUVET ISLAND', 'BRAZIL', 'BRITISH INDIAN OCEAN TERRITORY', 'BRUNEI DARUSSALAM', 'BULGARIA', 'BURKINA FASO', 'BURUNDI', 'CAMBODIA', 'CAMEROON', 'CANADA', 'CAPE VERDE', 'CAYMAN ISLANDS', 'CENTRAL AFRICAN REPUBLIC', 'CHAD', 'CHILE', 'CHINA', 'CHRISTMAS ISLAND', 'COCOS (KEELING) ISLANDS', 'COLOMBIA', 'COMOROS', 'CONGO', 'CONGO, THE DEMOCRATIC REPUBLIC OF THE', 'COOK ISLANDS', 'COSTA RICA', "CÔTE D'IVOIRE", 'CROATIA', 'CUBA', 'CURAÇAO', 'CYPRUS', 'CZECH REPUBLIC', 'DENMARK', 'DJIBOUTI', 'DOMINICA', 'DOMINICAN REPUBLIC', 'ECUADOR', 'EGYPT', 'EL SALVADOR', 'EQUATORIAL GUINEA', 'ERITREA', 'ESTONIA', 'ETHIOPIA', 'FALKLAND ISLANDS (MALVINAS)', 'FAROE ISLANDS', 'FIJI', 'FINLAND', 'FRANCE', 'FRENCH GUIANA', 'FRENCH POLYNESIA', 'FRENCH SOUTHERN TERRITORIES', 'GABON', 'GAMBIA', 'GEORGIA', 'GERMANY', 'GHANA', 'GIBRALTAR', 'GREECE', 'GREENLAND', 'GRENADA', 'GUADELOUPE', 'GUAM', 'GUATEMALA', 'GUERNSEY', 'GUINEA', 'GUINEA-BISSAU', 'GUYANA', 'HAITI', 'HEARD ISLAND AND MCDONALD ISLANDS', 'HOLY SEE (VATICAN CITY STATE)', 'HONDURAS', 'HONG KONG', 'HUNGARY', 'ICELAND', 'INDIA', 'INDONESIA', 'IRAN, ISLAMIC REPUBLIC OF', 'IRAQ', 'IRELAND', 'ISLE OF MAN', 'ISRAEL', 'ITALY', 'JAMAICA', 'JAPAN', 'JERSEY', 'JORDAN', 'KAZAKHSTAN', 'KENYA', 'KIRIBATI', "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF", 'KOREA, REPUBLIC OF', 'KUWAIT', 'KYRGYZSTAN', "LAO PEOPLE'S DEMOCRATIC REPUBLIC", 'LATVIA', 'LEBANON', 'LESOTHO', 'LIBERIA', 'LIBYA', 'LIECHTENSTEIN', 'LITHUANIA', 'LUXEMBOURG', 'MACAO', 'MACEDONIA, REPUBLIC OF', 'MADAGASCAR', 'MALAWI', 'MALAYSIA', 'MALDIVES', 'MALI', 'MALTA', 'MARSHALL ISLANDS', 'MARTINIQUE', 'MAURITANIA', 'MAURITIUS', 'MAYOTTE', 'MEXICO', 'MICRONESIA, FEDERATED STATES OF', 'MOLDOVA, REPUBLIC OF', 'MONACO', 'MONGOLIA', 'MONTENEGRO', 'MONTSERRAT', 'MOROCCO', 'MOZAMBIQUE', 'MYANMAR', 'NAMIBIA', 'NAURU', 'NEPAL', 'NETHERLANDS', 'NEW CALEDONIA', 'NEW ZEALAND', 'NICARAGUA', 'NIGER', 'NIGERIA', 'NIUE', 'NORFOLK ISLAND', 'NORTHERN MARIANA ISLANDS', 'NORWAY', 'OMAN', 'PAKISTAN', 'PALAU', 'PALESTINIAN TERRITORY, OCCUPIED', 'PANAMA', 'PAPUA NEW GUINEA', 'PARAGUAY', 'PERU', 'PHILIPPINES', 'PITCAIRN', 'POLAND', 'PORTUGAL', 'PUERTO RICO', 'QATAR', 'RÉUNION', 'ROMANIA', 'RUSSIAN FEDERATION', 'RWANDA', 'SAINT BARTHÉLEMY', 'SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA', 'SAINT KITTS AND NEVIS', 'SAINT LUCIA', 'SAINT MARTIN (FRENCH PART)', 'SAINT PIERRE AND MIQUELON', 'SAINT VINCENT AND THE GRENADINES', 'SAMOA', 'SAN MARINO', 'SAO TOME AND PRINCIPE', 'SAUDI ARABIA', 'SENEGAL', 'SERBIA', 'SEYCHELLES', 'SIERRA LEONE', 'SINGAPORE', 'SINT MAARTEN (DUTCH PART)', 'SLOVAKIA', 'SLOVENIA', 'SOLOMON ISLANDS', 'SOMALIA', 'SOUTH AFRICA', 'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS', 'SPAIN', 'SRI LANKA', 'SUDAN', 'SURINAME', 'SOUTH SUDAN', 'SVALBARD AND JAN MAYEN', 'SWAZILAND', 'SWEDEN', 'SWITZERLAND', 'SYRIAN ARAB REPUBLIC', 'TAIWAN, PROVINCE OF CHINA', 'TAJIKISTAN', 'TANZANIA, UNITED REPUBLIC OF', 'THAILAND', 'TIMOR-LESTE', 'TOGO', 'TOKELAU', 'TONGA', 'TRINIDAD AND TOBAGO', 'TUNISIA', 'TURKEY', 'TURKMENISTAN', 'TURKS AND CAICOS ISLANDS', 'TUVALU', 'UGANDA', 'UKRAINE', 'UNITED ARAB EMIRATES', 'UNITED KINGDOM', 'UNITED STATES', 'UNITED STATES MINOR OUTLYING ISLANDS', 'URUGUAY', 'UZBEKISTAN', 'VANUATU', 'VENEZUELA, BOLIVARIAN REPUBLIC OF', 'VIETNAM', 'VIRGIN ISLANDS, BRITISH', 'VIRGIN ISLANDS', 'USA', 'WALLIS AND FUTUNA', 'YEMEN', 'ZAMBIA', 'ZIMBABWE'
]

# Create your views here.


class team_autocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Team.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def get_result_label(self, item):
        print(item)
        return format_html('<span><img src="{}" width="20px" height="20px"> {}</span>', item.logo, item.name)

    def get_selected_result_label(self, item):
        return format_html('{}', item.name)


def index(request):
    search_form = TeamSearch()
    articles = get_league_articles()
    page_data = {
        "articles": articles,
        "search_form": search_form,
    }
    return render(request, 'soccer/index.html', page_data)


def team_not_found(request):
    return render(request, "soccer/team_not_found.html")


def call_api(endpoint):
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
    conn.request("GET", endpoint, headers=SOCCER_API_HEADERS)
    res = conn.getresponse()
    data = res.read()
    json_dict = json.loads(data)
    results = json_dict['results']
    if results == 0:
        return None
    return json_dict['response']


def get_player_details(player_id):
    endpoint = "/v3/players?id=" + \
        str(player_id) + "&season=" + str(cur_season)
    print(endpoint)
    payload = call_api(endpoint)
    if payload is None:
        return None

    nationality = payload[0]['player']['nationality']
    short_name = payload[0]['player']['name']
    print(short_name)
    firstname = payload[0]['player']['firstname']
    lastname = payload[0]['player']['lastname']

    player_weight = payload[0]['player']['weight']
    if player_weight:
        weight_kgs = int(payload[0]['player']['weight'].split()[0])
        weight_pounds = round(weight_kgs * 2.205)
    else:
        weight_pounds = None

    player_height = payload[0]['player']['height']
    if player_height:
        height_cms = int(payload[0]['player']['height'].split()[0])
        height_ft = int(height_cms / 30.48)
        height_in = round(
            float('0.' + str(height_cms/30.48).split('.')[-1]) * 12)
    else:
        height_ft = None
        height_in = None

    player_details = {
        'short_name': short_name,
        'firstname': firstname,
        'lastname': lastname,
        'nationality': nationality,
        'weight': weight_pounds,
        'height_ft': height_ft,
        'height_in': height_in
    }
    return player_details


def shorten_player_position(position):
    if position == "Attacker":
        return 'F'
    elif position == "Defender":
        return 'D'
    elif position == "Goalkeeper":
        return 'GK'
    elif position == "Midfielder":
        return 'M'


def get_player_best_name(general_name, short_name, firstname, lastname):
    if general_name.count(' ') > 1 or '.' in general_name:
        # Don't use general name
        if '.' in short_name:
            print("There is a period in: " + short_name)
            lastname = ' '.join(short_name.split('. ')[1:])
            firstname = firstname.split()[0]
            best_name = firstname + ' ' + lastname

        elif short_name.count(' ') > 1:
            # Don't use short name
            best_name = firstname.split()[0] + ' ' + lastname
        else:
            # Use short name
            best_name = short_name
    else:
        #  Use general name
        best_name = general_name
    return best_name


def get_players(team_obj):
    print("GETTING PLAYERS")
    if Player.objects.filter(team=team_obj).exists():
        players = Player.objects.filter(team=team_obj)
        print("FOUND CACHED PLAYERS")
        return players
    else:
        print("NO CACHED PLAYERS, FETCHING FROM API")
        team_id = team_obj.teamID
        team_players_endpoint = '/v3/players/squads?team=' + str(team_id)
        team_squad = call_api(team_players_endpoint)
        if team_squad is None:
            return None
        player_list = team_squad[0]['players']
        for player_item in player_list:
            if not player_item['number']:
                continue
            position = shorten_player_position(player_item['position'])
            print("CURRENT PLAYER ID:", player_item['id'])
            player_details = get_player_details(player_item['id'])
            print("CURRENT PLAYER DETAILS:", player_details)
            player_name = get_player_best_name(
                player_item['name'],
                player_details['short_name'],
                player_details['firstname'],
                player_details['lastname']
            )
            Player.objects.create(
                player_id=player_item['id'],
                name=player_name,
                age=player_item['age'],
                team=team_obj,
                jersey_number=player_item['number'],
                position=position,
                photo=player_item['photo'],
                nationality=player_details['nationality'],
                height_feet=player_details['height_ft'],
                height_inches=player_details['height_in'],
                weight=player_details['weight'],
            )
        players = Player.objects.filter(team=team_obj)
        return players

# retrieves team ID based on team search to send to template to render widget with team's matches


def get_team(team_name):
    print("Looking for team name" + team_name)
    try:
        team = Team.objects.get(name__icontains=team_name)
    except:
        if team_name.upper() in COUNTRIES:
            endpoint = '/v3/teams?name=' + team_name.replace(" ", "%20")
        else:
            endpoint = "/v3/teams?search=" + team_name.replace(" ", "%20")
        team_results = call_api(endpoint)
        if not team_results:
            return None
        team_info = team_results[0]['team']
        team_name = team_info['name']
        team_id = team_info['id']
        team_logo = team_info['logo']
        league = get_league(team_id)
        team_details = {
            "team_name": team_name,
            "team_id": team_id,
            "league": league,
            "logo": team_logo
        }
        create_team(team_details)
        team = Team.objects.get(teamID=team_id)
    return team


def team_page(request, team_name=None):
    search_form = TeamSearch()
    user_is_signed_in = not request.user.is_anonymous
    if(request.method == "POST"):
        print("IN TEAM PAGE VIEW")
        search_form = TeamSearch(request.POST)
        if(search_form.is_valid()):  # process form data which is the searched team name
            team_search = search_form.cleaned_data["team_query"]
            team = get_team(team_search)
            if team is None:
                team_not_found_url = "/soccer/team-not-found?team=" + \
                    team_search.replace(" ", "+")
                return HttpResponseRedirect(team_not_found_url)

            team_page = "/soccer/team-page/" + team.name.replace(" ", "-")
            return HttpResponseRedirect(team_page)
    else:
        team_name_formatted = team_name
        if(team_name == 'U.N.A.M.---Pumas'):
            team_name = 'U.N.A.M. - Pumas'
        else:
            team_name = team_name.replace("-", " ")

        team = get_team(team_name)
        league_id = get_league(team.teamID).league_id
        print("TEAM LEAGUE ID", league_id)
        print("CUR SEASON: ", cur_season)
        articles = get_team_articles(team)
        players = get_players(team)

        if user_is_signed_in:
            team_is_liked = team.liked_by.filter(id=request.user.id).exists()
        else:
            team_is_liked = False

        page_data = {
            "search_form": search_form,
            "team_name_formatted": team_name_formatted,
            "team_is_liked": team_is_liked,
            "team": team,
            "players": players,
            "articles": articles,
            "league_id": league_id,
            "cur_season": cur_season,
        }
    print("FINSIHED TEAM PAGE FUNCTION")
    return render(request, 'soccer/team_page.html', page_data)


def get_league(team_id):
    if Team.objects.filter(teamID=team_id).exists():
        league = Team.objects.get(teamID=team_id).league
    else:
        endpoint = "/v3/leagues?team=" + str(team_id)
        league_results = call_api(endpoint)
        if not league_results:
            return None
        most_relavent_league = league_results[0]['league']
        league_id = most_relavent_league['id']
        league_name = most_relavent_league['name']
        league_logo = most_relavent_league['logo']

        league, created = League.objects.get_or_create(
            league_id=league_id,
            name=league_name,
        )
    return league


def create_team(team_details):
    print("Creating team")
    team_name = team_details['team_name']
    team_id = team_details['team_id']
    team_logo = team_details['logo']
    team_league = get_league(team_id)
    Team.objects.create(name=team_name, teamID=team_id,
                        league=team_league, logo=team_logo)


def call_news_api(endpoint):
    print(endpoint)
    conn = http.client.HTTPSConnection("newsapi.org")
    conn.request("GET", endpoint, headers=NEWS_API_HEADERS)
    res = conn.getresponse()
    data = res.read()
    json_dict = json.loads(data)
    if json_dict['status'] == "error":
        print("Error calling news API: " + json_dict['message'])
        return None

    results = json_dict['totalResults']
    if results == 0:
        print("NO RESULTS FOUND")
        return None
    return json_dict['articles']

# Takes articles from api response as argument and returns list of articles sorted by date


def sort_article_list(unsorted_articles):
    print("ARTICLES TO SORT:", unsorted_articles)
    final_articles = []
    for article in unsorted_articles:
        title = article["title"]
        author = article["author"]
        if author is None:
            author = ""
        description = article["description"]
        if description:
            # description = clean_html(description)
            description = re.sub('<[^<]+?>', '', description)
        else:
            description = ""
        thumbnail = article["urlToImage"]
        url = article["url"]
        publishedDate = article["publishedAt"]
        second = int(publishedDate[17:19])
        minute = int(publishedDate[14:16])
        hour = int(publishedDate[11:13])
        day = int(publishedDate[8:10])
        month = int(publishedDate[5:7])
        year = int(publishedDate[0:4])
        dateObj = datetime(year, month, day, hour, minute, second)

        final_articles.append({
            "date": dateObj,
            "title": title,
            "author": author,
            "description": description,
            "thumbnail": thumbnail,
            "url": url
        })

    final_articles.sort(key=lambda x: x['date'])
    return final_articles


def create_and_get_team_article_short_list(article_item_list, num_articles, team):
    REUTERS_DEFAULT_PICS = [
        'https://s1.reutersmedia.net/resources_v2/images/rcom-default.png?w=800',
        'https://www.reuters.com/pf/resources/images/reuters/reuters-default.png?d=124'
    ]
    article_obj_list = []
    for article in article_item_list:
        if len(article_obj_list) == num_articles:
            break
        title = article["title"]
        author = article["author"]
        if author is None:
            author = ""
        description = article["description"]
        thumbnail = article["thumbnail"]
        if thumbnail is None or thumbnail in REUTERS_DEFAULT_PICS:
            continue
        url = article["url"]
        if not TeamArticle.objects.filter(title=title).exists():
            TeamArticle.objects.create(
                team=team,
                title=title,
                author=author,
                thumbnail=thumbnail,
                description=description,
                url=url
            )
            article_obj = TeamArticle.objects.get(title=title)
            article_obj_list.append(article_obj)
    print("newly created articles: ", article_obj_list)
    return reversed(article_obj_list)


def create_and_get_league_article_short_list(article_item_list, num_articles, league):
    REUTERS_DEFAULT_PICS = [
        'https://s1.reutersmedia.net/resources_v2/images/rcom-default.png?w=800',
        'https://www.reuters.com/pf/resources/images/reuters/reuters-default.png?d=124'
    ]
    article_obj_list = []
    for article in article_item_list:
        if len(article_obj_list) == num_articles:
            break
        title = article["title"]
        author = article["author"]
        if author is None:
            author = ""
        description = article["description"]
        thumbnail = article["thumbnail"]
        if thumbnail is None or thumbnail in REUTERS_DEFAULT_PICS:
            continue
        url = article["url"]
        if not LeagueArticle.objects.filter(title=title).exists():
            LeagueArticle.objects.create(
                league=league,
                title=title,
                author=author,
                thumbnail=thumbnail,
                description=description,
                url=url
            )
            article_obj = LeagueArticle.objects.get(title=title)
            article_obj_list.append(article_obj)
    # print("newly created articles: ", article_obj_list)
    return reversed(article_obj_list)


def get_team_articles_from_api(team):
    print("GETTING ARTICLES FROM API")
    KEY = str(env("NEWS_API_KEY"))
    ARTICLE_API_Q_CHAR_LIMIT = 500
    JOINING_CHAR_COUNT = 6
    NUM_ARTICLES = 6
    players = get_players(team)
    team_nickname = team.name.split()[-1]
    if team.name.upper() in COUNTRIES:
        q = '"' + team.name + ' soccer'
    else:
        # q = '"' + team.name + '" OR "' + team_nickname + '"'
        q = f'+"{team.name}"'
    # for player in players:
    #     if len(q) + len(unidecode(player.name)) + JOINING_CHAR_COUNT <= ARTICLE_API_Q_CHAR_LIMIT:
    #         q += ' OR "' + unidecode(player.name) + '"'
    #     else:
    #         break
    q = q.replace(' ', '%20')
    # endpoint = "/v2/everything?sortBy=publishedAt&language=en&q=" + q + \
    #     "&apiKey=" + KEY
    endpoint = "/v2/everything?sortBy=publishedAt&language=en&searchIn=title&q=" + q + \
        "&apiKey=" + KEY
    print(endpoint)
    api_articles_results = call_news_api(endpoint)
    sorted_articles = sort_article_list(api_articles_results)
    article_obj_list = create_and_get_team_article_short_list(
        sorted_articles, NUM_ARTICLES, team)
    return article_obj_list


def get_league_articles_from_api(league_obj):
    KEY = str(env("NEWS_API_KEY"))
    NUM_ARTICLES = 1
    formatted_league_name = league_obj.name.replace(' ', '%20')
    endpoint = '/v2/everything?sortBy=publishedAt&language=en&q=' + \
        f'+"{formatted_league_name}"' + \
        '&apiKey=' + KEY + '&sortBy=publishedAt'
    api_article_results = call_news_api(endpoint)
    sorted_articles = sort_article_list(api_article_results)
    article_obj_list = create_and_get_league_article_short_list(
        sorted_articles, NUM_ARTICLES, league_obj)
    return article_obj_list


def get_team_articles(team):
    one_day_ago = timezone.now() - timedelta(days=1)
    cached_articles = TeamArticle.objects.filter(
        team=team).order_by('-retrieval_date')
    if cached_articles.exists():
        print("FOUND CACHED ARTICLES")
        if cached_articles[0].retrieval_date <= one_day_ago:
            print("last created article is outdated, fetching new ones")
            articles = get_team_articles_from_api(team)
        else:
            print("Serving CACHED ARTICLES")
            articles = cached_articles[:5]
    else:
        # No team articles exist, fetch some
        articles = get_team_articles_from_api(team)
    return articles


def get_league_articles():
    one_day_ago = timezone.now() - timedelta(days=1)
    LEAGUE_IDS = [PREMIER_LEAGUE_ID, LA_LIGA_ID,
                  SERIE_A_ID, BUNDESLIGA_ID, LIGUE_1_ID]
    cached_articles = LeagueArticle.objects.filter().order_by('-retrieval_date')

    if not cached_articles.exists():
        articles = []
        for league in LEAGUES:
            league_obj, created = League.objects.get_or_create(
                league_id=league['id'],
                name=league['name'],
            )
            articles += get_league_articles_from_api(league_obj)

    else:
        print("FOUND CACHED ARTICLES")
        if cached_articles[0].retrieval_date <= one_day_ago:
            print("last created article is outdated, fetching new ones")
            articles = []
            for league in LEAGUES:
                print("GETTING ARTICLES FOR LEAGUE: ", league['id'])
                league_obj, created = League.objects.get_or_create(
                    league_id=league['id'],
                    name=league['name'],
                )
                articles += get_league_articles_from_api(league_obj)
        else:
            print("Serving CACHED ARTICLES")
            premier_league_obj = League.objects.get(
                league_id=PREMIER_LEAGUE_ID)
            la_liga_obj = League.objects.get(league_id=LA_LIGA_ID)
            serie_a_obj = League.objects.get(league_id=SERIE_A_ID)
            bundesliga_obj = League.objects.get(league_id=BUNDESLIGA_ID)
            ligue_1_obj = League.objects.get(league_id=LIGUE_1_ID)

            cached_premier_league_article = LeagueArticle.objects.filter(
                league=premier_league_obj).order_by('-retrieval_date')[:1]
            cached_la_liga_article = LeagueArticle.objects.filter(
                league=la_liga_obj).order_by('-retrieval_date')[:1]
            cached_serie_a_article = LeagueArticle.objects.filter(
                league=serie_a_obj).order_by('-retrieval_date')[:1]
            cached_bundesliga_article = LeagueArticle.objects.filter(
                league=bundesliga_obj).order_by('-retrieval_date')[:1]
            cached_ligue_1_article = LeagueArticle.objects.filter(
                league=ligue_1_obj).order_by('-retrieval_date')[:1]
            articles = list(cached_premier_league_article) + list(cached_la_liga_article) + \
                list(cached_serie_a_article) + \
                list(cached_bundesliga_article) + list(cached_ligue_1_article)
    return articles


def upcoming_matches(request, team_id):
    page_data = {
        "team_id": team_id
    }
    return render(request, "soccer/upcoming_matches.html", page_data)


def toggle_team_like(request):
    liked = request.GET.get('liked', False) == 'true'
    team_id = request.GET.get('teamID', False)
    team = Team.objects.get(teamID=team_id)
    try:
        if liked:
            team.liked_by.remove(request.user)
            team.save()
            return JsonResponse({
                "success": True,
                "team_is_now_liked": False
            })
        else:
            team.liked_by.add(request.user)
            team.save()
            return JsonResponse({
                "success": True,
                "team_is_now_liked": True
            })
    except Exception as e:
        return JsonResponse({
            "success": False,
        })


def chat(request):
    return render(request, 'soccer/chat.html')


def room(request, room_name):
    page_data = {
        "room_name": room_name
    }
    return render(request, 'soccer/chat_room.html', page_data)
