from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from soccer.models import Team, Article
from soccer.forms import TeamSearch
from nba.models import Team as NBATeam
from django.contrib.auth.decorators import login_required
import http.client
import json
import datetime
import environ
import re

env = environ.Env()
environ.Env.read_env()

cur_date = datetime.date.today()
cur_season = cur_date.year-1

headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': env("SOCCER_API_KEY")
}

countries = [
    'AFGHANISTAN', 'ALAND ISLANDS', 'ALBANIA', 'ALGERIA', 'AMERICAN SAMOA', 'ANDORRA', 'ANGOLA', 'ANGUILLA', 'ANTARCTICA', 'ANTIGUA AND BARBUDA', 'ARGENTINA', 'ARMENIA', 'ARUBA', 'AUSTRALIA', 'AUSTRIA', 'AZERBAIJAN', 'BAHAMAS', 'BAHRAIN', 'BANGLADESH', 'BARBADOS', 'BELARUS', 'BELGIUM', 'BELIZE', 'BENIN', 'BERMUDA', 'BHUTAN', 'BOLIVIA, PLURINATIONAL STATE OF', 'BONAIRE, SINT EUSTATIUS AND SABA', 'BOSNIA AND HERZEGOVINA', 'BOTSWANA', 'BOUVET ISLAND', 'BRAZIL', 'BRITISH INDIAN OCEAN TERRITORY', 'BRUNEI DARUSSALAM', 'BULGARIA', 'BURKINA FASO', 'BURUNDI', 'CAMBODIA', 'CAMEROON', 'CANADA', 'CAPE VERDE', 'CAYMAN ISLANDS', 'CENTRAL AFRICAN REPUBLIC', 'CHAD', 'CHILE', 'CHINA', 'CHRISTMAS ISLAND', 'COCOS (KEELING) ISLANDS', 'COLOMBIA', 'COMOROS', 'CONGO', 'CONGO, THE DEMOCRATIC REPUBLIC OF THE', 'COOK ISLANDS', 'COSTA RICA', "CÔTE D'IVOIRE", 'CROATIA', 'CUBA', 'CURAÇAO', 'CYPRUS', 'CZECH REPUBLIC', 'DENMARK', 'DJIBOUTI', 'DOMINICA', 'DOMINICAN REPUBLIC', 'ECUADOR', 'EGYPT', 'EL SALVADOR', 'EQUATORIAL GUINEA', 'ERITREA', 'ESTONIA', 'ETHIOPIA', 'FALKLAND ISLANDS (MALVINAS)', 'FAROE ISLANDS', 'FIJI', 'FINLAND', 'FRANCE', 'FRENCH GUIANA', 'FRENCH POLYNESIA', 'FRENCH SOUTHERN TERRITORIES', 'GABON', 'GAMBIA', 'GEORGIA', 'GERMANY', 'GHANA', 'GIBRALTAR', 'GREECE', 'GREENLAND', 'GRENADA', 'GUADELOUPE', 'GUAM', 'GUATEMALA', 'GUERNSEY', 'GUINEA', 'GUINEA-BISSAU', 'GUYANA', 'HAITI', 'HEARD ISLAND AND MCDONALD ISLANDS', 'HOLY SEE (VATICAN CITY STATE)', 'HONDURAS', 'HONG KONG', 'HUNGARY', 'ICELAND', 'INDIA', 'INDONESIA', 'IRAN, ISLAMIC REPUBLIC OF', 'IRAQ', 'IRELAND', 'ISLE OF MAN', 'ISRAEL', 'ITALY', 'JAMAICA', 'JAPAN', 'JERSEY', 'JORDAN', 'KAZAKHSTAN', 'KENYA', 'KIRIBATI', "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF", 'KOREA, REPUBLIC OF', 'KUWAIT', 'KYRGYZSTAN', "LAO PEOPLE'S DEMOCRATIC REPUBLIC", 'LATVIA', 'LEBANON', 'LESOTHO', 'LIBERIA', 'LIBYA', 'LIECHTENSTEIN', 'LITHUANIA', 'LUXEMBOURG', 'MACAO', 'MACEDONIA, REPUBLIC OF', 'MADAGASCAR', 'MALAWI', 'MALAYSIA', 'MALDIVES', 'MALI', 'MALTA', 'MARSHALL ISLANDS', 'MARTINIQUE', 'MAURITANIA', 'MAURITIUS', 'MAYOTTE', 'MEXICO', 'MICRONESIA, FEDERATED STATES OF', 'MOLDOVA, REPUBLIC OF', 'MONACO', 'MONGOLIA', 'MONTENEGRO', 'MONTSERRAT', 'MOROCCO', 'MOZAMBIQUE', 'MYANMAR', 'NAMIBIA', 'NAURU', 'NEPAL', 'NETHERLANDS', 'NEW CALEDONIA', 'NEW ZEALAND', 'NICARAGUA', 'NIGER', 'NIGERIA', 'NIUE', 'NORFOLK ISLAND', 'NORTHERN MARIANA ISLANDS', 'NORWAY', 'OMAN', 'PAKISTAN', 'PALAU', 'PALESTINIAN TERRITORY, OCCUPIED', 'PANAMA', 'PAPUA NEW GUINEA', 'PARAGUAY', 'PERU', 'PHILIPPINES', 'PITCAIRN', 'POLAND', 'PORTUGAL', 'PUERTO RICO', 'QATAR', 'RÉUNION', 'ROMANIA', 'RUSSIAN FEDERATION', 'RWANDA', 'SAINT BARTHÉLEMY', 'SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA', 'SAINT KITTS AND NEVIS', 'SAINT LUCIA', 'SAINT MARTIN (FRENCH PART)', 'SAINT PIERRE AND MIQUELON', 'SAINT VINCENT AND THE GRENADINES', 'SAMOA', 'SAN MARINO', 'SAO TOME AND PRINCIPE', 'SAUDI ARABIA', 'SENEGAL', 'SERBIA', 'SEYCHELLES', 'SIERRA LEONE', 'SINGAPORE', 'SINT MAARTEN (DUTCH PART)', 'SLOVAKIA', 'SLOVENIA', 'SOLOMON ISLANDS', 'SOMALIA', 'SOUTH AFRICA', 'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS', 'SPAIN', 'SRI LANKA', 'SUDAN', 'SURINAME', 'SOUTH SUDAN', 'SVALBARD AND JAN MAYEN', 'SWAZILAND', 'SWEDEN', 'SWITZERLAND', 'SYRIAN ARAB REPUBLIC', 'TAIWAN, PROVINCE OF CHINA', 'TAJIKISTAN', 'TANZANIA, UNITED REPUBLIC OF', 'THAILAND', 'TIMOR-LESTE', 'TOGO', 'TOKELAU', 'TONGA', 'TRINIDAD AND TOBAGO', 'TUNISIA', 'TURKEY', 'TURKMENISTAN', 'TURKS AND CAICOS ISLANDS', 'TUVALU', 'UGANDA', 'UKRAINE', 'UNITED ARAB EMIRATES', 'UNITED KINGDOM', 'UNITED STATES', 'UNITED STATES MINOR OUTLYING ISLANDS', 'URUGUAY', 'UZBEKISTAN', 'VANUATU', 'VENEZUELA, BOLIVARIAN REPUBLIC OF', 'VIETNAM', 'VIRGIN ISLANDS, BRITISH', 'VIRGIN ISLANDS', 'USA', 'WALLIS AND FUTUNA', 'YEMEN', 'ZAMBIA', 'ZIMBABWE'
]

# Create your views here.


def getLikedNBATeams(user):
    liked_teams = NBATeam.new_manager.filter(liked_by=user)
    liked_team_names = []
    for team in liked_teams:
        print(team.name)
        liked_team_names.append(team.name)
    liked_teams = []
    for team_name in liked_team_names:
        team = {
            "name": team_name,
            "formatted_name": team_name.replace(" ", "-")
        }
        liked_teams.append(team)
    return liked_teams


def index(request):
    search_form = TeamSearch()
    user_is_logged_in = not request.user.is_anonymous
    articles = get_articles("soccer")
    if user_is_logged_in:
        liked_soccer_teams = getLikedSoccerTeams(request.user)
        liked_nba_teams = getLikedNBATeams(request.user)
    else:
        liked_soccer_teams = []
        liked_nba_teams = []
    page_data = {
        "articles": articles,
        "search_form": search_form,
        "liked_soccer_teams": liked_soccer_teams,
        "liked_nba_teams": liked_nba_teams
    }
    return render(request, 'soccer/index.html', page_data)


def team_not_found(request):
    return render(request, "soccer/team_not_found.html")


def getLikedSoccerTeams(user):
    liked_teams = Team.new_manager.filter(liked_by=user)
    liked_team_names = []
    for team in liked_teams:
        # print(team.name)
        liked_team_names.append(team.name)
    liked_teams = []
    for team_name in liked_team_names:
        team = {
            "name": team_name,
            "formatted_name": team_name.replace(" ", "-")
        }
        liked_teams.append(team)
    return liked_teams


# retrieves team ID based on team search to send to template to render widget with team's matches
def team_page(request, team_name=None):
    search_form = TeamSearch()
    user_is_signed_in = not request.user.is_anonymous
    if(request.method == "POST"):
        print("IN TEAM PAGE VIEW")
        search_form = TeamSearch(request.POST)
        if(search_form.is_valid()):  # process form data which is the searched team name
            team_search = search_form.cleaned_data["team_query"]

            # retrieves team ID based on searched team
            team_id = get_teamID(team_search)
            print(team_id)
            if team_id is None:
                page_data = {
                    "team_found": False
                }
                team_not_found_url = "/soccer/team-not-found?team=" + \
                    team_search.replace(" ", "+")
                return HttpResponseRedirect(team_not_found_url)

            # if team is in DB or in API endpoint
            if user_is_signed_in:
                team = get_object_or_404(Team, teamID=team_id)
                if team.liked_by.filter(id=request.user.id).exists():
                    team_is_liked = True
                else:
                    team_is_liked = False
                liked_NBA_teams = getLikedNBATeams(request.user)
                liked_soccer_teams = getLikedSoccerTeams(request.user)
            else:
                team_is_liked = False

            league_id = get_leagueID(team_id)
            team_name = get_teamName(team_id)
            team_logo = get_teamLogo(team_id)

            # Fetch news articles using NewsAPI
            team = Team.objects.get(name=team_name)
            team_name_formatted = team_name.replace(" ", "-")
            articles = get_articles(team)

            page_data = {
                "search_form": search_form,
                "team_is_liked": team_is_liked,
                "team": team,
                "team_name_formatted": team_name_formatted,
                "team_logo": team_logo,
                "articles": articles,
                "league_id": league_id,
                "cur_season": cur_season,
                # "liked_teams": liked_teams,
            }
            team_name = team_name.replace(" ", "-")
            team_page = "/soccer/team-page/" + team_name
            return HttpResponseRedirect(team_page)
    else:
        team_name_formatted = team_name
        if(team_name == 'U.N.A.M.---Pumas'):
            team_name = 'U.N.A.M. - Pumas'
        else:
            team_name = team_name.replace("-", " ")
        print(team_name)
        team_id = get_teamID(team_name)
        print(team_id)
        team_logo = get_teamLogo(team_id)
        league_id = get_leagueID(team_id)
        team = Team.objects.get(teamID=team_id)
        # team = get_object_or_404(Team, name=team_name)
        if user_is_signed_in:
            if team.liked_by.filter(id=request.user.id).exists():
                team_is_liked = True
                print("should have removed")
            else:
                team_is_liked = False
                print("should have been added")
            liked_nba_teams = getLikedNBATeams(request.user)
            liked_soccer_teams = getLikedSoccerTeams(request.user)
        else:
            liked_soccer_teams = []
            liked_nba_teams = []
            team_is_liked = False

        articles = get_articles(team)

        page_data = {
            "search_form": search_form,
            "team_name_formatted": team_name_formatted,
            "team_is_liked": team_is_liked,
            "team": team,
            "team_logo": team_logo,
            "articles": articles,
            "league_id": league_id,
            "cur_season": cur_season,
            "liked_soccer_teams": liked_soccer_teams,
            "liked_nba_teams": liked_nba_teams
        }
    return render(request, 'soccer/team_page.html', page_data)


def get_teamLogo(team_id):
    return Team.objects.get(teamID=team_id).logo


def get_teamID(team_search):
    # check if team searched is currently in DB
    if Team.objects.filter(name__icontains=team_search).exists():
        team_id = Team.objects.get(name__icontains=team_search).teamID

    # if team is currently in Database, make api call to search for team, get ID, and create team object
    else:
        conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
        if team_search.upper() in countries:
            endpoint = '/v3/teams?name=' + team_search
        else:
            team_search = team_search.replace(" ", "%20")
            endpoint = "/v3/teams?search=" + team_search
        # send GET request to host
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()  # Get response from server
        data = res.read()  # Reads and returns the response body
        # convert JSON format to Python dictionary
        result_dict = json.loads(data)
        results = result_dict['results']
        if results == 0:
            return None

        teams = result_dict['response']  # actual useful data
        errors = result_dict['errors']  # store any possible errors

        if len(errors) > 0:  # check to see if there were errors in the response receieved
            print("Error(s) occured\n")

        team_info = teams[0]['team']

        team_name = team_info['name']
        team_id = team_info['id']
        team_logo = team_info['logo']

        leagueID = get_leagueID(team_id)

        team_details = {
            "team_name": team_name,
            "team_id": team_id,
            "leagueID": leagueID,
            "logo": team_logo
        }
        createTeam(team_details)
    return team_id


def get_teamName(team_id):
    return Team.objects.get(teamID=team_id).name


def get_leagueID(team_id):
    if Team.objects.filter(teamID=team_id).exists():
        leagueID = Team.objects.get(teamID=team_id).leagueID
    else:
        conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
        endpoint = "/v3/leagues?team=" + str(team_id)
        # send GET request to host
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()  # Get response from server
        data = res.read()  # Reads and returns the response body
        # convert JSON format to Python dictionary
        result_dict = json.loads(data)
        payload = result_dict['response']  # actual useful data
        errors = result_dict['errors']  # store any possible errors

        first_league = payload[0]['league']
        leagueID = first_league['id']
    return leagueID


def createTeam(team_details):
    print("Creating team")
    team_name = team_details['team_name']
    team_id = team_details['team_id']
    team_logo = team_details['logo']
    leagueID = team_details['leagueID']
    Team.objects.create(name=team_name, teamID=team_id,
                        leagueID=leagueID, logo=team_logo)

# Takes a leagueID and checks if season has ended


def hasLeagueSeasonEnded(leagueID):
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
    endpoint = "/v3/leagues?id=" + leagueID
    conn.request("GET", endpoint, headers=headers)  # send GET request to host
    res = conn.getresponse()  # Get response from server
    data = res.read()  # Reads and returns the response body


def get_articles_fromAPI(search_term, num_articles):
    print("GETTING ARTICLES FROM API")
    user_agent = {'User-agent': 'Mozilla/5.0'}
    articles = []
    conn = http.client.HTTPSConnection("newsapi.org")
    key = str(env("NEWS_API_KEY"))
    endpoint = "/v2/everything?language=en&q=" + search_term + "&apiKey=" + key
    conn.request("GET", endpoint, headers=user_agent)
    res = conn.getresponse()
    data = res.read()
    result_dict = json.loads(data)

    try:
        article_results = result_dict["articles"]
    except:
        return []
    article_list = []
    for article in article_results:
        title = article["title"]
        author = article["author"]
        if author is None:
            author = ""
        description = article["description"]
        thumbnail = article["urlToImage"]
        url = article["url"]
        publishedDate = article["publishedAt"]
        second = int(publishedDate[17:19])
        minute = int(publishedDate[14:16])
        hour = int(publishedDate[11:13])
        day = int(publishedDate[8:10])
        month = int(publishedDate[5:7])
        year = int(publishedDate[0:4])
        dateObj = datetime.datetime(year, month, day, hour, minute, second)

        article_list.append({
            "date": dateObj,
            "title": title,
            "author": author,
            "description": description,
            "thumbnail": thumbnail,
            "url": url
        })

    article_list.sort(key=lambda x: x['date'])
    for article in article_list:
        if len(articles) < num_articles:
            title = article["title"]
            author = article["author"]
            if author is None:
                author = ""
            description = article["description"]
            thumbnail = article["thumbnail"]
            url = article["url"]
            description = re.sub('<[^<]+?>', '', description)
            article = {
                "title": title,
                "author": author,
                "description": description,
                "thumbnail": thumbnail,
                "url": url
            }
            articles.append(article)
    return reversed(articles)


def get_cached_articles(team):
    article_set = Article.objects.filter(team=team)[:5:-1]
    articles = []
    for articleObj in article_set:
        article = {
            "author": articleObj.author,
            "title": articleObj.title,
            "description": articleObj.description,
            "thumbnail": articleObj.thumbnail,
            "url": articleObj.url
        }
        articles.append(article)
    return articles


def appendArticleLists(laLigaArticles, premierLeagueArticles, serieaArticles, ligue1Articles, bundesligaArticles):
    articles = []
    for article in premierLeagueArticles:
        articles.append(article)
    for article in laLigaArticles:
        articles.append(article)
    for article in serieaArticles:
        articles.append(article)
    for article in ligue1Articles:
        articles.append(article)
    for article in bundesligaArticles:
        articles.append(article)
    return articles


def get_articles(team):
    if team == "soccer":
        num_articles = 1
        laLigaArticles = get_articles_fromAPI("la+liga", num_articles)
        premierLeagueArticles = get_articles_fromAPI(
            "premier+league", num_articles)
        serieaArticles = get_articles_fromAPI("serie+a", num_articles)
        ligue1Articles = get_articles_fromAPI("ligue+1", num_articles)
        bundesligaArticles = get_articles_fromAPI("bundesliga", num_articles)
        articles = appendArticleLists(
            laLigaArticles, premierLeagueArticles, serieaArticles, ligue1Articles, bundesligaArticles)
    elif team.name.upper() in countries:
        search_query = team.name + "+" + "soccer"
        print("ARTICLE SEARCH QUERY = " + search_query)
        articles = get_articles_fromAPI(search_query, 5)
    else:
        num_articles = 5
        team_name_cleaned = team.name.replace(" ", "+")
        articles = get_articles_fromAPI(team_name_cleaned, num_articles)
    return articles


def upcoming_matches(request, id):
    page_data = {
        "id": id
    }
    return render(request, "soccer/upcoming_matches.html", page_data)


def toggle_team_like(request):
    liked = request.GET.get('liked', False) == 'true'
    teamID = request.GET.get('teamID', False)
    team = Team.objects.get(teamID=teamID)
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


def liked_list(request):
    teams_liked = Team.new_manager.filter(liked_by=request.user)
    print(teams_liked)
    page_data = {
        "teams_liked": teams_liked
    }
    return render(request, "accounts/liked.html", page_data)


def chat(request):
    return render(request, 'soccer/chat.html')


def room(request, room_name):
    page_data = {
        "room_name": room_name
    }
    return render(request, 'soccer/chat_room.html', page_data)
