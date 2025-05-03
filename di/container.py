from typing import Dict, Any, Type, TypeVar, cast

T = TypeVar('T')


class Container:
    def __init__(self):
        self._services: Dict[str, Any] = {}

    def register(self, service_type: Type[T], instance: T) -> None:
        """Register a service instance"""
        self._services[service_type.__name__] = instance

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service by type"""
        service_name = service_type.__name__
        if service_name in self._services:
            return cast(T, self._services[service_name])
        raise KeyError(f"Service {service_name} not registered")
