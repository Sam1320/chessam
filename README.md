# chessam
Simple chess game with GUI and different bots implemented from scratch in python.

## HumanvsHuman
This version allows for local human vs human play.

## HumanvsBot
This version allows the user to play against different chess bots.

- ### Random 
    Plays a random move from the available options.
- ### Random attack
    Plays a random attacking move (i.e. takes an opponent piece) whenever possible, otherwise makes a random move.
- ### N-step Lookahead
    Asses the possible moves N steps in the future and plays the best move assuming optimal play and using a simple board evaluation heuristic.
- ### Stockfish
    State of the art open-source chess engine. In order to be able to play against it its necessary to first download the compatible binary to your OS from https://stockfishchess.org/download/ and place it under chessam/ . 

## Documentation
This project was done in the context of the Simulation and Modelling module of the Bachelor of Informatics and Computational Sciene at the Univerisity of Potsdam.
The ***project_report.pdf*** file contains a complete summary of the main aspects of the project together with a short discussion of the final result and possible next steps.
