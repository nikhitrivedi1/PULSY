# Eval Pipeline for the Agentic RAG System
# Base class + subclasses for Tool Traces, Precision@3 (retriever + agent), and full-episode evaluation.

import sys
from pathlib import Path

# Ensure agentic_interface is on path so Agentic_RAG can be imported
_evals_dir = Path(__file__).resolve().parent
_agentic_interface = _evals_dir.parent
if str(_agentic_interface) not in sys.path:
    sys.path.insert(0, str(_agentic_interface))

from Agentic_RAG.agent import AgenticRAG
from Agentic_RAG.tools import get_Andrew_Huberman_Insights
import json
import os
import asyncio
from openai import OpenAI, AsyncOpenAI
from datetime import datetime
from abc import abstractmethod
from tqdm import tqdm
from config.settings import settings

# ---------------------------------------------------------------------------
# Base: shared state, loaders, parse_case, config, run_evals interface
# ---------------------------------------------------------------------------
class BaseEvalPipeline:
    """Generic parent for eval pipelines. Subclasses implement run_evals() for specific metrics."""

    def __init__(
        self,
        evals_data_path: str = "evals/pulsy_evals_v1.jsonl",
        system_instructions_path: str = "Agentic_RAG/system_prompts/system_instructions_v2.md",
    ):
        self.agent = AgenticRAG()
        self.input_arr = self._load_evals_data(evals_data_path)
        self.user_id = "trivedi.nik"
        self.system_instructions = self._load_system_instructions(system_instructions_path)
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.llm_type = 'gpt-4o'

    def _load_evals_data(self, file_path: str) -> list[dict]:
        rows = []
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def _load_system_instructions(self, file_path: str) -> str:
        with open(file_path, "r") as file:
            return file.read()

    def _parse_case(self, input_case: dict) -> tuple[str, list[str], list[str]]:
        """Extract latest_query, user_history, ai_history from a test case."""
        messages = input_case["messages"]
        latest_query = messages[-1]["content"]
        user_history = []
        ai_history = []
        for msg in messages[:-1]:
            if msg["role"] == "user":
                user_history.append(msg["content"])
            else:
                ai_history.append(msg["content"])
        return latest_query, user_history, ai_history

    def _get_config(self, input_case: dict) -> dict:
        return {
            "configurable": {
                "thread_id": f"eval_{input_case['id']}",
                "model": "smolLM2_1.7B",
            },
            "recursion_limit": 10,
        }
    
    async def run_evals(self, concurrent_evals: int = 5, output_file_path: str = "evals/evals_results.jsonl") -> dict:
        sem = asyncio.Semaphore(concurrent_evals)
        total_correct = 0
        total = 0

        async def bounded(case):
            async with sem:
                return await self.one_case_eval(case)

        tasks = [asyncio.create_task(bounded(c)) for c in self.input_arr]
        with tqdm(total=len(tasks), unit="eval", desc="Eval") as pbar:
            with open(output_file_path, "w") as f:
                for case_result in asyncio.as_completed(tasks):
                    result = await case_result
                    f.write(json.dumps(result) + "\n")
                    f.flush()
                    total_correct += result.get("correct", 0)
                    total += result.get("total", 0)
                    pbar.update(1)
                    acc = total_correct / total if total else 0.0
                    pbar.set_postfix(acc=f"{acc:.2%}")
        print(f"Eval Complete: Total Correct: {total_correct} | Total: {total}")
        print(f"Accuracy: {total_correct / total if total else 0.0}")
        return {
            "total_correct": total_correct,
            "total": total,
        }


    @abstractmethod
    async def one_case_eval(self, input_case: dict) -> dict:
        """Override in subclasses. Return dict with at least 'correct' and 'total' keys."""
        raise NotImplementedError("Subclasses must implement one_case_eval()")


TOOL_TRACES_JUDGE_PROMPT = """You are an impartial judge. Given a user query and a set of tool invocations (name + arguments), determine whether this set of tool calls was correct and appropriate for answering the query.

INPUTS:
- Tools Available: {tools_available}
- Expected processes by query type (use to assess if the tool call aligns with the intended workflow):
{tool_processes}
- Today's date: {today_date} it is acceptable for queries asking about last week or last month data to start from today's date.


USER QUERY: {query}

Full tool trace for this episode (ordered):
{tool_full_trace}

Tool call under evaluation (judge only this call given the trace above): {current_tool_display}

RULES (highest priority first):
R1. If tool_name == "get_Andrew_Huberman_Insights" AND there exists ANY prior tool call in this trace that is a valid data acquisition tool for the query (e.g., get_sleep_data, get_activity_data, etc.), THEN output {{"correct": true, ...}}.
R2. If tool_name == "get_Andrew_Huberman_Insights" AND there is NO prior valid data acquisition tool call, THEN judge it on whether the query asks for general advice (correct) vs user-specific analysis without data (incorrect).
R3. For non-Huberman tools, judge whether the tools and their arguments match the query type/workflow and whether the arguments are reasonable.
R4. It is acceptable for no tool calls to be made if the query is not related to the scope of the tools available and outside the scope of the system instructions mark these cases as correct.


EVALUATION STEPS (follow exactly):
1) Identify the query type from {tool_processes}.
2) Determine which tools are valid data acquisition tools for that query type.
3) Apply RULES R1-R4.
4) Return JSON with correct (true/false) and reason (brief explanation)."""

TOOL_TRACES_JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "correct": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["correct", "reason"],
    "additionalProperties": False,
}

TOOLS_AVAILABLE = """
get_sleep_data(start_date, end_date, user_key): Fetch sleep metrics from Oura Ring API. Retrieves sleep score (0-100), contributors (deep sleep, REM, latency, etc.), and sleep timing/quality. Dates in YYYY-MM-DD.
get_heart_rate_data(start_date, end_date, user_key): Get heart rate data from Oura API between start and end date. Returns max/min BPM, average BPM (workout vs non-workout). Dates in YYYY-MM-DD.
get_stress_data(start_date, end_date, user_key): Fetch stress metrics from Oura Ring API. Daily stress data: day summary, high stress periods (daytime), recovery stress (nighttime). Dates in YYYY-MM-DD.
get_Andrew_Huberman_Insights(query): Search Pinecone VectorDB for relevant insights from Andrew Huberman podcast transcripts. Single arg: query string.
sleep_analysis(start_date, end_date, user_key): Analyze sleep for a date range. Returns bedtime start/end, heart rate avg/low/high, HRV, movement, durations. End date must be greater than start date. Dates in YYYY-MM-DD.
"""

PROCESSES = """
Query Types and Expected Processes (from system instructions). Use these to judge whether tool calls and arguments align with the intended process for the query type. 
Keep in mind that we are evaluating tool calls and arguments not necessarily the actual analysis of the query.

1. Specific Data Query
   When user requests a specific health metric for a specific day:
   - Return only the metric name and score
   - Use get_sleep_data() or get_heart_rate_data() or get_stress_data() or sleep_analysis() for the specific date
   - Include source as <user, device_name, date>

2. Daily Sleep Summary Query
   When user requests general summary of recent scores (e.g. "How did I do last night?", "Daily Summary?"):
   - Fetch all latest available data via get_sleep_data()
   - Identify any concerning scores
   - For concerning scores: use get_Andrew_Huberman_Insights() for potential causes
   - If Huberman response is irrelevant, retry with rephrased query; if still irrelevant, proceed without insight

3. Sleep Trend Analysis Query
   When user requests metric data over time (e.g. "Tell me about my REM sleep from the past week"):
   - Fetch only requested metric data for specified timeframe via get_sleep_data()
   - Identify concerning scores
   - For concerning scores: use get_Andrew_Huberman_Insights()
   - Time conventions: "Last week" = current date minus 7 days, "Last month" = current date minus 1 month

4. Stress Queries
   When users ask about their stress:
   - Fetch stress data via get_stress_data()
   - Analyze Day Summary field to identify high stress days
   - Use get_Andrew_Huberman_Insights() for methods to reduce stress on high stress days
   - If no high stress days: mention user is doing well

5. Heart Rate Queries
   When asked about heart rate:
   - Can only retrieve heart rate for a SINGLE day (too much data for multiple days)
   - Fetch via get_heart_rate_data()
   - Only present known values; skip if unknown
   - Use get_Andrew_Huberman_Insights() for context (e.g. "How to reduce resting heart rate", "correlations between heart rate and sleep")

6. General Check-In
   When asked "how was my day yesterday", "how were my scores on 11/1":
   - Fetch heart rate, sleep scores, stress scores (get_heart_rate_data, get_sleep_data, get_stress_data)
   - Identify any bad scores
   - Use get_Andrew_Huberman_Insights() for insights on how to improve bad scores

7. In-depth Sleep Analysis
   When asked for in-depth sleep analysis (e.g. "Provide an analysis of my sleep from yesterday", "How did my bedtime vary last week?"):
   - Use sleep_analysis() (not just get_sleep_data) for detailed metrics
   - Identify bad scores or noticeable trends
   - Use get_Andrew_Huberman_Insights() for improvement insights
   - Present data in highly structured format separating data from insights
"""


class ToolTracesEval(BaseEvalPipeline):
    """Evaluate tool-calling accuracy via LLM-as-judge. Uses response.get('tool_calls', [])."""
    def __init__(self, eval_data_path: str = "evals/pulsy_evals_v1.jsonl", system_instructions_path: str = "Agentic_RAG/system_prompts/system_instructions_v2.md", unique_eval_path: str = None):
        super().__init__(unique_eval_path or eval_data_path, system_instructions_path)

    async def one_case_eval(self, input_case: dict) -> dict:
        case_id = input_case["id"]
        latest_query, user_history, ai_history = self._parse_case(input_case)
        config = self._get_config(input_case)
        try:
            response = await self.agent.run(
                latest_query, self.user_id, user_history, ai_history,
                eval_mode=True, config=config,
            )
        except Exception as e:
            return {
                "id": case_id,
                "category": input_case.get("category"),
            "source": input_case.get("source"),
            "error": str(e),
            "tool_call_judgments": [],
            "correct": 0,
            "total": 0,
        }
        tool_calls = response.get("tool_calls", [])
        case_correct = 0

        if not tool_calls:
            # If the tool call is empty - we have to evaluate whether the query is related to the scope of the tools available and outside the scope of the system instructions.
            # If it is - we should mark the case as correct.
            # If it is not - we should mark the case as incorrect.
            tool_full_trace_str = "(no tool calls)"
            current_tool_display = "(no tool calls)"
            prompt = TOOL_TRACES_JUDGE_PROMPT.format(
                query=latest_query,
                tool_full_trace=tool_full_trace_str,
                current_tool_display=current_tool_display,
                tool_processes=PROCESSES,
                today_date=datetime.now().strftime("%Y-%m-%d"),
                tools_available=TOOLS_AVAILABLE,
            )

            try:
                judge_response = await self.client.responses.create(
                    model=self.llm_type,
                    input=prompt,
                    text={
                        "format": {
                            "type": "json_schema",
                            "schema": TOOL_TRACES_JUDGE_SCHEMA,
                            "name": "tool_judge",
                            "strict": True,
                        }
                    },
                )
                text = judge_response.output[0].content[0].text
                parsed = json.loads(text)
                if parsed.get("correct"):
                    case_correct = 1
                tool_call_judgment = {
                    "correct": parsed.get("correct", False),
                    "reason": parsed.get("reason", ""),
                }
            except Exception as e:
                tool_call_judgment = {"correct": False, "reason": str(e)}
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "tool_calls": [],
                "tool_call_judgments": [tool_call_judgment],
                "correct": case_correct,
                "total": 1,
            }

        # Build the entire tool trace once (ordered list) for judge context
        trace_entries = []
        for tc in tool_calls:
            name = tc.get("name", "")
            args = tc.get("args") or tc.get("function", {}).get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    pass
            if isinstance(args, dict):
                args_str = json.dumps(args)
            else:
                args_str = str(args)
            trace_entries.append((name, args_str))
        tool_full_trace_str = "\n".join(
            f"{i + 1}. {name}({args_str})" for i, (name, args_str) in enumerate(trace_entries)
        )

        tool_call_judgments = []
        for idx, tc in enumerate(tool_calls):
            name = tc.get("name", "")
            args = tc.get("args") or tc.get("function", {}).get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    pass
            if isinstance(args, dict):
                args_str = json.dumps(args)
            else:
                args_str = str(args)
            current_tool_display = f"Call {idx + 1} of {len(tool_calls)}: {name}({args_str})"
            prompt = TOOL_TRACES_JUDGE_PROMPT.format(
                query=latest_query,
                tool_full_trace=tool_full_trace_str,
                current_tool_display=current_tool_display,
                tool_processes=PROCESSES,
                today_date=datetime.now().strftime("%Y-%m-%d"),
                tools_available=TOOLS_AVAILABLE,
            )
            try:
                judge_response = await self.client.responses.create(
                    model=self.llm_type,
                    input=prompt,
                    text={
                        "format": {
                            "type": "json_schema",
                            "schema": TOOL_TRACES_JUDGE_SCHEMA,
                            "name": "tool_judge",
                            "strict": True,
                        }
                    },
                )
                text = judge_response.output[0].content[0].text
                parsed = json.loads(text)
                if parsed.get("correct"):
                    case_correct += 1
                tool_call_judgments.append({
                    "correct": parsed.get("correct", False),
                    "reason": parsed.get("reason", ""),
                })
            except Exception as e:
                tool_call_judgments.append({"correct": False, "reason": str(e)})
        return {
            "id": case_id,
            "category": input_case.get("category"),
            "source": input_case.get("source"),
            "tool_calls": tool_calls,
            "tool_call_judgments": tool_call_judgments,
            "correct": case_correct,
            "total": len(tool_calls),
        }


# ---------------------------------------------------------------------------
# Subclass 2: Precision@3 via direct retriever (no agent run)
# ---------------------------------------------------------------------------

PRECISION_JUDGE_PROMPT = """You are an impartial judge. Given a user query and a list of retrieved passages (from a knowledge base), determine how many of the passages are relevant to answering the query.

User query: {query}

Passages (one per line, format "Source: ..., Text: ..."):
{passages}

Instructions:
1. Count how many of these passages (0, 1, 2, or 3) are relevant to the query. Set relevant_count to that integer.
2. If relevant_count < 3 (i.e. at least one passage is not relevant or no passages are relevant), you MUST provide a brief reason explaining why the retrieved passages were not fully relevant (e.g. which passage(s) are off-topic and why, or how the query was not well addressed).
3. If all 3 passages are relevant, no need to provide a reason"""

PRECISION_JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "relevant_count": {"type": "integer", "minimum": 0, "maximum": 3},
        "reason": {"type": "string"},
    },
    "required": ["relevant_count", "reason"],
    "additionalProperties": False,
}


def _parse_huberman_passages(content: str) -> list[str]:
    """Parse get_Andrew_Huberman_Insights return string into list of passage strings (one per line)."""
    if not content or not content.strip():
        return []
    lines = [ln.strip() for ln in content.split("\n") if ln.strip()]
    return lines[:3]


class PrecisionAt3RetrieverEval(BaseEvalPipeline):
    """Precision@3 by calling get_Andrew_Huberman_Insights directly; LLM judge relevance."""
    def __init__(self, eval_data_path: str = "evals/pulsy_evals_v1.jsonl", system_instructions_path: str = "Agentic_RAG/system_prompts/system_instructions_v2.md", unique_eval_path: str = None):
        super().__init__(unique_eval_path or eval_data_path, system_instructions_path)

    async def one_case_eval(self, input_case: dict) -> dict:
        case_id = input_case["id"]
        latest_query, _, _ = self._parse_case(input_case)
        try:
            content = get_Andrew_Huberman_Insights(latest_query)
        except Exception as e:
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "error": str(e),
                "precision_at_3": None,
                "correct": 0,
                "total": 0,
                "judge_reason": "",
            }
        passages = _parse_huberman_passages(content)
        k = len(passages) or 1
        if not passages:
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "passages": [],
                "relevant_count": 0,
                "precision_at_3": 0.0,
                "correct": 0,
                "total": 1,
                "judge_reason": "No passages retrieved; judge not invoked.",
            }
        passages_text = "\n".join(passages)
        prompt = PRECISION_JUDGE_PROMPT.format(query=latest_query, passages=passages_text)
        try:
            judge_response = await self.client.responses.create(
                model=self.llm_type,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "schema": PRECISION_JUDGE_SCHEMA,
                        "name": "precision_judge",
                        "strict": True,
                    }
                },
            )
            text = judge_response.output[0].content[0].text
            parsed = json.loads(text)
            relevant_count = min(3, max(0, parsed.get("relevant_count", 0)))
            judge_reason = parsed.get("reason", "")
        except Exception as e:
            relevant_count = 0
            judge_reason = str(e)
        p3 = relevant_count / k
        return {
            "id": case_id,
            "category": input_case.get("category"),
            "source": input_case.get("source"),
            "passages": passages,
            "relevant_count": relevant_count,
            "precision_at_3": p3,
            "correct": relevant_count,
            "total": k,
            "judge_reason": judge_reason,
        }


# ---------------------------------------------------------------------------
# Subclass 3: Precision@3 via AgenticRAG workflow (agent may rewrite query)
# ---------------------------------------------------------------------------

class PrecisionAt3AgentEval(BaseEvalPipeline):
    """Precision@3 on passages the agent actually received from get_Andrew_Huberman_Insights. Uses response.get('tool_results', [])."""
    def __init__(self, eval_data_path: str = "evals/pulsy_evals_v1.jsonl", system_instructions_path: str = "Agentic_RAG/system_prompts/system_instructions_v2.md", unique_eval_path: str = None):
        super().__init__(unique_eval_path or eval_data_path, system_instructions_path)

    async def one_case_eval(self, input_case: dict) -> dict:
        case_id = input_case["id"]
        latest_query, user_history, ai_history = self._parse_case(input_case)
        config = self._get_config(input_case)
        try:
            response = await self.agent.run(
                latest_query, self.user_id, user_history, ai_history,
                eval_mode=True, config=config,
            )
        except Exception as e:
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "error": str(e),
                "precision_at_3": None,
                "correct": 0,
                "total": 0,
                "judge_reason": "",
            }
        tool_results = response.get("tool_results", [])
        huberman_contents = [
            tr["content"] for tr in tool_results
            if tr.get("name") == "get_Andrew_Huberman_Insights"
        ]
        if not huberman_contents:
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "huberman_called": False,
                "precision_at_3": None,
                "correct": 0,
                "total": 0,
                "judge_reason": "",
            }
        content = huberman_contents[0]
        passages = _parse_huberman_passages(content)
        k = len(passages) or 1
        if not passages:
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "huberman_called": True,
                "passages": [],
                "relevant_count": 0,
                "precision_at_3": 0.0,
                "correct": 0,
                "total": 1,
                "judge_reason": "No passages from Huberman tool; judge not invoked.",
            }
        passages_text = "\n".join(passages)
        prompt = PRECISION_JUDGE_PROMPT.format(query=latest_query, passages=passages_text)
        try:
            judge_response = await self.client.responses.create(
                model=self.llm_type,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "schema": PRECISION_JUDGE_SCHEMA,
                        "name": "precision_judge",
                        "strict": True,
                    }
                },
            )
            text = judge_response.output[0].content[0].text
            parsed = json.loads(text)
            relevant_count = min(3, max(0, parsed.get("relevant_count", 0)))
            judge_reason = parsed.get("reason", "")
        except Exception as e:
            relevant_count = 0
            judge_reason = str(e)
        p3 = relevant_count / k
        return {
            "id": case_id,
            "category": input_case.get("category"),
            "source": input_case.get("source"),
            "huberman_called": True,
            "passages": passages,
            "relevant_count": relevant_count,
            "precision_at_3": p3,
            "correct": relevant_count,
            "total": k,
            "judge_reason": judge_reason,
        }


# ---------------------------------------------------------------------------
# Subclass 4: Hit@3 — presence of actual answer in top-3 retrieved chunks (LLM judge)
# ---------------------------------------------------------------------------

HIT_AT_3_JUDGE_PROMPT = """You are an impartial judge. Given a user question and a list of retrieved passages (top 3 from a knowledge base, in rank order), determine whether at least one passage CONTAINS the actual answer or the information needed to correctly answer the question.

User question: {query}

Retrieved passages (top 3, in order):
{passages}

Instructions:
1. Decide if ANY of these passages contain the actual answer (or the key information required to answer) the user's question.
2. Set "hit" to true if at least one passage contains the answer; set "hit" to false if none of the passages contain the answer.
3. Provide a brief reason (e.g., which passage contained the answer, or why none did)."""

HIT_AT_3_JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "hit": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["hit", "reason"],
    "additionalProperties": False,
}


class HitAt3RetrieverEval(BaseEvalPipeline):
    """Hit@3: LLM judge determines if the actual answer is present in the top-3 retrieved chunks."""
    def __init__(self, eval_data_path: str = "evals/pulsy_evals_v1.jsonl", system_instructions_path: str = "Agentic_RAG/system_prompts/system_instructions_v2.md", unique_eval_path: str = None):
        super().__init__(unique_eval_path or eval_data_path, system_instructions_path)

    async def one_case_eval(self, input_case: dict) -> dict:
        case_id = input_case["id"]
        latest_query, _, _ = self._parse_case(input_case)
        try:
            content = get_Andrew_Huberman_Insights(latest_query)
        except Exception as e:
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "error": str(e),
                "hit": False,
                "correct": 0,
                "total": 1,
                "judge_reason": "",
            }
        passages = _parse_huberman_passages(content)
        if not passages:
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "passages": [],
                "hit": False,
                "correct": 0,
                "total": 1,
                "judge_reason": "No passages retrieved; judge not invoked.",
            }
        passages_text = "\n".join(f"Rank {i+1}: {p}" for i, p in enumerate(passages))
        prompt = HIT_AT_3_JUDGE_PROMPT.format(query=latest_query, passages=passages_text)
        try:
            judge_response = await self.client.responses.create(
                model=self.llm_type,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "schema": HIT_AT_3_JUDGE_SCHEMA,
                        "name": "hit_at_3_judge",
                        "strict": True,
                    }
                },
            )
            text = judge_response.output[0].content[0].text
            parsed = json.loads(text)
            hit = bool(parsed.get("hit", False))
            judge_reason = parsed.get("reason", "")
        except Exception as e:
            hit = False
            judge_reason = str(e)
        return {
            "id": case_id,
            "category": input_case.get("category"),
            "source": input_case.get("source"),
            "passages": passages,
            "hit": hit,
            "correct": 1 if hit else 0,
            "total": 1,
            "judge_reason": judge_reason,
        }


# ---------------------------------------------------------------------------
# Subclass 5: MRR (Mean Reciprocal Rank) — score = 1 / rank of first relevant passage
# ---------------------------------------------------------------------------

MRR_JUDGE_PROMPT = """You are an impartial judge. Given a user question and a list of retrieved passages in rank order (1 = first retrieved, 2 = second, 3 = third), determine at which rank the FIRST passage that contains the actual answer (or the information needed to answer the question) appears.

User question: {query}

Retrieved passages (in rank order):
{passages}

Instructions:
1. Consider each passage in order (rank 1, then 2, then 3).
2. Find the FIRST passage that contains the actual answer or the key information required to answer the question.
3. Set "rank" to that position: 1, 2, or 3. If none of the passages contain the answer, set "rank" to 0.
4. Provide a brief reason (e.g., "Passage 2 contains the answer because...")."""

MRR_JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "rank": {"type": "integer", "minimum": 0, "maximum": 3},
        "reason": {"type": "string"},
    },
    "required": ["rank", "reason"],
    "additionalProperties": False,
}


class MRRRetrieverEval(BaseEvalPipeline):
    """MRR: score = 1/rank where rank is the position of the first passage containing the answer (1-indexed)."""
    def __init__(self, eval_data_path: str = "evals/pulsy_evals_v1.jsonl", system_instructions_path: str = "Agentic_RAG/system_prompts/system_instructions_v2.md", unique_eval_path: str = None):
        super().__init__(unique_eval_path or eval_data_path, system_instructions_path)

    async def one_case_eval(self, input_case: dict) -> dict:
        case_id = input_case["id"]
        latest_query, _, _ = self._parse_case(input_case)
        try:
            content = get_Andrew_Huberman_Insights(latest_query)
        except Exception as e:
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "error": str(e),
                "rank": 0,
                "mrr_score": 0.0,
                "correct": 0,
                "total": 1,
                "judge_reason": "",
            }
        passages = _parse_huberman_passages(content)
        if not passages:
            return {
                "id": case_id,
                "category": input_case.get("category"),
                "source": input_case.get("source"),
                "passages": [],
                "rank": 0,
                "mrr_score": 0.0,
                "correct": 0,
                "total": 1,
                "judge_reason": "No passages retrieved; judge not invoked.",
            }
        passages_text = "\n".join(f"Rank {i+1}: {p}" for i, p in enumerate(passages))
        prompt = MRR_JUDGE_PROMPT.format(query=latest_query, passages=passages_text)
        try:
            judge_response = await self.client.responses.create(
                model=self.llm_type,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "schema": MRR_JUDGE_SCHEMA,
                        "name": "mrr_judge",
                        "strict": True,
                    }
                },
            )
            text = judge_response.output[0].content[0].text
            parsed = json.loads(text)
            rank = min(3, max(0, parsed.get("rank", 0)))
            judge_reason = parsed.get("reason", "")
        except Exception as e:
            rank = 0
            judge_reason = str(e)
        mrr_score = (1.0 / rank) if rank > 0 else 0.0
        return {
            "id": case_id,
            "category": input_case.get("category"),
            "source": input_case.get("source"),
            "passages": passages,
            "rank": rank,
            "mrr_score": mrr_score,
            "correct": mrr_score,
            "total": 1,
            "judge_reason": judge_reason,
        }



# ---------------------------------------------------------------------------
# Namespace Grid Search: run existing eval classes across multiple namespaces
# ---------------------------------------------------------------------------

def _load_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


async def run_namespace_grid_search(
    namespace_configs: list[dict],
    evals_data_path: str = "evals/retriever_evals.jsonl",
    concurrent_evals: int = 5,
    output_path: str = "evals/namespace_experiment_results.json",
) -> dict:
    """
    Run Precision@3, Hit@3, and MRR@3 across a list of Pinecone namespace
    configs using the existing eval classes.  For each namespace the function
    patches ``settings.PINECONE_NAMESPACE_1`` and ``PINECONE_EMBEDDING_MODE``
    so that ``get_Andrew_Huberman_Insights`` queries the right index, then
    creates fresh instances of each eval class and calls ``run_evals()``.

    Each config dict must have:
        namespace      – Pinecone namespace name
        embedding_mode – "huggingface" or "pinecone_inference"
    Extra keys (chunk_size, chunk_overlap, …) are carried into the output.

    Returns the full experiment dict and writes it to *output_path* as JSON.
    Per-case JSONL files are also written per namespace/metric for drill-down.
    """
    original_namespace = settings.PINECONE_NAMESPACE_1
    original_embedding_mode = settings.PINECONE_EMBEDDING_MODE

    experiment: dict = {
        "experiment_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "evals_data_path": evals_data_path,
        "namespace_results": [],
        "summary": [],
    }

    try:
        for ns_config in namespace_configs:
            namespace = ns_config["namespace"]
            embedding_mode = ns_config["embedding_mode"]

            settings.PINECONE_NAMESPACE_1 = namespace
            settings.PINECONE_EMBEDDING_MODE = embedding_mode

            print(f"\n{'=' * 60}")
            print(f"  Namespace : {namespace}")
            print(f"  Embedding : {embedding_mode}")
            for k, v in ns_config.items():
                if k not in ("namespace", "embedding_mode"):
                    print(f"  {k:<14}: {v}")
            print(f"{'=' * 60}")

            ns_metrics: dict = {}

            # ── Precision@3 ──────────────────────────────────────────
            p3_file = f"evals/{namespace}_precision_at_3.jsonl"
            p3_eval = PrecisionAt3RetrieverEval(unique_eval_path=evals_data_path)
            p3_agg = await p3_eval.run_evals(
                concurrent_evals=concurrent_evals, output_file_path=p3_file,
            )
            p3_score = (
                p3_agg["total_correct"] / p3_agg["total"]
                if p3_agg["total"] else 0.0
            )
            ns_metrics["precision_at_3"] = {
                "score": round(p3_score, 4),
                "total_relevant": p3_agg["total_correct"],
                "total_judged": p3_agg["total"],
                "details_file": p3_file,
                "per_case": _load_jsonl(p3_file),
            }

            # ── Hit@3 ────────────────────────────────────────────────
            h3_file = f"evals/{namespace}_hit_at_3.jsonl"
            h3_eval = HitAt3RetrieverEval(unique_eval_path=evals_data_path)
            h3_agg = await h3_eval.run_evals(
                concurrent_evals=concurrent_evals, output_file_path=h3_file,
            )
            h3_score = (
                h3_agg["total_correct"] / h3_agg["total"]
                if h3_agg["total"] else 0.0
            )
            ns_metrics["hit_at_3"] = {
                "score": round(h3_score, 4),
                "total_hits": h3_agg["total_correct"],
                "total_cases": h3_agg["total"],
                "details_file": h3_file,
                "per_case": _load_jsonl(h3_file),
            }

            # ── MRR@3 ────────────────────────────────────────────────
            mrr_file = f"evals/{namespace}_mrr_at_3.jsonl"
            mrr_eval = MRRRetrieverEval(unique_eval_path=evals_data_path)
            mrr_agg = await mrr_eval.run_evals(
                concurrent_evals=concurrent_evals, output_file_path=mrr_file,
            )
            mrr_score = (
                mrr_agg["total_correct"] / mrr_agg["total"]
                if mrr_agg["total"] else 0.0
            )
            ns_metrics["mrr_at_3"] = {
                "score": round(mrr_score, 4),
                "total_reciprocal_rank": round(mrr_agg["total_correct"], 4),
                "total_cases": mrr_agg["total"],
                "details_file": mrr_file,
                "per_case": _load_jsonl(mrr_file),
            }

            experiment["namespace_results"].append({
                "config": ns_config,
                "metrics": ns_metrics,
            })
            experiment["summary"].append({
                "namespace": namespace,
                "embedding_mode": embedding_mode,
                **{k: v for k, v in ns_config.items() if k not in ("namespace", "embedding_mode")},
                "precision@3": ns_metrics["precision_at_3"]["score"],
                "hit@3": ns_metrics["hit_at_3"]["score"],
                "mrr@3": ns_metrics["mrr_at_3"]["score"],
            })

            print(
                f"\n  >> {namespace}:  "
                f"precision@3={ns_metrics['precision_at_3']['score']:.4f}  "
                f"hit@3={ns_metrics['hit_at_3']['score']:.4f}  "
                f"mrr@3={ns_metrics['mrr_at_3']['score']:.4f}"
            )

    finally:
        settings.PINECONE_NAMESPACE_1 = original_namespace
        settings.PINECONE_EMBEDDING_MODE = original_embedding_mode

    # ── Summary table ────────────────────────────────────────────────
    print(f"\n{'=' * 80}")
    print("EXPERIMENT SUMMARY")
    print(f"{'=' * 80}")
    header = f"  {'Namespace':<30} {'Precision@3':>12} {'Hit@3':>12} {'MRR@3':>12}"
    print(header)
    print(f"  {'-' * 66}")
    for row in experiment["summary"]:
        print(
            f"  {row['namespace']:<30} "
            f"{row['precision@3']:>12.4f} "
            f"{row['hit@3']:>12.4f} "
            f"{row['mrr@3']:>12.4f}"
        )
    print(f"{'=' * 80}")

    with open(output_path, "w") as f:
        json.dump(experiment, f, indent=2)
    print(f"\nExperiment saved -> {output_path}")

    return experiment


if __name__ == "__main__":
    # Example: Precision@3 Retriever (single namespace, uses current settings)
    # precision_at_3_retriever_eval = PrecisionAt3RetrieverEval(unique_eval_path="evals/retriever_evals.jsonl")
    # out = asyncio.run(precision_at_3_retriever_eval.run_evals(concurrent_evals=5, output_file_path="evals/precision_at_3_retriever_evals_results.jsonl"))

    # Example: Hit@3 Retriever
    # eval_pipeline = HitAt3RetrieverEval(unique_eval_path="evals/retriever_evals.jsonl")
    # out = asyncio.run(eval_pipeline.run_evals(concurrent_evals=5, output_file_path="evals/hit_at_3_retriever_evals_results.jsonl"))

    # Example: MRR Retriever
    # eval_pipeline = MRRRetrieverEval(unique_eval_path="evals/retriever_evals.jsonl")
    # out = asyncio.run(eval_pipeline.run_evals(concurrent_evals=5, output_file_path="evals/mrr_retriever_evals_results.jsonl"))

    # Example: Tool Traces eval
    # eval_pipeline = ToolTracesEval()
    # out = asyncio.run(eval_pipeline.run_evals(concurrent_evals=5, output_file_path="evals/tool_traces_evals_results.jsonl"))

    # ── Namespace Grid Search ────────────────────────────────────────
    # Same configs used in content_aggregation.py GRID_SEARCH_CONFIGS
    NAMESPACE_CONFIGS = [
        {"chunk_size": 1000, "chunk_overlap": 200, "embedding_mode": "huggingface",        "namespace": "hf_cs1000_co200"},
        {"chunk_size": 750,  "chunk_overlap": 150, "embedding_mode": "huggingface",        "namespace": "hf_cs750_co150"},
        {"chunk_size": 500,  "chunk_overlap": 100, "embedding_mode": "huggingface",        "namespace": "hf_cs500_co100"},
        {"chunk_size": 500,  "chunk_overlap": 150, "embedding_mode": "huggingface",        "namespace": "hf_cs500_co150"},
        {"chunk_size": 300,  "chunk_overlap": 75,  "embedding_mode": "huggingface",        "namespace": "hf_cs300_co75"},
        # {"chunk_size": 1000, "chunk_overlap": 200, "embedding_mode": "pinecone_inference", "namespace": "llama_cs1000_co200"},
        # {"chunk_size": 750,  "chunk_overlap": 150, "embedding_mode": "pinecone_inference", "namespace": "llama_cs750_co150"},
        # {"chunk_size": 500,  "chunk_overlap": 100, "embedding_mode": "pinecone_inference", "namespace": "llama_cs500_co100"},
        # {"chunk_size": 500,  "chunk_overlap": 150, "embedding_mode": "pinecone_inference", "namespace": "llama_cs500_co150"},
        # {"chunk_size": 300,  "chunk_overlap": 75,  "embedding_mode": "pinecone_inference", "namespace": "llama_cs300_co75"},
    ]

    experiment = asyncio.run(run_namespace_grid_search(
        namespace_configs=NAMESPACE_CONFIGS,
        evals_data_path="evals/retriever_evals.jsonl",
        concurrent_evals=5,
        output_path="evals/namespace_experiment_results.json",
    ))
