# jGame
jGame is a web application where users can wager points and answer questions used in the game show *Jeopardy!*

A current demo of the webapp can be found [here](j-game.herokuapp.com). A link to the "About" page can be found [here](http://j-game.herokuapp.com/about)

## game logic
The game's finite state machine is a constantly running loop. Every state in the FSM is represented by a page. Details of each page is provided in the how to play page, link [here](http://j-game.herokuapp.com/learn). 

## database structures
There are two schemas used in this webapp: User and Clues.

The User schema follows closely to what Miguel Grinberg uses in his Mega Flask Tutorial. There is a User table which holds the user data (nickname, email, etc). There is also an Email table used to hold every unique email used to login, which is linked to a single user. This was done for a future modification to allow users to link multiple emails to a single account.

The Clue schema uses five different tables. The main table is the Clue table, which holds the question as wells as its specified category, answer, value, and episode. The other tables (Category Table, Answer Table, Value Table, and Episode Table) all hold every possible entry for each table and can be linked to many different clues. This schema was chosen because of the order of which the database is queried as well as the ability to reduce the number of rows required due to the limited number or rows available from the free tier of Heroku Postgres (no need for an association table).

## clue query order
There is a specific order querying is done. First we query a random category from the category table. Then we gather a list of all possible unique answers from that category from the Clue Table, shuffle the list, and return the first three. The reason why we don't query the first three random answers from the clues table is because it leaves the possibility of repeated answers. From the three possible answers we select one as the correct answer and query a random clue with the same category and answer from the Clue Table.