from abc import ABC, abstractmethod


class Piece(ABC):

    type: str
    color: str
    value: int
    position: tuple

    @abstractmethod
    def move(self):
        pass


class Pawn(Piece):
    def move(self):
        pass


pawn1 = Pawn()


pawn1.move()
# print(pawn1.type)
