import threading
from ultralytics.solutions import ParkingPtsSelection
from .models import ParkingAnnotation
from .extensions import db
import os
import json


ANNOTATIONS_DIR = "./annotations"

def start_parking_annotation_process(parking):
    thread = threading.Thread(
        target=ParkingPtsSelection(parking),
        args=(parking,),
        daemon=True
    )
    thread.start()
    
    
def save_annotation_to_db(parking_id, file_path, annotation_json):
    annotation = ParkingAnnotation(
        parking_spot_id=parking_id,
        file_path=file_path,
        annotation_data=annotation_json
    )

    db.session.add(annotation)
    db.session.commit()

