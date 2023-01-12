from dateutil import tz
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from nba.models import Team, Game, Conference, Player, TeamArticle, NBAArticle
from nba.forms import TeamSearch
from django.contrib.auth.decorators import login_required
import http.client
import re
import json
import environ
from datetime import datetime, date, timedelta
from dal import autocomplete
from django.utils.html import format_html
from django.utils import timezone

env = environ.Env()
environ.Env.read_env()

utc_zone = tz.tzutc()
pst_zone = tz.tzlocal()

NBA_API_HEADERS = {
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
    'x-rapidapi-key': env('NBA_API_KEY')
}

NEWS_API_HEADERS = {
    'User-agent': 'Mozilla/5.0'
}

EAST_CONFERENCE = [41, 38, 27, 26, 24, 21, 20, 15, 10, 7, 6, 5, 4, 2, 1]
WEST_CONFERENCE = [40, 31, 30, 29, 28, 25, 23, 22, 19, 17, 16, 14, 11, 9, 8]

cur_date = date.today()
cur_datetime = timezone.now()
# cur_season = str(cur_date.year)
cur_season = 2022


# Create your views here.
def team_not_found(request):
    return render(request, "nba/team-not-found.html")


def index(request):
    search_form = TeamSearch()
    live_games = get_live_games()
    articles = get_articles()

    page_data = {
        "articles": articles,
        "search_form": search_form,
        "live_games": live_games,
    }
    return render(request, 'nba/index.html', page_data)


def call_api(endpoint):
    conn = http.client.HTTPSConnection('api-nba-v1.p.rapidapi.com')
    conn.request('GET', endpoint, headers=NBA_API_HEADERS)
    res = conn.getresponse()  # Get response from server
    data = res.read()
    json_dict = json.loads(data)
    results = json_dict['results']
    if results == 0:
        return None
    return json_dict['response']


def get_live_games():
    print("IN LIVE GAMES")
    endpoint = "/games?live=all"
    games = call_api(endpoint)
    if not games:
        return None
    live_games = []
    for game in games:
        if game["league"] != "standard":
            continue
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

        try:
            home_team = Team.objects.get(teamID=home_team_id)
        except:
            home_team_name = game["teams"]["home"]["name"]
            home_team_logo = game["teams"]["home"]["logo"]
            home_team = create_team(
                home_team_name, home_team_id, home_team_logo)
            if not home_team:
                continue

        try:
            away_team = Team.objects.get(teamID=away_team_id)
        except:
            away_team_name = game["teams"]["visitors"]["name"]
            away_team_logo = game["teams"]["visitors"]["logo"]
            away_team = create_team(
                away_team_name, away_team_id, away_team_logo)
            if not away_team:
                continue

        away_team_points = game["scores"]["visitors"]["points"]
        home_team_points = game["scores"]["home"]["points"]
        quarter = game["periods"]["current"]
        status = game["status"]["long"]
        clock = game["status"]["clock"]
        print("API: QUARTER = ", quarter)
        live_games.append({
            "home_team": home_team,
            "away_team": away_team,
            "quarter": quarter,
            "clock": clock,
            "home_team_points": home_team_points,
            "away_team_points": away_team_points,
        })
    print(live_games)
    return live_games


def get_games(team):
    games_are_outdated = cur_datetime >= team.last_updated + \
        timedelta(days=1)
    team_is_new = team.last_updated == team.created_on

    # if team is new (has no cached games) or team is in DB and games are outdated:
    if games_are_outdated or team_is_new:
        print("GETTING GAMES FROM API")
        games = get_games_from_api(team)

    # if team is in DB and games are current:
    else:
        print("GETTING GAMES FROM CACHE")
        games = get_cached_games(team)
    return games


def team_page(request, team_name=None):
    user_is_signed_in = not request.user.is_anonymous
    search_form = TeamSearch()
    if(request.method == "POST"):
        search_form = TeamSearch(request.POST)
        if(search_form.is_valid()):  # process form data which is the searched team name
            team_search = search_form.cleaned_data["team_query"]
            team = get_team(team_search)
            if team is None:
                print("TEAM NOT FOUND")
                return render(request, "nba/team_not_found.html")

            formatted_team_name = team.name.replace(" ", "-")
            team_page = "/nba/team-page/" + formatted_team_name
            return HttpResponseRedirect(team_page)
    else:
        formatted_team_name = team_name
        team_name = team_name.replace("-", " ")

        # Get and or create team object
        team = get_team(team_name)
        games = get_games(team)
        standings = get_standings(team)
        articles = get_articles(team)
        players = get_players(team)

        if user_is_signed_in:
            team_is_liked = team.liked_by.filter(id=request.user.id).exists()
        else:
            team_is_liked = False

        page_data = {
            "search_form": search_form,
            "team_is_liked": team_is_liked,
            "team": team,
            "formatted_team_name": formatted_team_name,
            "games": games,
            "articles": articles,
            "standings": standings,
            "players": players,
        }
        return render(request, "nba/team_page.html", page_data)


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


def get_players(team_obj):
    print("GETTING PLAYERS")
    if Player.objects.filter(team=team_obj).exists():
        players = Player.objects.filter(team=team_obj)
        print("FOUND CACHED PLAYERS")
        return players
    else:
        # Fetch players from api
        print("NO CACHED PLAYERS, FETCHING FROM API")
        endpoint = "/players?team=" + \
            str(team_obj.teamID) + "&season=" + str(cur_season)
        player_list = call_api(endpoint)
        if not player_list:
            return None
        for player in player_list:
            if player['birth']['date']:
                player_birthdate = datetime.strptime(
                    player['birth']['date'], '%Y-%m-%d')
                age = get_player_age(player_birthdate)
            else:
                age = None
            Player.objects.create(
                player_id=player['id'],
                firstname=player['firstname'],
                lastname=player['lastname'],
                team=team_obj,
                age=age,
                height_feet=player['height']['feets'],
                height_inches=player['height']['inches'],
                weight=player['weight']['pounds'],
                jersey_number=player['leagues']['standard']['jersey'],
                position=player['leagues']['standard']['pos']
            )
        players = Player.objects.filter(team=team_obj)
        return players


def get_player_age(player_birthdate_obj):
    age = cur_date.year - player_birthdate_obj.year
    if player_birthdate_obj.month > cur_date.month or (player_birthdate_obj.month == cur_date.month and player_birthdate_obj.day < cur_date.day):
        age -= 1
    return age


# Get team object from DB or from API
def get_team(team_name):
    print("looking for team name" + team_name)
    try:
        team = Team.objects.get(name__icontains=team_name)
    except:
        endpoint = "/teams?search=" + team_name.replace(" ", "%20")
        team_results = call_api(endpoint)
        if not team_results:
            return None
        team_info = team_results[0]
        team_id = team_info['id']
        team_name = team_info['name']
        team_logo = team_info['logo']
        team_conference = team_info['leagues']['standard']['conference']
        try:
            conference_obj = Conference.objects.get(region=team_conference)
        except:
            conference_obj = Conference.objects.create(region=team_conference)
        Team.objects.create(teamID=team_id, name=team_name,
                            logo=team_logo, conference=conference_obj,
                            last_updated=cur_datetime, created_on=cur_datetime
                            )
        team = Team.objects.get(teamID=team_id)
    return team


def get_standings(team_obj):
    endpoint = "/standings?league=standard&season=" + \
        str(cur_season) + "&conference=" + team_obj.conference.region
    standings = call_api(endpoint)
    for position in standings:
        team_info = position["team"]
        team_id = team_info["id"]
        try:
            team = Team.objects.get(teamID=team_id)
        except:
            Team.objects.create(name=team_info["name"],
                                teamID=team_id, logo=team_info["logo"], conference=team_obj.conference,
                                last_updated=cur_datetime, created_on=cur_datetime
                                )
            team = Team.objects.get(teamID=team_id)

        team.rank = position["conference"]["rank"]
        team.win_pct = float(position["win"]["percentage"])
        team.wins = position["win"]["total"]
        team.losses = position["loss"]["total"]
        team.save()
    standings = Team.objects.filter(
        conference=team_obj.conference).order_by("rank")
    return standings


def update_game_score(game_id):
    print("FIXING GAME SCORE")
    endpoint = "/games?id=" + str(game_id)
    game_stats = call_api(endpoint)[0]
    home_team_points = game_stats['scores']['home']['points']
    away_team_points = game_stats['scores']['visitors']['points']
    game_obj_to_fix = Game.objects.get(game_id=game_id)
    game_obj_to_fix.home_team_points = home_team_points
    game_obj_to_fix.away_team_points = away_team_points
    game_obj_to_fix.save()


def get_cached_games(teamObj):
    previous_five_games = Game.objects.filter(Q(home_team=teamObj, date__lte=cur_date)
                                              | Q(away_team=teamObj, date__lte=cur_date)).order_by('-date')[:5]
    upcoming_three_games = Game.objects.filter(Q(home_team=teamObj, date__gte=cur_date)
                                               | Q(away_team=teamObj, date__gte=cur_date)).order_by('date')[:3]
    for game in previous_five_games:
        if not game.home_team_points or not game.away_team_points:
            update_game_score(game.game_id)
            game = Game.objects.filter(game_id=game.game_id)
    games = {
        "previous_games": reversed(previous_five_games),
        "upcoming_games": upcoming_three_games
    }
    return games


def create_team(team_name, team_id, team_logo):
    if team_id in EAST_CONFERENCE:
        team_conference_region = "East"
    elif team_id in WEST_CONFERENCE:
        team_conference_region = "West"
    else:
        return None
    try:
        team_conference = Conference.objects.get(region=team_conference_region)
    except:
        team_conference = Conference.objects.create(
            region=team_conference_region)

    Team.objects.create(name=team_name, teamID=team_id, logo=team_logo,
                        conference=team_conference, last_updated=cur_datetime,
                        created_on=cur_datetime)
    return Team.objects.get(teamID=team_id)


def get_games_from_api(team_obj):
    team_obj.last_updated = cur_date
    team_obj.save()
    main_team_name = team_obj.name
    endpoint = "/games?season=" + \
        str(cur_season) + "&team=" + str(team_obj.teamID)
    games = call_api(endpoint)
    if not games:
        return None
    game_list = []
    print("GOING THRU GAMES")
    for game in games:
        game_id = game["id"]
        game_status = game["status"]["long"]

        # get home team object
        home_team_name = game["teams"]["home"]["name"]
        try:
            home_team = Team.objects.get(name=home_team_name)
        except:
            home_team_id = game["teams"]["home"]["id"]
            home_team_logo = game["teams"]["home"]["logo"]
            home_team = create_team(
                home_team_name, home_team_id, home_team_logo)
            if not home_team:
                continue

        # get away team object
        away_team_name = game["teams"]["visitors"]["name"]
        try:
            away_team = Team.objects.get(name=away_team_name)
        except:
            away_team_id = game["teams"]["visitors"]["id"]
            away_team_logo = game["teams"]["visitors"]["logo"]
            away_team = create_team(
                away_team_name, away_team_id, away_team_logo)
            if not away_team:
                continue

        home_team_points = game["scores"]["home"]["points"]
        away_team_points = game["scores"]["visitors"]["points"]

        game_date = game["date"]["start"]
        second = int(game_date[17:19])
        minute = int(game_date[14:16])
        hour = int(game_date[11:13])
        day = int(game_date[8:10])
        month = int(game_date[5:7])
        year = int(game_date[0:4])
        date_obj_utc = datetime(
            year, month, day, hour, minute, second)
        date_obj_utc = date_obj_utc.replace(tzinfo=utc_zone)
        date_obj_pst = date_obj_utc.astimezone(pst_zone)
        try:
            Game.objects.create(game_id=game_id,
                                home_team=home_team, away_team=away_team,
                                home_team_points=home_team_points, away_team_points=away_team_points,
                                date=date_obj_pst
                                )
        except:
            # Game object already exists and was created by the opposite team Obj
            pass

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
        # print("FINISHED EXAMINING ONE GAME")
    print("DONE GOING THRU GAMES")
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
            if game["home_team"].name == main_team_name:
                opponent = game["away_team"].name
            elif game["away_team"].name == main_team_name:
                opponent = game["home_team"].name

            if previous_opponent == "":
                previous_opponent = opponent

            # check if last game was against same opponent if so increment consequtive matchups
            if previous_opponent == opponent:
                consequtive_matchups += 1

                # check if last game against same opponent was won
                if winner == main_team_name:
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
            if len(upcoming_games) < 3 and game["status"] == "Scheduled" and game["date_pst"] > cur_datetime.replace(tzinfo=pst_zone):
                upcoming_games.append(game)

    games = {
        "previous_games": reversed(previous_games),
        "upcoming_games": upcoming_games
    }
    return games


def get_articles_from_api(team=None):
    print("Getting articles from API")
    key = str(env('NEWS_API_KEY'))
    if team:
        players = get_players(team)
        team_nickname = team.name.split()[-1]
        q = '"' + team.name.replace(' ', '-') + '" OR "' + team_nickname + '"'
        for player in players:
            q += ' OR "' + player.firstname + '-' + player.lastname + '"'
        q = q.replace(' ', '%20')
        endpoint = "/v2/everything?sortBy=publishedAt&language=en&q=" + q + \
            "&apiKey=" + key + '&sources=bleacher-report' + '&searchIn=title'
    else:
        endpoint = "/v2/everything?sortBy=publishedAt&language=en&q=" + \
            "nba" + "&apiKey=" + key + '&sources=bleacher-report'

    api_article_results = call_news_api(endpoint)
    sorted_articles = create_sorted_article_list(api_article_results)
    print("GOING THRU ARTICLES ")
    article_obj_list = create_and_get_article_short_list(sorted_articles, team)
    print("ARTICLES ABOUT TO BE RETURNED ", article_obj_list)
    return article_obj_list


def get_articles(team=None):
    one_day_ago = timezone.now() - timedelta(days=1)
    if team:
        cached_articles = TeamArticle.objects.filter(
            team=team).order_by('-retrieval_date')
    else:
        cached_articles = NBAArticle.objects.filter().order_by("-retrieval_date")

    if cached_articles.exists():
        print("FOUND CACHED ARTICLES")
        if cached_articles[0].retrieval_date <= one_day_ago:
            print("last created article is outdated, fetching new ones")
            articles = get_articles_from_api(team)
        else:
            print("Serving CACHED ARTICLES")
            articles = cached_articles[:5]
    else:
        # No general nba articles exist, fetch new ones
        articles = get_articles_from_api(team)
    return articles


# Solution to remove HTML tags from descriptions of NBA articles:
# https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
CLEANR = re.compile('<.*?>')


def clean_html(raw_html):
    cleanText = re.sub(CLEANR, '', raw_html)
    return cleanText


def call_news_api(endpoint):
    conn = http.client.HTTPSConnection("newsapi.org")
    conn.request("GET", endpoint, headers=NEWS_API_HEADERS)
    res = conn.getresponse()
    data = res.read()
    json_dict = json.loads(data)
    results = json_dict['totalResults']
    if results == 0:
        return None
    return json_dict['articles']


# Takes articles from api response as argument and returns list of articles sorted by date
def create_sorted_article_list(unsorted_articles):
    final_articles = []
    for article in unsorted_articles:
        title = article["title"]
        author = article["author"]
        if author is None:
            author = ""
        description = article["description"]
        if description:
            description = clean_html(description)
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


def create_and_get_article_short_list(article_item_list, team=None):
    article_obj_list = []
    for article in article_item_list:
        if len(article_obj_list) == 6:
            break
        title = article["title"]
        author = article["author"]
        if author is None:
            author = ""
        description = article["description"]
        thumbnail = article["thumbnail"]
        if thumbnail is None:
            continue
        url = article["url"]
        if team and not TeamArticle.objects.filter(title=title).exists():
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
        elif not team and not NBAArticle.objects.filter(title=title).exists():
            NBAArticle.objects.create(
                title=title,
                author=author,
                thumbnail=thumbnail,
                description=description,
                url=url
            )
            article_obj = NBAArticle.objects.get(title=title)
            article_obj_list.append(article_obj)
    return reversed(article_obj_list)


@login_required(login_url='/login')
def toggle_team_like(request):
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
