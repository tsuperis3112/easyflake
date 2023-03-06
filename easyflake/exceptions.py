class SequenceOverflowError(Exception):
    def __init__(self, bits: int):
        self.bits = bits
        max_val = (1 << bits) - 1
        super().__init__("The sequence has reached the maximum value of %s.", max_val)
