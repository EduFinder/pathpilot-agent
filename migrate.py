"""
Database migration script to create/update tables based on ORM models.
Run this script to sync your database schema with your Python models.
"""
from sqlalchemy import create_engine, inspect, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def migrate():
    print("Starting database migration...")
    
    try:
        inspector = inspect(engine)
        
        # Check if students table exists
        if 'students' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('students')]
            
            if 'user_id' not in columns:
                print("Adding user_id column to students table...")
                with engine.connect() as conn:
                    conn.execute(text("""
                        ALTER TABLE students 
                        ADD COLUMN user_id UUID;
                    """))
                    conn.commit()
                print("✓ user_id column added successfully")
            else:
                print("✓ user_id column already exists")
        else:
            print("⚠ students table doesn't exist yet - it will be created by Supabase")
        
        print("\n✅ Migration completed successfully!")
        print("\nNote: The students table should have these columns:")
        print("  - id (UUID, primary key)")
        print("  - name (text)")
        print("  - email (text)")
        print("  - resume_url (text)")
        print("  - user_id (UUID) ← links to auth.users")
        print("  - created_at (timestamp)")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()
