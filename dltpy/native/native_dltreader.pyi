import typing

class DltReader:

    def __init__(self, expect_storage: bool, filters: typing.List[typing.Tuple[str, str]]):
        pass

    def read(self) -> bool:
        pass
    def get_buffer(self) -> memoryview:
        pass

    def get_payload(self) -> memoryview:
        pass

    def get_message(self) -> memoryview:
        pass

    def consume_message(self):
        pass

    def update_buffer(self, bytes_read: int):
        pass

    def get_basic(self) -> dict:
        pass

    def get_extended(self) -> dict:
        pass

    def get_storage(self) -> dict:
        pass