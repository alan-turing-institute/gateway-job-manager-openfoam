"""
Test the simulator connection.
"""

from config import DevelopmentConfig

from connection.simulator import SSH_Credentials,SimulatorConnection

from .fixtures import demo_app 

def test_simulator_connection():
    app = demo_app()
    devconfig = DevelopmentConfig()
    app.config.from_object(devconfig)
    credentials = SSH_Credentials(app.config)
    connection = SimulatorConnection(credentials)
    # out, err, exit_code = connection._run_remote_command('echo hello')
    # print(out, err, exit_code)
    # print(connection.hostname)
