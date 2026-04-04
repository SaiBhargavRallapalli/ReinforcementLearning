# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Code Output Assessment Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import CodeAssessmentAction, CodeAssessmentObservation


class CodeAssessmentEnv(
    EnvClient[CodeAssessmentAction, CodeAssessmentObservation, State]
):
    """
    Client for the Code Output Assessment Environment.

    This client maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions with lower latency.
    Each client instance has its own dedicated environment session on the server.

    Example:
        >>> # Connect to a running server
        >>> with FirstRlProjEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset()
        ...     print(result.observation.problem_description)
        ...     print(result.observation.test_case_input)
        ...
        ...     result = client.step(FirstRlProjAction(answer="8"))
        ...     print(result.observation.is_correct)

    Example with Docker:
        >>> # Automatically start container and connect
        >>> client = FirstRlProjEnv.from_docker_image("first_rl_proj:latest")
        >>> try:
        ...     result = client.reset()
        ...     result = client.step(FirstRlProjAction(answer="8"))
        ... finally:
        ...     client.close()
    """

    def _step_payload(self, action: CodeAssessmentAction) -> Dict:
        """
        Convert CodeAssessmentAction to JSON payload for step message.

        Args:
            action: CodeAssessmentAction instance

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "answer": action.answer,
        }

    def _parse_result(self, payload: Dict) -> StepResult[CodeAssessmentObservation]:
        """
        Parse server response into StepResult[CodeAssessmentObservation].

        Args:
            payload: JSON response data from server

        Returns:
            StepResult with CodeAssessmentObservation
        """
        obs_data = payload.get("observation", {})
        observation = CodeAssessmentObservation(
            problem_description=obs_data.get("problem_description", ""),
            difficulty=obs_data.get("difficulty", "easy"),
            test_case_input=obs_data.get("test_case_input", ""),
            expected_output=obs_data.get("expected_output"),
            feedback=obs_data.get("feedback", ""),
            is_correct=obs_data.get("is_correct", False),
            partial_credit=obs_data.get("partial_credit", 0.0),
            problems_solved=obs_data.get("problems_solved", 0),
            current_streak=obs_data.get("current_streak", 0),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """
        Parse server response into State object.

        Args:
            payload: JSON response from state request

        Returns:
            State object with episode_id and step_count
        """
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
