from itertools import combinations

from app.modules.astrology.domain.natal_chart import Aspect, ChartPoint

ASPECT_DEFINITIONS = (
    ("conjunction", 0.0, 8.0),
    ("sextile", 60.0, 4.0),
    ("square", 90.0, 6.0),
    ("trine", 120.0, 6.0),
    ("opposition", 180.0, 8.0),
)


def angular_separation(longitude_a: float, longitude_b: float) -> float:
    difference = abs((longitude_a % 360.0) - (longitude_b % 360.0))
    return min(difference, 360.0 - difference)


def calculate_aspects(positions: tuple[ChartPoint, ...]) -> tuple[Aspect, ...]:
    aspects: list[Aspect] = []
    for body_a, body_b in combinations(positions, 2):
        actual_angle = angular_separation(body_a.longitude, body_b.longitude)
        for aspect_type, exact_angle, maximum_orb in ASPECT_DEFINITIONS:
            orb = abs(actual_angle - exact_angle)
            if orb <= maximum_orb:
                aspects.append(
                    Aspect(
                        body_a=body_a.name,
                        body_b=body_b.name,
                        aspect_type=aspect_type,
                        exact_angle=exact_angle,
                        actual_angle=actual_angle,
                        orb=orb,
                    )
                )
                break
    return tuple(aspects)
