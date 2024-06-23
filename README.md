# CSMS (Charging Station Management System)

## Context 
This project began it's development life as my master's thesis at ECAM Brussels.
In the actual context of energy transition network operators want to be able to balance the electricity grid's demand. This could be done by remotely managing and monitoring charging poles. This is the main reason why this project was created: to understand how we can access the information that charging stations are exchanging through the OCPP (Open Charge Point Protocol). It will only be available for OCPP 2.0.1 as this is the most recent version and the parallell research work was done on this version.

## How to Use 
To use the simulator please download the repo first.
To start the simulator with the command lines please navigate to the simulation\v201 directory.
Run the central_system.py file that will act as the central management system. 
For the charging points run the charge_point.py files according to how many charging stations you want to have in your simulation.

For the frontend React client please navigate to the csms-dashboard directory and run the following commands: \
`npm install` to install dependencies. \
`npm start` to build the application. \
You should be able to consult the application on `http://localhost:3000`. \















&copy; ELophem