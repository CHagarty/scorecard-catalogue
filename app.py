import os
import json

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import quote, unquote


from helpers import apology, login_required
from datetime import datetime
from models import db, Course18, Course9, Score18, Score9, Round, Player, User 

# Configure application
app = Flask(__name__)

# TODO fix apology message


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://scorecarddb_wdu7_user:ZDmoeidlKgUr7k68ldDPO9Y38Dw7ZMXO@dpg-d1m1fundiees738vlc00-a.ohio-postgres.render.com/scorecarddb_wdu7"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


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

    user = User.query.get(session["user_id"])
    name = user.nickname


    # DISPLAY MOST RECENT ROUND

    round_data = Round.query.filter_by(user_id=session["user_id"]) \
            .order_by(Round.date.desc(), Round.round_id.desc()) \
            .first()

    scores = []
    players = []
    courses = []
    combined = []
    date = []
    recent_holes = round_data.holes if round_data else 0
    latest_score = 0

    # Get scores for the latest round

    if round_data:

        if round_data.holes == 18:
            score_list = Score18.query.filter_by(round_id=round_data.round_id).all()
            scores.append(score_list)
            latest_score = score_list[0].total if score_list else 0
            
        else:
            score_list = Score9.query.filter_by(round_id=round_data.round_id).all()
            scores.append(score_list)
            latest_score = score_list[0].total if score_list else 0 
            
            # Get course info for latest round

        if round_data.course_18_id:
            course = Course18.query.get(round_data.course_18_id)
            courses.append(course)

        else:
            course = Course9.query.get(round_data.course_9_id)
            courses.append(course)

            # Get player names for round, if there are any

        
        names = []
        for player_id in [round_data.player_id_1, round_data.player_id_2, round_data.player_id_3]:
            if player_id:
                player = Player.query.get(player_id)
                if player:
                    names.append(player.first_name)
        players.append(names)


        # Convert datetime to ex. "July 1, 2025"

        date_str = round_data.date
        pretty_date = date_str.strftime("%B %-d, %Y")
        date.append(pretty_date)

        combined = zip([round_data], scores, courses, players, date)

    # DISPLAY STATS ON HOMEPAGE

    # Get all rounds for this user
    rounds = Round.query.filter_by(user_id=session["user_id"]).all()

    albatrosses = eagles = birdies = pars = bogeys = double_bogeys = triple_bogeys = hole_in_one = 0
    total_18 = total_9 = total_front = total_back = best_18 = best_9 = best_front = best_back = 0
    rounds_played = 0
    rounds_18 = 0
    rounds_9 = 0

    for round_data in rounds:
        round_id = round_data.round_id
        holes = round_data.holes
        rounds_played += 1

        # Get course
        if round_data.course_18_id:
            course = Course18.query.get(round_data.course_18_id)
        else:
            course = Course9.query.get(round_data.course_9_id)

        # Get score
        if holes == 18:
            score = Score18.query.filter_by(round_id=round_id, is_user=True).first()
        else:
            score = Score9.query.filter_by(round_id=round_id, is_user=True).first()

        round_total = 0

        # Calculate stats
        for hole in range(1, holes + 1):
            if score and course:
                s = getattr(score, f"hole_{hole}")
                p = getattr(course, f"par_{hole}")
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
            total_front += score.front
            total_back += score.back
            if best_18 == 0:
                best_18 = round_total
            else:
                if round_total < best_18:
                    best_18 = round_total
            if best_front == 0:
                best_front = score.front
            else:
                if score.front < best_front:
                    best_front = score.front
            if best_back == 0:
                best_back = score.back
            else:
                if score.back < best_back:
                    best_back = score.back
        else:
            total_9 += round_total
            rounds_9 += 1
            if best_9 == 0:
                best_9 = round_total
            else:
                if round_total < best_9:
                    best_9 = round_total

    average_18 = round(total_18 / rounds_18) if rounds_18 else 0
    average_9 = round(total_9 / rounds_9) if rounds_9 else 0
    average_front = round(total_front / rounds_18) if rounds_18 else 0
    average_back = round(total_back / rounds_18) if rounds_18 else 0

    # Calculate handicap index based on 8 best rounds from 20 most recent

    recent_20 = Round.query.filter_by(user_id=session["user_id"]) \
                .order_by(Round.date.desc(), Round.round_id.desc()) \
                .limit(20).all()

    recent_scores = []

    for round_data in recent_20:
        round_id = round_data.round_id
        holes = round_data.holes

        if holes == 18:
            score = Score18.query.filter_by(round_id=round_id, is_user=True).first()
            total = score.total if score else None
        else:
            score = Score9.query.filter_by(round_id=round_id, is_user=True).first()
            total = score.total * 2 if score else None

        if total is not None:
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

    return render_template("index.html", name=name, combined=combined, stats=stats, latest_score=latest_score, recent_holes=recent_holes)


# -------------------------------------------------------------------------------------------------------------------------------------
    # COURSES
# -------------------------------------------------------------------------------------------------------------------------------------

# LIST USER'S COURSES

@app.route("/courses")
@login_required
def courses():
    
    items = Course18.query.filter_by(user_id=session["user_id"]).all()

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

        # Create new course instance
        course = Course9(name=name, user_id=user_id, total=total, course_holes=course_holes)

        # Set hole info dynamically for holes 1 through 9
        for i in range(1, 10):
            setattr(course, f'yards_{i}', int(request.form.get(f'yards_{i}')))
            setattr(course, f'handicap_{i}', int(request.form.get(f'handicap_{i}')))
            setattr(course, f'par_{i}', int(request.form.get(f'par_{i}')))

        # Add and commit
        db.session.add(course)
        db.session.commit()

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

        # Create course instance
        course = Course18(
            name=name,
            user_id=user_id,
            front=front_par,
            back=back_par,
            total=total_par,
            front_yards=front_yards,
            back_yards=back_yards,
            total_yards=total_yards,
            course_holes=course_holes
        )

        # Set hole-by-hole data dynamically
        for i in range(1, 19):
            setattr(course, f"yards_{i}", int(request.form.get(f"yards_{i}")))
            setattr(course, f"handicap_{i}", int(request.form.get(f"handicap_{i}")))
            setattr(course, f"par_{i}", int(request.form.get(f"par_{i}")))

        # Add to DB and commit
        db.session.add(course)
        db.session.commit()

        return redirect("/courses")

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

        course_obj = Course18.query.filter_by(name=course, user_id=session["user_id"]).first()

        if not course_obj:
            course_obj = Course9.query.filter_by(name=course, user_id=session["user_id"]).first()

            if not course_obj:
                return apology("Course does not exist", 400)

            else:
                course_id = course_obj.course_id
                course_holes = course_obj.course_holes

        else:
            course_id = course_obj.course_id
            course_holes = course_obj.course_holes

        # If a solo round, insert just the user_id, course_id, date, and holes into rounds table

            # 1 player, 18 hole round

        if players == 1 and course_holes == 18 and holes == 18:

            # 1. Create new Round
            round_obj = Round(
                course_18_id=course_id,
                user_id=session["user_id"],
                date=date,
                holes=holes
            )
            db.session.add(round_obj)
            db.session.flush()  # Ensures round_obj.round_id is populated before committing

            # 2. Create new Score18 record
            score_obj = Score18(
                round_id=round_obj.round_id,
                user_id=session["user_id"],
                is_user=True
            )
            db.session.add(score_obj)

            # 3. Gather hole-by-hole scores
            front = 0
            back = 0
            total = 0

            for i in range(1, 19):  # holes == 18
                score = int(request.form.get(f"player_0_score_{i}"))
                setattr(score_obj, f"hole_{i}", score)
                total += score
                if i <= 9:
                    front += score
                else:
                    back += score

            score_obj.front = front
            score_obj.back = back
            score_obj.total = total

            # 4. Commit everything
            db.session.commit()

            # Optionally get score_id and round_id after commit
            score_id = score_obj.score_id
            round_id = round_obj.round_id

                # 1 player, 9 hole round

        elif players == 1 and course_holes == 18 and holes == 9:

            # 1. Create new Round
            round_obj = Round(
                course_18_id=course_id,
                user_id=session["user_id"],
                date=date,
                holes=holes
            )
            db.session.add(round_obj)
            db.session.flush()  # Ensures round_obj.round_id is populated before committing

            # 2. Create new Score9 record
            score_obj = Score9(
                round_id=round_obj.round_id,
                user_id=session["user_id"],
                is_user=True
            )
            db.session.add(score_obj)

            total = 0

            for i in range(1, 10):  # holes == 9
                score = int(request.form.get(f"player_0_score_{i}"))
                setattr(score_obj, f"hole_{i}", score)
                total += score
                
            score_obj.total = total

            # 4. Commit everything
            db.session.commit()

            # 1 player, 9 hole course
            # 9 HOLE COURSES NOT CURRENTLY USED BUT CODE IS LEFT FOR FUTURE USE

        elif players == 1 and course_holes == 9:

            # 1. Create new Round
            round_obj = Round(
                course_9_id=course_id,
                user_id=session["user_id"],
                date=date,
                holes=holes
            )
            db.session.add(round_obj)
            db.session.flush()  # Ensures round_obj.round_id is populated before committing

            # 2. Create new Score9 record
            score_obj = Score9(
                round_id=round_obj.round_id,
                user_id=session["user_id"],
                is_user=True
            )
            db.session.add(score_obj)

            total = 0

            for i in range(1, 10):  # holes == 9
                score = int(request.form.get(f"player_0_score_{i}"))
                setattr(score_obj, f"hole_{i}", score)
                total += score
                
            score_obj.total = total

            # 4. Commit everything
            db.session.commit()
            
        elif players > 4:
            return apology("Too many players", 400)

        # If more than one player, add players ids as well
        else:

            
            # Create Round object (support both 18 and 9 holes)
            round_obj = Round(
                course_18_id=course_id if course_holes == 18 else None,
                course_9_id=course_id if course_holes == 9 else None,
                user_id=session["user_id"],
                date=date,
                holes=holes
            )
            db.session.add(round_obj)
            db.session.flush()  # Populate round_obj.round_id before continuing

            # Add player IDs (player_id_1, player_id_2, etc.)
            for i in range(1, players):  # Skip index 0 (user)
                player_id = player_ids[i - 1]
                if not player_id:
                    return apology(f"Must select player {i}", 400)

                # Dynamically set player_id_1, player_id_2, etc.
                setattr(round_obj, f"player_id_{i}", player_id)

            db.session.commit()
            round_id = round_obj.round_id


            # MULTIPLE PLAYERS, 18 HOLE ROUND

            if holes == 18:
                # Record user's score
                user_score = Score18(
                    round_id=round_id,
                    user_id=session["user_id"],
                    is_user=True
                )

                front = 0
                back = 0
                total = 0

                for i in range(1, 19):  # holes = 18
                    score = int(request.form.get(f"player_0_score_{i}"))
                    setattr(user_score, f"hole_{i}", score)
                    total += score
                    if i <= 9:
                        front += score
                    else:
                        back += score

                user_score.front = front
                user_score.back = back
                user_score.total = total

                db.session.add(user_score)

                # Record other players' scores
                if players > 1:
                    for player in range(1, players):
                        player_id = player_ids[player - 1]
                        player_score = Score18(
                            round_id=round_id,
                            user_id=session["user_id"],
                            player_id=player_id,
                            is_user=False
                        )

                        front = 0
                        back = 0
                        total = 0

                        for hole in range(1, 19):
                            score = int(request.form.get(f"player_{player}_score_{hole}"))
                            setattr(player_score, f"hole_{hole}", score)
                            total += score
                            if hole <= 9:
                                front += score
                            else:
                                back += score

                        player_score.front = front
                        player_score.back = back
                        player_score.total = total

                        db.session.add(player_score)

                # Commit all at once
                db.session.commit()

            else:
                # 9 hole round. Record user's scores

                if holes == 9:
                    # Record user's 9-hole score
                    user_score = Score9(
                        round_id=round_id,
                        user_id=session["user_id"],
                        is_user=True
                    )

                    total = 0

                    for i in range(1, 10):
                        score = int(request.form.get(f"player_0_score_{i}"))
                        setattr(user_score, f"hole_{i}", score)
                        total += score

                    user_score.total = total
                    db.session.add(user_score)

                    # Record other players’ scores
                    if players > 1:
                        for player in range(1, players):
                            player_id = player_ids[player - 1]

                            player_score = Score9(
                                round_id=round_id,
                                user_id=session["user_id"],  # scorer's ID (not the player's)
                                player_id=player_id,
                                is_user=False
                            )

                            total = 0
                            for hole in range(1, 10):
                                score = int(request.form.get(f"player_{player}_score_{hole}"))
                                setattr(player_score, f"hole_{hole}", score)
                                total += score

                            player_score.total = total
                            db.session.add(player_score)

                    db.session.commit()

        return redirect("/")

    else:
        # GET request: retrieve number of players and holes
        players = request.args.get("players", type=int)
        holes = request.args.get("holes", type=int)

        # Get player IDs if multiplayer
        if players > 1:
            player_ids = request.args.get("player_ids")
            if not player_ids:
                return apology("No players selected", 400)
            player_ids = json.loads(unquote(player_ids))  # JSON decoded player list

        # Retrieve 18- and 9-hole courses for this user
        course_18 = Course18.query.filter_by(user_id=session["user_id"]).all()
        course_9 = Course9.query.filter_by(user_id=session["user_id"]).all()

        # Get user's nickname from users table
        user = User.query.get(session["user_id"])
        if not user:
            return apology("User not found", 400)

        # Build player_names list with user's nickname
        player_names = [user.nickname]

        # Add other player names if multiplayer
        if players > 1:
            for player_id in player_ids:
                player = Player.query.filter_by(player_id=player_id, user_id=session["user_id"]).first()
                if player:
                    player_names.append(player.first_name)
                else:
                    return apology("Player not found", 400)

        # Render template
        return render_template(
            "add_round.html",
            player_names=player_names,
            player_ids=player_ids if players > 1 else None,
            players=players,
            holes=holes,
            course_18=course_18,
            course_9=course_9
        )


# LIST USER'S ROUNDS


@app.route("/my_rounds")
@login_required
def my_rounds():

    # Get user's nickname
    user = User.query.get(session["user_id"])
    if not user:
        return apology("User not found", 400)
    name = user.nickname

    # Get all rounds for the user, ordered by most recent
    rounds = Round.query.filter_by(user_id=session["user_id"]) \
        .order_by(Round.date.desc(), Round.round_id.desc()).all()

    scores = []
    players = []
    courses = []
    dates = []

    for round_obj in rounds:
        # Get score record
        if round_obj.holes == 18:
            score = Score18.query.filter_by(round_id=round_obj.round_id).all()
        else:
            score = Score9.query.filter_by(round_id=round_obj.round_id).all()
        scores.append(score)

        # Get course info
        if round_obj.course_18_id:
            course = Course18.query.filter_by(course_id=round_obj.course_18_id).first()
        else:
            course = Course9.query.filter_by(course_id=round_obj.course_9_id).first()
        courses.append(course)

        # Get player names
        names = []
        for key in ["player_id_1", "player_id_2", "player_id_3"]:
            player_id = getattr(round_obj, key)
            if player_id:
                player = Player.query.filter_by(player_id=player_id).first()
                if player:
                    names.append(player.first_name)
        players.append(names)

        # Format date
        pretty_date = round_obj.date.strftime("%B %-d, %Y")
        dates.append(pretty_date)

    # Combine everything
    combined = zip(rounds, scores, courses, players, dates)

    return render_template("my_rounds.html", name=name, combined=combined)





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
        player_names = Player.query.filter_by(user_id=session["user_id"]).all()

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
            first_name = request.form.get(f"first_name_{i}")
            last_name = request.form.get(f"last_name_{i}")

            player = Player(
                first_name=first_name,
                last_name=last_name,
                user_id=session["user_id"]
            )

            db.session.add(player)

        db.session.commit()


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

    # TODO Split average score into averages for 18 and 9 hole rounds

    # Get all players for current user
    players = Player.query.filter_by(user_id=session["user_id"]).all()

    # Get all rounds for this user
    rounds = Round.query.filter_by(user_id=session["user_id"]).all()

    for player in players:
        albatrosses = eagles = birdies = pars = bogeys = double_bogeys = triple_bogeys = holes_in_one = 0
        total_18 = total_9 = total_front = total_back = best_18 = best_9 = best_front = best_back = 0
        rounds_played = 0
        rounds_18 = 0
        rounds_9 = 0
        player_id = player.player_id
        

        for round_data in rounds:
            round_id = round_data.round_id
            holes = round_data.holes
            
            # Get course — optional, depending on if you need course data for stats
            if round_data.course_18_id:
                course = Course18.query.get(round_data.course_18_id)
            else:
                course = Course9.query.get(round_data.course_9_id)

            # Get player's score for this round
            if holes == 18:
                score = Score18.query.filter_by(round_id=round_id, player_id=player_id).first()
            else:
                score = Score9.query.filter_by(round_id=round_id, player_id=player_id).first()

            if not score:
                continue

            if score and course:
                rounds_played += 1
                round_total = 0

                for hole in range(1, holes + 1):
                    s = getattr(score, f"hole_{hole}")
                    p = getattr(course, f"par_{hole}")

                    if s is None or p is None:
                        continue  # skip if score or par is missing

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
                        holes_in_one += 1

                if holes == 18:
                    total_18 += round_total
                    rounds_18 += 1
                    total_front += score.front
                    total_back += score.back
                    if best_18 == 0:
                        best_18 = round_total
                    else:
                        if round_total < best_18:
                            best_18 = round_total
                    if best_front == 0:
                        best_front = score.front
                    else:
                        if score.front < best_front:
                            best_front = score.front
                    if best_back == 0:
                        best_back = score.back
                    else:
                        if score.back < best_back:
                            best_back = score.back
                else:
                    total_9 += round_total
                    rounds_9 += 1
                    if best_9 == 0:
                        best_9 = round_total
                    else:
                        if round_total < best_9:
                            best_9 = round_total

        # Calculate average scores

        average_18 = round(total_18 / rounds_18) if rounds_18 else 0
        average_9 = round(total_9 / rounds_9) if rounds_9 else 0
        average_front = round(total_front / rounds_18) if rounds_played else 0
        average_back = round(total_back / rounds_18) if rounds_played else 0

        # Assign default values if no stats were recorded

        albatrosses = albatrosses or 0
        eagles = eagles or 0
        birdies = birdies or 0
        pars = pars or 0
        bogeys = bogeys or 0
        double_bogeys = double_bogeys or 0
        triple_bogeys = triple_bogeys or 0
        holes_in_one = holes_in_one or 0
        average_18 = average_18 or 0
        average_9 = average_9 or 0
        average_front = average_front or 0
        average_back = average_back or 0
        best_18 = best_18 or 0
        best_9 = best_9 or 0
        best_front = best_front or 0
        best_back = best_back or 0

        # Calculate the player's handicap index based on best 8 rounds in most recent 20 rounds
        # Step 1: Get the 20 most recent rounds the player played in
        recent_20 = (
            Round.query
            .filter(
                (Round.player_id_1 == player_id) |
                (Round.player_id_2 == player_id) |
                (Round.player_id_3 == player_id)
            )
            .order_by(Round.date.desc(), Round.round_id.desc())
            .limit(20)
            .all()
        )

        recent_scores = []

        for round_data in recent_20:
            round_id = round_data.round_id
            holes = round_data.holes

            if holes == 18:
                score = Score18.query.filter_by(round_id=round_id, player_id=player_id).first()
                if score:
                    total = score.total
            else:
                score = Score9.query.filter_by(round_id=round_id, player_id=player_id).first()
                if score:
                    total = score.total * 2  # approximate 18-hole round

            if score and total:
                recent_scores.append(total)

        # Step 2: Calculate handicap index
        if recent_scores:
            best_8 = sorted(recent_scores)[:8]
            avg_best_8 = sum(best_8) / len(best_8)
            handicap_index = round((avg_best_8 - 72) * 0.96, 1)  # Assuming course rating = 72
        else:
            handicap_index = None

        # Step 3: Update player with calculated stats
        player.rounds_played = rounds_played
        player.albatrosses = albatrosses
        player.eagles = eagles
        player.birdies = birdies
        player.pars = pars
        player.bogeys = bogeys
        player.eagles = eagles
        player.double_bogeys = double_bogeys
        player.triple_bogeys = triple_bogeys
        player.holes_in_one = holes_in_one
        player.handicap = handicap_index
        player.average_18 = average_18
        player.average_9 = average_9
        player.average_front = average_front
        player.average_back = average_back
        player.best_18 = best_18
        player.best_9 = best_9
        player.best_front = best_front
        player.best_back = best_back

        db.session.commit()

        # Step 4: Re-query players if needed for display
        players = Player.query.filter_by(user_id=session["user_id"]).order_by(Player.rounds_played.desc()).all()

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

        # Query database for user
        user = User.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user.id

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

        # Check if username already exists

        new_username = request.form.get("username")
        nickname = request.form.get("nickname")  # assuming you collect this too
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        # Check if username already exists
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            return apology("Username already exists", 400)

        # Check password confirmation
        if password != confirm_password:
            return apology("Passwords do not match", 400)

        # Hash password
        hash = generate_password_hash(password, method="pbkdf2:sha256")

        # Create new user instance
        user = User(username=new_username, hash=hash, nickname=nickname)

        # Add and commit to DB
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return apology("Username already exists", 400)

        return redirect("/")

    else:
        return render_template("register.html")
