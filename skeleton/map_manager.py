import os
import sys


#SUMO_HOME
os.environ["SUMO_HOME"] = r"E:\sumo"

# Add the traci python library to the tools path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib

class map_manager:
    """
    docstring
    """
    def __init__(self,network_path):
        if not os.path.exists(network_path):
            print ("map_manager: provided 'network_path' is Invalid")
        self._net = sumolib.net.readNet(network_path)
        edges = self._net.getEdges()
        self._numEdges = len(edges)

        # stores edge ids
        self._edgeIDs=[e.getID() for e in edges]

        # store node ids
        nodes = self._net.getNodes()
        self._numNodes = len(nodes)
        self._nodeIDs = [n.getID() for n in nodes]

    def getEdgeIDs(self):
        return self._edgeIDs
    
    def getEdge(self,id):
        return self._net.getEdge(id)
    
    def hasEdge(self,id):
        return id in self._edgeIDs
    
    def getEdgeIDsWithourInterval(self):
        return [e.getID() for e in self._net.getEdges() if e.getFunction() == '']
    
    def getNodeIDs(self):
        return self._nodeIDs
    def getNode(self,id):
        return self._net.getNode(id)
    def hasNode(self,id):
        return id in self._nodeIDs

    # input edge id "from" and edge id "to" return the result of pair [edgelist, cost], if path is not found (edge not connected), then return[None, maxCost]
    # if edge id doesn't exist return [None,None]
    def getShortestPaths(self,edgeID_from,edgeID_to):
        if (edgeID_from in self._edgeIDs) and (edgeID_to in self._edgeIDs):
            return self._net.getShortestPath(self.getEdge(edgeID_from),self.getEdge(edgeID_to))
        else:
            return None,None


    
# if __name__=="__main__":
#     filePath = "F:\\polyhack\\trafficmap\\aarhus\\osm.net.xml"
#     # test network reading function
#     network = map_manager(filePath)
#     ids = network.getEdgeIDs()
#     print('\nlength of ids size: {}'.format(len(ids)))

#     nodeids = network.getNodeIDs()
#     print('\nlength of nodes size: {}'.format(len(nodeids)))

#     shortest,cost = network.getShortestPaths(ids[0],ids[-1])
#     print('\nstart id to end id: \n {}'.format([e.getID() for e in shortest]))
#     print('\n with cost: {}'.format(cost))




        

    
