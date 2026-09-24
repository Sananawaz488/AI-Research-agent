"""
Defines the single-agent research crew.

One Agent (a "Senior Research Analyst") with one Tool (DuckDuckGo search)
and one Task (research the topic and write a report).
"""

from crewai import Agent, Task, Crew, Process, LLM
from tools.search_tool import DuckDuckGoSearchTool

DEFAULT_MODEL = "groq/openai/gpt-oss-120b"

# --- Workaround for a known CrewAI + Groq bug -----------------------------
# When CrewAI talks to Groq through LiteLLM, it sometimes adds a
# "cache_breakpoint" field (meant for providers like Anthropic/OpenAI that
# support prompt caching). Groq's API rejects this field with:
#   "property 'cache_breakpoint' is unsupported"
# We patch litellm.completion to strip that field before the request goes
# out. This is safe to remove once CrewAI/LiteLLM fix this upstream.
import litellm

_original_litellm_completion = litellm.completion


def _patched_litellm_completion(*args, **kwargs):
    kwargs.pop("is_litellm", None)
    messages = kwargs.get("messages")
    if messages:
        for m in messages:
            if isinstance(m, dict):
                m.pop("cache_breakpoint", None)
    return _original_litellm_completion(*args, **kwargs)


litellm.completion = _patched_litellm_completion
# ---------------------------------------------------------------------------


def build_crew(topic: str, groq_api_key: str, model: str = DEFAULT_MODEL) -> Crew:
    # CrewAI's LLM class talks to Groq directly - no extra wrapper library needed.
    llm = LLM(model=model, api_key=groq_api_key, temperature=0.3)

    search_tool = DuckDuckGoSearchTool()

    researcher = Agent(
        role="Senior Research Analyst",
        goal=f"Produce a clear, accurate, well-organized report on: {topic}",
        backstory=(
            "You are an experienced research analyst known for turning raw "
            "web search results into concise, well-structured reports. You "
            "always search before writing, cross-check facts when possible, "
            "and clearly flag anything you are unsure about."
        ),
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description=(
            f"Research the topic: '{topic}'.\n\n"
            "Steps:\n"
            "1. Use the DuckDuckGo Search tool at least 2-3 times with "
            "different, specific search queries to gather up-to-date "
            "information (don't rely on a single search).\n"
            "2. Identify the most important facts, trends, numbers, and any "
            "differing viewpoints you find.\n"
            "3. Write a well-structured final report."
        ),
        expected_output=(
            "A markdown report with three sections:\n"
            "## Overview\n(2-3 sentence summary)\n"
            "## Key Findings\n(bullet points with the most important facts)\n"
            "## Sources\n(list the links you used)"
        ),
        agent=researcher,
    )

    return Crew(
        agents=[researcher],
        tasks=[research_task],
        process=Process.sequential,
        verbose=True,
    )


def run_research(topic: str, groq_api_key: str, model: str = DEFAULT_MODEL) -> str:
    crew = build_crew(topic, groq_api_key, model)
    result = crew.kickoff()
    return str(result)
