# ELCA Challenge PolyHACK 2020

## Image
![ELCA Challenge](challenge_header.png)

## Title
Traffic optimization with real-time simulation

## Short Description
As the people and vehicle density in the city continuously grows, traffic optimizations are getting more and more important.
In this challenge, you will try to optimize a traffic problem with new ways with the help of a simulator.

## Long Description

### Background
With the growing population, traffic management is getting more and more important, especially in cities. To evaluate new possibilities of traffic optimization and test them out, sophisticated simulations are ideal tools to verify or further optimize them.

### Starting Position
We prepared a street network based on the center of Aarhus (Denmark) with simulated car traffic for one day.
In that network, random pedestrians are generated which want to travel from one location to another with public transport.
The simulation will run with the open source simulation software SUMO (created by Deutsches Zentrum für Luft- und Raumfahrt).
There is a python-based library available to interact with the simulation in real time by reading out data or creating and controlling vehicles.

### Challenge
Read out information from the pedestrians with the given API and find out who wants to travel where.
Generate buses which can fulfill the travel needs of the pedestrians.
Optimize the public transport routes in various ways and try to transport as many pedestrians as possible in the shortest time possible without overloading the traffic.

#### Rules
- It's allowed to use any number of buses for this
- Capacity of the buses is given
- Max speed of the buses is given
- Buses may stop at any place
- Buses must enter and leave the simulation at the predefined bus depot locations.
- Passengers just enter the bus at the position where they wait and leave the bus only when it stops at their destination position.
  
#### Rating
The challenge is solved best in an incremental way. The rating criterias depends on the level reached.

##### Level 1
The goal here is to ensure that we transport as much passenger as possible and fullfill the needs with a minimal amount of buses of the same capacity.
The score will be calculated based on:
- number of buses
- number of passengers not transported

##### Level 2
The goal is here to reduce the number of kilometers driven by all the buses in total and minimize again the number of buses.
The score will be calculated based on:
- number of buses
- kilometers driven by all buses
- total wait time of all transported passengers
- number of passengers not transported
- bonus for level2

##### Level 3
In addition to level 2, we need to minimize the total capacity of all buses in addition. Therefore, this level allows to use smaller bus sizes as well.
The score will be calculated based on:
- number of buses
- kilometers driven by all buses
- total wait time of all transported passengers
- number of passengers not transported
- total capacity of all buses
- bonus for level3
