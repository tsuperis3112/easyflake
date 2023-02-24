class ExhaustedSequenceError(Exception):
    def __init__(self, bits: int):
        msg = f"The sequence has been exhausted, all {1<<bits} items have been used up."
        super().__init__(msg)
