# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Code Output Assessment Environment.

This environment tests an agent's ability to produce correct outputs for coding problems
across three difficulty levels: easy, medium, and hard.
"""

from typing import Literal, Optional
from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class CodeAssessmentAction(Action):
    """Action for submitting an answer to a coding problem."""

    answer: str = Field(..., description="The agent's answer/output for the current problem")


class CodeAssessmentObservation(Observation):
    """Observation containing the problem, feedback, and assessment results."""

    problem_description: str = Field(default="", description="Description of the coding problem")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="easy", description="Difficulty level")
    test_case_input: str = Field(default="", description="Input for the current test case")
    expected_output: Optional[str] = Field(default=None, description="Expected output (shown only after submission)")
    feedback: str = Field(default="", description="Feedback on the submitted answer")
    is_correct: bool = Field(default=False, description="Whether the answer was correct")
    partial_credit: float = Field(default=0.0, description="Partial credit score (0.0 to 1.0)")
    problems_solved: int = Field(default=0, description="Total number of problems solved so far")
    current_streak: int = Field(default=0, description="Current streak of correct answers")
