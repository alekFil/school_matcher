from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.find_matches import predict

app = FastAPI()


class SchoolRequest(BaseModel):
    school_name: str
    region: str


class MatchResponse(BaseModel):
    id: Optional[int]
    score: float
    name: str


@app.post("/find_matches/", response_model=List[MatchResponse])
def find_school_matches(request: SchoolRequest):
    """
    Find school matches based on the given school name and region.

    - **school_name**: Name of the school
    - **region**: Region of the school

    Example response:
    [
        {"id": 92, "score": 0.7885993344073151, "name": "ляпкина"},
        {"id": 1842, "score": 0.4511433586943585, "name": ""спортивный школа олимпийский резерв один""},
        {"id": null, "score": 0.4511433586943585, "name": ""спортивный школа олимпийский резерв один""},
        {"id": 218, "score": 0.4511433586943585, "name": ""спортивный школа олимпийский резерв один""},
        {"id": null, "score": 0.4511433586943585, "name": ""спортивный школа олимпийский резерв один""}
    ]
    """
    matches = predict(request.school_name, request.region)
    if matches:
        return matches
    else:
        raise HTTPException(status_code=404, detail="Matches not found")
