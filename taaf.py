# -*- coding: utf-8 -*-
"""TAAF (LLM + KG + State System) - Main Analysis Script

This script provides the core functionality for the Trace Abstraction and Analysis Framework.
It includes functions for loading knowledge graphs, analyzing trace data, and querying LLMs.
"""

#@title Install required libraries
!pip install -q openai

#@title Import libraries and setup
import json
from openai import OpenAI
from google.colab import userdata

# Initialize OpenAI client with secure API key
client = OpenAI(
    api_key=userdata.get("YOUR_API_KEY")  # From Colab secrets
)

#@title Data Loading Functions
def load_kg_data(file_path):
    """Load Knowledge Graph JSON file as raw string"""
    try:
        with open(file_path, 'r') as f:
            return json.dumps(json.load(f)), None
    except Exception as e:
        return None, f"Error loading KG file: {str(e)}"

def load_raw_data(file_path):
    """Load raw text file as string"""
    try:
        with open(file_path, 'r') as f:
            return f.read(), None
    except Exception as e:
        return None, f"Error loading raw file: {str(e)}"

"""#Graph Schema Description"""

KG_SCHEMA = """
Nodes:
  - CPU:
      • cpu_id (string): Unique identifier of the CPU core.
      • busy_time_ns (integer): Total busy time in nanoseconds during the trace interval.
      • num_unique_threads (integer): Number of distinct threads that ran on this CPU.
      • avg_busy_time_per_thread_ns (float): Average busy time per thread on this CPU.
      • total_edge_occurrences (integer): Total count of `used_cpu` edges for this CPU.
      • max_avg_edge_time_ns (integer): Maximum of all `avg_time_per_occurrence_ns` values on this CPU.
      • id (string): Internal node identifier.
  - Thread:
      • thread_id (string): Unique thread identifier.
      • id (string): Internal node identifier.

Edges:
  - used_cpu (Thread → CPU):
      • sum_accumulated_times_ns (integer): Total CPU time accumulated by the thread on that CPU.
      • edge_occurrence_count (integer): Number of times the thread was scheduled on that CPU.
      • time_per_occurrence (list of integers): Duration of each scheduling occurrence ("N/A" for the first occurrence since only cumulative times are available. This is achived by subtracting an specific accumulated time from its previous).
      • avg_time_per_occurrence_ns (float): Average duration per scheduling occurrence.
      • avg_accumulated_edge_time_ns (float): Average of the accumulated times at each occurrence.
      • accumulated_times (list of integers): Cumulative CPU time after each scheduling event.
      • source (string): ID of the Thread node (edge source).
      • target (string): ID of the CPU node (edge target).
"""

#@title Prompt Templates
KG_PROMPT = """
First, think step by step how to use the schema and the provided graph context to answer the question. Outline your reasoning clearly.

{schema}

1. Focus on the question:
   Analyze the provided TraceCompass State System knowledge graph data to answer the question. You must focus on answering this specific question, and your response should be derived exclusively from the provided knowledge graph data.

2. Use the provided data:
   The data you will use is from the TraceCompass State System, specifically in the form of a knowledge graph. Ensure your analysis strictly uses this data for the answer.

3. Leverage your knowledge:
   You may use your understanding of TraceCompass State System analysis methods (such as CPU usage analysis, active thread analysis, and Ease script queries) as context for interpreting the data. Keep in mind that the provided data comes from an Ease script query run on the TraceCompass system.

4. Reason over the graph:
   The data may not always be explicitly present in the graph, and you may need to reason over the graph's structure and relationships to derive the answer. However be careful because it may also mean there is no data in the graph.

5. Explain your reasoning:
   After your step-by-step reasoning above, explain how you arrived at the answer:
     - Which nodes and relationships you used.
     - How specific schema fields informed your conclusion.

6. Answer directly:
   After that, provide a direct, concise final answer to the question as well

7. Question and context:
   Question: {question}
   TraceCompass Knowledge Graph Context:
   {context}

8. Graph feature instructions:
   - The field "sum_accumulated_times_ns" represents the amount of time that the thread has run, accumulated up to its last occurrence on that CPU (i.e., from timestamp 0 until that occurrence).
   - The field "time_per_occurrence" shows, for each occurrence within the query's time interval (e.g., mid timestamp to mid timestamp + 1s), the duration that the thread ran on that CPU. It is essentially calculated as the difference between successive accumulated times.

9. Time interval context:
   The graph data is generated for a specific time interval (e.g., mid timestamp to mid timestamp + 1s), providing insights into thread behavior and CPU usage within that particular period.
"""

RAW_PROMPT = """
First, think step by step through the raw trace data and how it supports your answer. Outline your reasoning clearly.

1. Focus on the question:
   Analyze the provided raw TraceCompass system trace data to answer the question.
2. Use the provided data:
   Rely exclusively on the raw trace measurements in the context.
3. Leverage your knowledge:
   Apply your understanding of TraceCompass State System analysis methods.
4. Reason:
   Walk through which parts of the raw data inform each step of your logic.
5. Answer directly:
   After your reasoning, provide a clear, concise final answer.
6. Explain your reasoning:
   Briefly recap how the raw data supports your answer.

Question: {question}
Raw Data Context: {context}

"""

#@title Analysis Functions
def query_gpt4(prompt):
    """Execute GPT-4o query using modern client syntax"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            # gpt-4.1-nano
            # gpt-4o
            # o4-mini
            # in case of using o4-mini, comment the temprature and use reasoning_effort instead
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            # reasoning_effort="high",  # Options: "low", "medium", "high"
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"API Error: {str(e)}"

def analyze_kg(question, file_path):
    """Knowledge Graph analysis pipeline"""
    context, error = load_kg_data(file_path)
    if error:
        return error

    prompt = KG_PROMPT.format(
        schema=KG_SCHEMA,
        question=question,
        context=context
    )
    return query_gpt4(prompt)

def analyze_raw(question, file_path):
    """Raw data analysis pipeline"""
    context, error = load_raw_data(file_path)
    if error:
        return error

    prompt = RAW_PROMPT.format(
        question=question,
        context=context
    )
    return query_gpt4(prompt)

#@title Main Execution
def full_analysis(question, kg_path="data/mid-10s.json", raw_path="data/mid-10s.txt"):
    """Run complete analysis with both approaches"""
    print(f"\n🔍 Question: {question}")
    print("="*60)

    #print("\n\n📈 Raw Data Analysis:")
    #print(analyze_raw(question, raw_path))

    print("\n📊 Knowledge Graph Analysis:")
    print(analyze_kg(question, kg_path))



# Example usage
if __name__ == "__main__":
    sample_question = '''True or False? CPU 0 has the highest number of unique threads compared to all other CPUs.
    '''

    full_analysis(sample_question)

