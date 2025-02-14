CREATE TABLE User (
    User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(32) UNIQUE,
    Email VARCHAR(32) UNIQUE,
    Password VARCHAR(255), --needs to be long for hashing
    Height INT,
    Weight INT,
    Age INT,
    Sex INT
);

CREATE TABLE User_Body (
    User_Body_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    User_ID INT,
    Shoulders_Percent INT,
    Back_Percent INT,
    Arms_Percent INT,
    Legs_Percent INT,
    Chest_Percent INT,
    Last_Reset DATE,
    FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

CREATE TABLE Workouts (
    Workout_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    User_ID INT,
    Date DATE,
    Field VARCHAR(32),
    FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

CREATE TABLE Exercise (
    Exercise_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Workout_ID INT,
    No_Sets INT,
    No_Reps_Per_Set INT,
    Exercise_Name VARCHAR(32),
    Weight INT,
    FOREIGN KEY (Workout_ID) REFERENCES Workouts(Workout_ID)
);
CREATE TABLE WeightLog (
    WeightLog_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    User_ID INTEGER NOT NULL,
    Date DATE DEFAULT (DATE('now')),
    Weight REAL NOT NULL,
    FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);
