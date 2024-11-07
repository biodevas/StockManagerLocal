from app import app, db
from models import Beverage
from sqlalchemy import text

def verify_schema():
    with app.app_context():
        # Check if column exists
        sql = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'beverage' AND column_name = 'is_active';
        """)
        result = db.session.execute(sql).fetchone()
        
        if result:
            print("is_active column exists with type:", result[1])
            
            # Check all beverages
            beverages = Beverage.query.all()
            print(f"\nFound {len(beverages)} beverages:")
            for beverage in beverages:
                print(f"- {beverage.name}: is_active = {beverage.is_active}")
        else:
            print("is_active column does not exist!")

if __name__ == "__main__":
    verify_schema()
