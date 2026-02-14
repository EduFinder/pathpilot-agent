from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# quick test
def test_connection():
    return supabase.table("students").select("*").execute()
print(test_connection())
