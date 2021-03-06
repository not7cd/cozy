from abc import ABC, abstractmethod


class Chapter(ABC):
    id: int

    @property
    @abstractmethod
    def name(self):
        pass

    @name.setter
    @abstractmethod
    def name(self, new_name: str):
        pass

    @property
    @abstractmethod
    def number(self):
        pass

    @number.setter
    @abstractmethod
    def number(self, new_number: int):
        pass

    @property
    @abstractmethod
    def disk(self):
        pass

    @disk.setter
    @abstractmethod
    def disk(self, new_disk: int):
        pass

    @property
    @abstractmethod
    def position(self):
        pass

    @position.setter
    @abstractmethod
    def position(self, new_position: int):
        pass

    @property
    @abstractmethod
    def file(self):
        pass

    @file.setter
    @abstractmethod
    def file(self, new_file: str):
        pass

    @property
    @abstractmethod
    def length(self):
        pass

    @length.setter
    @abstractmethod
    def length(self, new_length: float):
        pass

    @property
    @abstractmethod
    def modified(self):
        pass

    @modified.setter
    @abstractmethod
    def modified(self, new_modified: int):
        pass
