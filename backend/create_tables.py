from database import engine, Base
from models import RecordingSession

Base.metadata.create_all(bind=engine)
