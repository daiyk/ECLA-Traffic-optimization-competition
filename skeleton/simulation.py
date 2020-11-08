import math
from collections import defaultdict
from time import sleep
import sys
import traci
import traci.constants as tc


class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge, network,
                 List_bus_person):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = pedestrians
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge

        self.network = network
        self.List_bus_person = List_bus_person

        self.bus = []
        self.bus_index = 0

    def BusDict_timestamp(self, step: int):
        List_bus_timestamp = self.List_bus_person[step][0]
        if List_bus_timestamp == [0, 0, 0]:
            return {}
        else:
            dictionary_bus = {step: []}
            if List_bus_timestamp[0] > 0:
                for _ in range(int(List_bus_timestamp[0])):
                    dictionary_bus[step].append({'bus_id': f'bus_{self.bus_index}', 'bus_type': "BUS_L", 'capacity': 8})
                    self.bus_index += 1
            if List_bus_timestamp[1] > 0:
                for _ in range(int(List_bus_timestamp[1])):
                    dictionary_bus[step].append({'bus_id': f'bus_{self.bus_index}', 'bus_type': "BUS_M", 'capacity': 4})
                    self.bus_index += 1
            if List_bus_timestamp[2] > 0:
                for _ in range(int(List_bus_timestamp[2])):
                    dictionary_bus[step].append({'bus_id': f'bus_{self.bus_index}', 'bus_type': "BUS_S", 'capacity': 2})
                    self.bus_index += 1
            return dictionary_bus

    # This needs to be checked
    def Get_Onboard_Person_list(self, bus_id: str):
        list_passengersID = traci.vehicle.getPersonIDList(bus_id)
        list_pedestrians_onboard = []
        for i in list_passengersID:
            for pedestrian in self.pedestrians:
                if i == pedestrian.id:
                    list_pedestrians_onboard.append(pedestrian)
                else:
                    pass
        return list_pedestrians_onboard

    def pick_up_persons(self, currentEdgePerson, step):

        # # todo: creaete bus, update bus list (L; M; S)
        # bus_id = f'bus_{self.bus_index}'
        # self.bus_index += 1
        # self.bus.append(bus_id)
        # traci.vehicle.subscribe(bus_id, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_POSITION, tc.VAR_NEXT_STOPS))
        #
        # # todo: get bus_type and capacity, default BUS_L
        # bus_type = "BUS_L"
        # personCapacity = 8

        # todo: which person to pick from currentEdgePerson
        buses = self.BusDict_timestamp(step)
        persons_to_bus = self.List_bus_person[step][-1]

        for p in persons_to_bus:
            if p.edge_from not in currentEdgePerson:
                currentEdgePerson[p.edge_from] = [p]
            else:
                currentEdgePerson[p.edge_from].append(p)

        i = 0
        for bus in buses[step]:
            bus_id = bus['bus_id']
            bus_type = bus['bus_type']
            personCapacity = bus['capacity']
            traci.vehicle.add(vehID=bus_id, typeID=bus_type, routeID="", depart=step, departPos=0,
                              departSpeed=0, departLane=0, personCapacity=personCapacity)
            traci.vehicle.subscribe(bus_id, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_POSITION, tc.VAR_NEXT_STOPS))
            self.bus.append(bus_id)

            person = persons_to_bus[i]
            i += personCapacity

            edgeID_from = person.edge_from
            shortestPath = self.network.getWeighedShortestPaths(edgeID_from, personCapacity, currentEdgePerson)

            # if len(shortestPath) == 0:
            #     shortestPath = []
            #     for i in range(len(currentEdgePerson)):
            #         if i == 0:
            #             self.network.getShortestPaths(edgeID_from, edgeID_to)




            persons_to_travel = defaultdict()
            for sp in shortestPath:
                while personCapacity > 0 and len(currentEdgePerson[sp]) > 0:
                    if sp not in persons_to_travel:
                        persons_to_travel[sp] = [currentEdgePerson[sp].pop(0)]
                    else:
                        persons_to_travel[sp].append(currentEdgePerson[sp].pop(0))
                    personCapacity -= 1

            if len(shortestPath) == 0:
                p = currentEdgePerson[person.edge_from].pop(0)
                traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
                traci.vehicle.changeTarget(bus_id, p.edge_from)
                traci.vehicle.setStop(vehID=bus_id, edgeID=p.edge_from, pos=p.position_from, laneIndex=0,
                                      duration=10, flags=tc.STOP_DEFAULT)
                persons_to_travel[p.edge_from] = [p]

            for i in range(len(shortestPath)):

                persons = persons_to_travel[shortestPath[i]]
                if i == 0:
                    traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
                    traci.vehicle.changeTarget(bus_id, shortestPath[i])
                else:
                    traci.vehicle.setRoute(bus_id, [shortestPath[i - 1], shortestPath[i]])
                    traci.vehicle.changeTarget(bus_id, shortestPath[i])
                for p in persons:
                    traci.vehicle.setStop(vehID=bus_id, edgeID=shortestPath[i], pos=p.position_from, laneIndex=0,
                                          duration=10, flags=tc.STOP_DEFAULT)

            list_pedestrians_onboard = []
            for sp in persons_to_travel:
                list_pedestrians_onboard.append(persons_to_travel[sp])

            # main runnig part
            persons = list_pedestrians_onboard[-1]
            last_person = persons[-1]
            cost_des = self.find_cost_des(last_person, persons)

            for i in range(0, len(persons)):
                person_des = self.send_passenger_leave(cost_des, persons, last_person, bus_id)
                last_person = person_des
                persons.remove(person_des)  # remove left passenger
                cost_des = self.find_cost_des(last_person, persons)

        # todo: for each passengers in the bus, redirect the bus to send as many passangers as possible to the destinations
        for b in self.bus:
            if traci.vehicle.getNextStops(b) is None and (traci.vehicle.isAtBusStop(b)):
                personListIDs = traci.vehicle.getPersonIDList(b)
                # TODO: map personListIDs to personList! ! !
                personList = self.Get_Onboard_Person_list(b)
                currentEdgeID = traci.vehicle.getRoadID(b)
                costs = []
                for per in personList:
                    _, cost = self.network.getShortestPath(currentEdgeID, per.edge_to)
                    costs.append(cost)
                # sorted_person_index = sorted(range(len(costs)), key=lambda k: s[k])
                next_dest_ind = costs.index(min(costs))
                traci.vehicle.setRoute(b, [personList[next_dest_ind].edge_to])
                traci.vehicle.setStop(vehID=b, edgeID=personList[next_dest_ind].edge_from,
                                      pos=personList[next_dest_ind].position_from, laneIndex=0,
                                      duration=50, flags=tc.STOP_DEFAULT)


    def find_cost_des(self, last_person, list_pedestrians_onboard):
        cost_des = []

        for person in list_pedestrians_onboard:
            sp, cost = self.network.getShortestPaths(last_person.edge_from, person.edge_to)
            cost_des.append(cost)

        return cost_des

    def send_passenger_leave(self, cost_des, list_pedestrians_onboard, last_person, bus_id):
        # find the next leaving point
        passenger_des_index = sorted(range(len(cost_des)), key=lambda k: cost_des[k])
        person_des = list_pedestrians_onboard[passenger_des_index[0]]  # find the passenger with least cose
        des_sp, cost = self.network.getShortestPaths(last_person.edge_from, person_des.edge_to)

        des_sp = [sp.getID() for sp in des_sp]
        # set SP route
        traci.vehicle.setRoute(bus_id, des_sp)
        traci.vehicle.changeTarget(bus_id, person_des.edge_to)
        traci.vehicle.setStop(vehID=bus_id, edgeID=person_des.edge_to, pos=person_des.position_to, laneIndex=0,
                              duration=50, flags=tc.STOP_DEFAULT)

        return person_des

        # todo: return the bus to the end_edge.
        # todo: how to manage the bus return.
        # todo: for each passengers in the bus, redirect the bus to send as many passangers as possible to the destinations



    def run(self):

        # dict {step: [person1, person2, ,..., ] }
        pedestrians_steps = defaultdict()
        for person in self.pedestrians:
            depart = math.ceil(person.depart)
            if depart not in pedestrians_steps:
                pedestrians_steps[depart] = [person]
            else:
                pedestrians_steps[depart].append(person)

        currentEdgePerson = defaultdict()
        #  { Edges_id : [person1, person2....]    }

        step = 0
        while step <= self.simulation_steps:

            # [ step t = 000, yes, #bus, (S,M,L), [people list]  [yes(no), bus_type], None ,    ]

            # person = person_t
            traci.simulationStep()

            persons = pedestrians_steps.get(step)

            if persons is not None:
                # build currentEdgePerson
                for p in persons:
                    if p.edge_from not in currentEdgePerson:
                        currentEdgePerson[p.edge_from] = [p]
                    else:
                        currentEdgePerson[p.edge_from].append(p)

            # todo: update currentEdgePerson
            self.pick_up_persons(currentEdgePerson, step)

            if self.sleep_time > 0:
                sleep(self.sleep_time)
            step += 1
            # print(traci.vehicle.getSubscriptionResults('bus_0'))

            # # todo: total wait time,  total km driven
            # # check person waiting stage for bus i
            # # 0 for not-yet-departed
            # # 1 for waiting
            # # 2 for walking
            # # 3 for driving
            # # 4 for access to busStop or trainStop
            # # 5 for personTrip
            # stage = traci.person.getStage(person.id).type

        traci.close()
