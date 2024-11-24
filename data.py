from __future__ import annotations
import csv
from typing import Any, Union
import json

import networkx as nx
import pandas as pd


class _Vertex:
    """A vertex in the food delivery database, used to represent a single user.

    The user is identified by a user id, which is stored as the item of the vertex.

    Instance Attributes:
        - item: The user id used to identify the user stored in this Vertex
        - one_time_orders: A mapping of a tuple containing the restaurant and cuisine of the order to the rating the
         user gave the order. This dictionary stores info for orders that have been placed only once by the user.
        - repeated_orders: A mapping of a tuple containing the restaurant and cuisine of the order to the rating the
         user gave the order. This dictionary stores info for orders that have been placed repeatedly by the user.
        - neighbours: The vertices that are adjacent to this vertex. These represent other users that have been
        "matched" with this user

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - all(u not in self.repeated_orders for u in self.one_time_orders)
    """
    item: Any
    one_time_orders: dict[tuple[str, str], int]
    repeated_orders: dict[tuple[str, str], int]
    neighbours: dict[_Vertex: Any]

    def __init__(self, item: Any) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours and no orders.
        """
        self.item = item
        self.one_time_orders = {}
        self.repeated_orders = {}
        self.neighbours = {}

    def add_order(self, restaurant: str, cuisine: str, rating: Any = 'N/A') -> None:
        """ Adds a new order to the users one_time_orders or repeated_orders, depending on whether the user has
        placed that order previously or not.

        Preconditions:
            - restaurant != ''
            - cuisine != ''
        """
        order = (restaurant, cuisine)
        if order not in self.one_time_orders and order not in self.repeated_orders:
            self.one_time_orders[order] = rating
        elif order in self.one_time_orders:
            self.repeated_orders[order] = rating
            self.one_time_orders.pop(order)
        else:
            pass


class Graph:
    """A graph used to represent the food delivery network. It contains all the users in the network and keeps track of
    the matches.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item)

    def add_edge(self, item1: Any, item2: Any, matched_cuisine: str) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours[v2] = matched_cuisine
            v2.neighbours[v1] = matched_cuisine
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def remove_edge(self, item1: Any, item2: Any) -> None:
        """Remove an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
            - self.adjacent(item1, item2)
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.remove(v2)
            v2.neighbours.remove(v1)
        else:
            raise ValueError

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self) -> set:
        """Return a set of all vertex items in this graph.
        """
        return set(self._vertices.keys())

    def save_to_json(self, filename: str) -> None:
        """Save the graph data to a JSON file."""
        user_id = int(filename)
        data2 = {
            str(user_id): [
                {str(k): v for k, v in self._vertices[user_id].one_time_orders.items()},
                {str(k): v for k, v in self._vertices[user_id].repeated_orders.items()},
                [str(user.item) for user in self._vertices[user_id].neighbours]  # Convert items to str
            ]
        }
        with open(filename, 'w') as file:
            json.dump(data2, file)

    def load_from_json(self, filename: str) -> None:
        """Load graph data from a JSON file."""
        user_id = int(filename)
        with open(filename, 'r') as file:
            data2 = json.load(file)
            self.add_vertex(user_id)
            self._vertices[user_id].one_time_orders = {
                tuple(map(str, k)): v for k, v in data2[str(user_id)][0].items()
            }
            self._vertices[user_id].repeated_orders = {
                tuple(map(str, k)): v for k, v in data2[str(user_id)][1].items()
            }
            for item in data2[str(user_id)][2]:
                self.add_edge(user_id, int(item))

    @property
    def vertices(self):
        return self._vertices


data = pd.read_csv("food_order.csv")
data = data.filter(items=['customer_id', 'restaurant_name', 'cuisine_type', 'rating'])

g = Graph()
menu = {}
for index, row in data.iterrows():
    if row['customer_id'] not in g.get_all_vertices():
        g.add_vertex(row['customer_id'])
        vertex = g.vertices[row['customer_id']]
        vertex.add_order(row['restaurant_name'], row['cuisine_type'], row['rating'])
    else:
        g.vertices[row['customer_id']].add_order(row['restaurant_name'], row['cuisine_type'], row['rating'])

    if row['restaurant_name'] not in menu:
        menu[row['restaurant_name']] = {row['cuisine_type']}
    else:
        menu[row['restaurant_name']].add(row['cuisine_type'])

for x in g.vertices:
    for y in g.vertices:
        if not g.adjacent(x, y):
            for a in g.vertices[x].repeated_orders:
                for b in g.vertices[y].repeated_orders:
                    if a == b:
                        g.add_edge(x, y, a[1])