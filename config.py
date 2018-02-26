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
    AZURE_ACCOUNT_NAME='sgmiddleware'
    AZURE_ACCOUNT_KEy='4RwfWUWnxoVz/GdMkP8mbX9TrAx4eIOWil1ZAgISNDHxCqa643t2yld/QrejL5F1IdOAJBCsg+/ASGr3+X4Qmg=='
    TMP_SCRIPT_DIR="/tmp/"

    
class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    pass
