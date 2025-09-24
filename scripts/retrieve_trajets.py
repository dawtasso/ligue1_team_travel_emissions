from backend.services.train_service import TrainTrajetService
from backend.services.plane_service import PlaneTrajetService
from backend.services.car_service import CarTrajetService
from dotenv import load_dotenv
import os
from backend.global_variables import TRAIN_EMISSIONS_FILENAME, FLIGHT_EMISSIONS_FILENAME, CAR_EMISSIONS_FILENAME
load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

def main():
    # Initialize services
    train_service = TrainTrajetService(api_key)
    plane_service = PlaneTrajetService(api_key)
    car_service = CarTrajetService(api_key)

    # print("Processing train routes...")
    train_service.run_complete_analysis()
    print(f"Train routes saved to {TRAIN_EMISSIONS_FILENAME}")

    print("Processing plane routes...")
    plane_service.run_complete_analysis()
    print(f"Plane routes saved to {FLIGHT_EMISSIONS_FILENAME}")

    print("Processing car routes...")
    car_service.run_complete_analysis()
    print(f"Car routes saved to {CAR_EMISSIONS_FILENAME}")

if __name__ == "__main__":
    main()
