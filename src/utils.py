"""Utils for blinky eyeblink detector."""
from configparser import ConfigParser

class Parameters:
    """Class for handling camera parameters loading and saving to file."""
    def __init__(self, filename=None, params=dict()):
        self.filename = filename
        self.params = params

    def load_parameters(self):
        config = ConfigParser()
        config.read(str(self.filename))
        for key, val in config.items(section='Parameters'):
            self.params[key] = int(val)

    def save_parameters(self):
        print(self.filename)
        config = ConfigParser()
        config['Parameters'] = self.params
        with open(self.filename, 'w') as configfile:
            config.write(configfile)
