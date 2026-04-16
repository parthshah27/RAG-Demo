## What to do when the live hackathon problem arrives

### 1. First, understand the problem completely
- Read the prompt carefully.
- Identify the main requirement:
  - New data ingestion?
  - New domain-specific analysis?
  - New query type?
  - New UI flow?
  - Evaluation or metric requirements?

### 2. Match it to our current architecture
You already have a good structure:
- main.py → API endpoints
- rag.py → RAG pipeline + ChromaDB
- auth.py → JWT/demo auth
- upload.py → dynamic file indexing
- db.py → traditional DB templates
- Chat.js → chat interface
- api.js → API client

So ask yourself:
- Can the new problem be solved by changing config/data only?
- Do we need a new backend route?
- Do we need a new frontend page or component?
- Do we need additional storage (auth/audit/history)?

### 3. Use browser ChatGPT as a design assistant
Browser ChatGPT won’t know your repo, so give it a concise summary:
- “I have a FastAPI backend with a RAG module using ChromaDB, a simple JWT login, and a React chat frontend.”
- Mention specifically which files exist.
- Then paste the new problem statement and ask for:
  - architecture suggestions
  - targeted code snippets
  - how to modify rag.py or main.py
  - how to update the frontend to support the new flow

### 4. Ask ChatGPT for targeted help, not a full rewrite
Good prompt style:
- “Given this architecture, how should I implement feature X in rag.py?”
- “What is the smallest change to support CSV upload for new problem Y?”
- “How can I extend the existing `/ask` flow to include feature Z?”

Bad prompt style:
- “Write the whole solution from scratch.”
- “Replace my app with a new app.”

### 5. Practical implementation plan
1. Identify the exact new requirement.
2. Decide if it is:
   - data/config only
   - backend-only
   - frontend-only
   - both backend and frontend
3. If it’s data-driven:
   - add files under data
   - update `backend/config/...` or `CONFIG_FILE`
4. If it’s a new backend feature:
   - extend main.py or rag.py
   - keep the change limited and modular
5. If it’s UI-related:
   - update Chat.js, or add a new page/component
   - reuse existing API client in api.js
6. Test locally quickly before moving on

### 6. How to integrate new solution into this repo
Use the existing code as a baseline:
- For answers and retrieval: modify rag.py
- For new endpoint: add route in main.py
- For uploads/ingestion: use upload.py
- For auth or logging: use db.py templates if needed
- For frontend: update Chat.js and maybe api.js

### 7. What to tell browser ChatGPT
Give it:
- current architecture summary
- exact files and their roles
- the live problem statement
- what you already want to reuse

Example:
- “I have a FastAPI app with a ChromaDB vector search in rag.py. I want to add X. What is the minimal change to the existing approach?”

### 8. Final advice
- Use ChatGPT for planning, pseudocode, and edge-case checks.
- Implement in VS Code yourself.
- Keep changes small and test each step.
- Use the docs we created (DATABASE_CHOICES.md, LIVE_EVENT_AUDIT.md) to justify architecture decisions if needed.

---

## Short answer
Use browser ChatGPT as a consultant, not a black-box solver:
1. Tell it the repo structure and current modules.
2. Give it the live problem.
3. Ask for targeted code changes.
4. Implement those changes in `backend/app/...` and `frontend/src/...`.
5. Keep it modular and confirm with local tests.

That is the safest and best way to get an answer and then apply it cleanly to your project.