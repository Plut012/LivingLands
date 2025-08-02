"""
database.py - Database Management for Mythic Bastionlands

PLAN:
1. Setup SQLAlchemy engine
2. Define database models
3. Session management
4. Basic CRUD operations
5. Migration utilities

FRAMEWORK:
- Use SQLite for simplicity (easily switch to PostgreSQL)
- Keep models aligned with game objects
- Handle sessions properly
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, List
import json
from datetime import datetime

# STEP 1: Database configuration
DATABASE_URL = "sqlite:///./mythic_bastionlands.db"  # Use SQLite for development
# For production: "postgresql://user:password@localhost/mythic_bastionlands"

# STEP 2: Create engine and base
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Only for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# STEP 3: Define database models
class DBGameSession(Base):
    """Game session in database"""
    __tablename__ = "game_sessions"
    
    id = Column(String, primary_key=True)
    company_name = Column(String, nullable=False)
    current_hex_x = Column(Integer, default=0)
    current_hex_y = Column(Integer, default=0)
    turn_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # JSON fields for complex data
    world_state = Column(JSON)  # Serialized world hexes
    combat_state = Column(JSON)  # Active combat if any
    
    # Relationships
    characters = relationship("DBCharacter", back_populates="session")

class DBCharacter(Base):
    """Character in database"""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("game_sessions.id"))
    name = Column(String, nullable=False)
    is_knight = Column(Boolean, default=True)
    
    # Virtues
    vigor = Column(Integer, default=10)
    clarity = Column(Integer, default=10)
    spirit = Column(Integer, default=10)
    
    # Guard
    current_guard = Column(Integer, default=6)
    max_guard = Column(Integer, default=6)
    
    # JSON fields
    equipment = Column(JSON, default=list)
    wounds = Column(JSON, default=list)
    
    # Relationship
    session = relationship("DBGameSession", back_populates="characters")

class DBAction(Base):
    """Action history"""
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("game_sessions.id"))
    turn_number = Column(Integer)
    timestamp = Column(DateTime, server_default=func.now())
    
    # Action details
    intent = Column(String)
    leverage = Column(String)
    cost = Column(String, nullable=True)
    risk = Column(String)
    
    # Outcome
    success = Column(Boolean)
    outcome = Column(String)
    narrative = Column(String)

# STEP 4: Database initialization
def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# STEP 5: Session CRUD operations
def create_game_session(db: Session, session_id: str, company_name: str) -> DBGameSession:
    """Create a new game session"""
    db_session = DBGameSession(
        id=session_id,
        company_name=company_name,
        world_state={},
        combat_state=None
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_game_session(db: Session, session_id: str) -> Optional[DBGameSession]:
    """Retrieve a game session"""
    return db.query(DBGameSession).filter(DBGameSession.id == session_id).first()

def update_game_session(db: Session, session_id: str, updates: Dict):
    """Update game session"""
    db_session = get_game_session(db, session_id)
    if db_session:
        for key, value in updates.items():
            if hasattr(db_session, key):
                setattr(db_session, key, value)
        db.commit()
    return db_session

# STEP 6: Character CRUD operations
def create_character(db: Session, session_id: str, character_data: Dict) -> DBCharacter:
    """Create a new character"""
    db_char = DBCharacter(
        session_id=session_id,
        name=character_data["name"],
        is_knight=character_data.get("is_knight", True),
        vigor=character_data.get("vigor", 10),
        clarity=character_data.get("clarity", 10),
        spirit=character_data.get("spirit", 10),
        current_guard=character_data.get("guard", 6),
        max_guard=character_data.get("max_guard", 6),
        equipment=character_data.get("equipment", []),
        wounds=character_data.get("wounds", [])
    )
    db.add(db_char)
    db.commit()
    db.refresh(db_char)
    return db_char

def get_characters(db: Session, session_id: str) -> List[DBCharacter]:
    """Get all characters for a session"""
    return db.query(DBCharacter).filter(DBCharacter.session_id == session_id).all()

def update_character(db: Session, character_id: int, updates: Dict):
    """Update a character"""
    db_char = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
    if db_char:
        for key, value in updates.items():
            if hasattr(db_char, key):
                setattr(db_char, key, value)
        db.commit()
    return db_char

# STEP 7: Action logging
def log_action(db: Session, session_id: str, action_data: Dict):
    """Log an action for history"""
    db_action = DBAction(
        session_id=session_id,
        turn_number=action_data.get("turn", 0),
        intent=action_data["intent"],
        leverage=action_data.get("leverage", ""),
        cost=action_data.get("cost"),
        risk=action_data.get("risk", "no_risk"),
        success=action_data.get("success", True),
        outcome=action_data.get("outcome", ""),
        narrative=action_data.get("narrative", "")
    )
    db.add(db_action)
    db.commit()
    return db_action

def get_action_history(db: Session, session_id: str, limit: int = 10) -> List[DBAction]:
    """Get recent actions for a session"""
    return db.query(DBAction)\
        .filter(DBAction.session_id == session_id)\
        .order_by(DBAction.timestamp.desc())\
        .limit(limit)\
        .all()

# STEP 8: World state management
def save_world_state(db: Session, session_id: str, world_hexes: Dict):
    """Save the world state as JSON"""
    # Convert world hex objects to serializable format
    serializable_world = {}
    for coords, hex_data in world_hexes.items():
        # Convert tuple key to string
        key = f"{coords[0]},{coords[1]}"
        serializable_world[key] = {
            "landmark": hex_data.landmark,
            "myth_id": hex_data.myth_id,
            "current_omen": hex_data.current_omen,
            "explored": hex_data.explored
        }
    
    update_game_session(db, session_id, {"world_state": serializable_world})

def load_world_state(db: Session, session_id: str) -> Dict:
    """Load world state from JSON"""
    db_session = get_game_session(db, session_id)
    if not db_session or not db_session.world_state:
        return {}
    
    # Convert back to proper format
    world_hexes = {}
    for key, hex_data in db_session.world_state.items():
        # Convert string key back to tuple
        x, y = map(int, key.split(','))
        world_hexes[(x, y)] = hex_data
    
    return world_hexes

# STEP 9: Cleanup old sessions
def cleanup_old_sessions(db: Session, days_old: int = 30):
    """Remove sessions older than specified days"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    old_sessions = db.query(DBGameSession)\
        .filter(DBGameSession.updated_at < cutoff_date)\
        .all()
    
    for session in old_sessions:
        # Delete related data first
        db.query(DBCharacter).filter(DBCharacter.session_id == session.id).delete()
        db.query(DBAction).filter(DBAction.session_id == session.id).delete()
        db.delete(session)
    
    db.commit()
    return len(old_sessions)

# STEP 10: Database utilities
def export_session(db: Session, session_id: str) -> Dict:
    """Export a complete session as JSON"""
    session = get_game_session(db, session_id)
    if not session:
        return None
    
    characters = get_characters(db, session_id)
    actions = get_action_history(db, session_id, limit=1000)
    
    return {
        "session": {
            "id": session.id,
            "company_name": session.company_name,
            "current_hex": [session.current_hex_x, session.current_hex_y],
            "turn_count": session.turn_count,
            "world_state": session.world_state
        },
        "characters": [
            {
                "name": c.name,
                "vigor": c.vigor,
                "clarity": c.clarity,
                "spirit": c.spirit,
                "guard": c.current_guard,
                "equipment": c.equipment,
                "wounds": c.wounds
            }
            for c in characters
        ],
        "history": [
            {
                "turn": a.turn_number,
                "intent": a.intent,
                "outcome": a.outcome,
                "narrative": a.narrative
            }
            for a in actions
        ]
    }
