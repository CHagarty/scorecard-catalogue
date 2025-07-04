import os
import json

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import quote, unquote


from helpers import apology, login_required
from datetime import datetime

# Configure application
app = Flask(__name__)

# TODO fix apology message


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("postgresql://golfdb_99x4_user:V7TvFN8p7Vt4DZVHf1Tb3QHbPV4T7TwD@dpg-d1k1o2ili9vc738vaa10-a/golfdb_99x4")  or "slqite:///project.db" # This should be set in Render or locally
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db = SQLAlchemy(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# -----------------------------------------------------------------------------------------------------
    # HOME PAGE
# -----------------------------------------------------------------------------------------------------


@app.route("/")
@login_required
def index():

    user_list = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    name = user_list[0]["nickname"]

    # DISPLAY MOST RECENT ROUND

    rounds = db.execute(
        "SELECT * FROM rounds WHERE user_id = ? ORDER BY date DESC, round_id DESC LIMIT 1", session["user_id"])
    scores = []
    players = []
    courses = []
    combined = []
    date = []
    recent_holes = rounds[0]["holes"]

    # Get scores for the latest round

    for i in range(len(rounds)):

        if rounds[i]["holes"] == 18:
            scores.append(db.execute(
                "SELECT * FROM score_18 WHERE round_id = ?", rounds[i]["round_id"]))
        else:
            scores.append(db.execute(
                "SELECT * FROM score_9 WHERE round_id = ?", rounds[i]["round_id"]))

            # Get course info for latest round

        if rounds[i]["course_18_id"]:
            result = db.execute("SELECT * FROM courses_18 WHERE course_id = ?",
                                rounds[i]["course_18_id"])
            courses.append(result[0] if result else None)
        else:
            result = db.execute("SELECT * FROM courses_9 WHERE course_id = ?",
                                rounds[i]["course_9_id"])
            courses.append(result[0] if result else None)

            # Get player names for round, if there are any

    for round_data in rounds:
        names = []
        for key in ["player_id_1", "player_id_2", "player_id_3"]:
            player_id = round_data.get(key)
            if player_id:
                result = db.execute("SELECT first_name FROM players WHERE player_id = ?", player_id)
                if result:
                    names.append(f"{result[0]['first_name']}")
        players.append(names)

        # Convert datetime to ex. "July 1, 2025"

    for round_data in rounds:
        date_str = round_data["date"]
        pretty_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %-d, %Y")
        date.append(pretty_date)

    combined = zip(rounds, scores, courses, players, date)

    # DISPLAY STATS ON HOMEPAGE

    # Get all rounds for this user
    rounds = db.execute("SELECT * FROM rounds WHERE user_id = ?", session["user_id"])

    albatrosses = eagles = birdies = pars = bogeys = double_bogeys = triple_bogeys = hole_in_one = 0
    total_18 = total_9 = total_front = total_back = best_18 = best_9 = best_front = best_back = 0
    rounds_played = 0
    rounds_18 = 0
    rounds_9 = 0

    for round_data in rounds:
        round_id = round_data["round_id"]
        holes = round_data["holes"]
        rounds_played += 1

        # Get course
        if round_data["course_18_id"]:
            course = db.execute("SELECT * FROM courses_18 WHERE course_id = ?",
                                round_data["course_18_id"])
        else:
            course = db.execute("SELECT * FROM courses_9 WHERE course_id = ?",
                                round_data["course_9_id"])

        # Get score
        if holes == 18:
            score = db.execute(
                "SELECT * FROM score_18 WHERE round_id = ? AND is_user = ?", round_id, 1)
        else:
            score = db.execute(
                "SELECT * FROM score_9 WHERE round_id = ? AND is_user = ?", round_id, 1)

        round_total = 0

        # Calculate stats
        for hole in range(1, holes + 1):
            if score and course:
                s = score[0][f"hole_{hole}"]
                p = course[0][f"par_{hole}"]
                round_total += s

            if s == p - 3:
                albatrosses += 1
            elif s == p - 2:
                eagles += 1
            elif s == p - 1:
                birdies += 1
            elif s == p:
                pars += 1
            elif s == p + 1:
                bogeys += 1
            elif s == p + 2:
                double_bogeys += 1
            elif s == p + 3:
                triple_bogeys += 1
            elif s == 1:
                hole_in_one += 1

        if holes == 18:
            total_18 += round_total
            rounds_18 += 1
            total_front += score[0]["front"]
            total_back += score[0]["back"]
            if best_18 == 0:
                best_18 = round_total
            else:
                if round_total < best_18:
                    best_18 = round_total
            if best_front == 0:
                best_front = score[0]["front"]
            else:
                if score[0]["front"] < best_front:
                    best_front = score[0]["front"]
            if best_back == 0:
                best_back = score[0]["back"]
            else:
                if score[0]["back"] < best_back:
                    best_back = score[0]["back"]
        else:
            total_9 += round_total
            rounds_9 += 1
            if best_9 == 0:
                best_9 = round_total
            else:
                if round_total < best_9:
                    best_9 = round_total

    average_18 = round(total_18 / rounds_18) if rounds_played else None
    average_9 = round(total_9 / rounds_9) if rounds_played else None
    average_front = round(total_front / rounds_18) if rounds_played else None
    average_back = round(total_back / rounds_18) if rounds_played else None

    # Calculate handicap index based on 8 best rounds from 20 most recent

    recent_20 = db.execute(
        "SELECT * FROM rounds WHERE user_id = ? ORDER BY date DESC, round_id DESC LIMIT 20", session["user_id"])

    recent_scores = []

    for round_data in recent_20:
        round_id = round_data["round_id"]
        holes = round_data["holes"]

        if holes == 18:
            score = db.execute(
                "SELECT total FROM score_18 WHERE round_id = ? AND is_user = ?", round_id, 1)
            total = score[0]["total"]
        else:
            score = db.execute(
                "SELECT total FROM score_9 WHERE round_id = ? AND is_user = ?", round_id, 1)
            total = score[0]["total"] * 2

        recent_scores.append(total)

    if recent_scores:
        best_8 = sorted(recent_scores)[:8]      # Handicap index formula provided by ChatGPT
        avg_best_8 = sum(best_8) / len(best_8)
        handicap_index = round((avg_best_8 - 72) * 0.96, 1)  # Assuming course rating is 72
    else:
        handicap_index = None

    stats = {
        "rounds_played": rounds_played,
        "handicap_index": handicap_index,
        "average_18": average_18,
        "average_9": average_9,
        "average_front": average_front,
        "average_back": average_back,
        "best_9": best_9,
        "best_18": best_18,
        "best_front": best_front,
        "best_back": best_back,
        "albatrosses": albatrosses,
        "eagles": eagles,
        "birdies": birdies,
        "pars": pars,
        "bogeys": bogeys,
        "double_bogeys": double_bogeys,
        "triple_bogeys": triple_bogeys,
        "hole_in_one": hole_in_one,


    }

    latest_score = scores[0][0]

    return render_template("index.html", name=name, combined=combined, stats=stats, latest_score=latest_score, recent_holes=recent_holes)


# -------------------------------------------------------------------------------------------------------------------------------------
    # COURSES
# -------------------------------------------------------------------------------------------------------------------------------------

# LIST USER'S COURSES

@app.route("/courses")
@login_required
def courses():

    items = db.execute("SELECT * FROM courses_18 WHERE user_id = ?", session["user_id"])

    return render_template("courses.html", items=items)

# SELECT 18 HOLE OR 9 HOLE COURSE

    # DECIDED TO ONLY ALLOW 18 HOLE COURSES BUT LEFT THE CODE FOR 9 HOLE OPTION FOR FUTURE USE


@app.route("/new_courses")
@login_required
def new_courses():

    return render_template("new_courses.html")

# CREATE A NEW 9 HOLE COURSE


@app.route("/new9", methods=["GET", "POST"])
@login_required
def new9():

    if request.method == "POST":

        # Ensure that all of the inputs were filled out
        if not request.form.get("course"):
            return apology("Must fill out course", 400)

        for i in range(1, 10):
            if not request.form.get(f"yards_{i}"):
                return apology("Must fill out yards for hole {i}", 400)

            if not request.form.get(f"handicap_{i}"):
                return apology("Must fill out handicap for hole {i}", 400)

            if not request.form.get(f"par_{i}"):
                return apology("Must fill out par for hole {i}", 400)

        if not request.form.get("front"):
            return apology("Must fill out front", 400)

        if not request.form.get("back"):
            return apology("Must fill out back", 400)

        if not request.form.get("total"):
            return apology("Must fill out total", 400)

        # Insert course details

        name = request.form.get("course")
        user_id = session["user_id"]
        total = int(request.form.get("total"))
        course_holes = 9

        db.execute("INSERT INTO courses_9 (name, user_id, total, course_holes) VALUES (?, ?, ?, ?)",
                   name, user_id, total, course_holes)

        course_list = db.execute("SELECT course_id FROM courses_9 WHERE user_id = ?", user_id)

        course_id = course_list[0]["course_id"]

        for i in range(1, 10):
            db.execute(f"UPDATE courses_9 SET yards_{i} = ?, handicap_{i} = ?, par_{i} = ? WHERE course_id = ?", int(
                request.form.get(f"yards_{i}")), int(request.form.get(f"handicap_{i}")), int(request.form.get(f"par_{i}")), course_id)

        return redirect("/")

    else:

        return render_template("new9.html")

# CREATE A NEW 18 HOLE COURSE


@app.route("/new18", methods=["GET", "POST"])
@login_required
def new18():

    if request.method == "POST":

        # Ensure that all of the inputs were filled out
        if not request.form.get("course"):
            return apology("Must fill out course", 400)

        for i in range(1, 19):
            if not request.form.get(f"yards_{i}"):
                return apology("Must fill out yards for hole {i}", 400)

            if not request.form.get(f"handicap_{i}"):
                return apology("Must fill out handicap for hole {i}", 400)

            if not request.form.get(f"par_{i}"):
                return apology("Must fill out par for hole {i}", 400)

        if not request.form.get("front_par"):
            return apology("Must fill out front par", 400)

        if not request.form.get("front_yards"):
            return apology("Must fill out front yards", 400)

        if not request.form.get("back_par"):
            return apology("Must fill out back par", 400)

        if not request.form.get("back_yards"):
            return apology("Must fill out back yards", 400)

        if not request.form.get("total_par"):
            return apology("Must fill out total par", 400)

        if not request.form.get("total_yards"):
            return apology("Must fill out total yards", 400)

        # Insert course details

        name = request.form.get("course")
        user_id = session["user_id"]
        front_par = int(request.form.get("front_par"))
        back_par = int(request.form.get("back_par"))
        total_par = int(request.form.get("total_par"))
        front_yards = int(request.form.get("front_yards"))
        back_yards = int(request.form.get("back_yards"))
        total_yards = int(request.form.get("total_yards"))
        course_holes = 18

        db.execute("INSERT INTO courses_18 (name, user_id, front, back, total, front_yards, back_yards, total_yards, course_holes) VALUES (?, ?, ?, ? , ?, ?, ?, ?, ?)",
                   name, user_id, front_par, back_par, total_par, front_yards, back_yards, total_yards, course_holes)
        course_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

        for i in range(1, 19):
            db.execute(f"UPDATE courses_18 SET yards_{i} = ?, handicap_{i} = ?, par_{i} = ? WHERE course_id = ?", int(
                request.form.get(f"yards_{i}")), int(request.form.get(f"handicap_{i}")), int(request.form.get(f"par_{i}")), course_id)

        return redirect("/")

    else:

        return render_template("new18.html")


# ----------------------------------------------------------------------------------------------------------------------------
        # ROUNDS
# ----------------------------------------------------------------------------------------------------------------------------

# ADD A NEW ROUND


@app.route("/add_round", methods=["GET", "POST"])
@login_required
def add_round():

    if request.method == "POST":

        # Ensure course was selected
        if not request.form.get("course"):
            return apology("Must select a course", 400)

        # Ensure date was filled out
        if not request.form.get("date"):
            return apology("Must fill out date", 400)

        # Retrieve initial data from form

        course = request.form.get("course")
        date = request.form.get("date")
        players = int(request.form.get("players"))
        holes = int(request.form.get("holes"))

        # JSON SOLUTION PROVIDED BY CHATGPT

        if players > 1:
            player_ids = json.loads(request.form.get("player_ids"))

        course_list = db.execute(
            "SELECT * FROM courses_18 WHERE name = ? AND user_id = ?", course, session["user_id"])

        if not course_list:
            course_list = db.execute(
                "SELECT * FROM courses_9 WHERE name = ? AND user_id = ?", course, session["user_id"])

            if not course_list:
                return apology("Course does not exist", 400)

            else:
                course_id = course_list[0]["course_id"]
                course_holes = course_list[0]["course_holes"]

        else:
            course_id = course_list[0]["course_id"]
            course_holes = course_list[0]["course_holes"]

        # If a solo round, insert just the user_id, course_id, date, and holes into rounds table

            # 1 player, 18 hole round

        if players == 1 and course_holes == 18 and holes == 18:

            db.execute("INSERT INTO rounds (course_18_id, user_id, date, holes) VALUES (?, ?, ?, ?)",
                       course_id, session["user_id"], date, holes)
            round_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

            db.execute("INSERT INTO score_18 (round_id, user_id, is_user) VALUES (?, ?, ?)",
                       round_id, session["user_id"], True)
            score_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

            front = 0
            back = 0
            total = 0

            # Get score for each hole from form and calculate front, back, and total

            for i in range(1, holes + 1):
                score = int(request.form.get(f"player_0_score_{i}"))
                if i < 10:
                    front += score
                    db.execute(f"UPDATE score_18 SET front = ? WHERE score_id = ?", front, score_id)
                if i > 9 and holes < 19:
                    back += score
                    db.execute(f"UPDATE score_18 SET back = ? WHERE score_id = ?", back, score_id)
                total += score

                db.execute(
                    f"UPDATE score_18 SET hole_{i} = ?, total = ? WHERE score_id = ?", score, total, score_id)

                # 1 player, 9 hole round

        elif players == 1 and course_holes == 18 and holes == 9:

            db.execute("INSERT INTO rounds (course_18_id, user_id, date, holes) VALUES (?, ?, ?, ?)",
                       course_id, session["user_id"], date, holes)
            round_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

            db.execute("INSERT INTO score_9 (round_id, user_id, is_user) VALUES (?, ?, ?)",
                       round_id, session["user_id"], True)
            score_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

            total = 0

            for i in range(1, holes + 1):
                score = int(request.form.get(f"player_0_score_{i}"))
                total += score
                db.execute(
                    f"UPDATE score_9 SET hole_{i} = ?, total = ? WHERE score_id = ?", score, total, score_id)

            # 1 player, 9 hole course
            # 9 HOLE COURSES NOT CURRENTLY USED BUT CODE IS LEFT FOR FUTURE USE

        elif players == 1 and course_holes == 9:

            db.execute("INSERT INTO rounds (course_9_id, user_id, date, holes) VALUES (?, ?, ?, ?)",
                       course_id, session["user_id"], date, holes)
            round_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

            db.execute("INSERT INTO score_9 (round_id, user_id, is_user) VALUES (?, ?, ?)",
                       round_id, session["user_id"], True)
            score_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

            total = 0

            for i in range(1, holes + 1):
                score = int(request.form.get(f"player_0_score_{i}"))
                total += score
                db.execute(
                    f"UPDATE score_9 SET hole_{i} = ?, total = ? WHERE score_id = ?", score, total, score_id)

        elif players > 4:
            return apology("Too many players", 400)

        # If more than one player, add players ids as well
        else:

            if course_holes == 18:
                db.execute("INSERT INTO rounds (course_18_id, user_id, date, holes) VALUES (?, ?, ?, ?)",
                           course_id, session["user_id"], date, holes)

                # 9 HOLE COURSES NOT CURRENTLY USED, LEFT FOR FUTURE USE

            elif course_holes == 9:
                db.execute("INSERT INTO rounds (course_9_id, user_id, date, holes) VALUES (?, ?, ?, ?)",
                           course_id, session["user_id"], date, holes)

            round_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

            for i in range(1, players):
                player_id = player_ids[i - 1]
                if not player_id:
                    return apology(f"Must select player {i}", 400)
                db.execute(
                    f"UPDATE rounds SET player_id_{i} = ? WHERE round_id = ?", player_id, round_id)

            # MULTIPLE PLAYERS, 18 HOLE ROUND

            if holes == 18:

                # Record user's scores

                db.execute("INSERT INTO score_18 (round_id, user_id, is_user) VALUES (?, ?, ?)",
                           round_id, session["user_id"], True)
                score_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

                front = 0
                back = 0
                total = 0

                for i in range(1, holes + 1):
                    score = int(request.form.get(f"player_0_score_{i}"))
                    if i < 10:
                        front += score
                        db.execute(f"UPDATE score_18 SET front = ? WHERE score_id = ?",
                                   front, score_id)
                    elif i > 9 and holes < 19:
                        back += score
                        db.execute(f"UPDATE score_18 SET back = ? WHERE score_id = ?", back, score_id)
                    total += score
                    db.execute(
                        f"UPDATE score_18 SET hole_{i} = ?, total = ? WHERE score_id = ?", score, total, score_id)

                # Record player scores
                if players > 1:

                    # Insert initial information into score_18 and then retrieve score_id
                    for player in range(1, players):
                        player_id = player_ids[player - 1]
                        db.execute("INSERT INTO score_18 (round_id, user_id, player_id) VALUES (?, ?, ?)",
                                   round_id, session["user_id"], player_id)
                        score_id = db.execute("SELECT last_insert_rowid()")[
                            0]["last_insert_rowid()"]

                        front = 0
                        back = 0
                        total = 0

                        # Update player scores from round, calculate front, back, and total
                        for hole in range(1, holes + 1):
                            score = int(request.form.get(f"player_{player}_score_{hole}"))
                            if hole < 10:
                                front += score
                                db.execute(
                                    f"UPDATE score_18 SET front = ? WHERE score_id = ?", front, score_id)
                            if hole > 9 and holes < 19:
                                back += score
                                db.execute(
                                    f"UPDATE score_18 SET back = ? WHERE score_id = ?", back, score_id)
                            total += score
                            db.execute(
                                f"UPDATE score_18 SET hole_{hole} = ?, total = ? WHERE score_id = ?", score, total, score_id)
            else:
                # 9 hole round. Record user's scores

                db.execute("INSERT INTO score_9 (round_id, user_id, is_user) VALUES (?, ?, ?)",
                           round_id, session["user_id"], True)
                score_id = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

                total = 0

                for i in range(1, holes + 1):
                    score = int(request.form.get(f"player_0_score_{i}"))
                    total += score
                    db.execute(
                        f"UPDATE score_9 SET hole_{i} = ?, total = ? WHERE score_id = ?", score, total, score_id)

                # Record player scores
                if players > 1:

                    # Insert initial information into score_18 and then retrieve score_id
                    for player in range(1, players):
                        player_id = player_ids[player - 1]
                        db.execute("INSERT INTO score_9 (round_id, user_id, player_id) VALUES (?, ?, ?)",
                                   round_id, session["user_id"], player_id)
                        score_id = db.execute("SELECT last_insert_rowid()")[
                            0]["last_insert_rowid()"]
                        total = 0

                        # Update player scores from round, calculate total
                        for hole in range(1, holes + 1):
                            score = int(request.form.get(f"player_{player}_score_{hole}"))
                            total += score
                            db.execute(
                                f"UPDATE score_9 SET hole_{hole} = ?, total = ? WHERE score_id = ?", score, total, score_id)

        return redirect("/")

    else:
        # If request = GET retreive the players and holes from new_round_players
        players = request.args.get("players", type=int)
        holes = request.args.get("holes", type=int)

        # If more than one player, get the player ids
        if players > 1:
            player_ids = request.args.get("player_ids")
            if not player_ids:
                return apology("No players selected", 400)
            player_ids = json.loads(unquote(player_ids))  # JSON SOLUTION PROVIDED BY CHATGPT

        # Retrieve courses

        course_18 = db.execute("SELECT * FROM courses_18 WHERE user_id = ?", session["user_id"])
        course_9 = db.execute("SELECT * FROM courses_9 WHERE user_id = ?", session["user_id"])

        # Retrieve player names

        name_list = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Get user's nickname
        name = name_list[0]["nickname"]

        # Add user's nickname as the first name in player_names list
        player_names = []
        player_names.append(name)

        # If multiple players, add their first names to the player_names list
        if players > 1:
            for player_id in player_ids:
                player = db.execute(
                    "SELECT first_name FROM players WHERE player_id = ? AND user_id = ?", player_id, session["user_id"])
                if player:
                    player_names.append(f"{player[0]['first_name']}")
                else:
                    return apology("Player not found", 400)

        if players == 1:
            return render_template("add_round.html", player_names=player_names, players=players, holes=holes, course_18=course_18, course_9=course_9)

        else:
            return render_template("add_round.html", player_names=player_names, player_ids=player_ids, players=players, holes=holes, course_18=course_18, course_9=course_9)

# LIST USER'S ROUNDS


@app.route("/my_rounds")
@login_required
def my_rounds():

    # Get user's nickname
    user_name = db.execute("SELECT nickname FROM users WHERE id = ?", session["user_id"])
    name = user_name[0]["nickname"]

    rounds = db.execute(
        "SELECT * FROM rounds WHERE user_id = ? ORDER BY date DESC, round_id DESC", session["user_id"])

    scores = []
    players = []
    courses = []
    combined = []
    dates = []

    for i in range(len(rounds)):

        # Get either score_18 or score_9 depending on number of holes
        if rounds[i]["holes"] == 18:
            scores.append(db.execute(
                "SELECT * FROM score_18 WHERE round_id = ?", rounds[i]["round_id"]))
        else:
            scores.append(db.execute(
                "SELECT * FROM score_9 WHERE round_id = ?", rounds[i]["round_id"]))

        # 9 HOLE COURSES NOT CURRENTLY USED, CODE LEFT FOR FUTURE USE
        if rounds[i]["course_18_id"]:
            result = db.execute("SELECT * FROM courses_18 WHERE course_id = ?",
                                rounds[i]["course_18_id"])
            courses.append(result[0] if result else None)
        else:
            result = db.execute("SELECT * FROM courses_9 WHERE course_id = ?",
                                rounds[i]["course_9_id"])
            courses.append(result[0] if result else None)

    for round_data in rounds:
        names = []
        for key in ["player_id_1", "player_id_2", "player_id_3"]:
            player_id = round_data.get(key)
            # IF DECIDING TO USE INTITALS FOR 4 PLAYER ROUNDS, NEED TO APPEND LAST NAME
            if player_id:
                result = db.execute(
                    "SELECT first_name, last_name FROM players WHERE player_id = ?", player_id)
                if result:
                    names.append(f"{result[0]['first_name']}")
        players.append(names)

    # Change from datetime to ex. "July 1, 2025
    for round_data in rounds:
        date_str = round_data["date"]
        pretty_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %-d, %Y")
        dates.append(pretty_date)

    combined = zip(rounds, scores, courses, players, dates)  # ZIP SOLUTION PROVIDED BY CHATGPT

    return render_template("my_rounds.html", name=name, combined=combined)

    # rounds=rounds, scores=scores, courses=courses, players=players)


# FILL OUT NEW ROUND INFORMATION (NUMBER OF PLAYERS AND HOLES)


@app.route("/new_round", methods=["GET", "POST"])
@login_required
def new_round():

    if request.method == "POST":

        # Ensure number of players was filled out

        if not request.form.get("players"):
            return apology("Must select number of players", 400)

        if not request.form.get("holes"):
            return apology("Must select number of holes", 400)

        players = int(request.form.get("players"))

        holes = request.form.get("holes")

        # If solo round, just go straight to add_round
        if players == 1:
            return redirect(url_for("add_round", players=players, holes=holes))

        # If multiple players, redirect to new_round_players
        else:
            return redirect(url_for("new_round_players", players=players, holes=holes))

    else:
        return render_template("new_round.html")

# IF MORE THAN ONE PLAYER, SELECT ADDITIONAL PLAYERS FROM MY PLAYERS


@app.route("/new_round_players", methods=["GET", "POST"])
@login_required
def new_round_players():

    if request.method == "POST":

        # Ensure number of players was filled out

        if not request.form.get("players"):
            return apology("Must select number of players", 400)

        players = request.form.get("players", type=int)

        holes = request.form.get("holes", type=int)

        # Get player ids

        player_ids = []

        for i in range(players - 1):
            player_id = request.form.get(f"player_ids_{i}")
            if not player_id:
                return apology(f"Must select player {i + 1}", 400)

            player_ids.append(player_id)

        # JSON SOLUTION PROVIDED BY CHATGPT
        return redirect(url_for("add_round", players=players, holes=holes, player_ids=quote(json.dumps(player_ids))))

    else:

        players = request.args.get("players", type=int)
        holes = request.args.get("holes", type=int)
        player_names = db.execute("SELECT * FROM players WHERE user_id = ?", session["user_id"])

        return render_template("new_round_players.html", players=players, holes=holes, player_names=player_names)


# -------------------------------------------------------------------------------------------------------------------------
        # PLAYERS
# -------------------------------------------------------------------------------------------------------------------------

# ADD NEW PLAYERS


@app.route("/add_players", methods=["GET", "POST"])
@login_required
def add_players():

    if request.method == "POST":

        # Get number of players to be added
        players = int(request.form.get("num_players"))

        # Ensure first name and last name for new player(s) was provided
        for i in range(1, players):
            if not request.form.get(f"first_name_{i}"):
                return apology(f"Must fill out player {i} first name", 400)
            if not request.form.get(f"last_name_{i}"):
                return apology(f"Must fill out player {i} last name", 400)

        # Add player information to players table
        for i in range(1, players):
            db.execute("INSERT INTO players (first_name, last_name, user_id) VALUES (?, ?, ?)", request.form.get(
                f"first_name_{i}"), request.form.get(f"last_name_{i}"), session["user_id"])

        return redirect("/players")

    else:

        players = request.args.get("players", type=int)

        players += 1

        return render_template("add_players.html", players=players)


# SELECT THE NUMBER OF PLAYERS


@app.route("/number_players", methods=["GET", "POST"])
@login_required
def number_players():

    if request.method == "POST":

        # Ensure number of players was filled out

        if not request.form.get("players"):
            return apology("Must select number of players", 400)

        players = request.form.get("players")

        return redirect(url_for("add_players", players=players))

    else:
        return render_template("number_players.html")

# LIST USER'S PLAYERS


@app.route("/players")
@login_required
def players():

    players = db.execute("SELECT * FROM players WHERE user_id = ?", session["user_id"])

    # DISPLAY STATS Of PLAYERS

    # Get all rounds for this user
    rounds = db.execute("SELECT * FROM rounds WHERE user_id = ?", session["user_id"])

    for player in players:

        birdies = pars = bogeys = eagles = double_bogeys = triple_bogeys = holes_in_one = total_score = 0
        rounds_played = 0
        average_score = 0

        for round_data in rounds:
            round_id = round_data["round_id"]
            holes = round_data["holes"]
            player_id = player["player_id"]

            # Get course
            if round_data["course_18_id"]:
                course = db.execute("SELECT * FROM courses_18 WHERE course_id = ?",
                                    round_data["course_18_id"])
            # 9 HOLE COURSES NOT CURRENTLY USED, CODE LEFT FOR FUTURE USE
            else:
                course = db.execute("SELECT * FROM courses_9 WHERE course_id = ?",
                                    round_data["course_9_id"])

            # Get score
            if holes == 18:
                score = db.execute(
                    "SELECT * FROM score_18 WHERE round_id = ? AND player_id = ?", round_id, player_id)
            else:
                score = db.execute(
                    "SELECT * FROM score_9 WHERE round_id = ? AND player_id = ?", round_id, player_id)

            # Calculate birdies, pars, etc
            if score:
                rounds_played += 1
                round_total = 0

                for hole in range(1, holes + 1):
                    if score and course:
                        s = score[0][f"hole_{hole}"]
                        p = course[0][f"par_{hole}"]
                        round_total += s

                    if s == p - 1:
                        birdies += 1
                    elif s == p - 2:
                        eagles += 1
                    elif s == p:
                        pars += 1
                    elif s == p + 1:
                        bogeys += 1
                    elif s == p + 2:
                        double_bogeys += 1
                    elif s == p + 3:
                        triple_bogeys += 1
                    elif s == 1:
                        holes_in_one += 1

                if holes == 18:
                    total_score += round_total
                else:
                    total_score += (round_total * 2)

        # Calculate average score
        # TODO Split average score into averages for 18 and 9 hole rounds

        average_score = round(total_score / rounds_played) if rounds_played else None

        # Calculate the player's handicap index based on best 8 rounds in most recent 20 rounds
        recent_20 = db.execute(
            "SELECT * FROM rounds WHERE player_id_1 = ? OR player_id_2 = ? or player_id_3 = ? ORDER BY date DESC, round_id DESC LIMIT 20", player_id, player_id, player_id)

        recent_scores = []

        for round_data in recent_20:
            round_id = round_data["round_id"]
            holes = round_data["holes"]

            if holes == 18:
                score = db.execute(
                    "SELECT total FROM score_18 WHERE round_id = ? AND player_id = ?", round_id, player_id)
                total = score[0]["total"]
            else:
                score = db.execute(
                    "SELECT total FROM score_9 WHERE round_id = ? AND player_id = ?", round_id, player_id)
                # Multiply 9 hole total by 2 to approximate an 18 hole rounds
                total = score[0]["total"] * 2

            recent_scores.append(total)

        if recent_scores:
            best_8 = sorted(recent_scores)[:8]      # Handicap index formula provided by ChatGPT
            avg_best_8 = sum(best_8) / len(best_8)
            handicap_index = round((avg_best_8 - 72) * 0.96, 1)  # Assuming course rating is 72
        else:
            handicap_index = None

        db.execute("UPDATE players SET rounds_played = ?, average_score = ?, birdies = ?, pars = ?, bogeys = ?, handicap = ?, eagles = ?, double_bogeys = ?, triple_bogeys = ?, holes_in_one = ? WHERE player_id = ?",
                   rounds_played, average_score, birdies, pars, bogeys, handicap_index, eagles, double_bogeys, triple_bogeys, holes_in_one, player_id)

        players = db.execute(
            "SELECT * FROM players WHERE user_id = ? ORDER BY rounds_played DESC", session["user_id"])

    return render_template("players.html", players=players)


# --------------------------------------------------------------------------------------------------------------------------------
    # LOGIN, LOGOUT, REGISTER
# --------------------------------------------------------------------------------------------------------------------------------

# LOGIN ROUTE FROM CS50 FINANCE

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# LOGOUT ROUTE FROM CS50 FINANCE

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# REGISTER

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure nickname was submitted
        if not request.form.get("nickname"):
            return apology("must provide nickname", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        nickname = request.form.get("nickname")

        # Check if username already exists

        new_username = request.form.get("username")

        check_username_list = db.execute(
            "SELECT username FROM users WHERE username = ?", new_username)

        # Return apology if username already exists

        if check_username_list:
            return apology("Username already exists", 400)

        password = request.form.get("password")

        confirm_password = request.form.get("confirmation")

        # Return apology if password and confirm password doesn't match
        if password != confirm_password:
            return apology("Passwords do not match", 400)

        hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, hash, nickname) VALUES (?, ?, ?)",
                       new_username, hash, nickname)

        except:
            return apology("Username already exists", 400)

        return redirect("/")

    else:
        return render_template("register.html")
