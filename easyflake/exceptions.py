class SequenceOverflowError(Exception):
    def __init__(self, bits: int):
        self.max_value = (1 << bits) - 1

    def __str__(self):
        return f"The sequence has reached the maximum value of {self.max_value}."
