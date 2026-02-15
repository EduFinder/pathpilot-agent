from supabase import create_client, ClientOptions
import os
from dotenv import load_dotenv

load_dotenv()

# We need to explicitly set the Authorization header to ensure the Service Key works correctly
# and isn't overridden by some default 'anon' behavior of the client.
key = os.getenv("SUPABASE_KEY")
url = os.getenv("SUPABASE_URL")

class SupabaseServiceRoleClient:
    def __init__(self):
        self.client = create_client(
            url,
            key,
            options=ClientOptions(
                postgrest_client_timeout=10,
                schema="public",
                auto_refresh_token=False,
                persist_session=False
            )
        )

    def table(self, text):
        return self.client.table(text)

    @property
    def storage(self):
        # Storage often needs the service role key explicitly if RLS is strict
        # But standard client init should handle it if key is correct.
        return self.client.storage

    @property
    def auth(self):
        return self.client.auth

supabase = SupabaseServiceRoleClient()

# quick test
def test_connection():
    try:
        response = supabase.table("students").select("*").execute()
        return response
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(test_connection())
