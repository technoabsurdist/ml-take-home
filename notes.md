Important notes:

- I had to modify the outputs of problem [234B](https://codeforces.com/problemset/problem/234/B) test because the expected outputs in the original files were all "File not found." I'm guessing a problem with the extraction code. I included the tests from the example, so I guess this problem counts as "free" because the solutions are included in the example.

### checkpoint 1

architecture:

<div align="center">
  <img src="resources/agent-workflow.svg" alt="IOI Agent Workflow Diagram" width="800">
</div>

results:

```
Total cost: $0.02
{
  "score": 0.4666666666666667,
  "total_questions": 30,
  "passed_count": 14
}
```

notes:

- experimented with increasing the number of retries - with no effect to results
- it could be useful to have context from previous runs, so model always knows what it's already tried? we currently only store n - 1 run in prompt
-

### checkpoint 2

architecture:

same as above, just passing more context back on failed tests

notes:

Noticed that sometimes LLMs were retrying and repeating previous mistakes. So, implemented a retry mechanism that tracks solution history across multiple attempts (up to 5), providing the LLM with context about all previous solutions and their specific test failures.

results:

```
Total cost: $0.05
{
  "score": 0.53...,
  "total_questions": 30,
  "passed_count": 16
}
```

- we're still spending only about 1.31 seconds per question, when the limit is 30.
  - tested with increasing the number of retries with no visible difference in results

### checkpoint 3

I invested ~20 hours in this project. Initial improvement from 30% to 50% accuracy occurred within the first 5 hours through test extraction and retry mechanisms (checkpoints 1 and 2). The next 15 hours involved a very large number of failed experiments:

1. **Algorithmic approach extraction**: Attempted to categorize problems into algorithmic solution types (Greedy, DP, etc.) via prompt engineering. No improvement in evals.

2. **Model fine-tuning**: Fine-tuned a model on problem descriptions and solution approach tags. Despite accurate categorization, solution accuracy remained at ~50% when giving the model the correct approach to tackle a problem with beforehand (e.g., greedy, dp, etc.).

3. **Test-driven Development**: Enhanced extracted tests to build solutions incrementally from basic to complex tests. No accuracy improvement.

4. **OpenAI paper Implementation**: Read through and applied some insights from OAI's "Competitive Programming with Large Reasoning Models":

   - Implemented self-consistency via multiple generations with majority voting
   - Attempted subtask decomposition with independent verification
   - Applied structured code execution and refinement with multi-turn prompting
   - None of these techniques improved eval performance.

5. **Alpha Code**: Implemented approaches inspired on the Alpha Code paper:
   - Diversity sampling to generate multiple solutions per step
   - Test-time augmentation to force model generalization
   - Meta-prompting for failure analysis and improvement suggestions
   - None of these techniques improved eval performance.

Despite implementing a hybrid approach combining these techniques, improvements remained negligible. Final accuracy stayed at approximately 50%.

Overall, even though I learned a lot by reading through papers and banging my head against the wall for hours trying to figure out how to set up a workflow which would let the model explore various solutions and know which path to go towards, none of the solutions ended up working at the end. The more complex tests almost always failed and none of the strategies I implemented ended up fixing that. If it wasn't finals period this coming week, I would've spent a really long time trying to crack this, because it's actually so fun and I feel like I've learned a LOT from doing it!
