from app import app, db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        sql = text("ALTER TABLE beverage ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL;")
        try:
            db.session.execute(sql)
            db.session.commit()
            print("Successfully added is_active column to beverage table")
        except Exception as e:
            print(f"Error adding column: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    update_schema()
