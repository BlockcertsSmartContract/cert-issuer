from typing import List, Optional
from functools import lru_cache
from fastapi import Depends, FastAPI
from cert_tools import instantiate_v3_alpha_certificate_batch, create_v3_alpha_certificate_template
from pydantic import BaseModel
import configargparse
import os

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

class Batch(BaseModel):
    publicKey: str
    recipient_name: Optional[str]
    email: Optional[str]
    SHA256: List[str]

    class Config:
        schema_extra = {
            "example": {
                "publicKey": "0x69575606E8b8F0cAaA5A3BD1fc5D032024Bb85AF",
                "recipient_name": "Albert Einstein",
                "email": "einstein@mpg.de",
                "SHA256": ["0x0e4ded5319861c8daac00d425c53a16bd180a7d01a340a0e00f7dede40d2c9f6", "0xfda3124d5319861c8daac00d425c53a16bd180a7d01a340a0e00f7dede40d2c9f6"],
            }
        }


@app.post("/createUnsignedCertificateBatch")
def createUnsignedCertificate(batch: Batch):
    #create_v3_alpha_certificate_template(recipient_name, email)
    conf = create_v3_alpha_certificate_template.get_config()
    create_v3_alpha_certificate_template.write_certificate_template(conf, batch.recipient_name, batch.email)
    conf_instantiate = instantiate_v3_alpha_certificate_batch.get_config()
    instantiate_v3_alpha_certificate_batch.instantiate_batch(conf_instantiate, batch.publicKey, batch.recipient_name, batch.email, batch.SHA256)

    return {"Unsigned Certificate Created!"}

@app.post("/createCertificateBatch")
def createCertificateBatch(batch: Batch):
    conf = instantiate_v3_alpha_certificate_batch.get_config()
    instantiate_v3_alpha_certificate_batch.instantiate_batch(conf, batch.publicKey, batch.recipient_name, batch.email, batch.SHA256)

    return {"Batch Created!"}
