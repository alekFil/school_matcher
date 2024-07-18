from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.find_matches import predict

app = FastAPI()


class SchoolRequest(BaseModel):
    school_name: str


@app.post("/find_matches/", response_model=List[int])
def find_school_matches(request: SchoolRequest) -> List[int]:
    """
    Функция для нахождения соответствие названия школы записи в базе данных.
    Возвращает список id наиболее вероятных совпадений, от большего
    к меньшему

    - **school_name**: str, название школы и регион, разделенные запятой

    Example response: [92, 1842, 152, 218, 51]
    """
    matches = predict(request.school_name)
    if matches:
        return matches
    else:
        raise HTTPException(status_code=404, detail="Matches not found")
