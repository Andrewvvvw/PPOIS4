import os
import sys
from pathlib import Path
from django.core.management import execute_from_command_line


def main() -> None:
    common_path = Path(__file__).resolve().parent.parent / "common"
    common_str = str(common_path)
    if common_str not in sys.path:
        sys.path.insert(0, common_str)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salon_site.settings")

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
