class BaseConfig:
    """Base configuration"""
    TESTING = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SSH_USER='testuser'
    SSH_HOSTNAME='localhost'
    SSH_PORT=10022
    SSH_PRIVATE_KEY_PATH='keys/simulator_key'
    SIM_ROOT='/home/testuser'


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    pass
