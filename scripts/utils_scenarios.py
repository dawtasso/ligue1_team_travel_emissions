from typing import Dict, List, Tuple

import pandas as pd

ScenarioRow = pd.Series
ScenarioEntries = List[Dict[str, object]]


def append_scenario(
    entries: ScenarioEntries,
    scenario_base: str,
    visiting_team: str,
    hosting_team: str,
    transport_type: str,
    emissions_kg_co2: float,
    emissions_kg_co2_wo_empty_bus: float,
    travel_time_seconds: float,
    alternative_selected: bool,
) -> None:
    """Append both the base scenario and its prime (') variant."""
    emission_empty_bus = emissions_kg_co2 - emissions_kg_co2_wo_empty_bus
    entries.append(
        {
            "scenario": scenario_base,
            "visiting_team": visiting_team,
            "hosting_team": hosting_team,
            "transport_type": transport_type,
            "emissions_kg_co2_from_transport": emissions_kg_co2_wo_empty_bus,
            "emissions_kg_co2_from_empty_bus": emission_empty_bus,
            "travel_time_seconds": travel_time_seconds,
            "alternative_selected": alternative_selected,
        }
    )
    entries.append(
        {
            "scenario": f"{scenario_base}'",
            "visiting_team": visiting_team,
            "hosting_team": hosting_team,
            "transport_type": transport_type,
            "emissions_kg_co2_from_transport": emissions_kg_co2_wo_empty_bus,
            "emissions_kg_co2_from_empty_bus": 0,
            "travel_time_seconds": travel_time_seconds,
            "alternative_selected": alternative_selected,
        }
    )


def select_option(
    row: ScenarioRow,
    threshold_seconds: float,
) -> Tuple[float, float, float, str, bool]:
    """Return emissions/time/transport based on thresholds logic."""

    use_alternative = row["alternative_travel_time_seconds"] < threshold_seconds

    particule = "alternative_" if use_alternative else ""

    return (
        row[f"{particule}emissions_kg_co2"],
        row[f"{particule}emissions_kg_co2_wo_empty_bus"],
        row[f"{particule}travel_time_seconds"],
        row[f"{particule}transport_type"],
        use_alternative,
    )


def build_scenarios(
    df: pd.DataFrame,
    scenario_time_limits: Dict[str, float],
) -> ScenarioEntries:
    """Generate all scenarios per travel row."""
    entries: ScenarioEntries = []

    for _, row in df.iterrows():
        visiting_team = row["visiting_team"]
        hosting_team = row["hosting_team"]
        if visiting_team == hosting_team:
            continue

        # Thresholded scenarios only apply to planes
        # if row["transport_type"] == "avion":
        for scenario in scenario_time_limits.keys():
            threshold = scenario_time_limits[scenario]
            (
                emissions,
                emissions_wo_empty_bus,
                travel_time,
                transport_type,
                alt_sel,
            ) = select_option(row, threshold_seconds=threshold)
            append_scenario(
                entries,
                scenario,
                visiting_team,
                hosting_team,
                transport_type,
                emissions,
                emissions_wo_empty_bus,
                travel_time,
                alt_sel,
            )

    return entries
