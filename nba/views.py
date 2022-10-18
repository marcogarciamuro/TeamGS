from calendar import day_abbr
from dateutil import tz
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db.models import Q
from nba.models import Team, Game, Article
from soccer.models import Team as SoccerTeam
from soccer.forms import TeamSearch
from django.contrib.auth.decorators import login_required
import http.client
import re
import json
import datetime
import environ

env = environ.Env()
environ.Env.read_env()

utc_zone = tz.tzutc()
pst_zone = tz.tzlocal()

headers = {
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
    'x-rapidapi-key': env('NBA_API_KEY')
}

cur_date = datetime.date.today()
cur_datetime = datetime.datetime.now()
cur_season = str(cur_date.year-1)


# Create your views here.
def ajax_change_team_like_status(request):
    liked = request.GET.get('liked')


def team_not_found(request):
    return render(request, "nba/team-not-found.html")


def index(request):
    search_form = TeamSearch()
    live_games = getLiveGames()
    articles = get_articles("nba")

    user_is_signed_in = not request.user.is_anonymous
    if user_is_signed_in:
        liked_nba_teams = getLikedNBATeams(request.user)
        liked_soccer_teams = getLikedSoccerTeams(request.user)
    else:
        liked_nba_teams = []
        liked_soccer_teams = []
    page_data = {
        "articles": articles,
        "search_form": search_form,
        "live_games": live_games,
        "liked_nba_teams": liked_nba_teams,
        "liked_soccer_teams": liked_soccer_teams
    }
    return render(request, 'nba/index.html', page_data)


def getLikedSoccerTeams(user):
    liked_teams = SoccerTeam.new_manager.filter(liked_by=user)
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


def getLikedNBATeams(user):
    liked_teams = Team.new_manager.filter(liked_by=user)
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


def getLiveGames():
    print("IN LIVE GAMES")
    conn = http.client.HTTPSConnection("api-nba-v1.p.rapidapi.com")
    endpoint = "/games?live=all"
    conn.request("GET", endpoint, headers=headers)
    conn_res = conn.getresponse()  # Get response from server
    data = conn_res.read()  # Reads and returns the response body
    response = json.loads(data)
    num_results = response["results"]
    if num_results == 0:
        return None

    games = response["response"]
    for game in games:
        if game["league"] != "standard":
            return None
        game_id = game["id"]
        home_team_id = game["teams"]["home"]["id"]
        away_team_id = game["teams"]["visitors"]["id"]
        game_date = game["date"]["start"]
        try:
            second = int(game_date[18:19])
        except:
            second = 0
        print(second)
        try:
            minute = int(game_date[14:15])
        except:
            minute = 0
        try:
            hour = int(game_date[11:12])
        except:
            hour = 0
        day = int(game_date[8:10])
        month = int(game_date[5:7])
        year = int(game_date[0:4])
        date_obj = datetime.datetime(year, month, day, hour, minute, second)

        try:
            home_team = Team.objects.get(teamID=home_team_id)
            pass
        except:
            continue

        try:
            away_team = Team.objects.get(teamID=away_team_id)
            pass
        except:
            continue

        away_team_points = game["scores"]["visitors"]["points"]
        home_team_points = game["scores"]["home"]["points"]
        quarter = game["periods"]["current"]
        status = game["status"]["long"]
    # if Game.objects.filter(game_id=game_id).exists():
        print("API: QUARTER = ", quarter)
        live_games = []
        live_games.append({
            "home_team": home_team,
            "away_team": away_team,
            "quarter": quarter,
            "home_team_points": home_team_points,
            "away_team_points": away_team_points,
        })
        return live_games


def team_page(request, team_name=None):
    user_is_signed_in = not request.user.is_anonymous
    search_form = TeamSearch()
    if(request.method == "POST"):
        search_form = TeamSearch(request.POST)
        if(search_form.is_valid()):  # process form data which is the searched team name
            team_search = search_form.cleaned_data["team_query"]
            team_name = team_search
            team_id = get_teamID(team_name)
            if team_id is None:
                print("TEAM NOT FOUND")
                return render(request, "nba/team_not_found.html")

            print(team_id)
            teamObj = Team.objects.get(teamID=team_id)
            team_name = teamObj.name
            games = get_games(teamObj)
            standings = get_standings(teamObj)
            articles = get_articles(teamObj)

            if user_is_signed_in:
                team = Team.objects.get(teamID=team_id)
                if team.liked_by.filter(id=request.user.id).exists():
                    team_is_liked = True
                else:
                    team_is_liked = False
                liked_nba_teams = getLikedNBATeams(request.user)
                liked_soccer_teams = getLikedSoccerTeams(request.user)
            else:
                liked_nba_teams = []
                liked_soccer_teams = []
                team_is_liked = False

            formatted_team_name = team_name.replace(" ", "-")
            page_data = {
                "search_form": search_form,
                "team_is_liked": team_is_liked,
                "team": teamObj,
                "formatted_team_name": formatted_team_name,
                "games": games,
                "articles": articles,
                "standings": standings,
                "liked_nba_teams": liked_nba_teams,
                "liked_soccer_teams": liked_soccer_teams
            }
            team_page = "/nba/team-page/" + formatted_team_name
            return HttpResponseRedirect(team_page)
    else:
        formatted_team_name = team_name
        team_name = team_name.replace("-", " ")
        team_id = get_teamID(team_name)
        team = Team.objects.get(teamID=team_id)
        articles = get_articles(team)
        games = get_games(team)
        standings = get_standings(team)

        if user_is_signed_in:
            team = Team.objects.get(teamID=team_id)
            if team.liked_by.filter(id=request.user.id).exists():
                team_is_liked = True
            else:
                team_is_liked = False
            liked_nba_teams = getLikedNBATeams(request.user)
            liked_soccer_teams = getLikedSoccerTeams(request.user)
        else:
            liked_soccer_teams = []
            liked_nba_teams = []
            team_is_liked = False

        page_data = {
            "search_form": search_form,
            "team_is_liked": team_is_liked,
            "team": team,
            "formatted_team_name": formatted_team_name,
            "games": games,
            "articles": articles,
            "standings": standings,
            "liked_nba_teams": liked_nba_teams,
            "liked_soccer_teams": liked_soccer_teams
        }
        return render(request, "nba/team_page.html", page_data)


def get_standings(teamObj):
    team_conference = teamObj.conference
    conn = http.client.HTTPSConnection("api-nba-v1.p.rapidapi.com")
    endpoint = "/standings?league=standard&season=" + \
        cur_season + "&conference=" + team_conference
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()  # Get response from server
    data = res.read()  # Reads and returns the response body

    # convert JSON format to Python dictionary
    api_response = json.loads(data)
    standings = api_response["response"]
    for position in standings:
        team_id = position["team"]["id"]
        team = Team.objects.get(teamID=team_id)
        team.rank = position["conference"]["rank"]
        team.win_pct = float(position["win"]["percentage"])
        team.wins = position["win"]["total"]
        team.losses = position["loss"]["total"]
        team.save()
    standings = Team.objects.filter(
        conference=team_conference).order_by("rank")
    return standings


def get_teamID(team_name):
    print("looking for team name" + team_name)
    # check if team searched is currently in DB
    if Team.objects.filter(name__icontains=team_name).exists():
        print("in database not making call to API")
        # retreive team ID
        team_id = Team.objects.get(name__icontains=team_name).teamID
        print(team_id)
    else:
        return None
        print("team not in DB")
    return str(team_id)


def get_games(teamObj):
    mainTeamName = teamObj.name
    team_id = str(teamObj.teamID)
    conn = http.client.HTTPSConnection("api-nba-v1.p.rapidapi.com")
    endpoint = "/games?season=" + cur_season + "&team=" + team_id
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()  # Get response from server
    data = res.read()  # Reads and returns the response body

    # convert JSON format to Python dictionary
    api_response = json.loads(data)
    games = api_response["response"]
    game_list = []
    for game in games:
        game_id = game["id"]
        game_status = game["status"]["long"]

        home_team_name = game["teams"]["home"]["name"]
        try:
            home_team = Team.objects.get(name=home_team_name)
            pass
        except:
            continue

        home_team.formatted_name = home_team.name.replace(" ", "-")
        home_team.save()

        away_team_name = game["teams"]["visitors"]["name"]
        try:
            away_team = Team.objects.get(name=away_team_name)
            pass
        except:
            continue

        away_team.formatted_name = away_team.name.replace(" ", "-")
        away_team.save()

        home_team_points = game["scores"]["home"]["points"]
        away_team_points = game["scores"]["visitors"]["points"]

        game_date = game["date"]["start"]
        try:
            second = int(game_date[17:19])
        except:
            second = 0
        try:
            minute = int(game_date[14:16])
        except:
            minute = 0
        try:
            hour = int(game_date[11:13])
        except:
            hour = 0
        day = int(game_date[8:10])
        month = int(game_date[5:7])
        year = int(game_date[0:4])
        date_obj_utc = datetime.datetime(
            year, month, day, hour, minute, second)
        date_obj_utc = date_obj_utc.replace(tzinfo=utc_zone)
        date_obj_pst = date_obj_utc.astimezone(pst_zone)
        date_obj_cleaned = date_obj_pst.strftime('%a %b, %d %I:%M %p')

        game_list.append({
            "id": game_id,
            "status": game_status,
            "date_pst": date_obj_pst,
            "date": date_obj_utc,
            "home_team": home_team,
            "home_team_points": home_team_points,
            "away_team": away_team,
            "away_team_points": away_team_points
        })
    game_list.sort(key=lambda x: x['date'])
    previous_games = []
    upcoming_games = []
    consequtive_matchups = 0
    # wins from consequtive matchups (ex: playoff series)
    consequtive_matchup_wins = 0
    consequtive_matchup_losses = 0
    previous_opponent = ""
    eliminated = False
    no_immediate_scheduled_games = False
    print("TEAM PAGE: ", mainTeamName)
    teamHasUpcomingGames = False
    for game in reversed(game_list):
        if game['status'] == "Scheduled":
            teamHasUpcomingGames = True
        if game["status"] == "Finished":
            # determine game winner
            if game["home_team_points"] > game["away_team_points"]:
                winner = game["home_team"].name
            else:
                winner = game["away_team"].name

            # determine current game opponent
            if game["home_team"].name == mainTeamName:
                opponent = game["away_team"].name
            elif game["away_team"].name == mainTeamName:
                opponent = game["home_team"].name

            if previous_opponent == "":
                previous_opponent = opponent

            # check if last game was against same opponent if so increment consequtive matchups
            if previous_opponent == opponent:
                consequtive_matchups += 1

                # check if last game against same opponent was won
                if winner == mainTeamName:
                    consequtive_matchup_wins += 1
                else:
                    consequtive_matchup_losses += 1
            else:
                consequtive_matchups = 0
                consequtive_matchup_wins = 0
                consequtive_matchup_losses = 0
                previous_opponent = ""

            if consequtive_matchup_wins == 4:
                print("SERIES IS DUNZO, SHOULD DISPLAY NO MORE")
                no_immediate_scheduled_games = True

            if consequtive_matchup_losses == 4:
                print("WE GOT DROPPPED OFF, SHOULD DISPLAY NO MORE")
                eliminated = True

            if(len(previous_games) < 5):
                previous_games.append(game)

    if no_immediate_scheduled_games == True or eliminated == True or teamHasUpcomingGames == False:
        upcoming_games = None

    else:
        for game in game_list:
            if game["date_pst"] > game["date"]:
                print("HELLER EVERYBDOU")
            if len(upcoming_games) < 3 and game["status"] == "Scheduled" and game["date_pst"] > cur_datetime.replace(tzinfo=pst_zone):
                print("ADDING TO UPCOMING GAME LIST")
                print(game["id"], ":", game["home_team"].name,
                      game["away_team"].name)
                upcoming_games.append(game)

    games = {
        "previous_games": reversed(previous_games),
        "upcoming_games": upcoming_games
    }
    return games


def get_articles(team):
    if team == "nba":
        articles = get_articles_from_API("nba")
    else:
        # uncomment to get articles from DB
        articles = get_articles_from_API(team)
    return articles

# Solution to remove HTML tags from descriptions of NBA articles:
# https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string


CLEANR = re.compile('<.*?>')


def cleanHTML(raw_html):
    cleanText = re.sub(CLEANR, '', raw_html)
    return cleanText


def get_articles_from_API(team):
    print("Getting articles from API")
    if type(team) is Team:
        team_name = team.name.replace(" ", "+")
    else:
        team_name = team
    articles = []
    conn = http.client.HTTPSConnection("newsapi.org")
    key = env('NEWS_API_KEY')
    endpoint = "/v2/everything?sortBy=publishedAt&language=en&q=+" + \
        team_name + "&apiKey=" + key
    user_agent = {'User-agent': 'Mozilla/5.0'}
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
        # if team_name.replace("+", " ").split()[-1] not in title:
        #     continue
        author = article["author"]
        if author is None:
            author = ""
        description = article["description"]
        if description is not None:
            description = cleanHTML(description)
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

    # for i in range(5):
    for article in article_list:
        if len(articles) < 5:
            title = article["title"]
            author = article["author"]
            if author is None:
                author = ""
            description = article["description"]
            thumbnail = article["thumbnail"]
            if thumbnail is None:
                continue
            url = article["url"]
            article = {
                "title": title,
                "author": author,
                "description": description,
                "thumbnail": thumbnail,
                "url": url
            }
            articles.append(article)
    return reversed(articles)


@login_required(login_url='/login')
def toggleTeamLike(request):
    liked = request.GET.get('liked') == 'true'
    teamID = request.GET.get('teamID', False)
    team = Team.objects.get(teamID=teamID)
    try:
        if liked:
            team.liked_by.remove(request.user)
            team.save()
            return JsonResponse({"success": True, "team_is_now_liked": False})
        else:
            team.liked_by.add(request.user)
            team.save()
            return JsonResponse({"success": True, "team_is_now_liked": True})
    except Exception as e:
        return JsonResponse({"success": False})


def liked_list(request):
    teams_liked = Team.new_manager.filter(liked_by=request.user)
    print(teams_liked)
    page_data = {
        "teams_liked": teams_liked
    }
    return render(request, "accounts/liked.html", page_data)


def room(request, room_name):
    page_data = {
        "room_name": room_name
    }
    return render(request, 'nba/chat_room.html', page_data)
