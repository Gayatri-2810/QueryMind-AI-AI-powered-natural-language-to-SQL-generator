# Natural Language to SQL Query Generator Using OpenAI GPT

Minimal terminal application: English question → OpenAI GPT → SQLGlot validation → real MySQL SELECT → Pandas table. No frontend or web framework.

## Requirements

- Windows, VS Code, Python **3.11** and Oracle MySQL Server 8.0/8.4 or newer.
- MySQL Workbench is optional; it is a client and does not replace MySQL Server.
- An OpenAI API key with API billing/credits and access to your selected model. ChatGPT subscription access does not configure this app's API credentials.
- Internet for the API call. Only the schema and question are sent to OpenAI, not query results. Do not put secrets in questions.

## 1. Extract and open

Extract the ZIP to `C:\Projects`. Open the inner `natural-language-to-sql` folder in VS Code (File → Open Folder). Open Terminal → New Terminal. Select **Command Prompt** as the terminal profile for the following commands.

```bat
cd C:\Projects\natural-language-to-sql
py -3.11 --version
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
```

In VS Code press Ctrl+Shift+P → Python: Select Interpreter → choose `.venv\Scripts\python.exe`. If using PowerShell and activation is blocked, activation is optional: run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.\.venv\Scripts\python.exe main.py` directly.

## 2. Configure MySQL

Start your MySQL service through Windows Services. Connect in Workbench with your **existing administrator password**. Creating a Workbench connection does not create a new password or change the server password.

Open `sample_database.sql`. Replace `Choose_A_Strong_Password_123!` with your own password, then execute the entire script once using the lightning-bolt button. It creates 10 fictional employee records and the dedicated reader account. Its grants should show only USAGE and SELECT on `nl_sql_demo.employees`. Never use an account with broader privileges in this app.

Alternative from Command Prompt, if `mysql` is on PATH:

```bat
mysql -u root -p < sample_database.sql
mysql -h localhost -P 3306 -u nl_sql_reader -p -D nl_sql_demo -e "SELECT COUNT(*) FROM employees;"
```

Enter your existing root password for the first command and your chosen reader password for the second. The count should be **10**. If `mysql` is not recognized, use Workbench, or the full path to `mysql.exe` in your MySQL Server `bin` directory.

If the reader user already exists, CREATE USER intentionally fails. Inspect it as administrator with `SHOW GRANTS FOR 'nl_sql_reader'@'localhost';`. Do not reuse an account with extra privileges. On a dedicated demo account you can revoke existing grants and set its password before granting SELECT:

```sql
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'nl_sql_reader'@'localhost';
ALTER USER 'nl_sql_reader'@'localhost' IDENTIFIED BY 'Your_New_Strong_Password';
GRANT SELECT ON nl_sql_demo.employees TO 'nl_sql_reader'@'localhost';
SHOW GRANTS FOR 'nl_sql_reader'@'localhost';
```

If the account has role grants, use a fresh dedicated account instead. Change DB_USER in `.env` to match it. Re-running sample inserts uses INSERT IGNORE and preserves existing employee IDs; it does not reset edited data.

## 3. Configure .env

Open `.env` in VS Code and set:

```dotenv
OPENAI_API_KEY=your_actual_api_key
OPENAI_MODEL=gpt-5-mini
DB_HOST=localhost
DB_PORT=3306
DB_USER=nl_sql_reader
DB_PASSWORD="the_same_password_you_set_in_the_SQL_script"
DB_NAME=nl_sql_demo
MAX_ROWS=100
QUERY_TIMEOUT_MS=5000
```

Create/manage API keys at https://platform.openai.com/api-keys . Keep `.env` private; it is excluded by `.gitignore`. Leave quotes around passwords containing `#` or spaces. Existing operating-system environment variables take precedence over `.env`.

The model is configurable. `gpt-5-mini` supports the Responses API; use another supported model available to your API project if needed. See https://developers.openai.com/api/docs/models/gpt-5-mini and https://developers.openai.com/api/reference/python/resources/responses/methods/create .

## 4. Run

```bat
python main.py
```

Or, without activation:

```bat
.venv\Scripts\python.exe main.py
```

Try:

- Show employees earning more than 50000, ordered by employee_id.
- What is the average salary in each department?
- Show the three highest-paid employees.
- Show employees who joined after January 1, 2024.
- How many employees work in IT?

Type `exit` to quit. Each question is independent; conversational follow-up questions are not supported.

## Example

For "Show employees earning more than 50000, ordered by employee_id", a possible generated query is:

```sql
SELECT * FROM employees WHERE salary > 50000 ORDER BY employee_id;
```

The app prints generated SQL, then the validated SQL with `LIMIT 100`, then an actual Pandas table. With the unchanged sample data, matching IDs are **1, 3, 4, 6, 8, 10**. GPT may choose different equivalent SQL. Invalid or unsupported output is rejected rather than executed.

## Files and flow

- `main.py`: environment settings, terminal loop and error handling.
- `database.py`: connection, actual schema discovery using SHOW COLUMNS, read-only execution and Pandas conversion.
- `gpt_sql.py`: official OpenAI Python SDK, Responses API, configurable model.
- `sql_validator.py`: parses one SELECT, checks table/functions/forbidden features, applies row cap and regenerates SQL.
- `sample_database.sql`: database/table, fictional records and SELECT-only account.
- `.env.example`, `.gitignore`, `requirements.txt`: configuration and dependencies.

## Safeguards and scope

The validator permits only the unqualified `employees` table, a conservative function allowlist and a single SELECT. It rejects modifying statements, multiple statements, comments (including executable MySQL comments), variables, file output, locks, hints, CTEs and set operations. MySQL resolves column names and reports unknown columns normally. This deliberately small demo does not support every valid read-only SQL construct.

The executed SQL is regenerated from the validated AST. Its outer LIMIT is capped at MAX_ROWS (1–1000), and fetching is capped too. MySQL `MAX_EXECUTION_TIME` enforces the configured SELECT timeout (1–60000 ms). Queries run in a read-only transaction with a SELECT-only account. These controls must remain in place; parsing alone does not make arbitrary generated SQL safe. A row cap limits output, not aggregation/join work. This is a local demo, not a production arbitrary-SQL sandbox. Oracle MySQL is required: MariaDB uses different timeout settings.

## Troubleshooting

- **Access denied / 1045:** verify the reader username/password and account host. Setting a Workbench connection password does not reset MySQL's password.
- **Cannot connect / 2003:** start the MySQL service and verify port 3306.
- **Unknown database/table:** execute the sample script with the administrator connection.
- **API authentication:** check the key; do not paste it into chat or source code.
- **API rate limit/quota:** check API billing/credits and retry later.
- **Model not found/access denied:** choose a Responses-compatible model available to your API project in OPENAI_MODEL.
- **Query timed out:** simplify the question or adjust QUERY_TIMEOUT_MS within the allowed range.
- **Unsupported function:** rephrase using ordinary filtering, grouping, sorting and aggregates; the validator intentionally fails closed.
- **Python 3.12 not found:** this project needs **3.11**, not 3.12. Create the environment with `py -3.11 -m venv .venv`.

## Verification performed during packaging

All Python files compile, imports succeed, and 14 validator checks passed (four accepted SELECT examples and ten rejection cases including writes, multiple statements, file access, SLEEP, system tables, comments, locks and variables). Packaging environment: Python 3.12; source syntax was additionally checked against Python 3.11 grammar. No local MySQL Server or user API key was available, so live MySQL/OpenAI end-to-end execution was not performed. Follow the setup above to run the real integrations on your Windows machine.
