## Building Tool-Calling patterns: OpenAI-compatible with Ollama
- [Course Concept](#course-concept)
    - [Using AI to Learn This Course: The Experiment](#using-ai-to-learn-this-course-the-experiment)
    - [Week 1: Starting from Zero](#week-1-starting-from-zero)
    - [Week 2: The Tool-Calling Journey](#week-2-the-tool-calling-journey)
    - [Week 3: Frontend Wire-up](#week-3-frontend-wire-up)
- [Why Local First?](#why-local-first)
- [A Note on Terminology](#a-note-on-terminology)

---

_Overview_:
This 3-week, 9-chapter course builds a full-stack LLM tool-calling system from scratch.

**Week 1:** Python FastAPI backend with Pydantic validation, OpenAI-compatible tool calling, and SSE streaming. Everything runs locally via Docker and Ollama.

**Week 2:** Continue backend development, focusing on tool-calling patterns, error handling, logging, and validation.

**Week 3:** TypeScript React frontend with shadcn, TailwindCSS, and Zustand for state management.

By the end, you have a complete tool-calling application running on your machine with 5 local models. Every layer is yours to modify.

## Course Concept

### Using AI to Learn This Course: The Experiment

This course experiments with AI-assisted learning: use the provided prompts and RAG context to have AI explain the code to you. How well can today's AI teach tool calling? We'll discover together.

Reality today: Quantized models (which are nearly all local models) aren't great at code understanding, nor is Ollama truly SSE compliant, so it's slow at streaming.

Each chapter will include a directory with all files extracted as plain text with CONTENT and BRANCH labels. You can add these as documents to Ollama for natural language search with a model using `#`. I've included a custom system prompt that will load automatically to assist the models in interpreting them better.

### Week 1: Starting from Zero

Many tutorials assume you have a working development environment. Development setups are personal; if you have one that works, keep using it. This is the setup I used to build this course.

By Friday, you'll watch different models return radically different responses to the same prompt. Some models use `<think>` tags, others don't. This variety made me ask "how could I use these differences?" rather than treating all models as interchangeable.

### Week 2: The Tool-Calling Journey

The OpenAI spec requires two requests for tool calling. When I discovered this, I realized tool-calling implementations hide this gap I never knew about. Knowing this now, I want to build a bridge first with error checking, logging, and validation before allowing the second request through.

Week 2 concludes where our FastAPI endpoints streaming responses need rethinking for frontend integration. I didn't see this coming when I built it, and I want you to experience the same realization (but with the solution ready in the next part!)

### Week 3: Frontend Wire-up

Here's where we build something deployable. A TypeScript React UI that could actually ship to production.

But complexity comes back. Just because you can send SSE events doesn't mean your frontend knows what to do with them. How do you handle tool calls versus chat responses in your UI? We'll tackle all these questions.

---

### Why Local First?

This isn't about avoiding cloud services; cloud models are superior in many ways for tool calling. This course is about understanding the mechanics before you scale.

- **Privacy**: Your prompts, your tools, your data. All on your machine.
- **Cost**: Learn and experiment without burning through credits. Save them for production.
- **Speed**: No network latency during development. GPU-accelerated Ollama runs with millisecond response times. CPU inference in Docker is slower but works the same.
- **Control**: Debug, modify, break, fix. See exactly what's happening.

---

### A Note on Terminology

"Agent" means too many things to be useful here and is avoided intentionally.

To me, "agent" describes systems with different orchestration approaches:

- Computer use: Loop until task completion
- Assistant APIs: Manage conversation threads and state
- Framework agents: Route between chained LLM calls
- Autonomous systems: Recursively decompose and execute

Chapter 5 implements the OpenAI spec's required pattern: tool call request → execution → synthesis to natural language. This is one round, not a loop.

The synthesis pattern is a building block. You could use it to build many of the above architectures, but the pattern itself isn't an agent - it's the two-phase execution the OpenAI spec defines.

Using precise terms clarifies what we're building: tool-calling with synthesis, not autonomous decision loops.