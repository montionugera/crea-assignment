import os
from typing import List

import pytest

from main import Route
from main import RouteNotFoundException
from main import TripGraph
from main import routes_from_csv

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_example():
    assert 1 == 1


def test_load_csv_should_success() -> None:
    data = routes_from_csv(os.path.join(dir_path, "../example.csv"))
    assert data == [Route(origin='A', destination='B', minutes_spend=5),
                    Route(origin='B', destination='C', minutes_spend=5),
                    Route(origin='C', destination='D', minutes_spend=7),
                    Route(origin='A', destination='D', minutes_spend=15),
                    Route(origin='E', destination='F', minutes_spend=5),
                    Route(origin='F', destination='G', minutes_spend=5),
                    Route(origin='G', destination='H', minutes_spend=10),
                    Route(origin='H', destination='I', minutes_spend=3),
                    Route(origin='I', destination='J', minutes_spend=5),
                    Route(origin='G', destination='J', minutes_spend=20)]


@pytest.mark.parametrize(
    "origin,destination,expected_routes", [
        ('A', 'B', [Route(origin='A', destination='B', minutes_spend=5)]),
        ('A', 'D', [Route(origin='A', destination='D', minutes_spend=15)]),
        ('G', 'I', [Route(origin='G', destination='H', minutes_spend=10),
                    Route(origin='H', destination='I', minutes_spend=3), ]),
        ('G', 'J', [Route(origin='G', destination='H', minutes_spend=10),
                    Route(origin='H', destination='I', minutes_spend=3),
                    Route(origin='I', destination='J', minutes_spend=5), ])
    ]
)
def test_find_trip_should_success(origin: str, destination: str, expected_routes: List[Route]) -> None:
    routes = routes_from_csv(os.path.join(dir_path, "../example.csv"))
    graph = TripGraph(origin, routes)
    routes = graph.find_shortest_path(destination)
    assert routes == expected_routes


@pytest.mark.parametrize(
    "origin,destination", [
        ('A', 'J'),
    ]
)
def test_find_trip_destination_can_not_reach_should_error(origin: str, destination: str) -> None:
    routes = routes_from_csv(os.path.join(dir_path, "../example.csv"))
    graph = TripGraph(origin, routes)
    with pytest.raises(RouteNotFoundException):
        graph.find_shortest_path(destination)
