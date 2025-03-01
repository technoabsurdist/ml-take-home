
import os
from agent import Agent
from src.llm.openai import OpenAI
from src.llm.core import TextChat, TextUserMessage

from dotenv import load_dotenv
load_dotenv()
# Initialize
llm = OpenAI(model="gpt-4o-mini-2024-07-18", api_key=os.getenv("OPENAI_API_KEY")) 

# Get single response
question = "A permutation of length n is an array consisting of n distinct integers from 1 to n in arbitrary order. For example, [2,3,1,5,4] is a permutation, but [1,2,2] is not a permutation (2 appears twice in the array) and [1,3,4] is also not a permutation (n=3 but there is 4 in the array).\n\nConsider a permutation p of length n, we build a graph of size n using it as follows: \n\n  * For every 1 \u2264 i \u2264 n, find the largest j such that 1 \u2264 j < i and p_j > p_i, and add an undirected edge between node i and node j \n  * For every 1 \u2264 i \u2264 n, find the smallest j such that i < j \u2264 n and p_j > p_i, and add an undirected edge between node i and node j \n\n\n\nIn cases where no such j exists, we make no edges. Also, note that we make edges between the corresponding indices, not the values at those indices.\n\nFor clarity, consider as an example n = 4, and p = [3,1,4,2]; here, the edges of the graph are (1,3),(2,1),(2,3),(4,3).\n\nA permutation p is cyclic if the graph built using p has at least one simple cycle. \n\nGiven n, find the number of cyclic permutations of length n. Since the number may be very large, output it modulo 10^9+7.\n\nPlease refer to the Notes section for the formal definition of a simple cycle\n\nInput\n\nThe first and only line contains a single integer n (3 \u2264 n \u2264 10^6).\n\nOutput\n\nOutput a single integer 0 \u2264 x < 10^9+7, the number of cyclic permutations of length n modulo 10^9+7.\n\nExamples\n\nInput\n\n\n4\n\n\nOutput\n\n\n16\n\nInput\n\n\n583291\n\n\nOutput\n\n\n135712853\n\nNote\n\nThere are 16 cyclic permutations for n = 4. [4,2,1,3] is one such permutation, having a cycle of length four: 4 \u2192 3 \u2192 2 \u2192 1 \u2192 4.\n\nNodes v_1, v_2, \u2026, v_k form a simple cycle if the following conditions hold: \n\n  * k \u2265 3. \n  * v_i \u2260 v_j for any pair of indices i and j. (1 \u2264 i < j \u2264 k) \n  * v_i and v_{i+1} share an edge for all i (1 \u2264 i < k), and v_1 and v_k share an edge. "
chat = TextChat(messages=[TextUserMessage(content=question)])
agent = Agent()
response = agent.predict(llm, question)
print(response)
