"""
Check database tables and schema
"""
from app.db.db import supabase

try:
    # Try to query students table
    print("Checking students table...")
    result = supabase.table("students").select("*").limit(1).execute()
    print(f"✅ Students table exists")
    print(f"Columns: {list(result.data[0].keys()) if result.data else 'No data yet'}")
    
    # Check if user_id column exists
    try:
        result = supabase.table("students").select("user_id").limit(1).execute()
        print("✅ user_id column exists")
    except Exception as e:
        if "user_id" in str(e):
            print("❌ user_id column does NOT exist")
        else:
            print(f"⚠ Error checking user_id: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nThe students table might not exist yet.")
    print("You need to create it in Supabase Dashboard > Table Editor")
