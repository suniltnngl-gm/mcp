# src/llm_wrapper/mcp/game_rules_server.py

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, CallToolResult
from pydantic import BaseModel, Field

# Assuming DocManagerClient will be available to interact with DocManagerServer
# from src.llm_wrapper.mcp.doc_manager_client import DocManagerClient


class GameSession(BaseModel):
    """Represents an active game session."""

    session_id: str
    puzzle_id: str
    start_time: str
    status: str = "active"  # active, solved, abandoned
    questions_asked: int = 0
    guesses_made: int = 0


class PuzzleDefinition(BaseModel):
    """Defines a lateral thinking puzzle."""

    puzzle_id: str
    title: str
    story_intro: str
    secret_solution: str  # The core secret to be guarded by the judge
    hints: List[str] = Field(default_factory=list)  # Optional hints


class StartGameInput(BaseModel):
    """Input schema for the start_game tool."""

    puzzle_id: str = Field(..., description="The ID of the puzzle to start.")


class EvaluateQuestionInput(BaseModel):
    """Input schema for the evaluate_question tool."""

    session_id: str = Field(..., description="The ID of the active game session.")
    question: str = Field(..., description="The user's question to the judge.")


class CheckGuessInput(BaseModel):
    """Input schema for the check_guess tool."""

    session_id: str = Field(..., description="The ID of the active game session.")
    user_guess: str = Field(
        ..., description="The user's guess for the puzzle solution."
    )


class GameRulesServer:
    """
    An MCP server for hosting lateral thinking games.
    Manages game sessions and acts as a "Judge" for user questions.
    """

    DB_NAME = "game_rules.db"

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._initialize_db()
        self._load_starter_puzzles()  # Load puzzles into DB
        self.mcp_server = FastMCP(name="game_rules_manager")
        self.mcp_server.add_tool(
            self._start_game_tool,
            name="start_game",
            description="Starts a new game session for a given puzzle.",
        )
        self.mcp_server.add_tool(
            self._evaluate_question_tool,
            name="evaluate_question",
            description="Evaluates a user's yes/no question against the puzzle's secret solution.",
        )
        self.mcp_server.add_tool(
            self._check_guess_tool,
            name="check_guess",
            description="Checks if the user's guess matches the puzzle's secret solution.",
        )

    def _initialize_db(self):
        """Initializes the SQLite database schema for puzzles and sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS puzzles (
                puzzle_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                story_intro TEXT NOT NULL,
                secret_solution TEXT NOT NULL,
                hints TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                session_id TEXT PRIMARY KEY,
                puzzle_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                status TEXT NOT NULL,
                questions_asked INTEGER,
                guesses_made INTEGER,
                FOREIGN KEY (puzzle_id) REFERENCES puzzles (puzzle_id)
            )
        """)
        conn.commit()
        conn.close()

    def _load_starter_puzzles(self):
        """Loads some predefined lateral thinking puzzles into the database."""
        starter_puzzles = [
            PuzzleDefinition(
                puzzle_id="turtle_soup",
                title="Turtle Soup",
                story_intro="A man walks into a restaurant and orders turtle soup. After taking one spoonful, he stands up, walks outside, and shoots himself. Why?",
                secret_solution="The man was a sailor. He was shipwrecked on a desert island with other survivors. They had nothing to eat, and his friend suggested they eat turtle soup. He ate the soup, but later discovered they had actually eaten his friend. He recognized the taste of real turtle soup in the restaurant and realized what he had done, leading him to despair.",
                hints=[
                    "It's about taste.",
                    "It involves a past event.",
                    "Someone else was involved.",
                ],
            ),
            PuzzleDefinition(
                puzzle_id="elevator_man",
                title="The Elevator Man",
                story_intro="A man lives on the 12th floor of an apartment building. Every morning, he takes the elevator down to the ground floor and leaves for work. In the evening, he returns and takes the elevator to the 10th floor. He then walks up two flights of stairs to his apartment. Why?",
                secret_solution="The man is too short to reach the button for the 12th floor. He can only reach the 10th-floor button.",
                hints=[
                    "It's about physical limitations.",
                    "His routine changes depending on direction.",
                    "He could reach buttons for other floors.",
                ],
            ),
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for puzzle in starter_puzzles:
            cursor.execute(
                "INSERT OR IGNORE INTO puzzles (puzzle_id, title, story_intro, secret_solution, hints) VALUES (?, ?, ?, ?, ?)",
                (
                    puzzle.puzzle_id,
                    puzzle.title,
                    puzzle.story_intro,
                    puzzle.secret_solution,
                    json.dumps(puzzle.hints),
                ),
            )
        conn.commit()
        conn.close()
        print(f"Loaded {len(starter_puzzles)} starter puzzles into {self.db_path}")

    def _get_puzzle_details(self, puzzle_id: str) -> Optional[PuzzleDefinition]:
        """Retrieves puzzle details from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT puzzle_id, title, story_intro, secret_solution, hints FROM puzzles WHERE puzzle_id = ?",
            (puzzle_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return PuzzleDefinition(
                puzzle_id=row[0],
                title=row[1],
                story_intro=row[2],
                secret_solution=row[3],
                hints=json.loads(row[4]) if row[4] else [],
            )
        return None

    def _get_game_session(self, session_id: str) -> Optional[GameSession]:
        """Retrieves a game session from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT session_id, puzzle_id, start_time, status, questions_asked, guesses_made FROM game_sessions WHERE session_id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return GameSession(
                session_id=row[0],
                puzzle_id=row[1],
                start_time=row[2],
                status=row[3],
                questions_asked=row[4],
                guesses_made=row[5],
            )
        return None

    def _update_game_session(self, session: GameSession):
        """Updates an existing game session in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE game_sessions SET status = ?, questions_asked = ?, guesses_made = ? WHERE session_id = ?",
            (
                session.status,
                session.questions_asked,
                session.guesses_made,
                session.session_id,
            ),
        )
        conn.commit()
        conn.close()

    async def _start_game_tool(self, input: StartGameInput) -> CallToolResult:
        """MCP tool to start a new game session."""
        puzzle = self._get_puzzle_details(input.puzzle_id)
        if not puzzle:
            return CallToolResult(
                content=f"Error: Puzzle '{input.puzzle_id}' not found.", success=False
            )

        session_id = str(uuid.uuid4())
        start_time = datetime.now().isoformat()
        session = GameSession(
            session_id=session_id, puzzle_id=input.puzzle_id, start_time=start_time
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO game_sessions (session_id, puzzle_id, start_time, status, questions_asked, guesses_made) VALUES (?, ?, ?, ?, ?, ?)",
            (
                session.session_id,
                session.puzzle_id,
                session.start_time,
                session.status,
                session.questions_asked,
                session.guesses_made,
            ),
        )
        conn.commit()
        conn.close()

        return CallToolResult(
            content=f"Game started! Session ID: {session_id}. Puzzle: {puzzle.title}. Story: {puzzle.story_intro}",
            resources=[CallToolResult(data=json.dumps(session.model_dump()))],
        )

    async def _evaluate_question_tool(
        self, input: EvaluateQuestionInput
    ) -> CallToolResult:
        """MCP tool to evaluate a user's yes/no question."""
        session = self._get_game_session(input.session_id)
        if not session:
            return CallToolResult(
                content=f"Error: Session '{input.session_id}' not found.", success=False
            )
        if session.status != "active":
            return CallToolResult(
                content=f"Error: Session '{input.session_id}' is not active.",
                success=False,
            )

        puzzle = self._get_puzzle_details(session.puzzle_id)
        if not puzzle:
            return CallToolResult(
                content=f"Error: Puzzle '{session.puzzle_id}' not found for session.",
                success=False,
            )

        session.questions_asked += 1
        self._update_game_session(session)

        # --- JUDGE LOGIC (Simplified for now) ---
        # In a real scenario, an LLM (local or provider) would analyze the question
        # against the puzzle.secret_solution and return "Yes", "No", or "Irrelevant".
        # For this server, we simulate this by checking keywords.
        question_lower = input.question.lower()
        solution_lower = puzzle.secret_solution.lower()

        response = "Irrelevant"  # Default to irrelevant
        if any(
            keyword in question_lower
            for keyword in ["dead", "killed", "died", "murder"]
        ):
            if "turtle soup" in solution_lower and "friend" in solution_lower:
                response = "Yes"  # For turtle soup, if related to death/killing friend
        elif "short" in question_lower or "height" in question_lower:
            if "elevator" in solution_lower and "short" in solution_lower:
                response = "Yes"  # For elevator man, if related to height

        return CallToolResult(content=response, success=True)

    async def _check_guess_tool(self, input: CheckGuessInput) -> CallToolResult:
        """MCP tool to check the user's guess against the secret solution."""
        session = self._get_game_session(input.session_id)
        if not session:
            return CallToolResult(
                content=f"Error: Session '{input.session_id}' not found.", success=False
            )
        if session.status != "active":
            return CallToolResult(
                content=f"Error: Session '{input.session_id}' is not active.",
                success=False,
            )

        puzzle = self._get_puzzle_details(session.puzzle_id)
        if not puzzle:
            return CallToolResult(
                content=f"Error: Puzzle '{session.puzzle_id}' not found for session.",
                success=False,
            )

        session.guesses_made += 1
        self._update_game_session(session)

        user_guess_lower = input.user_guess.lower().strip()
        secret_lower = puzzle.secret_solution.lower().strip()

        is_correct = (
            user_guess_lower == secret_lower or user_guess_lower in secret_lower
        )  # Simple substring match for flexibility

        if is_correct:
            session.status = "solved"
            self._update_game_session(session)
            return CallToolResult(
                content="Correct! You've solved the puzzle!",
                success=True,
                details={"solved": True},
            )
        else:
            return CallToolResult(
                content="That's not quite right. Keep guessing!",
                success=True,
                details={"solved": False},
            )

    async def run_forever(self):
        """Starts the MCP FastMCP stdio server."""
        print(f"Game Rules Server starting, DB: {self.db_path}")
        await self.mcp_server.run_stdio_async()


if __name__ == "__main__":

    async def main():
        print("--- Testing GameRulesServer ---")
        temp_db_path = Path("temp_game_rules.db")
        if temp_db_path.exists():
            temp_db_path.unlink()  # Clean up previous test run

        server = GameRulesServer(db_path=temp_db_path)

        try:
            # Test starting a game
            print("\nCalling start_game tool for 'turtle_soup':")
            start_input = StartGameInput(puzzle_id="turtle_soup")
            start_result = await server._start_game_tool(start_input)
            print(f"Start Game Result: {start_result.content}")
            if not start_result.success or not start_result.resources:
                raise Exception("Failed to start game.")

            session_data = json.loads(start_result.resources[0].data)
            session_id = session_data["session_id"]
            print(f"Session ID: {session_id}")
            print(f"Puzzle Intro: {session_data['story_intro']}")

            # Test evaluating questions
            print("\nCalling evaluate_question tool:")
            eval_input_yes = EvaluateQuestionInput(
                session_id=session_id,
                question="Was the man killed because of the soup?",
            )
            eval_result_yes = await server._evaluate_question_tool(eval_input_yes)
            print(f"Evaluation (Yes) Result: {eval_result_yes.content}")

            eval_input_no = EvaluateQuestionInput(
                session_id=session_id, question="Did a fish kill him?"
            )
            eval_result_no = await server._evaluate_question_tool(eval_input_no)
            print(f"Evaluation (No) Result: {eval_result_no.content}")

            eval_input_irrelevant = EvaluateQuestionInput(
                session_id=session_id, question="What color was his car?"
            )
            eval_result_irrelevant = await server._evaluate_question_tool(
                eval_input_irrelevant
            )
            print(f"Evaluation (Irrelevant) Result: {eval_result_irrelevant.content}")

            # Test checking a guess (incorrect)
            print("\nCalling check_guess tool (incorrect):")
            guess_input_wrong = CheckGuessInput(
                session_id=session_id, user_guess="He was allergic to turtle soup."
            )
            guess_result_wrong = await server._check_guess_tool(guess_input_wrong)
            print(f"Guess (Wrong) Result: {guess_result_wrong.content}")

            # Test checking a guess (correct for turtle soup)
            print("\nCalling check_guess tool (correct):")
            guess_input_correct = CheckGuessInput(
                session_id=session_id,
                user_guess="He realized he had eaten his friend's flesh thinking it was turtle meat during a shipwreck.",
            )
            guess_result_correct = await server._check_guess_tool(guess_input_correct)
            print(f"Guess (Correct) Result: {guess_result_correct.content}")

            session_after_solve = server._get_game_session(session_id)
            print(f"Session status after correct guess: {session_after_solve.status}")

        except Exception as e:
            print(f"An error occurred during GameRulesServer test: {e}")
        finally:
            # Clean up dummy database
            if temp_db_path.exists():
                temp_db_path.unlink()
                print(f"Cleaned up temporary database: {temp_db_path}")

    asyncio.run(main())
