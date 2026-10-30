"""LangChain tools used by Boond's water-harvesting agents."""

import json

from langchain_core.tools import tool

from ..waterdata.rainfall import (
    estimate_harvestable_water_liters,
    fetch_rainfall_data,
)


@tool
def get_rainfall_harvest_estimate(location: str, roof_area_m2: float) -> str:
    """Fetch recent rainfall for a location and estimate rooftop harvest volume.

    Uses the latest 30 completed days of rainfall. The estimate assumes a
    runoff coefficient of 0.8, which can vary with roof and collection design.
    """
    rainfall = fetch_rainfall_data(location, days=30)
    runoff_coefficient = 0.8
    harvestable_liters = estimate_harvestable_water_liters(
        rainfall_mm=rainfall["total_rainfall_mm"],
        roof_area_m2=roof_area_m2,
        runoff_coefficient=runoff_coefficient,
    )

    result = {
        "location": rainfall["location"],
        "period": rainfall["period"],
        "total_rainfall_mm": rainfall["total_rainfall_mm"],
        "days_with_data": rainfall["days_with_data"],
        "estimated_harvestable_liters": harvestable_liters,
        "runoff_coefficient": runoff_coefficient,
        "data_source": rainfall["data_source"],
    }
    return json.dumps(result)
