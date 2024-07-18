from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.find_matches import find_matches

app = FastAPI()


class SchoolRequest(BaseModel):
    school_name: str
    region: str


@app.post("/find_matches/")
def find_school_matches(request: SchoolRequest):
    matches = find_matches(request.school_name, request.region)
    if matches:
        return matches
    else:
        raise HTTPException(status_code=404, detail="Matches not found")
