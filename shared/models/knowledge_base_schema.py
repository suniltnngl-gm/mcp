#!/usr/bin/env python3
"""
Knowledge Base Schema

This module defines the Pydantic models for the repository knowledge base.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import datetime

class EventType(str, Enum):
    """The type of an event."""
    CODE_REVIEW = "code_review"
    TEST_RUN = "test_run"
    REFACTORING = "refactoring"
    KNOWLEDGE_BASE_UPDATE = "knowledge_base_update"

class GlobalInfo(BaseModel):
    type: str = Field(..., description="The type of the document.")
    git_cli_version: str = Field(..., description="The version of the Git CLI.")

class RepositoryInfo(BaseModel):
    type: str = Field(..., description="The type of the document.")
    path: str = Field(..., description="The absolute path to the repository.")
    relative_path: str = Field(..., description="The relative path to the repository from the workspace root.")
    name: str = Field(..., description="The name of the repository.")
    current_branch: Optional[str] = Field(None, description="The current Git branch.")
    current_branch_error: Optional[str] = Field(None, description="Error message if the current branch could not be retrieved.")
    local_branches: List[str] = Field([], description="List of local Git branches.")
    local_branches_error: Optional[str] = Field(None, description="Error message if local branches could not be retrieved.")
    remote_branches: List[str] = Field([], description="List of remote Git branches.")
    remote_branches_error: Optional[str] = Field(None, description="Error message if remote branches could not be retrieved.")
    remote_urls: List[str] = Field([], description="List of remote URLs.")
    remote_urls_error: Optional[str] = Field(None, description="Error message if remote URLs could not be retrieved.")
    last_5_commits: List[str] = Field([], description="List of the last 5 commits.")
    last_commits_error: Optional[str] = Field(None, description="Error message if the last commits could not be retrieved.")
    is_clean: bool = Field(False, description="Whether the Git repository is clean.")
    status_details: List[str] = Field([], description="The details of the Git status.")
    status_error: Optional[str] = Field(None, description="Error message if the status could not be retrieved.")
    ahead_by: int = Field(0, description="The number of commits the local branch is ahead of the remote.")
    behind_by: int = Field(0, description="The number of commits the local branch is behind the remote.")
    remote_tracking_error: Optional[str] = Field(None, description="Error message if remote tracking information could not be retrieved.")
    last_commit_date: Optional[str] = Field(None, description="The date of the last commit.")
    last_commit_author_email: Optional[str] = Field(None, description="The email of the author of the last commit.")
    last_commit_subject: Optional[str] = Field(None, description="The subject of the last commit.")
    last_commit_details_error: Optional[str] = Field(None, description="Error message if the last commit details could not be retrieved.")
    total_commits: int = Field(0, description="The total number of commits.")
    total_commits_error: Optional[str] = Field(None, description="Error message if the total number of commits could not be retrieved.")
    configured_user_name: Optional[str] = Field(None, description="The configured Git user name.")
    configured_user_email: Optional[str] = Field(None, description="The configured Git user email.")
    submodules: List[str] = Field([], description="List of Git submodules.")
    tags: List[str] = Field([], description="List of Git tags.")
    stash_list: List[str] = Field([], description="List of Git stashes.")
    ignored_files: List[str] = Field([], description="List of ignored files.")
    ls_files_error: Optional[str] = Field(None, description="Error message if ls-files failed.")
    total_files: int = Field(0, description="The total number of files in the repository.")
    total_size_bytes: int = Field(0, description="The total size of the repository in bytes.")
    languages_detected: Dict[str, int] = Field({}, description="A dictionary of detected languages and their file counts.")
    frameworks_detected: List[str] = Field([], description="A list of detected frameworks.")
    dependency_files: List[str] = Field([], description="A list of dependency files.")
    documentation_files: List[str] = Field([], description="A list of documentation files.")
    license_file: Optional[str] = Field(None, description="The path to the license file.")
    config_files: List[str] = Field([], description="A list of configuration files.")
    last_modified_timestamp: Optional[str] = Field(None, description="The timestamp of the last modification.")
    build_test_commands: List[str] = Field([], description="A list of detected build and test commands.")
    error: Optional[str] = Field(None, description="An error message if an error occurred while processing the repository.")

class DuplicateInfo(BaseModel):
    type: str = Field(..., description="The type of the document.")
    duplicate_files_by_hash: Dict[str, List[str]] = Field(..., description="A dictionary of duplicate files, keyed by their hash.")

class Event(BaseModel):
    type: EventType = Field(..., description="The type of the event.")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat(), description="The timestamp of the event.")
    data: Dict[str, Any] = Field(..., description="The data associated with the event.")
