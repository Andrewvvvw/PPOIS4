from interface.cli import SalonCLI
from src.utils.data_manager import SalonDataManager

def main():
    data_manager = SalonDataManager("salon_save.json")
    salon = data_manager.load()

    cli = SalonCLI(salon)

    try:
        cli.run()
    finally:
        data_manager.save(salon)

if __name__ == "__main__":
    main()