class InvalidLocalDateTimeError(ValueError):
    """The supplied local date/time or timezone cannot be used."""


class AmbiguousTimeError(ValueError):
    """A local wall-clock time maps to two different UTC instants."""

    def __init__(self, valid_offsets: tuple[int, int]) -> None:
        self.valid_offsets = valid_offsets
        super().__init__("Local time is ambiguous; provide fold or one of the valid UTC offsets.")


class NonExistentTimeError(ValueError):
    """A local wall-clock time did not occur because clocks moved forward."""


class EphemerisConfigurationError(RuntimeError):
    """Required ephemeris data or configuration is unavailable."""


class EphemerisCalculationError(RuntimeError):
    """The ephemeris engine could not produce the requested calculation."""
