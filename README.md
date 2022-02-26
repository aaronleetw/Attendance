# Attendance
This is the much more robust [version 2](../../tree/v2) with MySQL, but was never presented.

## Technologies used
- Flask
- Mailgun (for FORGET password)
- MySQL
- Flask-Admin
- SQL Alchemy
- OpenPyXL

## v1 Introduction
[This is a link to the slides I used to present the system to our teachers](https://hackmd.io/@aaronlee/attendance-en-ppt/)

## v2 Improvements
After collecting feedback on v1, I created v2 with the intention of making teachers' lives easier. It's a shame v2 did not make it to production.

Main improvements include:
- Din-Shin (This is our school's special grading system, where every teacher can give a score on a scale of 1-5 depending on how the students behave in that period)
  - This can save another piece of paper
- Pre-recorded absence
  - The student's affairs office can record absence ahead of time
- Different absent types
  - A student will have many reasons for their absence: sick, official, etc.
- A robust database manager powered by Flask-Admin
- Everyone has their individual note area (not share a big area)
- Substitute class
  - Sometimes even teachers have things to deal with. They can switch classes with other teachers, and the attendance system will still work fine.
- Student have their own account for checking their records and make sure everything is correct.
- Group classes are "grouped" into one button instead of appearing separately in the dropdown.

## v2 Screenshots
![](https://i.imgur.com/lSxjAc8.png) ![](https://i.imgur.com/jkr9HPy.png) ![](https://i.imgur.com/BIdMqFJ.png) ![](https://i.imgur.com/Ae2nO4z.png) ![](https://i.imgur.com/52dTvre.png)
