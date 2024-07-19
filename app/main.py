from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.find_matches import predict

app = FastAPI()


class SchoolRequest(BaseModel):
    school_name: str


class MatchResponse(BaseModel):
    id: Optional[int]
    score: float


@app.post("/find_matches/", response_model=List[MatchResponse])
def find_school_matches(request: SchoolRequest) -> List[MatchResponse]:
    """
    Функция для нахождения соответствие названия школы записи в базе данных.
    Возвращает список id наиболее вероятных совпадений, от большего
    к меньшему

    - **school_name**: str, название школы и регион, разделенные запятой

    Example response:
    [
        {
            "id":1842,
            "score":0.7336769261592321,
        },
        {
            "id":206,
            "score":0.7336769261592321,
        },
        {
            "id":218,
            "score":0.7336769261592321,
        },
        {
            "id":219,
            "score":0.7336769261592321,
        },
        {
            "id":220,
            "score":0.7336769261592321,
        },
    ]
    """
    matches = predict(request.school_name)
    if matches:
        return matches
    else:
        raise HTTPException(status_code=404, detail="Matches not found")
