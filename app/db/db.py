import os
from dotenv import load_dotenv

# Load .env FIRST before anything else
load_dotenv()

from supabase import create_client, ClientOptions

def _get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError(
            f"Missing Supabase credentials. SUPABASE_URL={'SET' if url else 'MISSING'}, "
            f"SUPABASE_KEY={'SET' if key else 'MISSING'}"
        )

    return create_client(
        url,
        key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            schema="public",
            auto_refresh_token=False,
            persist_session=False,
        )
    )

supabase = _get_supabase_client()

# quick test
def test_connection():
    try:
        response = supabase.table("students").select("*").execute()
        return response
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(test_connection())
