import httpx
import asyncio
from typing import List, Optional
from app.core.config import settings

class PokeAPIClient:
    def __init__(self):
        self.base_url = settings.POKEAPI_BASE_URL
    async def get_pokemon_name_by_id(self, client: httpx.AsyncClient, pokemon_id: int) -> Optional[str]:
        """Fetch a single Pokemon by its ID and return its name."""
        if not (pokemon_id > 0): return None
        try:
            response = await client.get(f"{self.base_url}/{pokemon_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get("name")
            else:
                return None
        except httpx.RequestError as error:
            print(f"An error occurred while requesting {error.request.url!r}")
            return None
    
    async def get_pokemon_names_by_ids(self, pokemon_ids: List[int]) -> List[Optional[str]]:
        """Given a list of IDs, execute parallel HTTP requests and return their names."""
        if not pokemon_ids: return []
        
        async with httpx.AsyncClient() as client:
            tasks = [
                self.get_pokemon_name_by_id(client, pokemon_id)
                for pokemon_id in pokemon_ids
            ]
            results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]
    
poke_api_client = PokeAPIClient()