import secrets

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://ghostchinchilla:new_password1@localhost:5432/plantparty_db"

    
    # Other configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = secrets.token_hex(24)
    API_KEY = 'sk-trIY663657b86145f5348'


