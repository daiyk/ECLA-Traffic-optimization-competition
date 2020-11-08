import collections
import os
import sys
import math

#SUMO_HOME
os.environ["SUMO_HOME"] = r"C:\Users\admin\Documents\Eclipse\Sumo"

# Add the traci python library to the tools path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib


def calDistoThePoint(edges, x0, y0):
    # loop over the edges
    dist = []
    for e in edges:
        x1, y1 = e.getFromNode().getCoord()
        x2, y2 = e.getToNode().getCoord()
        x_e = x1 + x2 / 2.0
        y_e = y1 + y2 / 2.0
        dist.append(math.sqrt((x_e - x0) ** 2 + (y_e - y0) ** 2))
    return dist


class map_manager:
    """
    docstring
    """

    def __init__(self, network_path, bus_start_edge_id, bus_stop_edge_id):
        if not os.path.exists(network_path):
            print("map_manager: provided 'network_path' is Invalid")
        self._net = sumolib.net.readNet(network_path)
        edges = self._net.getEdges()
        self._numEdges = len(edges)

        # stores edge ids
        self._edgeIDs = [e.getID() for e in edges]

        # store node ids
        nodes = self._net.getNodes()
        self._numNodes = len(nodes)
        self._nodeIDs = [n.getID() for n in nodes]

        self._edgeDistToStart = None
        self._edgeDistToEnd = None
        if (bus_start_edge_id in self._edgeIDs) and (bus_stop_edge_id in self._edgeIDs):
            x_s1, y_s1 = self._net.getEdge(bus_start_edge_id).getFromNode().getCoord()
            x_s2, y_s2 = self._net.getEdge(bus_start_edge_id).getToNode().getCoord()
            self._edgeDistToStart = calDistoThePoint(edges, (x_s1 + x_s2) / 2.0, (y_s1 + y_s2) / 2.0)

            x_e1, y_e1 = self._net.getEdge(bus_stop_edge_id).getFromNode().getCoord()
            x_e2, y_e2 = self._net.getEdge(bus_stop_edge_id).getToNode().getCoord()
            self._edgeDistToEnd = calDistoThePoint(edges, (x_e1 + x_e2) / 2.0, (y_e1 + y_e2) / 2.0)

        self._nodeDict = {}
        # mapping from nodeID to index
        for idx, n in enumerate(nodes):
            self._nodeDict[n.getID()] = idx

        # build inital adjacent list
        self.edgeid_list = [["" for x in range(self._numNodes)] for y in range(self._numNodes)]
        self.adjacent_list = [[] for x in range(self._numNodes)]
        # init adjacent list, this should be adjusted according to the current traffic condition
        for e in edges:
            self.adjacent_list[self._nodeDict[e.getFromNode().getID()]].append(self._nodeDict[e.getToNode().getID()])
            self.edgeid_list[self._nodeDict[e.getFromNode().getID()]][self._nodeDict[e.getToNode().getID()]] = e.getID()
        # might need to store edge ids

    def getDistToStart(self):
        return self._edgeDistToStart

    def getDistToEnd(self):
        return self._edgeDistToEnd

    def getEdgeIDs(self):
        return self._edgeIDs

    def getEdge(self, id):
        return self._net.getEdge(id)

    def hasEdge(self, id):
        return id in self._edgeIDs

    def getEdgeIDsWithourInterval(self):
        return [e.getID() for e in self._net.getEdges() if e.getFunction() == '']

    def getEdgeFrom(self, id):
        if id in self._edgeIDs:
            return self._net.getEdge(id).getFromNode().getID()
        return None

    def getEdgeTo(self, id):
        if id in self._edgeIDs:
            return self._net.getEdge(id).getToNode().getID()
        else:
            return None

    def getNodeIDs(self):
        return self._nodeIDs

    def getNode(self, id):
        return self._net.getNode(id)

    def hasNode(self, id):
        return id in self._nodeIDs

    # input edge id "from" and edge id "to" return the result of pair [edgelist, cost], if path is not found (edge not connected), then return[None, maxCost]
    # if edge id doesn't exist return [None,None]
    def getShortestPaths(self, edgeID_from, edgeID_to):
        if (edgeID_from in self._edgeIDs) and (edgeID_to in self._edgeIDs):
            return self._net.getShortestPath(self.getEdge(edgeID_from), self.getEdge(edgeID_to))
        else:
            return None, None

    # currentEdgePerson should be the dictionary with[edgeId, persons]
    def getWeighedShortestPaths(self, edgeID_from, capacity, currentEdgePerson):
        if (edgeID_from not in self._edgeIDs):
            return None
        cost = [[-1, 0] for i in range(self._numNodes)]
        start_id = self._nodeDict[self.getEdge(edgeID_from).getToNode().getID()]
        cost[start_id][0] = 0
        personNum = [0 for i in range(self._numNodes)]
        personNum[start_id] = currentEdgePerson[
            self.edgeid_list[self._nodeDict[self.getEdge(edgeID_from).getFromNode().getID()]][start_id]]
        pre_id = [-1 for i in range(self._numNodes)]
        pre_id[start_id] = start_id

        # stores in the queue
        queue = []
        queue.append(start_id)
        FindTarget = False
        currentCap = 0
        endID = -1
        while queue:
            pop_id = queue.pop(0)
            if currentCap == capacity:
                break
            for neighbor in self.adjacent_list[pop_id]:
                if (cost[neighbor][0] == -1):
                    queue.append(neighbor)
                currentCost = cost[pop_id][0] + self.getEdge(self.edgeid_list[pop_id][neighbor]).getLength()
                if (currentCost < cost[neighbor][0] or cost[neighbor][0] == -1):
                    cost[neighbor][0] = currentCost
                    pre_id[neighbor] = pop_id
                    currentPersonNum = personNum[pop_id] + currentEdgePerson[self.edgeid_list[pop_id][neighbor]]
                    if (currentPersonNum >= capacity):
                        endID = neighbor
                        FindTarget = True
                        break
                    else:
                        personNum[neighbor] = currentPersonNum
            if FindTarget:
                break
        if not FindTarget:
            return []
        shortestPath = []
        while pre_id[endID] != endID:
            shortestPath.append(self.edgeid_list[pre_id[endID]][endID])
            endID = pre_id[endID]
        return shortestPath

# if __name__=="__main__":
#     filePath = "F:\\polyhack\\trafficmap\\aarhus\\osm.net.xml"
#     # test network reading function
#     bus_depot_start_edge = '744377000#0'
#     bus_depot_end_edge = '521059831#0'
#     network = map_manager(filePath,bus_depot_start_edge,bus_depot_end_edge)
#     ids = network.getEdgeIDs()
#     print('\nlength of ids size: {}'.format(len(ids)))
#
#     nodeids = network.getNodeIDs()
#     print('\nlength of nodes size: {}'.format(len(nodeids)))
#
#     shortest,cost = network.getShortestPaths(ids[0],ids[-1])
#     print('\nstart id to end id: \n {}'.format([e.getID() for e in shortest]))
#     print('\n with cost: {}'.format(cost))
#     print('\ndist to start: {}'.format(network.getDistToStart()))
#



        

    
