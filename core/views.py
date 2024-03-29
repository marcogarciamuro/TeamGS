from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from core.forms import JoinForm, LoginForm
from soccer.models import Team as SoccerTeam
from nba.models import Team as NBATeam


def about(request):
    return render(request, "core/about.html")


def getLikedTeams(request):
    username = request.GET.get('username')
    try:
        user = User.objects.get(username=username)
        liked_nba_teams_queryset = NBATeam.new_manager.filter(
            liked_by=user).values()
        liked_soccer_teams_queryset = SoccerTeam.new_manager.filter(
            liked_by=user).values()
        return JsonResponse({
            "success": True,
            "liked_soccer_teams": list(liked_soccer_teams_queryset),
            "liked_nba_teams": list(liked_nba_teams_queryset)
        })
    except Exception as e:
        return JsonResponse({"success": False})


def join(request):
    if(request.method == "POST"):
        join_form = JoinForm(request.POST)
        if(join_form.is_valid()):  # if signup data was valid
            user = join_form.save()  # save form data to DB
            username = join_form.cleaned_data['username']
            password = join_form.cleaned_data['password']
            user.set_password(user.password)  # encrypt the password
            user.save()  # save encrypt password to DB
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
            return redirect("/")
        else:
            print("INVALID REGISTRATIOn")
            join_form = JoinForm()
            page_data = {"join_form": join_form}
            return render(request, 'core/join.html', page_data)

    else:
        join_form = JoinForm()
        page_data = {"join_form": join_form}
        return render(request, 'core/join.html', page_data)


def user_login(request):
    if(request.method == 'POST'):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # First get the username and password supplied
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]

            # Use Django's built-in authentication function
            user = authenticate(username=username, password=password)

            # If we have a user
            if user:
                if user.is_active:  # Check if the account is active
                    login(request, user)
                    return redirect("/")
                else:
                    return HttpResponse("Your account is not active.")
            else:
                print("Incorrect username or password.")
                return render(request, 'core/login.html', {"login_form": LoginForm})

    else:
        return render(request, 'core/login.html', {"login_form": LoginForm})


def index(request):
    return render(request, 'core/index.html')


def user_logout(request):
    logout(request)
    return redirect("/")
