from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    hash = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String)

    # Relationships
    
    


class Player(db.Model):
    __tablename__ = 'players'

    player_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    rounds_played = db.Column(db.Integer)
    handicap = db.Column(db.Integer)
    average_18 = db.Column(db.Integer)
    average_9 = db.Column(db.Integer)
    average_front = db.Column(db.Integer)
    average_back = db.Column(db.Integer)
    best_18 = db.Column(db.Integer)
    best_9 = db.Column(db.Integer)
    best_front = db.Column(db.Integer)
    best_back = db.Column(db.Integer)
    albatrosses = db.Column(db.Integer)
    eagles = db.Column(db.Integer)
    birdies = db.Column(db.Integer)
    pars = db.Column(db.Integer)
    bogeys = db.Column(db.Integer)
    double_bogeys = db.Column(db.Integer)
    triple_bogeys = db.Column(db.Integer)
    holes_in_one = db.Column(db.Integer)

    


class Course18(db.Model):
    __tablename__ = 'courses_18'

    course_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    front = db.Column(db.Integer, nullable=False)
    back = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    front_yards = db.Column(db.Integer)
    back_yards = db.Column(db.Integer)
    total_yards = db.Column(db.Integer)
    course_holes = db.Column(db.Integer)

    # Hole-by-hole data
    yards_1 = db.Column(db.Integer)
    handicap_1 = db.Column(db.Integer)
    par_1 = db.Column(db.Integer)
    yards_2 = db.Column(db.Integer)
    handicap_2 = db.Column(db.Integer)
    par_2 = db.Column(db.Integer)
    yards_3 = db.Column(db.Integer)
    handicap_3 = db.Column(db.Integer)
    par_3 = db.Column(db.Integer)
    yards_4 = db.Column(db.Integer)
    handicap_4 = db.Column(db.Integer)
    par_4 = db.Column(db.Integer)
    yards_5 = db.Column(db.Integer)
    handicap_5 = db.Column(db.Integer)
    par_5 = db.Column(db.Integer)
    yards_6 = db.Column(db.Integer)
    handicap_6 = db.Column(db.Integer)
    par_6 = db.Column(db.Integer)
    yards_7 = db.Column(db.Integer)
    handicap_7 = db.Column(db.Integer)
    par_7 = db.Column(db.Integer)
    yards_8 = db.Column(db.Integer)
    handicap_8 = db.Column(db.Integer)
    par_8 = db.Column(db.Integer)
    yards_9 = db.Column(db.Integer)
    handicap_9 = db.Column(db.Integer)
    par_9 = db.Column(db.Integer)
    yards_10 = db.Column(db.Integer)
    handicap_10 = db.Column(db.Integer)
    par_10 = db.Column(db.Integer)
    yards_11 = db.Column(db.Integer)
    handicap_11 = db.Column(db.Integer)
    par_11 = db.Column(db.Integer)
    yards_12 = db.Column(db.Integer)
    handicap_12 = db.Column(db.Integer)
    par_12 = db.Column(db.Integer)
    yards_13 = db.Column(db.Integer)
    handicap_13 = db.Column(db.Integer)
    par_13 = db.Column(db.Integer)
    yards_14 = db.Column(db.Integer)
    handicap_14 = db.Column(db.Integer)
    par_14 = db.Column(db.Integer)
    yards_15 = db.Column(db.Integer)
    handicap_15 = db.Column(db.Integer)
    par_15 = db.Column(db.Integer)
    yards_16 = db.Column(db.Integer)
    handicap_16 = db.Column(db.Integer)
    par_16 = db.Column(db.Integer)
    yards_17 = db.Column(db.Integer)
    handicap_17 = db.Column(db.Integer)
    par_17 = db.Column(db.Integer)
    yards_18 = db.Column(db.Integer)
    handicap_18 = db.Column(db.Integer)
    par_18 = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship to rounds played on this course
    rounds = db.relationship('Round', backref='course18', lazy=True, foreign_keys='Round.course_18_id')


class Course9(db.Model):
    __tablename__ = 'courses_9'

    course_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    total_yards = db.Column(db.Integer)
    course_holes = db.Column(db.Integer)

    yards_1 = db.Column(db.Integer)
    handicap_1 = db.Column(db.Integer)
    par_1 = db.Column(db.Integer)
    yards_2 = db.Column(db.Integer)
    handicap_2 = db.Column(db.Integer)
    par_2 = db.Column(db.Integer)
    yards_3 = db.Column(db.Integer)
    handicap_3 = db.Column(db.Integer)
    par_3 = db.Column(db.Integer)
    yards_4 = db.Column(db.Integer)
    handicap_4 = db.Column(db.Integer)
    par_4 = db.Column(db.Integer)
    yards_5 = db.Column(db.Integer)
    handicap_5 = db.Column(db.Integer)
    par_5 = db.Column(db.Integer)
    yards_6 = db.Column(db.Integer)
    handicap_6 = db.Column(db.Integer)
    par_6 = db.Column(db.Integer)
    yards_7 = db.Column(db.Integer)
    handicap_7 = db.Column(db.Integer)
    par_7 = db.Column(db.Integer)
    yards_8 = db.Column(db.Integer)
    handicap_8 = db.Column(db.Integer)
    par_8 = db.Column(db.Integer)
    yards_9 = db.Column(db.Integer)
    handicap_9 = db.Column(db.Integer)
    par_9 = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship to rounds played on this course
    rounds = db.relationship('Round', backref='course9', lazy=True, foreign_keys='Round.course_9_id')


class Round(db.Model):
    __tablename__ = 'rounds'

    round_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    holes = db.Column(db.Integer)

    player_id_1 = db.Column(db.Integer, db.ForeignKey('players.player_id'))
    player_id_2 = db.Column(db.Integer, db.ForeignKey('players.player_id'))
    player_id_3 = db.Column(db.Integer, db.ForeignKey('players.player_id'))

    course_18_id = db.Column(db.Integer, db.ForeignKey('courses_18.course_id'))
    course_9_id = db.Column(db.Integer, db.ForeignKey('courses_9.course_id'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships for players (up to 3)
    player1 = db.relationship('Player', foreign_keys=[player_id_1])
    player2 = db.relationship('Player', foreign_keys=[player_id_2])
    player3 = db.relationship('Player', foreign_keys=[player_id_3])

    # Relationships to courses
    # (backrefs handled on Course18 and Course9)
    # Relationship to user is handled via User.rounds


class Score18(db.Model):
    __tablename__ = 'score_18'

    score_id = db.Column(db.Integer, primary_key=True)

    hole_1 = db.Column(db.Integer)
    hole_2 = db.Column(db.Integer)
    hole_3 = db.Column(db.Integer)
    hole_4 = db.Column(db.Integer)
    hole_5 = db.Column(db.Integer)
    hole_6 = db.Column(db.Integer)
    hole_7 = db.Column(db.Integer)
    hole_8 = db.Column(db.Integer)
    hole_9 = db.Column(db.Integer)
    hole_10 = db.Column(db.Integer)
    hole_11 = db.Column(db.Integer)
    hole_12 = db.Column(db.Integer)
    hole_13 = db.Column(db.Integer)
    hole_14 = db.Column(db.Integer)
    hole_15 = db.Column(db.Integer)
    hole_16 = db.Column(db.Integer)
    hole_17 = db.Column(db.Integer)
    hole_18 = db.Column(db.Integer)

    front = db.Column(db.Integer)
    back = db.Column(db.Integer)
    total = db.Column(db.Integer)

    is_user = db.Column(db.Boolean)

    round_id = db.Column(db.Integer, db.ForeignKey('rounds.round_id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.player_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    round = db.relationship('Round', backref='scores_18')
    player = db.relationship('Player', backref='scores_18')
    user = db.relationship('User', backref='scores_18')


class Score9(db.Model):
    __tablename__ = 'score_9'

    score_id = db.Column(db.Integer, primary_key=True)

    hole_1 = db.Column(db.Integer)
    hole_2 = db.Column(db.Integer)
    hole_3 = db.Column(db.Integer)
    hole_4 = db.Column(db.Integer)
    hole_5 = db.Column(db.Integer)
    hole_6 = db.Column(db.Integer)
    hole_7 = db.Column(db.Integer)
    hole_8 = db.Column(db.Integer)
    hole_9 = db.Column(db.Integer)

    total = db.Column(db.Integer)
    is_user = db.Column(db.Boolean)

    round_id = db.Column(db.Integer, db.ForeignKey('rounds.round_id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.player_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    round = db.relationship('Round', backref='scores_9')
    player = db.relationship('Player', backref='scores_9')
    user = db.relationship('User', backref='scores_9')
