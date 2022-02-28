import Edge


class Node:
    def __init__(self, state_list: tuple):
        self.state_list: tuple = state_list
        self.outgoing: list[Edge] = []
        self.outgoing_map: dict[tuple:Edge] = {}

    def add_outgoing(self, edge: Edge) -> None:
        self.outgoing.append(edge)
        self.outgoing_map[edge.n2.state_list] = edge

    def add_all_outgoing(self, edge_list: list[Edge]) -> None:
        self.outgoing += edge_list
        self.outgoing_map += {i.n2.state_list: i for i in edge_list}

    def compare(self, s_list: tuple) -> bool:
        return s_list == self.state_list
