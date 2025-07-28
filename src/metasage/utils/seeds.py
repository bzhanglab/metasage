class SeedGenerator:
    initial_state: int | str

    def __init__(self, initial_state: int | str):
        self.initial_state = initial_state

    def get_seed(self, *args, **kwargs) -> str | int | float:
        return 0


class FixedSeedGeneratorByRun(SeedGenerator):
    def __init__(self, initial_state):
        super().__init__(initial_state)

    def get_seed(self, *args, **kwargs):
        if "run" not in kwargs:
            raise ValueError(
                "'run' key not provided to get_seed function in FixedSeedGeneratorByRun object"
            )
        return kwargs["run"] + self.initial_state
