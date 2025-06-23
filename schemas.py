from pydantic import BaseModel

class IssueCreate(BaseModel):
    project: str
    summary: str
    description: str
    issuetype: str

class IssueUpdate(BaseModel):
    summary: str = None
    description: str = None

class Comment(BaseModel):
    comment: str

class Assign(BaseModel):
    username: str

class Transition(BaseModel):
    transition_id: str

class JQLQuery(BaseModel):
    jql: str
