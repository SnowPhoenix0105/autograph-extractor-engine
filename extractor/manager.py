
import logging
import traceback
from typing import cast, Dict, List, Tuple, Callable

import requests
from extractor.mq import QueueManager
from extractor.model import CallExtractorReqSchema, CallExtractorRespSchema, MQRequestSchema, MQRespSchema, SPOSchema, SPOWithExtractorSchema
import json

DEFAULT_REQ_QUEUE = "extractor_input"
DEFAULT_RESP_QUEUE = "extractor_output"

class ExtractorManager:
    def __init__(self, 
        req_queue: str=DEFAULT_REQ_QUEUE, 
        resp_queue: str=DEFAULT_RESP_QUEUE,
        ) -> None:
        self.req_queue = req_queue
        self.resp_queue = resp_queue
        self.mq_manager = QueueManager()
        self.logger = logging.getLogger(__name__)

    def send_resp(self, resp: MQRespSchema):
        self.mq_manager.send_object_by_json(self.resp_queue, resp.dict())

    def start_extractor_mq_service(self):
        """
        异步监听MQ
        """
        self.mq_manager.listen_on(self.req_queue, self.on_message)

    def on_message(self, msg: str):
        try:
            req = MQRequestSchema(**json.loads(msg))

            spo_res = self.call_extractors(req.text)

            resp = MQRespSchema(
                text=req.text,
                text_id=req.text_id,
                task_id=req.task_id,
                offset=req.offset,
                spo_list=spo_res,
            )

            self.send_resp(resp=resp)
        
        except Exception:
            logging.error(f"receive data error: {traceback.format_exc()}")

    def get_extractors_url_map(self) -> Dict[int, str]: # extractor_id -> url
        return {
            1: "localhost:8021/extract"
        }

    def call_extractor(self, url: str, text: str) -> List[SPOSchema]:
        req = CallExtractorReqSchema(text=text)

        if "http" not in url:
            url = "http://" + url

        resp_raw = requests.post(url=url, data=req.json(), headers={
            "Content-Type": "application/json"
        })

        resp = CallExtractorRespSchema(**resp_raw.json())

        return resp.spo_list

    def call_extractors(self, text: str) -> List[SPOWithExtractorSchema]:
        extractors = self.get_extractors_url_map()

        ret = cast(List[SPOWithExtractorSchema], [])

        for extractor_id, url in extractors.items():
            spo_list = self.call_extractor(url=url, text=text)

            for spo in spo_list:
                ret.append(spo.with_extractor_id(extractor_id=extractor_id))

        return ret

