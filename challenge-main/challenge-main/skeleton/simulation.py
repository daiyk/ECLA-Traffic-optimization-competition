from time import sleep
import sys
import traci
import traci.constants as tc

class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = pedestrians
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge

    def run(self):
        # Create a bus for the persons
        bus_index = 0
        for person in self.pedestrians:
            bus_id = f'bus_{bus_index}'
            bus_index += 1

            try:
                traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=person.depart + 240.0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
                traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
                
                traci.vehicle.changeTarget(bus_id, person.edge_from)
                traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
                

                traci.vehicle.setRoute(bus_id, [person.edge_from])
                traci.vehicle.changeTarget(bus_id, person.edge_to)
                traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

            except traci.exceptions.TraCIException as err:
                print("TraCIException: {0}".format(err))
            except:
                print("Unexpected error:", sys.exc_info()[0])

        traci.vehicle.subscribe('bus_0', (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_POSITION , tc.VAR_NEXT_STOPS ))

        step = 0
        while step <= self.simulation_steps:
            traci.simulationStep()
            if self.sleep_time > 0: 
                sleep(self.sleep_time)
            step += 1
            #print(traci.vehicle.getSubscriptionResults('bus_0'))

        traci.close()
