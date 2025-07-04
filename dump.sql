--PRAGMA foreign_keys=OFF;
--BEGIN TRANSACTION;
CREATE TABLE users (id SERIAL INTEGER PRIMARY KEY  NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, 'nickname' TEXT);
INSERT INTO users VALUES(1,'Chris','scrypt:32768:8:1$t8wzA6N5aPUIoCEp$ca7c76bdcd65dcc413eedd265a5b3fbc976d6ba49738ecad1e36371da917adec15c91b99f6fedfac3626baac4d0c60d975c1aaeea95237fca9d431b4d3698387','Chris');
INSERT INTO users VALUES(3,'Bobino','scrypt:32768:8:1$WDUItgUVGWHJLaH6$2ad2dbb583824f8e1ca4fed3572314f0fd0491072ba221d52f32f7179b1b63850f63514a26d21b664d1a9180cd724575adf9e103a7548b2762dfabafe59102a7','Bob');
CREATE TABLE courses_18 (
    course_id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    front INTEGER NOT NULL,
    back INTEGER NOT NULL,
    total INTEGER NOT NULL,


    yards_1 INTEGER,
    handicap_1 INTEGER,
    par_1 INTEGER,

    yards_2 INTEGER,
    handicap_2 INTEGER,
    par_2 INTEGER,

    yards_3 INTEGER,
    handicap_3 INTEGER,
    par_3 INTEGER,

    yards_4 INTEGER,
    handicap_4 INTEGER,
    par_4 INTEGER,

    yards_5 INTEGER,
    handicap_5 INTEGER,
    par_5 INTEGER,

    yards_6 INTEGER,
    handicap_6 INTEGER,
    par_6 INTEGER,

    yards_7 INTEGER,
    handicap_7 INTEGER,
    par_7 INTEGER,

    yards_8 INTEGER,
    handicap_8 INTEGER,
    par_8 INTEGER,

    yards_9 INTEGER,
    handicap_9 INTEGER,
    par_9 INTEGER,

    yards_10 INTEGER,
    handicap_10 INTEGER,
    par_10 INTEGER,

    yards_11 INTEGER,
    handicap_11 INTEGER,
    par_11 INTEGER,

    yards_12 INTEGER,
    handicap_12 INTEGER,
    par_12 INTEGER,

    yards_13 INTEGER,
    handicap_13 INTEGER,
    par_13 INTEGER,

    yards_14 INTEGER,
    handicap_14 INTEGER,
    par_14 INTEGER,

    yards_15 INTEGER,
    handicap_15 INTEGER,
    par_15 INTEGER,

    yards_16 INTEGER,
    handicap_16 INTEGER,
    par_16 INTEGER,

    yards_17 INTEGER,
    handicap_17 INTEGER,
    par_17 INTEGER,

    yards_18 INTEGER,
    handicap_18 INTEGER,
    par_18 INTEGER,

    front_yards INTEGER,
    back_yards INTEGER,
    total_yards INTEGER,
    course_holes INTEGER,

    user_id INTEGER NOT NULL,    

    FOREIGN KEY(user_id) REFERENCES users(id)
);
INSERT INTO courses_18 VALUES(1,'Stratford Municipal Golf Course',35,35,70,408,3,4,175,15,3,424,1,4,299,14,4,360,9,4,363,10,4,147,17,3,484,7,5,316,12,4,404,2,4,217,5,3,359,8,4,353,4,4,364,11,4,363,13,4,114,18,3,511,6,5,245,16,4,1,2976,2930,5906,18);
INSERT INTO courses_18 VALUES(2,'Mitchell Golf Club',35,36,71,334,13,4,357,5,4,136,17,3,399,1,4,444,11,5,349,9,4,150,15,3,489,3,5,185,7,3,116,18,3,345,6,4,339,12,4,148,8,3,503,2,5,503,4,5,337,14,4,142,16,3,466,10,5,1,2843,2899,5742,18);
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    user_id INTEGER, 
    rounds_played INTEGER, 
    handicap INTEGER, 
    average_score INTEGER, 
    birdies INTEGER, 
    pars INTEGER, 
    bogeys INTEGER, 
    eagles INTEGER, 
    double_bogeys INTEGER, 
    triple_bogeys INTEGER, 
    holes_in_one INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
INSERT INTO players VALUES(1,'Brett','Adair',1,4,23.500000000000000888,96,2,13,20,0,24,12,0);
INSERT INTO players VALUES(2,'Bennett','McCarthy',1,2,28.30000000000000071,102,1,4,10,0,7,2,0);
INSERT INTO players VALUES(3,'Derek','Vandentemple',1,3,21.100000000000003197,94,1,13,14,0,10,3,0);
INSERT INTO players VALUES(4,'Daniel','Bald',1,2,27.800000000000002486,101,3,5,4,0,6,6,0);
INSERT INTO players VALUES(5,'John ','Smith',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO players VALUES(6,'Jane','Doe',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO players VALUES(7,'Alexander','Hamilton',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO players VALUES(8,'George','Washinton',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO players VALUES(9,'John ','Adams',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO players VALUES(10,'Benjamin','Franklin',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE rounds (
    round_id INTEGER PRIMARY KEY,
    date DATE,
    player_id_1 INTEGER,
    player_id_2 INTEGER,
    player_id_3 INTEGER,
    course_18_id INTEGER,
    course_9_id INTEGER,
    holes INTEGER,
    user_id INTEGER, 
    FOREIGN KEY(player_id_1) REFERENCES players(player_id),
    FOREIGN KEY(player_id_2) REFERENCES players(player_id),
    FOREIGN KEY(player_id_3) REFERENCES players(player_id),
    FOREIGN KEY(course_18_id) REFERENCES courses_18(course_id),
    FOREIGN KEY(course_9_id) REFERENCES courses_9(course_id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
INSERT INTO rounds VALUES(1,'2025-06-21',1,NULL,NULL,1,NULL,1,18);
INSERT INTO rounds VALUES(2,'2025-06-25',2,NULL,NULL,2,NULL,1,18);
INSERT INTO rounds VALUES(3,'2025-06-25',1,3,4,1,NULL,1,18);
INSERT INTO rounds VALUES(4,'2025-06-25',NULL,NULL,NULL,2,NULL,1,9);
INSERT INTO rounds VALUES(5,'2025-06-25',1,NULL,NULL,1,NULL,1,18);
INSERT INTO rounds VALUES(6,'2025-06-28',2,3,4,2,NULL,1,9);
INSERT INTO rounds VALUES(7,'2025-06-29',1,3,NULL,1,NULL,1,18);
CREATE TABLE courses_9 (
    course_id INTEGER PRIMARY KEY NOT NULL,
    name TEXT,
    total INTEGER,


    yards_1 INTEGER,
    handicap_1 INTEGER,
    par_1 INTEGER,

    yards_2 INTEGER,
    handicap_2 INTEGER,
    par_2 INTEGER,

    yards_3 INTEGER,
    handicap_3 INTEGER ,
    par_3 INTEGER,

    yards_4 INTEGER,
    handicap_4 INTEGER,
    par_4 INTEGER,

    yards_5 INTEGER,
    handicap_5 INTEGER,
    par_5 INTEGER,

    yards_6 INTEGER,
    handicap_6 INTEGER,
    par_6 INTEGER,

    yards_7 INTEGER,
    handicap_7 INTEGER,
    par_7 INTEGER,

    yards_8 INTEGER,
    handicap_8 INTEGER,
    par_8 INTEGER,

    yards_9 INTEGER,
    handicap_9 INTEGER,
    par_9 INTEGER,

    course_holes INTEGER,

    user_id INTEGER NOT NULL, 

    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE score_18 (
    score_id INTEGER PRIMARY KEY,
    hole_1 INTEGER,
    hole_2 INTEGER,
    hole_3 INTEGER,
    hole_4 INTEGER,
    hole_5 INTEGER,
    hole_6 INTEGER,
    hole_7 INTEGER,
    hole_8 INTEGER,
    hole_9 INTEGER,
    hole_10 INTEGER,
    hole_11 INTEGER,
    hole_12 INTEGER,
    hole_13 INTEGER,
    hole_14 INTEGER,
    hole_15 INTEGER,
    hole_16 INTEGER,
    hole_17 INTEGER,
    hole_18 INTEGER,
    front INTEGER,
    back INTEGER,
    total INTEGER,

    round_id INTEGER,
    player_id INTEGER,
    is_user BOOLEAN,
    user_id INTEGER, 

    FOREIGN KEY(round_id) REFERENCES rounds(round_id),
    FOREIGN KEY(player_id) REFERENCES players(player_id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
INSERT INTO score_18 VALUES(1,4,5,4,3,4,4,5,4,4,5,6,5,4,5,4,5,5,4,37,43,80,1,NULL,1,1);
INSERT INTO score_18 VALUES(2,6,4,5,6,7,5,7,5,6,4,4,4,6,6,4,4,6,4,51,42,93,1,1,1,NULL);
INSERT INTO score_18 VALUES(3,5,4,3,4,6,5,6,5,4,3,3,5,4,5,4,5,5,4,42,38,80,2,NULL,1,1);
INSERT INTO score_18 VALUES(4,4,5,5,6,6,5,4,4,4,3,5,6,6,6,6,4,7,5,43,48,91,2,2,1,NULL);
INSERT INTO score_18 VALUES(5,4,3,4,4,3,5,5,6,4,5,5,4,4,4,5,5,5,5,38,42,80,3,NULL,1,1);
INSERT INTO score_18 VALUES(6,6,4,5,5,4,5,4,5,6,6,6,6,6,6,4,4,7,4,44,49,93,3,1,1,NULL);
INSERT INTO score_18 VALUES(7,5,3,3,6,5,4,7,6,5,4,7,5,5,5,6,6,5,6,44,49,93,3,3,1,NULL);
INSERT INTO score_18 VALUES(8,4,5,4,5,6,6,6,4,7,6,4,4,4,4,7,7,4,7,47,47,94,3,4,1,NULL);
INSERT INTO score_18 VALUES(9,4,3,5,4,7,5,7,5,4,4,5,7,3,5,4,3,4,4,44,39,83,5,NULL,1,1);
INSERT INTO score_18 VALUES(10,7,6,7,6,6,5,6,4,6,6,6,5,6,6,7,3,6,6,53,51,104,5,1,1,NULL);
INSERT INTO score_18 VALUES(11,2,4,3,5,7,5,6,6,4,7,5,5,6,6,5,7,6,7,42,54,96,7,NULL,1,1);
INSERT INTO score_18 VALUES(12,5,6,6,4,5,6,6,4,6,5,4,4,5,7,6,6,7,4,48,48,96,7,1,1,NULL);
INSERT INTO score_18 VALUES(13,7,4,7,6,4,4,4,6,6,4,5,6,5,4,4,5,6,4,48,43,91,7,3,1,NULL);
CREATE TABLE score_9 (
    score_id INTEGER PRIMARY KEY,
    hole_1 INTEGER,
    hole_2 INTEGER,
    hole_3 INTEGER,
    hole_4 INTEGER,
    hole_5 INTEGER,
    hole_6 INTEGER,
    hole_7 INTEGER,
    hole_8 INTEGER,
    hole_9 INTEGER,
    total INTEGER,

    round_id INTEGER,
    player_id INTEGER,
    is_user BOOLEAN,
    user_id INTEGER, 
    FOREIGN KEY(round_id) REFERENCES rounds(round_id),
    FOREIGN KEY(player_id) REFERENCES players(player_id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
INSERT INTO score_9 VALUES(1,3,5,4,5,4,5,3,6,5,40,4,NULL,1,1);
INSERT INTO score_9 VALUES(2,4,7,6,4,5,5,4,5,5,45,6,NULL,1,1);
INSERT INTO score_9 VALUES(3,6,6,5,8,6,5,7,7,6,56,6,2,1,NULL);
INSERT INTO score_9 VALUES(4,4,5,7,6,5,4,5,6,7,49,6,3,1,NULL);
INSERT INTO score_9 VALUES(5,3,8,6,5,7,7,7,6,5,54,6,4,1,NULL);
--DELETE FROM sqlite_sequence;
--INSERT INTO sqlite_sequence VALUES('users',3);
--COMMIT;
