import flask
import logging
import application.route as route
import config
from extractor.manager import ExtractorManager
from utils.log import config_logging, print_const_configs


if __name__ == '__main__':
    config_logging("test.log", logging.INFO, logging.DEBUG)
    print_const_configs()

    extractor_manager = ExtractorManager()

    extractor_manager.start_extractor_mq_service()

    app = flask.Flask(__name__)

    route.build(app)

    app.run(host="0.0.0.0", port=8002, debug=True)



