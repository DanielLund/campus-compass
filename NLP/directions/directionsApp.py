import pyowm
from a_star import A_Star, Node, Frontier
from config.config_reader import ConfigReader

class directionInformation():
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        """self.owmapikey = self.configuration['A*_SEARCH_API_KEY'] 
        self.owm = pyowm.OWM(self.owmapikey)"""

    def get_direction_info(self,input_string):

        self.input_string = input_string
        campus = A_Star("nodes_glossary.json", self.input_string)
        campus.solve()
        campus.format_output()
        output = " ".join(formatted_output)

        self.bot_says = output
        return self.bot_says
