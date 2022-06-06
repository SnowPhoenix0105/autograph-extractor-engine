import http
import io
import logging
from typing import Dict, Tuple, cast, Callable, List
import flask
import json

logger = logging.getLogger(__name__)

def build(app: flask.Flask):

    @app.route("/coffee")
    def coffee() -> Tuple[str, int]:
        return "I'm a teapot!", http.HTTPStatus.IM_A_TEAPOT



