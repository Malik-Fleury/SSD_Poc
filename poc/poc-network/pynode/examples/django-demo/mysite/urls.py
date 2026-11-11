from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.urls import path

from pynode import node


def index(request):
    with connection.cursor() as c:  # vérifie que SQLite marche sur le téléphone
        c.execute("select sqlite_version()")
        sqlite = c.fetchone()[0]
    return HttpResponse(f"<h1>Django sur {node.NAME}</h1><p>SQLite {sqlite}</p><p><a href='/api'>JSON</a></p>")


def api(request):
    return JsonResponse(node.info(request.path))


urlpatterns = [path("", index), path("api", api)]
