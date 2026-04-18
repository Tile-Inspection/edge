from sqlalchemy.orm import Session
from .models import Scan, Result


def create_scan(db: Session, name: str) -> Scan:
    """Create a new scan record in the database."""
    scan = Scan(name=name)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def get_scan(db: Session, scan_id: int) -> Scan:
    """Retrieve a scan by ID."""
    return db.query(Scan).filter(Scan.id == scan_id).first()


def get_all_scans(db: Session) -> list[Scan]:
    """Retrieve all scans from the database."""
    return db.query(Scan).all()


def get_scan_results(db: Session, scan_id: int) -> list[Result]:
    """Retrieve all results for a specific scan."""
    return db.query(Result).filter(Result.scan_id == scan_id).all()


def get_result(db: Session, result_id: int) -> Result:
    """Retrieve a single result by ID."""
    return db.query(Result).filter(Result.id == result_id).first()


def update_scan(db: Session, scan_id: int, name: str) -> Scan:
    """Update a scan's name."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.name = name
        db.commit()
        db.refresh(scan)
    return scan


def delete_scan(db: Session, scan_id: int) -> bool:
    """Delete a scan by ID."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        db.delete(scan)
        db.commit()
        return True
    return False
