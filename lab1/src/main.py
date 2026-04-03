from pathlib import Path

from salon_core.application.repositories.json_repository import JsonSalonRepository
from salon_core.application.service import SalonAppService
from src.interface.cli import SalonCLI


def main() -> None:
    save_path = Path(__file__).resolve().parent / "salon_save.json"
    repository = JsonSalonRepository(str(save_path), default_salon_name="BEST SALON")
    app_service = SalonAppService(repository)

    cli = SalonCLI(app_service)
    cli.run()


if __name__ == "__main__":
    main()
