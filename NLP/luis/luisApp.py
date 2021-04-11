from botbuilder.core import TurnContext,ActivityHandler
from botbuilder.ai.luis import LuisApplication,LuisPredictionOptions,LuisRecognizer
import json
from directions.directionsApp import directionInformation
from config.config_reader import ConfigReader
from logger.logger import Log

#class making instances of keys found in config. files
class LuisConnect(ActivityHandler):
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        self.luis_app_id=self.configuration['LUIS_APP_ID']
        self.luis_endpoint_key = self.configuration['LUIS_ENDPOINT_KEY']
        self.luis_endpoint = self.configuration['LUIS_ENDPOINT']
        self.luis_app = LuisApplication(self.luis_app_id,self.luis_endpoint_key,self.luis_endpoint)
        self.luis_options = LuisPredictionOptions(include_all_intents=True,include_instance_data=True)
        self.luis_recognizer = LuisRecognizer(application=self.luis_app,prediction_options=self.luis_options,include_api_results=True)
        self.log=Log()
 
#overwriting initial object to identify entity, which is then passed to API
    async def on_message_activity(self,turn_context:TurnContext):
        direction_info=directionInformation()
        luis_result = await self.luis_recognizer.recognize(turn_context)
        result = luis_result.properties["luisResult"]
        json_str = json.loads((str(result.entities[0])).replace("'", "\""))
        direction=direction_info.get_direction_info(json_str.get('entity'))
        self.log.write_log(sessionID='session1',log_message="Bot Says: "+str(direction))
        await turn_context.send_activity(f"{direction}")