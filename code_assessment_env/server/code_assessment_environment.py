# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Code Output Assessment Environment Implementation.

An RL environment that tests an agent's ability to solve coding problems
across three difficulty levels with automated grading and reward shaping.
"""

import difflib
import random
from uuid import uuid4
from typing import Dict, List, Set, Tuple, Literal

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import CodeAssessmentAction, CodeAssessmentObservation
except ImportError:
    from models import CodeAssessmentAction, CodeAssessmentObservation


# Problem sets for each difficulty level
PROBLEMS = {
    "easy": [
        {
            "description": "Add two numbers. Given input 'a,b', output a+b.",
            "test_cases": [("3,5", "8"), ("10,20", "30"), ("0,0", "0"), ("-5,5", "0")],
        },
        {
            "description": "Reverse a string. Given input 'hello', output 'olleh'.",
            "test_cases": [("hello", "olleh"), ("world", "dlrow"), ("a", "a"), ("12345", "54321")],
        },
        {
            "description": "Count vowels in a string (a,e,i,o,u). Return the count.",
            "test_cases": [("hello", "2"), ("aeiou", "5"), ("xyz", "0"), ("programming", "3")],
        },
        {
            "description": "Find maximum of two numbers. Given input 'a,b', output the larger number.",
            "test_cases": [("5,10", "10"), ("20,15", "20"), ("7,7", "7"), ("-5,3", "3")],
        },
    ],
    "medium": [
        {
            "description": "Check if a string is a palindrome. Output 'true' or 'false'.",
            "test_cases": [("racecar", "true"), ("hello", "false"), ("a", "true"), ("abba", "true")],
        },
        {
            "description": "Find the sum of all numbers in a comma-separated list. Input: '1,2,3', Output: '6'.",
            "test_cases": [("1,2,3", "6"), ("10,20,30", "60"), ("5", "5"), ("-1,1", "0")],
        },
        {
            "description": "Count occurrences of a character in a string. Input format: 'string,char'. Output: count.",
            "test_cases": [("hello,l", "2"), ("programming,m", "2"), ("test,x", "0"), ("aaa,a", "3")],
        },
        {
            "description": "Remove duplicates from a comma-separated list, keep order. Input: '1,2,2,3', Output: '1,2,3'.",
            "test_cases": [("1,2,2,3", "1,2,3"), ("a,b,a,c", "a,b,c"), ("1,1,1", "1"), ("1,2,3", "1,2,3")],
        },
    ],
    "hard": [
        {
            "description": "Find the longest word in a sentence. Input: sentence. Output: longest word.",
            "test_cases": [
                ("the quick brown fox", "quick"),
                ("hello world", "hello"),
                ("a bb ccc", "ccc"),
                ("programming is fun", "programming"),
            ],
        },
        {
            "description": "Find the nth Fibonacci number (0-indexed). Input: n. Output: fibonacci(n).",
            "test_cases": [("0", "0"), ("1", "1"), ("5", "5"), ("10", "55")],
        },
        {
            "description": "Check if parentheses are balanced. Input: string with (){}[]. Output: 'true' or 'false'.",
            "test_cases": [("()", "true"), ("({[]})", "true"), ("(]", "false"), ("(()", "false")],
        },
        {
            "description": "Find prime numbers up to n (comma-separated). Input: n. Output: primes.",
            "test_cases": [("10", "2,3,5,7"), ("20", "2,3,5,7,11,13,17,19"), ("2", "2"), ("1", "")],
        },
    ],
}


class CodeAssessmentEnvironment(Environment):
    """
    Code Output Assessment Environment.

    Tests an agent's ability to solve coding problems across three difficulty levels.
    Features automated grading with normalized scores (0.0-1.0) and shaped rewards.

    Difficulty Levels:
        - Easy: Basic operations (addition, string reversal, simple counting)
        - Medium: String/list processing, basic algorithms
        - Hard: Advanced algorithms, recursion, complex logic

    Grading System:
        All graders produce normalized scores between 0.0-1.0:
        - 1.0: Perfect answer
        - 0.5-0.9: High partial credit (very close)
        - 0.2-0.4: Low partial credit (some correct elements)
        - 0.0: Completely incorrect

    Reward Structure (grader score × difficulty multiplier):
        - Easy: score × 1.0 (max +1.0 for correct, +0.5 partial, 0.0 wrong)
        - Medium: score × 2.0 (max +2.0 for correct, +1.0 partial, 0.0 wrong)
        - Hard: score × 5.0 (max +5.0 for correct, +2.5 partial, -0.3 wrong)
        - Streak bonus: +0.5 for 3+ consecutive correct answers
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True
    MAX_STEPS: int = 15  # Maximum steps per episode

    def __init__(self):
        """Initialize the code assessment environment."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_problem: Dict = {}
        self._current_test_case_idx: int = 0
        self._difficulty: Literal["easy", "medium", "hard"] = "easy"
        self._problems_solved: int = 0
        self._current_streak: int = 0
        self._total_reward: float = 0.0
        self._used_problems: Set[str] = set()

    def reset(self) -> CodeAssessmentObservation:
        """
        Reset the environment and present the first problem.

        Returns:
            CodeAssessmentObservation with the first problem description
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._problems_solved = 0
        self._current_streak = 0
        self._total_reward = 0.0
        self._difficulty = "easy"
        self._used_problems = set()

        # Select a random problem from the easy category
        self._current_problem = random.choice(PROBLEMS["easy"])
        self._used_problems.add(self._current_problem["description"])
        self._current_test_case_idx = 0

        test_input, _ = self._current_problem["test_cases"][0]

        return CodeAssessmentObservation(
            problem_description=self._current_problem["description"],
            difficulty=self._difficulty,
            test_case_input=test_input,
            expected_output=None,
            feedback="Welcome! Solve the problem and submit your answer.",
            is_correct=False,
            partial_credit=0.0,
            problems_solved=0,
            current_streak=0,
            done=False,
            reward=0.0,
        )

    def step(self, action: CodeAssessmentAction) -> CodeAssessmentObservation:  # type: ignore[override]
        """
        Evaluate the submitted answer and provide feedback.

        Args:
            action: CodeAssessmentAction containing the agent's answer

        Returns:
            CodeAssessmentObservation with grading results and next problem
        """
        self._state.step_count += 1

        # Get current test case
        test_input, expected_output = self._current_problem["test_cases"][self._current_test_case_idx]
        
        # Grade the answer
        is_correct, partial_credit, feedback = self._grade_answer(action.answer, expected_output)
        
        # Calculate reward
        reward = self._calculate_reward(is_correct, partial_credit)
        self._total_reward += reward

        # Update statistics
        if is_correct:
            self._problems_solved += 1
            self._current_streak += 1
        else:
            self._current_streak = 0

        # Check if episode should end
        done = self._state.step_count >= self.MAX_STEPS

        # Move to next problem if current one is solved
        if is_correct:
            self._advance_to_next_problem()

        # Get next test case
        test_input, _ = self._current_problem["test_cases"][self._current_test_case_idx]

        return CodeAssessmentObservation(
            problem_description=self._current_problem["description"],
            difficulty=self._difficulty,
            test_case_input=test_input,
            expected_output=expected_output if not is_correct else None,
            feedback=feedback,
            is_correct=is_correct,
            partial_credit=partial_credit,
            problems_solved=self._problems_solved,
            current_streak=self._current_streak,
            done=done,
            reward=reward,
            metadata={
                "total_reward": self._total_reward,
                "step": self._state.step_count,
                "difficulty": self._difficulty,
            },
        )

    def _grade_answer(self, answer: str, expected: str) -> Tuple[bool, float, str]:
        """
        Grade the submitted answer and return normalized score (0.0-1.0).

        This grader produces scores between 0.0-1.0 regardless of difficulty:
        - 1.0: Perfect answer
        - 0.5-0.9: Partial credit (close, some correct elements)
        - 0.1-0.4: Format correct but values wrong
        - 0.0: Completely incorrect

        Args:
            answer: The agent's submitted answer
            expected: The expected correct answer

        Returns:
            Tuple of (is_correct, normalized_score, feedback)
        """
        answer_clean = answer.strip().lower()
        expected_clean = expected.strip().lower()

        # Exact match = 1.0
        if answer_clean == expected_clean:
            return True, 1.0, "✓ Correct! Well done."

        # Start evaluating partial credit
        score = 0.0
        feedback = "✗ Incorrect."

        # Check for numeric list answers (comma-separated numbers only)
        is_numeric_expected = (
            ',' in expected_clean
            and all(x.strip().lstrip('-').isdigit() for x in expected_clean.split(',') if x.strip())
        ) or (
            expected_clean.lstrip('-').isdigit()
        )

        if is_numeric_expected:
            try:
                expected_nums = [int(x.strip()) for x in expected_clean.split(',') if x.strip()]
                answer_nums = [int(x.strip()) for x in answer_clean.split(',') if x.strip()]

                if len(expected_nums) == len(answer_nums):
                    correct_count = sum(1 for e, a in zip(expected_nums, answer_nums) if e == a)
                    score = correct_count / len(expected_nums)
                    if score >= 0.8:
                        feedback = f"⚡ Very close! {int(score*100)}% correct values."
                    elif score >= 0.5:
                        feedback = f"⚡ Partial credit: {int(score*100)}% correct values."
                    elif score > 0:
                        feedback = f"⚡ Some correct: {int(score*100)}%. Review the problem."
                elif len(answer_nums) > 0:
                    score = 0.2
                    feedback = "⚡ Format is numeric, but count/values are wrong."
            except (ValueError, AttributeError):
                pass

        # String similarity for non-numeric answers
        if score == 0.0:
            similarity = difflib.SequenceMatcher(None, answer_clean, expected_clean).ratio()

            if similarity >= 0.7:
                score = 0.6
                feedback = f"⚡ Close! Similar to expected answer ({int(similarity*100)}% match)."
            elif similarity >= 0.4:
                score = 0.3
                feedback = f"⚡ Some similarity ({int(similarity*100)}%). Review requirements."
            elif ',' in expected and ',' in answer_clean:
                score = 0.1
                feedback = "⚡ Correct format style, but content is incorrect."

        return False, score, feedback

    def _calculate_reward(self, is_correct: bool, normalized_score: float) -> float:
        """
        Calculate reward by applying difficulty multipliers to normalized grader scores.

        The grader produces normalized scores (0.0-1.0), which are then scaled by difficulty:
        - Easy: 1x multiplier
        - Medium: 2x multiplier  
        - Hard: 5x multiplier

        Args:
            is_correct: Whether the answer was fully correct (score = 1.0)
            normalized_score: Grader score between 0.0-1.0

        Returns:
            The calculated reward (scaled by difficulty and bonuses)
        """
        # Difficulty multipliers
        multipliers = {
            "easy": 1.0,
            "medium": 2.0,
            "hard": 5.0,
        }

        base_multiplier = multipliers[self._difficulty]

        if is_correct:
            # Perfect score: full multiplier
            reward = base_multiplier * 1.0
            
            # Streak bonus for 3+ consecutive correct answers
            if self._current_streak >= 3:
                reward += 0.5
        elif normalized_score > 0:
            # Partial credit: scale the normalized score by difficulty
            reward = base_multiplier * normalized_score
            
            # Reduce partial rewards slightly for easy problems
            if self._difficulty == "easy":
                reward *= 0.5
        else:
            # Complete failure
            # Small penalty on hard problems to discourage random guessing
            reward = -0.3 if self._difficulty == "hard" else 0.0

        return reward

    def _advance_to_next_problem(self):
        """Advance to the next problem, increasing difficulty as needed."""
        # Move to next test case in current problem
        self._current_test_case_idx += 1

        # If completed all test cases, select new problem
        if self._current_test_case_idx >= len(self._current_problem["test_cases"]):
            self._current_test_case_idx = 0

            # Increase difficulty based on problems solved
            if self._problems_solved >= 8 and self._difficulty != "hard":
                self._difficulty = "hard"
            elif self._problems_solved >= 4 and self._difficulty == "easy":
                self._difficulty = "medium"

            # Select new random problem, avoiding repeats when possible
            candidates = [
                p for p in PROBLEMS[self._difficulty]
                if p["description"] not in self._used_problems
            ]
            if not candidates:
                # All used up — reset and allow repeats
                self._used_problems = set()
                candidates = PROBLEMS[self._difficulty]
            self._current_problem = random.choice(candidates)
            self._used_problems.add(self._current_problem["description"])

    @property
    def state(self) -> State:
        """
        Get the current environment state.

        Returns:
            Current State with episode_id and step_count
        """
        return self._state
