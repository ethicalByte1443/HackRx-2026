from pydantic import BaseModel

class UserQuery(BaseModel):
    user_query: str
    matched_clause: str
