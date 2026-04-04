---
title: Code Output Assessment Environment
emoji: 🧪
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - code-assessment
  - rl-environment
  - code-grading
---

# Code Output Assessment Environment

An OpenEnv RL environment that tests an agent's ability to solve coding problems across three difficulty levels with automated grading and shaped rewards.

## Overview

This environment challenges AI agents to:
- Solve coding problems at varying difficulty levels (Easy, Medium, Hard)
- Produce correct outputs for given test cases
- Maximize rewards through accuracy and maintaining solving streaks

## Difficulty Levels

### 🟢 Easy (1x multiplier)
- Basic arithmetic operations (addition, max)
- Simple string manipulation (reversal, vowel counting)
- **Example**: Add two numbers: `3,5` → `8`

### 🟡 Medium (2x multiplier)
- String/list processing (palindrome check, duplicate removal)
- Aggregation operations (sum of lists, character counting)
- **Example**: Check palindrome: `racecar` → `true`

### 🔴 Hard (5x multiplier)
- Advanced algorithms (Fibonacci, prime numbers)
- Complex logic (balanced parentheses, longest word)
- **Example**: Find primes up to n: `10` → `2,3,5,7`

## Grading & Reward System

### Normalized Grading (0.0-1.0)
All graders produce normalized scores regardless of difficulty:

| Score Range | Meaning | Feedback |
|-------------|---------|----------|
| 1.0 | Perfect answer | "✓ Correct!" |
| 0.8-0.9 | Very close | "⚡ Very close! 80-90% correct" |
| 0.5-0.7 | Moderate partial credit | "⚡ Partial credit: 50-70% correct" |
| 0.2-0.4 | Low partial credit | "⚡ Some correct elements" |
| 0.1 | Format credit only | "⚡ Correct format, wrong values" |
| 0.0 | Completely wrong | "✗ Incorrect" |

### Reward Calculation
**Formula**: `reward = grader_score × difficulty_multiplier + bonuses`

| Difficulty | Multiplier | Perfect (1.0) | High Partial (0.7) | Low Partial (0.3) | Wrong (0.0) |
|------------|------------|---------------|--------------------|--------------------|--------------|
| Easy | 1x | +1.0 | +0.35 | +0.15 | 0.0 |
| Medium | 2x | +2.0 | +1.4 | +0.6 | 0.0 |
| Hard | 5x | +5.0 | +3.5 | +1.5 | -0.3 |

**Bonuses**:
- Streak Bonus: +0.5 for maintaining 3+ consecutive correct answers
- Penalty: -0.3 on hard problems for completely wrong answers (discourages random guessing)

**Maximum Episode Reward**: ~28.0 (perfect accuracy with streaks)

## Quick Start

The simplest way to use the Code Assessment environment is through the `CodeAssessmentEnv` class:

```python
from code_assessment_env import CodeAssessmentAction, CodeAssessmentEnv

# Create environment from Docker image
env = CodeAssessmentEnv.from_docker_image("code_assessment_env:latest").sync()

# Reset to get first problem
result = env.reset()
print(f"Problem: {result.observation.problem_description}")
print(f"Difficulty: {result.observation.difficulty}")
print(f"Test Input: {result.observation.test_case_input}")

# Submit an answer
result = env.step(CodeAssessmentAction(answer="8"))
print(f"Correct: {result.observation.is_correct}")
print(f"Reward: {result.reward}")
print(f"Feedback: {result.observation.feedback}")

# Continue solving problems
for _ in range(10):
    obs = result.observation
    # Your agent logic here to solve obs.problem_description with obs.test_case_input
    answer = solve_problem(obs.problem_description, obs.test_case_input)
    result = env.step(CodeAssessmentAction(answer=answer))
    
    if result.done:
        break

env.close()
```

## Key Features

### ✅ Normalized Grading System
Each answer is graded on a 0.0-1.0 scale:
- **Exact match detection**: Full credit (1.0)
- **Partial credit**: 0.1-0.9 based on correctness percentage
- **Format validation**: Credit for proper structure even if values are wrong
- **String similarity**: Grading for text-based answers using overlap metrics

### ✅ Difficulty-Scaled Rewards
- Normalized grader scores (0.0-1.0) are multiplied by difficulty
- Easy: 1x, Medium: 2x, Hard: 5x multipliers
- Higher difficulty = higher potential rewards for correct answers
- Partial credit proportionally scaled by difficulty

### ✅ Progressive Difficulty
- Starts with Easy problems
- Advances to Medium after solving 4 problems
- Advances to Hard after solving 8 problems

### ✅ Shaped Rewards
- Base rewards scale with difficulty
- Partial credit for near-correct answers
- Streak bonuses for consecutive successes
- Penalties for repeated failures on hard problems

### ✅ Rich Feedback
Observations include:
- `problem_description`: What to solve
- `difficulty`: Current difficulty level
- `test_case_input`: Input to process
- `feedback`: Grading feedback ("✓ Correct!", "✗ Incorrect", etc.)
- `is_correct`: Boolean correctness flag
- `partial_credit`: Score between 0.0-1.0
- `problems_solved`: Total solved count
- `current_streak`: Consecutive correct answers

## Running with LLM Agent

Use the included inference script to test with an LLM:

```bash
# Set environment variables
export IMAGE_NAME=code_assessment_env:latest
export HF_TOKEN=your_huggingface_token

# Run inference
uv run python inferency.py
```

Expected output:
```
[START] task=code_output_assessment env=code_assessment_env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=answer='8' | correct=True | difficulty=easy reward=1.00 done=false error=null
[STEP] step=2 action=answer='olleh' | correct=True | difficulty=easy reward=1.00 done=false error=null
...
[END] success=true steps=15 score=0.720 rewards=1.00,1.00,2.00,2.00,5.00,...
```

## Development

### Building the Docker Image

```bash
cd code_assessment_env
docker build -t code_assessment_env:latest .
```

### Running Locally

```bash
# Start the server
docker run -p 8000:8000 code_assessment_env:latest

# Test with API
curl http://localhost:8000/docs  # Swagger UI
```

## API Endpoints

- `POST /reset` - Start new episode
- `POST /step` - Submit answer
- `GET /state` - Get episode state
- `GET /schema` - Get action/observation schemas
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Problem Examples

### Easy Problems
```python
# Addition
Input: "3,5" → Output: "8"

# String Reversal  
Input: "hello" → Output: "olleh"

# Vowel Counting
Input: "hello" → Output: "2"
```

### Medium Problems
```python
# Palindrome Check
Input: "racecar" → Output: "true"

# Sum List
Input: "1,2,3" → Output: "6"

# Remove Duplicates
Input: "1,2,2,3" → Output: "1,2,3"
```

### Hard Problems
```python
# Fibonacci
Input: "10" → Output: "55"

# Balanced Parentheses
Input: "({[]})" → Output: "true"

# Prime Numbers
Input: "20" → Output: "2,3,5,7,11,13,17,19"
```

## Training Tips

1. **Start Simple**: Master easy problems before advancing
2. **Pay Attention to Format**: Exact formatting matters (lowercase true/false, comma-separated lists)
3. **Build Streaks**: Maintain accuracy for streak bonuses
4. **Learn from Feedback**: Use partial credit signals to improve
5. **Optimize for Speed**: Solve quickly to maximize problems per episode

## License

BSD-style license - see LICENSE file for details.
- Connecting to the environment
- Container cleanup when you call `close()`

## Building the Docker Image

Before using the environment, you need to build the Docker image:

```bash
# From project root
docker build -t first_rl_proj-env:latest -f server/Dockerfile .
```

## Deploying to Hugging Face Spaces

You can easily deploy your OpenEnv environment to Hugging Face Spaces using the `openenv push` command:

```bash
# From the environment directory (where openenv.yaml is located)
openenv push

# Or specify options
openenv push --namespace my-org --private
```

The `openenv push` command will:
1. Validate that the directory is an OpenEnv environment (checks for `openenv.yaml`)
2. Prepare a custom build for Hugging Face Docker space (enables web interface)
3. Upload to Hugging Face (ensuring you're logged in)

### Prerequisites

- Authenticate with Hugging Face: The command will prompt for login if not already authenticated

### Options

- `--directory`, `-d`: Directory containing the OpenEnv environment (defaults to current directory)
- `--repo-id`, `-r`: Repository ID in format 'username/repo-name' (defaults to 'username/env-name' from openenv.yaml)
- `--base-image`, `-b`: Base Docker image to use (overrides Dockerfile FROM)
- `--private`: Deploy the space as private (default: public)

### Examples

```bash
# Push to your personal namespace (defaults to username/env-name from openenv.yaml)
openenv push

# Push to a specific repository
openenv push --repo-id my-org/my-env

# Push with a custom base image
openenv push --base-image ghcr.io/meta-pytorch/openenv-base:latest

# Push as a private space
openenv push --private

# Combine options
openenv push --repo-id my-org/my-env --base-image custom-base:latest --private
```

After deployment, your space will be available at:
`https://huggingface.co/spaces/<repo-id>`

The deployed space includes:
- **Web Interface** at `/web` - Interactive UI for exploring the environment
- **API Documentation** at `/docs` - Full OpenAPI/Swagger interface
- **Health Check** at `/health` - Container health monitoring
- **WebSocket** at `/ws` - Persistent session endpoint for low-latency interactions

## Environment Details

### Action
**FirstRlProjAction**: Contains a single field
- `message` (str) - The message to echo back

### Observation
**FirstRlProjObservation**: Contains the echo response and metadata
- `echoed_message` (str) - The message echoed back
- `message_length` (int) - Length of the message
- `reward` (float) - Reward based on message length (length × 0.1)
- `done` (bool) - Always False for echo environment
- `metadata` (dict) - Additional info like step count

### Reward
The reward is calculated as: `message_length × 0.1`
- "Hi" → reward: 0.2
- "Hello, World!" → reward: 1.3
- Empty message → reward: 0.0

## Advanced Usage

### Connecting to an Existing Server

If you already have a First Rl Proj environment server running, you can connect directly:

```python
from first_rl_proj import FirstRlProjEnv

# Connect to existing server
first_rl_projenv = FirstRlProjEnv(base_url="<ENV_HTTP_URL_HERE>")

# Use as normal
result = first_rl_projenv.reset()
result = first_rl_projenv.step(FirstRlProjAction(message="Hello!"))
```

Note: When connecting to an existing server, `first_rl_projenv.close()` will NOT stop the server.

### Using the Context Manager

The client supports context manager usage for automatic connection management:

```python
from first_rl_proj import FirstRlProjAction, FirstRlProjEnv

# Connect with context manager (auto-connects and closes)
with FirstRlProjEnv(base_url="http://localhost:8000") as env:
    result = env.reset()
    print(f"Reset: {result.observation.echoed_message}")
    # Multiple steps with low latency
    for msg in ["Hello", "World", "!"]:
        result = env.step(FirstRlProjAction(message=msg))
        print(f"Echoed: {result.observation.echoed_message}")
```

The client uses WebSocket connections for:
- **Lower latency**: No HTTP connection overhead per request
- **Persistent session**: Server maintains your environment state
- **Efficient for episodes**: Better for many sequential steps

### Concurrent WebSocket Sessions

The server supports multiple concurrent WebSocket connections. To enable this,
modify `server/app.py` to use factory mode:

```python
# In server/app.py - use factory mode for concurrent sessions
app = create_app(
    FirstRlProjEnvironment,  # Pass class, not instance
    FirstRlProjAction,
    FirstRlProjObservation,
    max_concurrent_envs=4,  # Allow 4 concurrent sessions
)
```

Then multiple clients can connect simultaneously:

```python
from first_rl_proj import FirstRlProjAction, FirstRlProjEnv
from concurrent.futures import ThreadPoolExecutor

def run_episode(client_id: int):
    with FirstRlProjEnv(base_url="http://localhost:8000") as env:
        result = env.reset()
        for i in range(10):
            result = env.step(FirstRlProjAction(message=f"Client {client_id}, step {i}"))
        return client_id, result.observation.message_length

# Run 4 episodes concurrently
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(run_episode, range(4)))
```

## Development & Testing

### Direct Environment Testing

Test the environment logic directly without starting the HTTP server:

```bash
# From the server directory
python3 server/first_rl_proj_environment.py
```

This verifies that:
- Environment resets correctly
- Step executes actions properly
- State tracking works
- Rewards are calculated correctly

### Running Locally

Run the server locally for development:

```bash
uvicorn server.app:app --reload
```

## Project Structure

```
first_rl_proj/
├── .dockerignore         # Docker build exclusions
├── __init__.py            # Module exports
├── README.md              # This file
├── openenv.yaml           # OpenEnv manifest
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependencies (generated)
├── client.py              # FirstRlProjEnv client
├── models.py              # Action and Observation models
└── server/
    ├── __init__.py        # Server module exports
    ├── first_rl_proj_environment.py  # Core environment logic
    ├── app.py             # FastAPI application (HTTP + WebSocket endpoints)
    └── Dockerfile         # Container image definition
```
