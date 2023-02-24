from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SequenceReply(_message.Message):
    __slots__ = ["sequence"]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    sequence: int
    def __init__(self, sequence: _Optional[int] = ...) -> None: ...

class SequenceRequest(_message.Message):
    __slots__ = ["bits"]
    BITS_FIELD_NUMBER: _ClassVar[int]
    bits: int
    def __init__(self, bits: _Optional[int] = ...) -> None: ...
