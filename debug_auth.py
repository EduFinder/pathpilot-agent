from dotenv import load_dotenv
import os
from supabase import create_client, ClientOptions

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key (first 10 chars): {key[:10] if key else 'None'}")

supabase = create_client(
    url,
    key,
    options=ClientOptions(
        postgrest_client_timeout=10,
        schema="public",
    )
)

print("\n--- Testing Insert into 'students' ---")
try:
    data = {
        "name": "Auth Test User",
        # Using a random email to avoid collision if unique constraint exists
        "email": f"test_{os.urandom(4).hex()}@example.com", 
        "resume_url": "http://example.com/cv.pdf"
    }
    response = supabase.table("students").insert(data).execute()
    print("SUCCESS: Inserted into students.")
    print(response.data)
except Exception as e:
    print(f"FAILED: {e}")

except Exception as e:
    print(f"FAILED: {e}")
