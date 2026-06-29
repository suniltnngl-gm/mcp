"""
🗄️ Database Models - Analysis History & Memory Persistence
=========================================================

SQLAlchemy models for storing analysis results, agent memory, and workflow history.
"""

import os
import uuid
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ai_orchestra.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnalysisSession(Base):
    """Stores complete analysis session results."""

    __tablename__ = "analysis_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario = Column(Text, nullable=False)
    iterations = Column(Integer, default=2)
    total_agents = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, running, completed, failed

    # Results
    final_recommendations = Column(JSON)
    analysis_metadata = Column(JSON)
    devops_automation = Column(JSON, nullable=True)
    github_templates = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    agent_analyses = relationship("AgentAnalysis", back_populates="session")
    agent_suggestions = relationship("AgentSuggestion", back_populates="session")


class AgentAnalysis(Base):
    """Stores individual agent analysis results."""

    __tablename__ = "agent_analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("analysis_sessions.id"))

    # Agent info
    agent_name = Column(String, nullable=False)
    agent_role = Column(String, nullable=False)
    iteration = Column(Integer, nullable=False)

    # Analysis results
    summary = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    analysis_metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("AnalysisSession", back_populates="agent_analyses")


class AgentSuggestion(Base):
    """Stores agent suggestions."""

    __tablename__ = "agent_suggestions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("analysis_sessions.id"))

    # Agent info
    agent_name = Column(String, nullable=False)
    iteration = Column(Integer, nullable=False)

    # Suggestions
    suggestions = Column(JSON)  # List of suggestion strings
    priority_scores = Column(JSON)  # Dict of suggestion -> score

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("AnalysisSession", back_populates="agent_suggestions")


class AgentMemory(Base):
    """Stores agent memory for context retention."""

    __tablename__ = "agent_memories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Agent info
    agent_name = Column(String, nullable=False)
    agent_role = Column(String, nullable=False)

    # Memory content
    memory_type = Column(String, nullable=False)  # analysis, suggestion, feedback
    content = Column(JSON, nullable=False)

    # Context
    session_id = Column(String, nullable=True)  # Optional link to analysis session
    tags = Column(JSON)  # List of tags for categorization

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)


class WorkflowTemplate(Base):
    """Stores generated workflow templates for reuse."""

    __tablename__ = "workflow_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Template info
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # github, ci-cd, security, performance

    # Template content
    workflow_yaml = Column(Text, nullable=False)
    supporting_files = Column(JSON)
    variables = Column(JSON)  # Template variables for customization

    # Usage stats
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# Database operations
class DatabaseManager:
    """Manages database operations for AI Orchestra."""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or DATABASE_URL
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Create tables
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()

    def save_analysis_session(self, scenario: str, results: dict[str, Any]) -> str:
        """Save complete analysis session to database."""
        db = self.get_session()
        try:
            session_record = AnalysisSession(
                scenario=scenario,
                iterations=len(results.get("iterations", [])),
                total_agents=results.get("metadata", {}).get("total_agents", 0),
                status="completed",
                final_recommendations=results.get("final_recommendations", []),
                analysis_metadata=results.get("metadata", {}),
                devops_automation=results.get("devops_automation"),
                github_templates=results.get("github_templates"),
                completed_at=datetime.utcnow(),
            )

            db.add(session_record)
            db.commit()

            # Save individual agent analyses
            for iteration_data in results.get("iterations", []):
                iteration_num = iteration_data["iteration"]

                # Save analyses
                for agent_name, analysis in iteration_data["analyses"].items():
                    analysis_record = AgentAnalysis(
                        session_id=session_record.id,
                        agent_name=agent_name,
                        agent_role=analysis.role.value,
                        iteration=iteration_num,
                        summary=analysis.summary,
                        confidence=analysis.confidence,
                        analysis_metadata=analysis.metadata,
                    )
                    db.add(analysis_record)

                # Save suggestions
                for agent_name, suggestions in iteration_data["suggestions"].items():
                    suggestion_record = AgentSuggestion(
                        session_id=session_record.id,
                        agent_name=agent_name,
                        iteration=iteration_num,
                        suggestions=suggestions.suggestions,
                        priority_scores=suggestions.priority_scores,
                    )
                    db.add(suggestion_record)

            db.commit()
            return session_record.id

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_analysis_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent analysis history."""
        db = self.get_session()
        try:
            sessions = (
                db.query(AnalysisSession)
                .order_by(AnalysisSession.created_at.desc())
                .limit(limit)
                .all()
            )

            history = []
            for session in sessions:
                history.append(
                    {
                        "id": session.id,
                        "scenario": (
                            session.scenario[:100] + "..."
                            if len(session.scenario) > 100
                            else session.scenario
                        ),
                        "total_agents": session.total_agents,
                        "iterations": session.iterations,
                        "status": session.status,
                        "created_at": session.created_at.isoformat(),
                        "completed_at": (
                            session.completed_at.isoformat()
                            if session.completed_at
                            else None
                        ),
                    }
                )

            return history

        finally:
            db.close()

    def save_agent_memory(
        self,
        agent_name: str,
        agent_role: str,
        memory_type: str,
        content: dict[str, Any],
        session_id: str = None,
    ):
        """Save agent memory entry."""
        db = self.get_session()
        try:
            memory_record = AgentMemory(
                agent_name=agent_name,
                agent_role=agent_role,
                memory_type=memory_type,
                content=content,
                session_id=session_id,
            )

            db.add(memory_record)
            db.commit()

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_agent_memory(
        self, agent_name: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get agent memory for context."""
        db = self.get_session()
        try:
            memories = (
                db.query(AgentMemory)
                .filter(AgentMemory.agent_name == agent_name)
                .order_by(AgentMemory.created_at.desc())
                .limit(limit)
                .all()
            )

            memory_list = []
            for memory in memories:
                memory_list.append(
                    {
                        "type": memory.memory_type,
                        "content": memory.content,
                        "created_at": memory.created_at.isoformat(),
                        "access_count": memory.access_count,
                    }
                )

            return memory_list

        finally:
            db.close()

    def save_workflow_template(
        self,
        name: str,
        description: str,
        category: str,
        workflow_yaml: str,
        supporting_files: dict = None,
    ) -> str:
        """Save a workflow template for reuse."""
        db = self.get_session()
        try:
            template = WorkflowTemplate(
                name=name,
                description=description,
                category=category,
                workflow_yaml=workflow_yaml,
                supporting_files=supporting_files or {},
            )

            db.add(template)
            db.commit()

            return template.id

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()


# Global database manager
db_manager = DatabaseManager()


if __name__ == "__main__":
    # Create tables
    print("🗄️ Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized!")
