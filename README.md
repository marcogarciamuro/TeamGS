# TeamGS

## Background
Team Gumshoe (gumshoe meaning detective) or TeamGS is a web application that
provides users with an easy way to discover and monitor what is happening
in the world of soccer and basketball.

The website features anything fans might want to know about their favorite
teams such as:
-   Previous/upcoming games
-   Current standings within their group
-   Current news articles

Users can create an account that will enable them to follow teams and quickly access those teams' pages from then on.

Any live games are also displayed and updated automatically in real time so
users can keep up with games on the fly or tune into a game they weren't aware was ongoing.

Sometimes fans feel like expressing their thoughts or ideas about a team to
others. This website has designated asynchronous chat
rooms for each team where fans can communicate with each other.

## Implementation

The driving forces behind the information that is displayed are APIs. In my
Django backend, I am making requests to REST APIs that are returning results
that is being passed to Django templates for the users to consume. If
beneficial and appropriate, API request results are cached in a database to
reduce load times by eliminating the need to fetch new results.

jQuery and Ajax were utilized to support asynchronous HTML updates and create a
seamless and responsive web interface for users.

There is a multi-model database that stores objects whose data is accessed and
then displayed using the Django template language.

Implementing the asynchronous chat rooms involves using Django channels that
handle WebSockets. I paired this with Daphne, and Redis to bring functionality
to the chat rooms.

## Deployment

When it comes to deployment, there are several working parts and steps that
need to be done. Some of these are hacky since there weren't any possible ways
of achieving what I wanted using the resources I had available.

1. First I transitioned from the default local SQLite database to a remote
   Postgresql database hosted on Google Cloud Platform.
2. Next, I utilized Docker to containerize different components of my Django
   project. After doing some research, it was advised to create separate
containers for my WSGI and ASGI applications. The WSGI application refers to
anything that does not require Django Channels and WebSockets (all of Django
project except for Chat Rooms). The ASGI application would be any chat room.
Lastly, I created a container for a Redis server. The images from which these
containers are spawned are created using Docker compose (docker-compose.yml).
The Dockerfiles for images contain scripts that run necessary services that I
will explain next.
3. I set up my project to serve content through Gunicorn, Daphne, and Nginx. I
   am using Gunicorn to run the WSGI side of my Django application. Nginx is
used to handle incoming requests and serve the appropriate application. If an
endpoint that contains "ws" (websocket) is requested (chat rooms), then Nginx
references Daphne which is running my chat rooms on port 8001. If the endpoint
does not include "ws", then Nginx references Gunicorn which is running my WSGI
application on port 8000.
4. After the images and containers are created, and the necessary packages and
   scripts are installed and running within the containers, local testing of
containers is done to ensure intended functionality.
5. Upon passing manual testing, I pushed my Docker images onto the Google Cloud
   Platform Container Registry.
6. I created an instance template from within Google Cloud and I provided a
   bash script to run on each virtual machine's startup. This script downloads
the published Docker images and creates and runs containers and scripts on the
specified ports. This script also works for updating currently installed images
and presently running containers.
7. I then created an instance group from this instance template and associated
   it with a static IP address that I reserved.
8. A load balancer was set up using Google Cloud Platform to balance website
   traffic. The main purpose for this was to be able to get an SSL
certification.
9. I then created an SSL certificate from within GCP. Lastly, I added SSL
   configuration information to my load balancer's frontend.
10. I purchased a domain name and associated my reserved static IP address
    which points to my instance group running my full application.

## Visuals

## Resources

[API-Football](https://www.api-football.com/)\
[API-NBA](https://api-sports.io/documentation/nba/v2#section/Authentication/RAPIDAPI-Account)\
[News API](https://newsapi.org/)
