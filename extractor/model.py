from typing import List, Optional
import pydantic

class EntitySchema(pydantic.BaseModel):
    name: str
    begin: int
    end: int

class SPOSchema(pydantic.BaseModel):
    relation: str
    head_entity: EntitySchema
    tail_entity: EntitySchema

    def with_extractor_id(self, extractor_id: int):
        return SPOWithExtractorSchema(
            extractor_id=extractor_id,
            relation=self.relation,
            head_entity=self.head_entity,
            tail_entity=self.tail_entity
        )

class SPOWithExtractorSchema(pydantic.BaseModel):
    extractor_id: int
    relation: str
    head_entity: EntitySchema
    tail_entity: EntitySchema

class MQRequestSchema(pydantic.BaseModel):
    text: str
    text_id: int
    task_id: Optional[int]
    offset: int

class MQRespSchema(pydantic.BaseModel):
    text: str
    text_id: int
    task_id: Optional[int]
    offset: int
    spo_list: List[SPOWithExtractorSchema]

class CallExtractorReqSchema(pydantic.BaseModel):
    text: str

class CallExtractorRespSchema(pydantic.BaseModel):
    spo_list: List[SPOSchema]
