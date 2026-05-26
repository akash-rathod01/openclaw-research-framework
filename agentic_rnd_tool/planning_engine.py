"""
Planning Engine - Adaptive Execution Planning
Part of OpenClaw Multi-Agent Framework v1.1

This engine creates and executes dynamic plans based on goals and current state.
It makes decisions about:
- What to scrape next
- When to stop or continue
- How to allocate resources
- Which agents to invoke

Author: Akash Rathod
License: MIT
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time


class TaskPriority(Enum):
    """Priority levels for tasks"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskStatus(Enum):
    """Status of execution tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """Represents a single executable task"""
    task_id: str
    task_type: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    data: Dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    estimated_time: float = 0.0
    actual_time: float = 0.0
    result: Any = None
    error: Optional[str] = None


@dataclass
class ExecutionGoal:
    """Represents the overall goal of execution"""
    goal_type: str  # 'quality', 'quantity', 'speed', 'comprehensive'
    target_sources: int = 50
    max_depth: int = 3
    min_quality_score: float = 0.7
    max_time_budget: float = 3600.0  # seconds
    require_summarization: bool = True
    prioritize_authority: bool = True


@dataclass
class ExecutionState:
    """Current state of execution"""
    sources_collected: int = 0
    sources_processed: int = 0
    summaries_generated: int = 0
    time_elapsed: float = 0.0
    current_depth: int = 0
    quality_scores: List[float] = field(default_factory=list)
    failed_sources: int = 0


class PlanningEngine:
    """
    Adaptive planning engine that creates and adjusts execution plans dynamically.
    Makes intelligent decisions about what to do next based on goals and current state.
    """
    
    def __init__(self, goal: ExecutionGoal):
        """
        Initialize the planning engine.
        
        Args:
            goal: ExecutionGoal defining what we want to achieve
        """
        self.goal = goal
        self.state = ExecutionState()
        self.tasks: List[Task] = []
        self.execution_log: List[str] = []
        self.start_time = time.time()
        
    def create_initial_plan(self, starting_url: str) -> List[Task]:
        """
        Create the initial execution plan based on the goal.
        
        Args:
            starting_url: The URL to start scraping from
            
        Returns:
            List of tasks to execute
        """
        self.tasks = []
        task_id = 0
        
        # Log planning decision
        self._log(f"Creating initial plan for goal: {self.goal.goal_type}")
        self._log(f"Target: {self.goal.target_sources} sources, max depth: {self.goal.max_depth}")
        
        # Task 1: Initial URL scraping (always highest priority)
        task_id += 1
        self.tasks.append(Task(
            task_id=f"scrape_{task_id}",
            task_type="scrape",
            priority=TaskPriority.CRITICAL,
            data={"url": starting_url, "depth": 0},
            estimated_time=10.0
        ))
        
        # Task 2: Source ranking (if prioritizing authority)
        if self.goal.prioritize_authority:
            task_id += 1
            self.tasks.append(Task(
                task_id=f"rank_{task_id}",
                task_type="rank_sources",
                priority=TaskPriority.HIGH,
                data={},
                dependencies=[f"scrape_1"],
                estimated_time=2.0
            ))
        
        # Task 3: Summarization (if required)
        if self.goal.require_summarization:
            task_id += 1
            self.tasks.append(Task(
                task_id=f"summarize_{task_id}",
                task_type="summarize",
                priority=TaskPriority.MEDIUM,
                data={},
                dependencies=[f"scrape_1"],
                estimated_time=15.0
            ))
        
        self._log(f"Initial plan created with {len(self.tasks)} tasks")
        return self.tasks
    
    def decide_next_action(self, current_results: Dict) -> Optional[str]:
        """
        Decide what action to take next based on current state and goals.
        
        Args:
            current_results: Results from recent actions
            
        Returns:
            Action string ('continue', 'stop', 'adjust_depth', 'focus_quality', etc.)
            or None if goal is met
        """
        self._update_state(current_results)
        
        # Check stopping conditions
        if self._should_stop():
            self._log("Decision: STOP - Goal met or constraints exceeded")
            return None
        
        # Goal-specific decision logic
        if self.goal.goal_type == 'quality':
            return self._decide_for_quality_goal()
        elif self.goal.goal_type == 'quantity':
            return self._decide_for_quantity_goal()
        elif self.goal.goal_type == 'speed':
            return self._decide_for_speed_goal()
        elif self.goal.goal_type == 'comprehensive':
            return self._decide_for_comprehensive_goal()
        else:
            return self._decide_balanced()
    
    def adjust_plan(self, action: str, context: Dict) -> List[Task]:
        """
        Adjust the execution plan based on a decision.
        
        Args:
            action: Action to take ('expand', 'optimize', 'focus', etc.)
            context: Additional context for adjustment
            
        Returns:
            Updated list of tasks
        """
        self._log(f"Adjusting plan based on action: {action}")
        
        if action == 'expand':
            # Add more scraping tasks
            new_urls = context.get('urls', [])
            for idx, url in enumerate(new_urls[:10]):  # Limit to 10 new tasks
                task_id = len(self.tasks) + 1
                self.tasks.append(Task(
                    task_id=f"scrape_{task_id}",
                    task_type="scrape",
                    priority=TaskPriority.MEDIUM,
                    data={"url": url, "depth": self.state.current_depth + 1},
                    estimated_time=10.0
                ))
        
        elif action == 'optimize':
            # Re-prioritize tasks based on source ranking
            ranked_urls = context.get('ranked_urls', [])
            for task in self.tasks:
                if task.status == TaskStatus.PENDING and task.task_type == "scrape":
                    url = task.data.get('url')
                    if url in ranked_urls[:5]:  # Top 5 URLs
                        task.priority = TaskPriority.HIGH
                    elif url in ranked_urls[:15]:
                        task.priority = TaskPriority.MEDIUM
                    else:
                        task.priority = TaskPriority.LOW
        
        elif action == 'focus_quality':
            # Skip low-priority tasks, focus on high-quality sources
            for task in self.tasks:
                if task.status == TaskStatus.PENDING and task.priority == TaskPriority.LOW:
                    task.status = TaskStatus.SKIPPED
                    self._log(f"Skipping task {task.task_id} to focus on quality")
        
        elif action == 'speed_up':
            # Reduce summarization tasks to save time
            for task in self.tasks:
                if task.status == TaskStatus.PENDING and task.task_type == "summarize":
                    task.priority = TaskPriority.LOW
        
        return self.tasks
    
    def _should_stop(self) -> bool:
        """Determine if execution should stop."""
        # Met target sources
        if self.state.sources_collected >= self.goal.target_sources:
            return True
        
        # Exceeded time budget
        if self.state.time_elapsed >= self.goal.max_time_budget:
            self._log("Time budget exceeded")
            return True
        
        # Too many failures
        failure_rate = self.state.failed_sources / max(1, self.state.sources_processed)
        if failure_rate > 0.5 and self.state.sources_processed > 10:
            self._log(f"High failure rate: {failure_rate:.1%}")
            return True
        
        # Reached max depth with no progress
        if self.state.current_depth >= self.goal.max_depth:
            pending_tasks = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)
            if pending_tasks == 0:
                return True
        
        return False
    
    def _decide_for_quality_goal(self) -> str:
        """Decision logic when goal is quality-focused."""
        avg_quality = sum(self.state.quality_scores) / max(1, len(self.state.quality_scores))
        
        if avg_quality < self.goal.min_quality_score:
            self._log(f"Quality below threshold ({avg_quality:.2f} < {self.goal.min_quality_score})")
            return 'focus_quality'
        
        if self.state.sources_collected < self.goal.target_sources * 0.5:
            return 'expand'
        
        return 'optimize'
    
    def _decide_for_quantity_goal(self) -> str:
        """Decision logic when goal is quantity-focused."""
        progress = self.state.sources_collected / self.goal.target_sources
        
        if progress < 0.5:
            return 'expand'
        elif progress < 0.8:
            return 'continue'
        else:
            return 'speed_up'
    
    def _decide_for_speed_goal(self) -> str:
        """Decision logic when goal is speed-focused."""
        time_ratio = self.state.time_elapsed / self.goal.max_time_budget
        progress_ratio = self.state.sources_collected / self.goal.target_sources
        
        if time_ratio > progress_ratio:
            # Behind schedule
            return 'speed_up'
        else:
            return 'continue'
    
    def _decide_for_comprehensive_goal(self) -> str:
        """Decision logic when goal is comprehensive coverage."""
        if self.state.current_depth < self.goal.max_depth:
            return 'expand'
        else:
            return 'optimize'
    
    def _decide_balanced(self) -> str:
        """Default balanced decision logic."""
        progress = self.state.sources_collected / self.goal.target_sources
        
        if progress < 0.3:
            return 'expand'
        elif progress < 0.7:
            return 'continue'
        else:
            return 'optimize'
    
    def _update_state(self, results: Dict):
        """Update execution state with new results."""
        self.state.sources_collected = results.get('sources_collected', self.state.sources_collected)
        self.state.sources_processed = results.get('sources_processed', self.state.sources_processed)
        self.state.summaries_generated = results.get('summaries_generated', self.state.summaries_generated)
        self.state.current_depth = results.get('current_depth', self.state.current_depth)
        self.state.failed_sources = results.get('failed_sources', self.state.failed_sources)
        
        # Update time
        self.state.time_elapsed = time.time() - self.start_time
        
        # Update quality scores
        if 'quality_score' in results:
            self.state.quality_scores.append(results['quality_score'])
    
    def _log(self, message: str):
        """Log a planning decision or event."""
        timestamp = time.time() - self.start_time
        log_entry = f"[{timestamp:.1f}s] {message}"
        self.execution_log.append(log_entry)
        print(f"[PLANNER] {log_entry}")
    
    def get_execution_report(self) -> str:
        """Generate a report of execution planning and decisions."""
        report = "\n" + "="*80 + "\n"
        report += "PLANNING ENGINE EXECUTION REPORT\n"
        report += "="*80 + "\n\n"
        
        report += f"Goal Type: {self.goal.goal_type}\n"
        report += f"Target Sources: {self.goal.target_sources}\n"
        report += f"Max Depth: {self.goal.max_depth}\n\n"
        
        report += "Current State:\n"
        report += f"  Sources Collected: {self.state.sources_collected}\n"
        report += f"  Sources Processed: {self.state.sources_processed}\n"
        report += f"  Summaries Generated: {self.state.summaries_generated}\n"
        report += f"  Time Elapsed: {self.state.time_elapsed:.1f}s\n"
        report += f"  Current Depth: {self.state.current_depth}\n"
        report += f"  Failed Sources: {self.state.failed_sources}\n"
        
        if self.state.quality_scores:
            avg_quality = sum(self.state.quality_scores) / len(self.state.quality_scores)
            report += f"  Average Quality: {avg_quality:.2f}\n"
        
        report += f"\nTotal Tasks: {len(self.tasks)}\n"
        report += f"  Completed: {sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)}\n"
        report += f"  Failed: {sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)}\n"
        report += f"  Skipped: {sum(1 for t in self.tasks if t.status == TaskStatus.SKIPPED)}\n"
        report += f"  Pending: {sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)}\n"
        
        report += "\nExecution Log:\n"
        for entry in self.execution_log[-10:]:  # Last 10 entries
            report += f"  {entry}\n"
        
        report += "\n" + "="*80 + "\n"
        
        return report


# Example usage
if __name__ == "__main__":
    # Create a quality-focused goal
    goal = ExecutionGoal(
        goal_type='quality',
        target_sources=50,
        max_depth=3,
        min_quality_score=0.8,
        require_summarization=True,
        prioritize_authority=True
    )
    
    # Initialize planner
    planner = PlanningEngine(goal)
    
    # Create initial plan
    tasks = planner.create_initial_plan("https://example.com")
    print(f"Created {len(tasks)} initial tasks")
    
    # Simulate some progress
    results = {
        'sources_collected': 15,
        'sources_processed': 15,
        'summaries_generated': 12,
        'current_depth': 1,
        'failed_sources': 1,
        'quality_score': 0.85
    }
    
    # Decide next action
    action = planner.decide_next_action(results)
    print(f"Next action: {action}")
    
    # Print report
    print(planner.get_execution_report())
