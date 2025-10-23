from supabase import create_client, Client
from config.settings import get_settings

settings = get_settings()  

class DBConnection:
    def __init__(self):
        self.client: Client = create_client(
            supabase_url=str(settings.api_keys.supabase_url),
            supabase_key=settings.api_keys.supabase_key.get_secret_value()
        )

    def get_client(self) -> Client:
        return self.client


db = DBConnection().get_client()


