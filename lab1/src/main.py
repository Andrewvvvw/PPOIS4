from src.interface.cli import SalonCLI
from src.utils.data_manager import SalonDataManager
from src.entities.salon import Salon

def main():
    data_manager: SalonDataManager = SalonDataManager("salon_save.json")
    salon: Salon = data_manager.load()

    cli: SalonCLI = SalonCLI(salon)

    try:
        cli.run()
    finally:
        data_manager.save(salon)

if __name__ == "__main__":
    main()