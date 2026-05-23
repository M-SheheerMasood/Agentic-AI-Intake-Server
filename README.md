Agentic AI Intake Server
A custom-built, locally hosted Agentic AI backend designed to automate customer intake and quote generation for a 3D printing business.

Architecture & Tech Stack:
  Network Layer: Custom Python TCP socket server handling raw byte-encoding.
  AI Engine: Google Gemini 3.5 Flash via the google-genai SDK.
  Agentic Routing: Built a custom tool-calling switchboard to bypass heavy frameworks (like LangChain) and handle deterministic execution natively.

Core Features:
  Automated Math: Extracts file types and routes .gcode uploads directly to a deterministic Python calculator for instant quoting based on material costs and machine wear.
  Contextual Edge-Case Handling: Pauses the tool-execution loop to educate users on terminology (e.g., "infill") before resuming the intake queue.
  Stateless Memory: Manages continuous conversational memory arrays over an active socket connection.
