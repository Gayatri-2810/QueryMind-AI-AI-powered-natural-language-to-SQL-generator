🧠 QueryMind AI
Ask questions in English. Get SQL queries and real database answers.
QueryMind AI is a terminal-based, AI-powered Natural Language to SQL Query Generator built with Python, Ollama, Qwen2.5-Coder, MySQL, SQLGlot, and Pandas. It translates plain-English questions into MySQL queries, validates them before execution, and displays the results in a readable table.
Runs with a local LLM: No paid OpenAI API credits are required for the demo. Ollama and the model must be installed locally.

✨ Features
- 💬 Natural-language querying: Ask database questions without writing SQL.
- 🧠 Local generative AI: Generate SQL with Qwen2.5-Coder through Ollama.
- 🗄️ Schema-aware prompts: Use database table/column information to guide generation.
- 🛡️ Query safeguards: Validate generated SQL with SQLGlot and reject modifying or multiple statements.
- 🔒 Read-only database access: Use a MySQL account with SELECT privileges only.
- ⏱️ Execution controls: Apply row limits and query timeouts to reduce runaway queries.
- 📊 Readable output: Display returned records with Pandas.
- 🧩 Modular Python design: Separate database access, model integration, validation, and CLI logic.


💡 Example Questions
Try questions such as:
Who are the top 3 highest-paid employees?
What is the average salary in each department?
Which departments have an average salary above 60000?
Find employees earning more than their department's average salary.
Which department has the highest total salary expenditure?
The generated SQL depends on the actual tables and columns in your connected database. These examples assume an employee-oriented sample database.
Example output (illustrative)
Question: Which department has the highest total salary expenditure?

Possible generated SQL (assuming an employees table with department and salary columns):
SELECT department, SUM(salary) AS total_salary
FROM employees
GROUP BY department
ORDER BY total_salary DESC
LIMIT 1;
The application then runs the validated query and prints the result. No sample result values are shown here because they depend on your database.
