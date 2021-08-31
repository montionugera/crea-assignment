from __future__ import annotations

import csv
import getopt
import sys
from collections import defaultdict
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel


class RouteNotFoundException(Exception):
    pass


class TripGraph:
    origin: str
    _routes_by_destination: Dict[str, List[Route]]
    _not_added_routes: List[Route]
    _routes_by_origin: Dict[str, Route]

    def __init__(self, origin: str, routes: List[Route]):
        self.origin = origin
        self._not_added_routes = [route for route in routes]
        self._not_added_routes.sort(key=lambda x: x.minutes_spend)
        self.cost_by_origin_destination_pair = {}
        self._routes_by_origin = defaultdict(list)
        for route in self._not_added_routes:
            self._routes_by_origin[route.origin].append(route)

        origin_routes = self._routes_by_origin[origin]
        if len(origin_routes) == 0:
            Exception(f"Origin '{origin}' not found in routes")

        self._routes_by_destination = {}
        shortest_origin_route = origin_routes[0]
        self._add_route(shortest_origin_route)

    def _add_route(self, route: Route):
        route_index = 0
        for index, _route_element in enumerate(self._not_added_routes):
            if route == _route_element:
                route_index = index
        self._not_added_routes.pop(route_index)
        routes = self._routes_by_destination.get(route.origin, []).copy()
        routes.append(route)
        self._routes_by_destination[route.destination] = routes

    def find_shortest_path(self, destination: str) -> List[Route]:
        if destination == self.origin:
            Exception(f"Invalid input destination == origin")
        match_routes = self._routes_by_destination.get(destination, None)
        while match_routes is None:
            print(f"self._routes_by_destination {self._routes_by_destination}")
            edges = [self.origin] + [node_key for node_key in list(self._routes_by_destination.keys())]
            cost_by_edge = {}
            for edge in edges:
                routes = self._routes_by_destination.get(edge, [])
                cost_by_edge[edge] = sum([route.minutes_spend for route in routes])
            # find shortest path
            target_route_cost: Optional[int] = None
            target_route: Optional[Route] = None
            for _route in self._not_added_routes:
                if _route.origin in edges:
                    _forecast_cost = _route.minutes_spend + cost_by_edge.get(_route.origin)
                    if target_route_cost is None or target_route_cost > _forecast_cost:
                        print(f"target_route {target_route}")
                        target_route_cost, target_route = _forecast_cost, _route
            if target_route is None:
                raise RouteNotFoundException("destination can not reach")
            else:
                self._add_route(target_route)
                match_routes = self._routes_by_destination.get(destination, None)
        return match_routes


class Route(BaseModel):
    origin: str
    destination: str
    minutes_spend: int

    def __init__(self, **kwargs):
        super(Route, self).__init__(**kwargs)


def routes_from_csv(file_path: str) -> List[Route]:
    with open(file_path, newline='') as csv_file:
        data = list(csv.reader(csv_file))
        rows = []
        for origin, destination, minutes_spend in data:
            rows.append(Route(origin=origin, destination=destination, minutes_spend=minutes_spend))
        return rows


HELP_MSG = """
Please run with --file argument
ex.
'main.py --file <input csv file>'
"""
if __name__ == '__main__':
    input_file = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:", ["file="])
    except getopt.GetoptError:
        print(HELP_MSG)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ["--file"]:
            input_file = arg
    if input_file == '':
        print(HELP_MSG)
        sys.exit(2)
    routes = routes_from_csv(input_file)
    origin = input("What station are you getting on the train?:")
    graph = TripGraph(origin, routes)
    destination = input("What station are you getting off the train?:")
    try:
        routes = graph.find_shortest_path(destination=destination)
        stop_num = len(routes) - 1
        total_time_in_minutes = sum([route.minutes_spend for route in routes])
        print(f'Your trip from {origin} to {destination} include {stop_num} stops' + \
              f'and will take {total_time_in_minutes} minutes.')
    except RouteNotFoundException:
        print(f"Your trip from {origin} to {destination} can not be found.")
        pass
