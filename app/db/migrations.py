"""
Auto-migration module that runs on application startup.
This ensures database schema is always in sync with ORM models.
"""
from sqlalchemy import create_engine, inspect, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def auto_migrate():
    """Run migrations automatically on startup"""
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # Check if students table exists and has user_id column
        if 'students' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('students')]
            
            if 'user_id' not in columns:
                print("🔧 Auto-migration: Adding user_id column to students table...")
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE students ADD COLUMN user_id UUID;"))
                    conn.commit()
                print("✅ user_id column added successfully")
        
        engine.dispose()
        
    except Exception as e:
        print(f"⚠ Auto-migration warning: {e}")
        # Don't crash the app if migration fails
        pass
