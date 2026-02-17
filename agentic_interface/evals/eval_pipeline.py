# Eval Pipeline for the Agentic RAG System
# Base class + subclasses for Tool Traces, Precision@3 (retriever + agent), and full-episode evaluation.

from Agentic_RAG.agent import AgenticRAG
from Agentic_RAG.tools import get_Andrew_Huberman_Insights
import json
import os
import asyncio
from openai import OpenAI, AsyncOpenAI
from datetime import datetime
from abc import abstractmethod
from tqdm import tqdm

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
        super().__init__(eval_data_path, system_instructions_path)
        if unique_eval_path:
            self.eval_data_path = unique_eval_path

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
                "tool_call_judgments": tool_call_judgment,
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

How many of these passages are relevant to the query? Reply with an integer 0, 1, 2, or 3 (number of relevant passages)."""

PRECISION_JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "relevant_count": {"type": "integer", "minimum": 0, "maximum": 3},
    },
    "required": ["relevant_count"],
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
        super().__init__(eval_data_path, system_instructions_path)
        if unique_eval_path:
            self.eval_data_path = unique_eval_path

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
        except Exception as e:
            relevant_count = 0
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
        }


# ---------------------------------------------------------------------------
# Subclass 3: Precision@3 via AgenticRAG workflow (agent may rewrite query)
# ---------------------------------------------------------------------------

class PrecisionAt3AgentEval(BaseEvalPipeline):
    """Precision@3 on passages the agent actually received from get_Andrew_Huberman_Insights. Uses response.get('tool_results', [])."""
    def __init__(self, eval_data_path: str = "evals/pulsy_evals_v1.jsonl", system_instructions_path: str = "Agentic_RAG/system_prompts/system_instructions_v2.md", unique_eval_path: str = None):
        super().__init__(eval_data_path, system_instructions_path)
        if unique_eval_path:
            self.eval_data_path = unique_eval_path

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
        except Exception as e:
            relevant_count = 0
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
        }


# ---------------------------------------------------------------------------
# Subclass 4: Full-episode evaluation (PASS/FAIL per case)
# ---------------------------------------------------------------------------

EPISODE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "STATUS": {"type": "string", "enum": ["PASS", "FAIL"]},
        "COMMENTS": {"type": "string"},
        "ERROR_CATEGORY": {
            "type": "string",
            "enum": [
                "incorrect tool calling",
                "answer generation",
                "non-compliant workflow",
                "inventing information",
                "improper formatting",
                "other",
            ],
        },
    },
    "required": ["STATUS", "COMMENTS", "ERROR_CATEGORY"],
    "additionalProperties": False,
}


class EpisodeEval(BaseEvalPipeline):
    """Full-episode evaluation: run agent, grade with LLM judge (PASS/FAIL, COMMENTS, ERROR_CATEGORY)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("evals/eval_prompt.md", "r") as f:
            self.grade_prompt = f.read()
        self.response_schema = EPISODE_RESPONSE_SCHEMA

    def _grade_evals(self, input_example: str) -> dict:
        response = self.client.responses.create(
            model=self.llm_type,
            instructions=self.grade_prompt,
            input=f"System Instructions: {self.system_instructions}\n{input_example}",
            text={
                "format": {
                    "type": "json_schema",
                    "schema": self.response_schema,
                    "name": "eval_response",
                    "strict": True,
                }
            },
        )
        try:
            results = json.loads(response.output[0].content[0].text)
            return {
                "STATUS": results["STATUS"],
                "COMMENT": results["COMMENTS"],
                "ERROR_CATEGORY": results["ERROR_CATEGORY"],
            }
        except Exception as e:
            return {"STATUS": "UNKNOWN", "COMMENT": str(e), "ERROR_CATEGORY": "unknown"}

    async def one_case_eval(self, input_case: dict) -> dict:
        case_id = input_case["id"]
        latest_query, user_history, ai_history = self._parse_case(input_case)
        config = self._get_config(input_case)
        try:
            response = await self.agent.run(
                latest_query, self.user_id, user_history, ai_history,
                eval_mode=True, config=config,
            )
            tool_calls = response.get("tool_calls", [])
            input_example = (
                f"Query: {latest_query}\n"
                f"Tool Calls: {tool_calls}\n"
                f"Response: {response['response']}"
            )
        except Exception as e:
            return {
                "id": case_id,
                "STATUS": "FAIL",
                "CATEGORY": input_case.get("category"),
                "SOURCE": input_case.get("source"),
                "COMMENT": str(e),
                "ERROR_CATEGORY": "unknown",
                "correct": 0,
                "total": 1,
            }
        graded = await self._grade_evals(input_example)
        graded["id"] = case_id
        graded["CATEGORY"] = input_case.get("category")
        graded["SOURCE"] = input_case.get("source")
        graded["correct"] = 1 if graded["STATUS"] == "PASS" else 0
        graded["total"] = 1
        return graded


if __name__ == "__main__":
    # Example: Precision@3 Retriever
    # eval_pipeline = PrecisionAt3RetrieverEval(unique_eval_path="evals/retriever_evals.jsonl")
    # out = asyncio.run(eval_pipeline.run_evals(concurrent_evals=5, output_file_path="evals/precision_at_3_retriever_evals_results.jsonl"))

    # Example: Tool Traces eval
    eval_pipeline = ToolTracesEval()
    out = asyncio.run(eval_pipeline.run_evals(concurrent_evals=5, output_file_path="evals/tool_traces_evals_results.jsonl"))
