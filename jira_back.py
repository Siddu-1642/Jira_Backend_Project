from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
from jira import JIRA
from schemas import (
    IssueCreate, IssueUpdate, Comment,
    Assign, Transition, JQLQuery
)

load_dotenv()

app = FastAPI()

# Load Jira credentials from .env
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Jira client
jira = JIRA(
    server=JIRA_URL,
    basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
)

@app.get("/")
def root():
    return {"message": " Jira API is LIVE!"}

@app.post("/create-issue/")
def create_issue(data: IssueCreate):
    try:
        issue_dict = {
            "project": {"key": data.project},
            "summary": data.summary,
            "description": data.description,
            "issuetype": {"name": data.issuetype},
        }
        issue = jira.create_issue(fields=issue_dict)
        return {
            "message": "Issue created successfully",
            "key": issue.key,
            "url": f"{JIRA_URL}/browse/{issue.key}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/issue/{issue_key}")
def get_issue(issue_key: str):
    try:
        issue = jira.issue(issue_key)
        return {
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description,
            "status": issue.fields.status.name
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/issue/{issue_key}")
def update_issue(issue_key: str, data: IssueUpdate):
    try:
        fields = {}
        if data.summary:
            fields["summary"] = data.summary
        if data.description:
            fields["description"] = data.description
        jira.issue(issue_key).update(fields=fields)
        return {"message": f"Issue {issue_key} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/issue/{issue_key}")
def delete_issue(issue_key: str):
    try:
        jira.issue(issue_key).delete()
        return {"message": f"Issue {issue_key} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/issue/{issue_key}/comment")
def add_comment(issue_key: str, comment: Comment):
    try:
        jira.add_comment(issue_key, comment.comment)
        return {"message": "Comment added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/issue/{issue_key}/comments")
def get_comments(issue_key: str):
    try:
        comments = jira.comments(issue_key)
        return [{"author": c.author.displayName, "body": c.body} for c in comments]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/issue/{issue_key}/assign")
def assign_issue(issue_key: str, data: Assign):
    try:
        jira.assign_issue(issue_key, data.username)
        return {"message": f"Issue {issue_key} assigned to {data.username}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/issue/{issue_key}/transition")
def transition_issue(issue_key: str, data: Transition):
    try:
        jira.transition_issue(issue_key, data.transition_id)
        return {"message": f"Issue {issue_key} transitioned using ID {data.transition_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/")
def search_issues(data: JQLQuery):
    try:
        issues = jira.search_issues(data.jql)
        return [{"key": i.key, "summary": i.fields.summary} for i in issues]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
