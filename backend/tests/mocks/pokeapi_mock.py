# tests/mocks/pokeapi_mock.py
from typing import List, Optional
import httpx

class FakePokeAPIClient:
    """
    Test client that mirrors the PokeAPIClient interface
    without making real HTTP requests.
    """

    def __init__(self, pokemon_db: Optional[dict[int, str]] = None):
        # Default ID-to-name mapping.
        self._db = pokemon_db or {
            1: "bulbasaur",
            4: "charmander",
            7: "squirtle",
            25: "pikachu",
        }

    async def get_pokemon_name_by_id(
        self, client: httpx.AsyncClient, pokemon_id: int
    ) -> Optional[str]:
        if pokemon_id <= 0:
            return None
        return self._db.get(pokemon_id)

    async def get_pokemon_names_by_ids(
        self, pokemon_ids: List[int]
    ) -> List[Optional[str]]:
        if not pokemon_ids:
            return []
        
        results = [self._db.get(pid) for pid in pokemon_ids]
        return [r for r in results if r is not None]