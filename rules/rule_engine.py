"""Abstract base class untuk aturan klasifikasi file."""

from abc import ABC, abstractmethod


class RuleEngine(ABC):
    @abstractmethod
    def determine_category(self, file):
        raise NotImplementedError

    @abstractmethod
    def generate_new_name(self, file, category: str) -> str:
        raise NotImplementedError
