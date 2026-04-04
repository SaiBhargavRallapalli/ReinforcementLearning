#!/usr/bin/env python3
"""
Demo script for Code Output Assessment Environment.

This script demonstrates how to interact with the environment both locally
and from a deployed Hugging Face Space.
"""

import asyncio
from code_assessment_env import CodeAssessmentAction, CodeAssessmentEnv


async def demo_local():
    """Demo using local Docker container."""
    print("=" * 60)
    print("DEMO: Code Output Assessment Environment (Local)")
    print("=" * 60)
    
    # Connect to local Docker container
    env = await CodeAssessmentEnv.from_docker_image("code_assessment_env:latest")
    
    try:
        # Reset environment
        result = await env.reset()
        obs = result.observation
        
        print(f"\n📝 Problem: {obs.problem_description}")
        print(f"🎚️  Difficulty: {obs.difficulty}")
        print(f"🔢 Test Input: {obs.test_case_input}")
        print(f"💬 Feedback: {obs.feedback}")
        
        # Example solutions for common problems
        solutions = {
            "Add two numbers": lambda inp: str(sum(map(int, inp.split(',')))),
            "Reverse a string": lambda inp: inp[::-1],
            "Count vowels": lambda inp: str(sum(1 for c in inp.lower() if c in 'aeiou')),
            "Find maximum": lambda inp: str(max(map(int, inp.split(',')))),
        }
        
        # Try to solve a few problems
        for step in range(1, 6):
            # Simple solver logic
            answer = "0"  # Default answer
            for problem_name, solver in solutions.items():
                if problem_name in obs.problem_description:
                    try:
                        answer = solver(obs.test_case_input)
                    except:
                        answer = "0"
                    break
            
            # Submit answer
            result = await env.step(FirstRlProjAction(answer=answer))
            obs = result.observation
            
            print(f"\n{'=' * 60}")
            print(f"Step {step}:")
            print(f"  Answer submitted: {answer}")
            print(f"  Correct: {'✓' if obs.is_correct else '✗'}")
            print(f"  Grader Score: {obs.partial_credit:.2f}")
            print(f"  Reward: {result.reward:.2f}")
            print(f"  Feedback: {obs.feedback}")
            print(f"  Problems Solved: {obs.problems_solved}")
            print(f"  Current Streak: {obs.current_streak}")
            
            if result.done:
                print("\n🏁 Episode complete!")
                break
            
            # Show next problem
            print(f"\n📝 Next Problem: {obs.problem_description}")
            print(f"🎚️  Difficulty: {obs.difficulty}")
            print(f"🔢 Test Input: {obs.test_case_input}")
        
        # Get final state
        state = await env.state()
        print(f"\n{'=' * 60}")
        print(f"Final Stats:")
        print(f"  Episode ID: {state.episode_id}")
        print(f"  Total Steps: {state.step_count}")
        print(f"  Problems Solved: {obs.problems_solved}")
        
    finally:
        await env.close()
        print("\n✅ Demo complete!\n")


async def demo_remote():
    """Demo using deployed Hugging Face Space."""
    print("=" * 60)
    print("DEMO: Code Output Assessment Environment (Remote)")
    print("=" * 60)
    
    # Connect to HF Space (replace with your actual space URL)
    env = CodeAssessmentEnv(base_url="https://TulasiSankar-code-assessment-env.hf.space")
    
    try:
        result = await env.reset()
        obs = result.observation
        
        print(f"\n📝 Problem: {obs.problem_description}")
        print(f"🎚️  Difficulty: {obs.difficulty}")
        print(f"🔢 Test Input: {obs.test_case_input}")
        
        # Submit a simple answer
        result = await env.step(CodeAssessmentAction(answer="8"))
        obs = result.observation
        
        print(f"\nAnswer submitted: '8'")
        print(f"Correct: {'✓' if obs.is_correct else '✗'}")
        print(f"Reward: {result.reward:.2f}")
        print(f"Feedback: {obs.feedback}")
        
    finally:
        await env.close()
        print("\n✅ Remote demo complete!\n")


async def demo_interactive():
    """Interactive demo where you can input answers."""
    print("=" * 60)
    print("INTERACTIVE DEMO: Solve Problems Yourself!")
    print("=" * 60)
    
    env = await FirstRlProjEnv.from_docker_image("first_rl_proj:latest")
    
    try:
        result = await env.reset()
        obs = result.observation
        
        print(f"\n📚 Starting Code Assessment Challenge!")
        print(f"You have 15 steps to solve as many problems as possible.\n")
        
        for step in range(1, 16):
            print(f"\n{'=' * 60}")
            print(f"Step {step}/15 | Difficulty: {obs.difficulty.upper()}")
            print(f"Problems Solved: {obs.problems_solved} | Streak: {obs.current_streak}")
            print(f"\n📝 Problem: {obs.problem_description}")
            print(f"🔢 Test Input: {obs.test_case_input}")
            
            # Get user input
            answer = input("\n💡 Your answer: ").strip()
            
            if answer.lower() in ['quit', 'exit', 'q']:
                print("Exiting...")
                break
            
            # Submit answer
            result = await env.step(FirstRlProjAction(answer=answer))
            obs = result.observation
            
            # Show results
            print(f"\n{'✓ CORRECT!' if obs.is_correct else '✗ Incorrect'}")
            print(f"Grader Score: {obs.partial_credit:.2f}/1.0")
            print(f"Reward: {result.reward:+.2f}")
            print(f"Feedback: {obs.feedback}")
            
            if result.done:
                print("\n🏁 Episode complete!")
                break
        
        print(f"\n{'=' * 60}")
        print(f"Final Score:")
        print(f"  Problems Solved: {obs.problems_solved}")
        print(f"  Best Streak: {obs.current_streak}")
        
    finally:
        await env.close()
        print("\n✅ Thanks for playing!\n")


async def main():
    """Run all demos."""
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "local":
            await demo_local()
        elif mode == "remote":
            await demo_remote()
        elif mode == "interactive":
            await demo_interactive()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python demo.py [local|remote|interactive]")
    else:
        print("\nAvailable demos:")
        print("  python demo.py local       - Run automated local demo")
        print("  python demo.py remote      - Test HF Space deployment")
        print("  python demo.py interactive - Play interactively")
        print("\nRunning local demo...\n")
        await demo_local()


if __name__ == "__main__":
    asyncio.run(main())
