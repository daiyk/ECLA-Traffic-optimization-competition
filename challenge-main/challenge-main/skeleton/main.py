import os
import sys
import xml.etree.ElementTree as ET
import random
import csv

#SUMO_HOME
os.environ["SUMO_HOME"] = r"C:\Temp\sumo-win64-git\sumo-git"

# Add the traci python library to the tools path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# Load traci
import traci
import traci.constants as tc
from simulation import Simulation


def main():

    ######################################################################
    # Paramters

    # number of simulation step (max. value is 86400 steps = 24 h * 60 min * 60 s)
    simulation_steps = 86400
    # sleep time between 2 simulation step. no sleep is set to 0.0
    sleep_time = 0.01

    # seed and scale factor for creating pedestrians
    pedestrians_seed = 30
    pedestrians_scale_factor = 10.0
    pedestrians_until_step = simulation_steps # create pedestrians up until this step

    # location of the sumocfg file
    sumocfg_file = r"..\..\trafficmap\aarhus\osm.sumocfg"
    # location of the XML file containing the city network
    network_xml_file = r'..\..\trafficmap\aarhus\osm.net.xml'

    # logfiles
    logs_folder = './logs/'
    sumo_log_file = logs_folder + 'sumo.log'
    traci_log_file = logs_folder + 'traci.log'
    delete_logs_at_start = False

    ######################################################################
    # Setup

    clean_logs(logs_folder=logs_folder, sumo_log_file=sumo_log_file, traci_log_file=traci_log_file, delete_logs_at_start=delete_logs_at_start)
    start_traci_simulation(sumocfg_file=sumocfg_file, sumo_log_file=sumo_log_file, traci_log_file=traci_log_file)
    pedestrians = add_pedestrians(seed=pedestrians_seed, scale_factor=pedestrians_scale_factor, net_xml_file=network_xml_file, max_steps=pedestrians_until_step)

    ######################################################################

    # Edges for the starting and ending for the bus depot
    bus_depot_start_edge = '744377000#0'
    bus_depot_end_edge = '521059831#0'

    simulation = Simulation(simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge)
    simulation.run()

    ######################################################################



def clean_logs(logs_folder: str, sumo_log_file: str, traci_log_file: str, delete_logs_at_start: bool):
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    if delete_logs_at_start:
        if os.path.exists(sumo_log_file):
            os.remove(sumo_log_file)
        if os.path.exists(traci_log_file):
            os.remove(traci_log_file)
    

def start_traci_simulation(sumocfg_file: str, sumo_log_file: str, traci_log_file: str):
    sumoBinary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui')
    sumoCmd = [sumoBinary, "-c", sumocfg_file, "--log", sumo_log_file]
    traci.start(sumoCmd, traceFile=traci_log_file)

def add_pedestrians(seed: int, scale_factor: float, net_xml_file: str, max_steps: int):
    pedestrians = generate_random_people(seed=seed, scale_factor=scale_factor, net_xml_file=net_xml_file, max_steps=max_steps)

    for person in pedestrians:
        id = person.id
        edge_from = person.edge_from
        edge_to = person.edge_to
        position_from = person.position_from
        position_to = person.position_to
        depart = person.depart

        traci.person.add(personID=id, edgeID=edge_from, pos=position_from, depart=depart, typeID='DEFAULT_PEDTYPE')
        stage = traci.simulation.Stage(type=tc.STAGE_DRIVING, line="ANY", edges=[edge_to],
                                       departPos=0, arrivalPos=position_to, description="Driven as passenger")
        traci.person.appendStage(id, stage)
        waitingStage = traci.simulation.Stage(type=tc.STAGE_WAITING, edges=[edge_to], travelTime=200, description="Arrived at destination")
        traci.person.appendStage(id, waitingStage)

    return pedestrians

def generate_random_people(seed: int, scale_factor: float, net_xml_file: str, max_steps: int):
    tree = ET.parse(net_xml_file)
    root = tree.getroot()

    edges = []
    for edge in root.findall('.//edge'):
        if edge.attrib['id'].startswith(':cluster_'):
            continue
        if not ('type' in edge.attrib):
            continue
        if float(edge.findall('./lane')[0].attrib['length']) < 40:
            continue
        edges.append(edge)
    random.seed(seed)

    pedestrian_weights = parse_pedestrian_weights()

    people = []
    for pedestrian_weight in pedestrian_weights:
        t0 = pedestrian_weight.t0
        t1 = pedestrian_weight.t1
        weight = round(pedestrian_weight.weight * scale_factor)

        if t0 >= max_steps:
            continue
        
        count = 0
        while count < weight:
            count += 1
            edge1_index = random.randint(0, len(edges) - 1)
            edge2_index = random.randint(0, len(edges) - 1)

            edge1 = edges[edge1_index]
            edge2 = edges[edge2_index]

            len1 = float(edge1.findall('./lane')[0].attrib['length'])
            len2 = float(edge2.findall('./lane')[0].attrib['length'])

            pos1 = random.uniform(len1 * 0.4, len1 * 0.6)
            pos2 = random.uniform(len2 * 0.4, len2 * 0.6)

            depart = random.uniform(t0, t1)

            i = len(people)
            person = Person(f'person_{i}', edge1.attrib['id'], edge2.attrib['id'], pos1, pos2, depart)
            people.append(person)
    return people

def parse_pedestrian_weights():
    pedestrian_weights = []
    with open('pedestrians_weights.csv', encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        first_line = True
        for row in csv_reader:
            if first_line:
                first_line = False
                continue
            else:
                pedestrian_weight = PedestrianWeight(int(row[0]), int(row[1]), float(row[2]))
                pedestrian_weights.append(pedestrian_weight)

    return pedestrian_weights

class Person:
    # init method or constructor
    def __init__(self, id: str, edge_from: str, edge_to: str, position_from: float, position_to: float, depart: float):
        self.id = id
        self.edge_from = edge_from
        self.edge_to = edge_to
        self.position_from = position_from
        self.position_to = position_to
        self.depart = depart

class PedestrianWeight:
    # init method or constructor
    def __init__(self, t0: int, t1: int, weight: float):
        self.t0 = t0
        self.t1 = t1
        self.weight = weight

if __name__ == '__main__':
    main()
