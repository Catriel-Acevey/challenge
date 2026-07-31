from typing import Optional

class UserRepository:
    def __init__(self):
        self._db = []
        self._auto_increment_id = 1

    def get_all(self) -> list[dict]:
        """ get all users from the database """
        return self._db
    
    def get_by_id(self, id: int) -> Optional[dict]:
        """ find a user by their id """
        for user in self._db:
            if user["id"] == id:
                return user
        return None

    def get_by_email(self, email: str) -> Optional[dict]:
        """Find a user by their email address."""
        for user in self._db:
            if user["email"] == email:
                return user
        return None

    def create(self, user_data: dict) -> dict:
        """Create and save a new user in the database."""
        new_user = {
            "id": self._auto_increment_id,
            "email": user_data["email"],
            "username": user_data["username"],
            "password": user_data["password"],
            "is_active": True
        }
        self._db.append(new_user)
        self._auto_increment_id += 1
        return new_user

    def update(self, id: str, user_data: dict) -> Optional[dict]:
        """ update a user in the database """
        if self.get_by_id(id) is None:
            return None
        self._db[id] = user_data
    
    def delete(self, id: str) -> bool:
        """ delete a user from the database """
        user = self.get_by_id(id)
        if user is None:
            return False
        self._db.remove(user)
        return True
