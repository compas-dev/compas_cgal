"""Triangulation plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.geometry import Point

    from compas_cgal.types import FacesNumpy
    from compas_cgal.types import VerticesFacesNumpy


@plugin(category="triangulation", requires=["compas_cgal"])
def delaunay_triangulation(points: list[Point]) -> FacesNumpy:
    from compas_cgal.triangulation import delaunay_triangulation as implementation

    return implementation(points)


@plugin(category="triangulation", requires=["compas_cgal"])
def constrained_delaunay_triangulation(boundary: list[Point], points=None, holes=None, curves=None) -> VerticesFacesNumpy:
    from compas_cgal.triangulation import constrained_delaunay_triangulation as implementation

    return implementation(boundary, points, holes, curves)


@plugin(category="triangulation", requires=["compas_cgal"])
def conforming_delaunay_triangulation(boundary, points=None, holes=None, curves=None) -> VerticesFacesNumpy:
    from compas_cgal.triangulation import conforming_delaunay_triangulation as implementation

    return implementation(boundary, points, holes, curves)


__all__ = ["conforming_delaunay_triangulation", "constrained_delaunay_triangulation", "delaunay_triangulation"]
