from app.db.database import SessionLocal, engine, Base
from app.db.models import Scan, Result

def populate_database():
    # 1. Ensure tables are created in the database
    Base.metadata.create_all(bind=engine)
    
    # 2. Open a session
    db = SessionLocal()
    
    try:
        # 3. Create a single Scan
        new_scan = Scan(name="Test 3x3 Grid Scan")
        db.add(new_scan)
        db.commit()
        db.refresh(new_scan) # Refresh to get the auto-generated ID
        
        # 4. Generate 9 Results for a 3x3 grid
        results = []
        for x in range(3):
            for y in range(3):
                result = Result(
                    scan_id=new_scan.id,
                    x=x,
                    y=y,
                    status="scanned",
                    # Adding some dummy classification data for variety
                    hollow_classification={"type": "hollow", "confidence": 0.85},
                    cracked_classification={"type": "cracked", "confidence": 0.92} if x != y else None,
                    image_file_path=f"/path/to/images/tile_{x}_{y}.jpg",
                    audio_file_path=f"/path/to/audio/tile_{x}_{y}.mp3"
                )
                results.append(result)
        
        # 5. Add and commit all results
        db.add_all(results)
        db.commit()
        print(f"Successfully added Scan ID {new_scan.id} with {len(results)} grid results to the database!")
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()
