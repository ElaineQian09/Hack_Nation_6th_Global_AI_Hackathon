from pydantic import BaseModel


class FilterOptions(BaseModel):
    capabilities: list[str]
    states: list[str]
    cities: list[str]
    trustLevels: list[str]
