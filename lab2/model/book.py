from dataclasses import dataclass, field

@dataclass
class Book:
    title: str
    author: str
    publisher: str
    volumes: int
    print_run: int
    id: int = None
    total_volumes: int = field(init=False)

    def __post_init__(self):
        if not isinstance(self.volumes, int) or not isinstance(self.print_run, int):
            raise ValueError("Число томов и тираж должны быть целыми числами.")
        self.total_volumes = self.volumes * self.print_run