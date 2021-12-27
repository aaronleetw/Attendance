CREATE DATABASE attendance;
USE attendance;
CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    email TEXT,
    name TEXT,
    oldUsername TEXT,
    role CHAR, /* S: SuperAdmin / A: Admin / R: Regular User */
    password TEXT
);

CREATE TABLE students (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    email TEXT,
    grade INT,
    class_ INT,
    num INT,
    name TEXT,
    ename TEXT,
    classes TEXT,
    password TEXT
    /* update column as wishes for group classes
     ALTER TABLE students ADD COLUMN IF NOT EXISTS "" VARCHAR(255); */
);

--- Schedule of different day for different class
CREATE TABLE schedule (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    grade INT,
    class_ INT,
    dow INT,
    period CHAR,
    subject TEXT,
    teacher TEXT
);

CREATE TABLE specschedule (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    grade INT,
    class_ INT,
    date TEXT,
    period CHAR,
    subject TEXT,
    teacher TEXT
);

CREATE TABLE gpclasses (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    category TEXT,
    subclass TEXT,
    about TEXT,
    accs TEXT
    /* Save as JSON
    {
        0: 'acc1',
        1: 'acc2'
    }
    */
);

CREATE TABLE homerooms (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    grade INT,
    class_ INT,
    accs TEXT
    /* Save as JSON
    {
        0: 'acc1',
        1: 'acc2'
    }
    */
);

CREATE TABLE submission (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    grade INT,
    class_ INT,
    date VARCHAR(11),
    period CHAR,
    signature LONGTEXT,
    dscfrm TEXT,
    /*
        Save as JSON
        {
            subClass: "signature",
            subClass2: "signature2"
        }
        or
        plain text if not GP
    */
    ds1 INT DEFAULT 5,
    ds2 INT DEFAULT 5,
    ds3 INT DEFAULT 5,
    ds4 INT DEFAULT 5,
    ds5 INT DEFAULT 5,
    ds6 INT DEFAULT 5,
    ds7 INT DEFAULT 5,
    notes TEXT
    /*
        Save as JSON
        {
            'num': 'whatevernote',
            'num2': 'morenote'
        }
    */
);

CREATE TABLE ds (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    grade INT,
    class_ INT,
    date VARCHAR(11),
    period CHAR,
    num INT,
    note TEXT,
    status CHAR DEFAULT 'X'
);

CREATE TABLE dates (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    date VARCHAR(11),
    dow INT
);

CREATE TABLE absent (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    grade INT,
    class_ INT,
    date VARCHAR(11),
    period CHAR,
    num INT,
    status CHAR, /* L: 遲到 / K: 曠課 / G: 事假 / S: 病假 / F: 喪假 / P: 疫情假 / O: 公假*/
    note TEXT
);

CREATE TABLE forgot (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    userType CHAR, /* T: teacher / S: student */
    resetID VARCHAR(11),
    email TEXT,
    reqTime VARCHAR(20)
);
