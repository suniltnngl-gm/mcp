import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from review_cycle.models import ScanFinding


HOME = Path.home()
PLAN_FILE = HOME / "Public" / "project" / "PLAN.md"


TASK_PATTERN = re.compile(
    r"\*\*Task (\d+\.\d+):\s*(.*?)\*\*.*?"
    r"\s+\*   \*\*Status:\*\*\s*(completed|pending|in_progress)",
    re.DOTALL,
)


class TaskChecker:
    def __init__(self, plan_path: Path = PLAN_FILE):
        self.plan_path = plan_path

    def scan(self) -> List[ScanFinding]:
        findings = []
        if not self.plan_path.exists():
            findings.append(
                ScanFinding(
                    repo="project",
                    category="plan_missing",
                    severity="blocker",
                    summary="PLAN.md not found",
                    detail=f"Expected at {self.plan_path}",
                    suggested_action="Restore PLAN.md from git",
                    score=1.0,
                )
            )
            return findings
        tasks = self._parse_tasks()
        stale = self._find_stale_tasks(tasks)
        for task_id, task_name, status, reason in stale:
            findings.append(
                ScanFinding(
                    repo="project",
                    category="task_stale",
                    severity="warning",
                    summary=f"Task {task_id} ({task_name}) may be stale",
                    detail=reason,
                    file_path=str(self.plan_path),
                    suggested_action=f"Review and update status for Task {task_id}",
                    score=0.5,
                )
            )
        unblocked = self._find_unblocked_tasks(tasks)
        for task_id, task_name in unblocked:
            findings.append(
                ScanFinding(
                    repo="project",
                    category="task_unblocked",
                    severity="info",
                    summary=f"Task {task_id} ({task_name}) may now be unblocked",
                    detail=f"Dependencies appear resolved",
                    file_path=str(self.plan_path),
                    suggested_action=f"Check and update Task {task_id} status to pending",
                    score=0.3,
                )
            )
        if not stale and not unblocked:
            findings.append(
                ScanFinding(
                    repo="project",
                    category="task_ok",
                    severity="info",
                    summary="All tasks appear up to date",
                    detail="No stale or newly unblocked tasks detected",
                    score=0.0,
                )
            )
        return findings

    def _parse_tasks(self) -> Dict[str, Tuple[str, str, List[str]]]:
        tasks: Dict[str, Tuple[str, str, List[str]]] = {}
        text = self.plan_path.read_text()
        current_phase = ""
        phase_status = ""
        for line in text.splitlines():
            phase_m = re.match(r"### Phase (\d+[.\d]*):\s*(.*)", line)
            if phase_m:
                current_phase = f"{phase_m.group(1)}. {phase_m.group(2).strip()}"
                continue
            status_m = re.match(r"\*\*Status:\*\*\s*(\w+)", line)
            if status_m and current_phase:
                phase_status = status_m.group(1)
            task_m = re.match(
                r"\*   \*\*Task (\d+\.\d+):\s*(.*?)\*\*", line
            )
            if task_m:
                tid = task_m.group(1)
                tname = task_m.group(2).strip()
                tasks[tid] = (tname, current_phase, [])
                current_task = tid
                continue
            if current_phase and phase_status and current_phase not in [v[1] for v in tasks.values()]:
                pass
        return tasks

    def _find_stale_tasks(
        self, tasks: Dict[str, Tuple[str, str, List[str]]]
    ) -> List[Tuple[str, str, str, str]]:
        stale = []
        text = self.plan_path.read_text()
        for task_id, (task_name, phase, _) in tasks.items():
            status_match = re.search(
                rf"Task {re.escape(task_id)}:.*?\n.*?\*\*Status:\*\*\s*(\w+)",
                text,
            )
            if status_match:
                status = status_match.group(1)
                if status == "pending":
                    file_pattern = self._guess_file_pattern(task_name)
                    if file_pattern and self._files_exist(file_pattern):
                        stale.append(
                            (
                                task_id,
                                task_name,
                                status,
                                f"Status is '{status}' but matching files found: {file_pattern}",
                            )
                        )
        return stale

    def _find_unblocked_tasks(
        self, tasks: Dict[str, Tuple[str, str, List[str]]]
    ) -> List[Tuple[str, str]]:
        unblocked = []
        text = self.plan_path.read_text()
        for task_id, (task_name, phase, _) in tasks.items():
            status_match = re.search(
                rf"Task {re.escape(task_id)}:.*?\n.*?\*\*Status:\*\*\s*(\w+)",
                text,
            )
            if status_match and status_match.group(1) == "pending":
                if "Blocked" in task_name or "Firestore" in task_name:
                    blockers = re.search(
                        rf"Task {re.escape(task_id)}.*?Blocked By.*?#(\d+)",
                        text,
                        re.DOTALL,
                    )
                    if blockers:
                        blocker_id = blockers.group(1)
                        blocker_status = re.search(
                            rf"\| {re.escape(blocker_id)} \|.*?\| (✅ Completed|⏳ Pending)",
                            text,
                        )
                        if blocker_status and "✅" in blocker_status.group(1):
                            unblocked.append((task_id, task_name))
        return unblocked

    def _guess_file_pattern(self, task_name: str) -> Optional[str]:
        task_lower = task_name.lower()
        if "ollama" in task_lower:
            return "**/ollama_cloud_server.py"
        if "strategy" in task_lower or "cooperative" in task_lower:
            return "**/cooperative_strategy.py"
        if "auth" in task_lower or "firebase" in task_lower:
            return "**/firebase_auth_*.py"
        if "test" in task_lower and "unit" in task_lower:
            return "**/test_cooperative_strategy.py"
        if "integration" in task_lower:
            return "**/test_integration_mcp.py"
        if "doc" in task_lower and "manager" in task_lower:
            return "**/doc_manager_*.py"
        return None

    def _files_exist(self, pattern: str) -> bool:
        try:
            result = subprocess.run(
                ["python3", "-c",
                 f"from pathlib import Path; "
                 f"print(len(list(Path('{HOME}/Public/project').rglob('{pattern}'))))"
                 ],
                capture_output=True, text=True, timeout=10,
            )
            count = int(result.stdout.strip())
            return count > 0
        except (ValueError, subprocess.TimeoutExpired):
            return False
