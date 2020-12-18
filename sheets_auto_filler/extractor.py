# Custom Extractor for Arkavidia Verification
import requests
import pytz
import json
from datetime import datetime
from bs4 import BeautifulSoup

with open("api_creds.json") as f:
    API_DATA = json.loads(f.read())

IDS = {"CTF": 9, "Datavidia": 6, "CP": 1, "Arkalogica": 5, "Arkav Game Jam": 7}
MAIN = API_DATA["url"]
TEAMS = MAIN + "/team/?competition__id__exact="
CREDS = dict(sessionid=API_DATA["token"])
TASKS = ["Identitas Diri", "Foto Diri", "Verifikasi Status Siswa / Mahasiswa"]


def get_create_date(tag):
    return tag.has_attr("class") and "field-created_at" in tag["class"]


def get_teams(tag):
    return (
        tag.name == "tr"
        and tag.has_attr("class")
        and ("row1" in tag["class"] or "row2" in tag["class"])
    )


def get_tasks(tag):
    return tag.has_attr("class") and "has_original" in tag["class"]

def extract_data(competition):
    teams = []
    keep_track_teams = set()
    total_teams = 0
    page = 0
    id = IDS[competition]
    while True:
        data = scrapping(id, page, keep_track_teams)
        teams += data[0]
        total_teams = data[1]
        page += 1
        if page*100 >= total_teams:
            break
    return teams[::-1]

def scrapping(id, page, keep_track_teams):
    r = requests.get("{}{}&p={}".format(TEAMS, id, page), cookies=CREDS)

    soup = BeautifulSoup(r.text, "html.parser")
    del r

    total_teams = int(next(soup.find("form", {"id": "changelist-search"}).div.span.children).split(" ")[0])
    teams = []
    for row in soup.find_all(get_teams):
        team = {"failed": False}

        # Extract team's general info
        for info in row.children:
            # Get the id
            if "field-id" in info["class"]:
                id = info.a.string
                # Check in case of real time update
                if id in keep_track_teams:
                    team["failed"] = True
                    break
                team["id"] = id
                keep_track_teams.add(id)
                team["link"] = "{}/team/{}/change".format(MAIN, id)
            # Get team's members count
            elif "field-member_count" in info["class"]:
                team["members"] = info.string

        # Dont add same team to my teams list
        if team["failed"]:
            continue

        # Get team's detail
        r = requests.get(team["link"], cookies=CREDS)
        team_data = BeautifulSoup(r.text, "html.parser")

        # Get creation date
        team["created_at"] = team_data.find_all(get_create_date)[0].p.string

        # Init task value
        for task in TASKS:
            team[task] = [0, 0]
        team["Payment"] = 0
        task = None

        # Extract tasks' information
        for row2 in team_data.find_all(get_tasks):
            for info in row2.children:
                if not str(info).strip(): # Don't check CRLF
                    continue
                # Get task's name
                if "field-task" in info["class"]:
                    task = info.p.string.split(" - ")[-1]
                # Get task status
                elif "field-status" in info["class"]:
                    status = info.p.string
                    if task in TASKS:
                        if status == "Completed":
                            team[task][0] += 1
                        elif status == "Rejected":
                            team[task][1] = 1
                    elif task == "Payment":
                        if status == "Completed":
                            team[task] = 1
                        elif status == "Rejected":
                            team[task] = 2
        del team_data, r
        # Add data
        teams.append(
            [
                team["created_at"],
                team["link"],
                datetime.now(pytz.timezone("Asia/Jakarta")).strftime(
                    "%m/%d/%Y %H:%M:%S"
                ),
                team["id"],
                team["members"],
                team["Identitas Diri"][0],
                team["Identitas Diri"][1],
                team["Verifikasi Status Siswa / Mahasiswa"][0],
                team["Verifikasi Status Siswa / Mahasiswa"][1],
                team["Foto Diri"][0],
                team["Foto Diri"][1],
                team["Payment"],
            ]
        )
    del soup
    return (teams, total_teams)
