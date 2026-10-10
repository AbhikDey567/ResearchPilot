
from app.agents.planner import plan_research


question = (
    "Compare React, Vue, and Svelte for production applications "
    "in terms of performance, ecosystem, scalability, and hiring demand."
)

queries = plan_research(question)

print("\nGenerated research queries:\n")

for index, query in enumerate(queries, start=1):
    print(f"{index}. {query}")
