from time import sleep
import sys
import traci
import traci.constants as tc
import math
from collections import defaultdict

class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge, network):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = pedestrians
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge

        self.network = network

        self.bus = []
        self.bus_index = 0

    def pick_up_person(self, currentEdgePerson, ):
        bus_id = f'bus_{self.bus_index}'
        self.bus_index += 1
        self.bus.append(bus_id)

        # todo: get bus_type and capacity, default BUS_L
        bus_type = "BUS_L"
        personCapacity = 8

        # todo: which person to pick from currentEdgePerson

        try:
            # todo: optimize depart time?
            traci.vehicle.add(vehID=bus_id, typeID=bus_type, routeID="", depart=person.depart + 240, departPos=0,
                              departSpeed=0, departLane=0, personCapacity=personCapacity)
            traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])

            # todo: maybe get some people on the way to person_t if possible
            traci.vehicle.changeTarget(bus_id, person.edge_from)
            # todo: optimize duration?
            traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0,
                                  duration=50, flags=tc.STOP_DEFAULT)

            shortest, cost = self.network.getShortestPaths(person.edge_from, person.edge_to)
            SP = [sp.getID() for sp in shortest]
            traci.vehicle.setRoute(bus_id, SP)
            traci.vehicle.changeTarget(bus_id, person.edge_to)
            traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0,
                                  duration=50, flags=tc.STOP_DEFAULT)

            # todo: how to get another people on the run?
            # todo: where the bus go, after 0 passengers.

        except traci.exceptions.TraCIException as err:
            print("TraCIException: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])


    def run(self):

        # dict {step: [person1, person2, ,..., ] }
        pedestrians_steps = defaultdict()
        for person in self.pedestrians:
            depart = math.ceil(person.depart)
            if depart not in pedestrians_steps:
                pedestrians_steps[depart] = [person]
            else:
                pedestrians_steps[depart].append(person)

        # traci.vehicle.subscribe('bus_0', (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_POSITION, tc.VAR_NEXT_STOPS))


        currentEdgePerson = defaultdict()
        step = 0
        while step <= self.simulation_steps:

            # # todo: get person at step
            # [ step t = 000, yes, #bus, (S,M,L), [people list]  [yes(no), bus_type], None ,    ]

            # person = person_t
            traci.simulationStep()

            # # todo: get bus_type and capacity, default BUS_L
            # bus_type = "BUS_L"
            # personCapacity = 8

            persons = pedestrians_steps.get(step)
            if persons is not None:

                # build currentEdgePerson
                for p in persons:
                    if p.edge_from not in currentEdgePerson:
                        currentEdgePerson[p.edge_from] = [p]
                    else:
                        currentEdgePerson[p.edge_from].append(p)

                # todo: update currentEdgePerson
                self.pick_up_person(currentEdgePerson)

            if self.sleep_time > 0:
                sleep(self.sleep_time)
            step += 1
            # print(traci.vehicle.getSubscriptionResults('bus_0'))


            # # todo: get bus_type and capacity, default BUS_L
            # bus_type = "BUS_L"
            # personCapacity = 8

            # # todo: total wait time,  total km driven
            # # check person waiting stage for bus i
            # # 0 for not-yet-departed
            # # 1 for waiting
            # # 2 for walking
            # # 3 for driving
            # # 4 for access to busStop or trainStop
            # # 5 for personTrip
            # stage = traci.person.getStage(person.id).type
            # # todo: it always return 0, I think this part need to be put at the simulation... or we can update the person stage?
            # if stage == 0:
            #     bus_id = f'bus_{bus_index}'
            #     bus_index += 1
            #     bus.append(bus_id)
            #
            #     try:
            #         # todo: optimize depart time?
            #         traci.vehicle.add(vehID=bus_id, typeID=bus_type, routeID="", depart=person.depart, departPos=0,
            #                           departSpeed=0, departLane=0, personCapacity=personCapacity)
            #         traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
            #
            #         # todo: maybe get some people on the way to person_t if possible
            #         traci.vehicle.changeTarget(bus_id, person.edge_from)
            #         # todo: optimize duration?
            #         traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0,
            #                               duration=50, flags=tc.STOP_DEFAULT)
            #
            #         shortest, cost = self.network.getShortestPaths(person.edge_from, person.edge_to)
            #         SP = [sp.getID() for sp in shortest]
            #         traci.vehicle.setRoute(bus_id, SP)
            #         traci.vehicle.changeTarget(bus_id, person.edge_to)
            #         traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0,
            #                               duration=50, flags=tc.STOP_DEFAULT)
            #
            #         # todo: how to get another people on the run?
            #         # todo: where the bus go, after 0 passengers.
            #
            #     except traci.exceptions.TraCIException as err:
            #         print("TraCIException: {0}".format(err))
            #     except:
            #         print("Unexpected error:", sys.exc_info()[0])


        traci.close()
