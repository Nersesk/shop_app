from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    async def get(self, _id):...

    @abstractmethod
    async def create(self, payload):...

    @abstractmethod
    async def update(self, _id, payload):...

    @abstractmethod
    async def delete(self, _id):...

    @abstractmethod
    async def list(self):...