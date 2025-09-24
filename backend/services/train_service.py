import pandas as pd
from typing import List, Tuple, Optional, Dict, Any

from backend.global_variables import TRAIN_EMISSIONS_FILENAME, TRAIN_EMISSION_FACTOR, NUMBER_OF_PASSENGERS
from backend.services.base_transport_service import BaseTransportService, RouteData


class TrainTrajetService(BaseTransportService):
    """
    Simplified service class for handling train journey calculations.
    
    This service provides functionality to:
    - Calculate train routes between stadiums using Google Maps transit API
    - Compare train vs car emissions for optimal route selection
    - Generate comprehensive carbon footprint analysis
    """
    
    def __init__(self, api_key: str) -> None:
        """
        Initialize the TrainTrajetService with Google Maps API key.
        
        Args:
            api_key (str): Google Maps API key for geocoding and directions
        """
        super().__init__(api_key)
        
        # Carbon emission constants (gCO2/passenger/km)
        # Source: https://bigmedia.bpifrance.fr/nos-dossiers/empreinte-carbone-des-trajets-en-train-calcul-et-decarbonation
        self.train_emission_factor = TRAIN_EMISSION_FACTOR  # kgCO2/passenger/km
        self.number_of_passengers = NUMBER_OF_PASSENGERS  # Number of passengers (team + staff)

    def calculate_route(self, departure: str, arrival: str, departure_coords: Tuple[float, float], 
                       arrival_coords: Tuple[float, float]) -> Optional[RouteData]:
        """
        Calculate train route between two stadiums.
        
        Args:
            departure: Departure stadium name
            arrival: Arrival stadium name
            departure_coords: Departure coordinates (lat, lng)
            arrival_coords: Arrival coordinates (lat, lng)
            
        Returns:
            RouteData object or None if calculation fails
        """
        origin_coords = self._format_coordinates(departure_coords[0], departure_coords[1])
        destination_coords = self._format_coordinates(arrival_coords[0], arrival_coords[1])
        
        # Get train route using transit mode
        train_route = self._get_train_route(origin_coords, destination_coords)
        
        if train_route:
            # Calculate train emissions
            train_emissions = self._calculate_train_emissions(train_route)
            
            return RouteData(
                departure=departure,
                arrival=arrival,
                travel_time=train_route['duration'],
                distance=train_route['distance'],
                emissions=train_emissions * 2,  # Round trip
                transport_type="train",
                route_details={"train_route_details":train_route['details']},
            )
        
        return RouteData(
                departure=departure,
                arrival=arrival,
                travel_time=0,
                distance=0,
                emissions=0,
                transport_type="train",
                route_details={"train_route_details":"No train route found"},
            )

    def _get_train_route(self, origin: str, destination: str) -> Optional[Dict[str, Any]]:
        """
        Get the fastest transit route involving trains between two coordinates.
        
        Args:
            origin (str): Origin coordinates as "lat,lng"
            destination (str): Destination coordinates as "lat,lng"
            
        Returns:
            Dict with route information or None if no train route found
        """
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "transit",
            "alternatives": "true",  # Get multiple alternatives to find best train route
            "key": self.api_key
        }
        
        data = self._make_google_maps_request("https://maps.googleapis.com/maps/api/directions/json", params)
        
        if data and data.get("status") == "OK" and data.get("routes"):
            # Find the fastest route that includes train segments
            best_route = None
            shortest_duration = float('inf')
            
            for route in data["routes"]:
                leg = route["legs"][0]
                train_details = self._extract_train_details(leg["steps"])
                
                # Only consider routes that have train segments
                if train_details:
                    duration = leg["duration"]["value"]
                    if duration < shortest_duration:
                        shortest_duration = duration
                        best_route = {
                            'duration': duration,
                            'distance': leg["distance"]["value"] / 1000,  # Convert to km
                            'details': train_details
                        }
            
            return best_route
        
        return None

    def _extract_train_details(self, steps: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """
        Extract train-specific details from route steps.
        
        Args:
            steps: List of route steps from Google Maps API
            
        Returns:
            List of train segment details or None if no train segments found
        """
        train_segments = []
        
        for step in steps:
            if step["travel_mode"] == "TRANSIT":
                transit = step["transit_details"]
                vehicle_type = transit["line"]["vehicle"]["type"]
                
                # Only include train routes
                if vehicle_type in ["LONG_DISTANCE_TRAIN", "HIGH_SPEED_TRAIN", "HEAVY_RAIL"]:
                    line_name = transit["line"].get("short_name") or transit["line"].get("name")
                    
                    train_segments.append({
                        'line_name': line_name,
                        'vehicle_type': vehicle_type,
                        'departure_stop': transit["departure_stop"]["name"],
                        'arrival_stop': transit["arrival_stop"]["name"],
                        'distance': step["distance"]["value"] / 1000,  # Convert to km
                        'duration': step["duration"]["value"]
                    })
        
        return train_segments if train_segments else None

    def _calculate_train_emissions(self, train_route: Dict[str, Any]) -> float:
        """
        Calculate carbon emissions for a train route.
        
        Args:
            train_route: Train route data with details
            
        Returns:
            Emissions in kg CO2 per passenger
        """
        total_emissions = 0
        
        for segment in train_route['details']:
            distance_km = segment['distance']
            vehicle_type = segment['vehicle_type']
            
            # Use appropriate emission factor based on train type
            if vehicle_type == "HIGH_SPEED_TRAIN":
                emission_factor = self.train_emission_factor
            else:
                emission_factor = self.train_emission_factor
            
            total_emissions += distance_km * emission_factor
        
        return total_emissions * self.number_of_passengers * 2 # kg of CO2

    def run_complete_analysis(self, output_filename: str = TRAIN_EMISSIONS_FILENAME) -> List[RouteData]:
        """
        Run the complete analysis pipeline.
        
        Args:
            output_filename: Name of the output CSV file
            
        Returns:
            List of RouteData objects
        """
        super().run_complete_analysis(output_filename)