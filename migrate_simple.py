"""
Simple migration script using Supabase RPC to add user_id column.
This avoids SQLAlchemy connection issues.
"""
from app.db.db import supabase

def migrate():
    print("Starting database migration using Supabase client...")
    
    try:
        # Use Supabase RPC to execute SQL
        # First, check if column exists by trying to select it
        try:
            result = supabase.table("students").select("user_id").limit(1).execute()
            print("✓ user_id column already exists")
        except Exception as e:
            error_msg = str(e)
            if "user_id" in error_msg and "column" in error_msg.lower():
                print("user_id column doesn't exist, adding it...")
                
                # We can't run DDL via PostgREST directly
                # User needs to run this SQL manually or we need a different approach
                print("\n⚠ Cannot add column via Supabase API client.")
                print("\nPlease run this SQL in Supabase Dashboard > SQL Editor:")
                print("-" * 60)
                print("ALTER TABLE students ADD COLUMN user_id UUID;")
                print("-" * 60)
            else:
                raise e
        
        print("\n✅ Migration check completed!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()
