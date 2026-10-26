"""Terminal application: English → Ollama → SQL → MySQL results."""

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

from database import execute_query, get_schema
from gpt_sql import generate_sql
from sql_validator import validate_sql


def main():
    load_dotenv(Path(__file__).with_name(".env"))

    try:
        if not os.getenv("DB_PASSWORD"):
            raise ValueError("Set DB_PASSWORD in .env first.")

        max_rows = int(os.getenv("MAX_ROWS", "100"))
        timeout_ms = int(os.getenv("QUERY_TIMEOUT_MS", "5000"))
        model_timeout = int(
            os.getenv("OLLAMA_TIMEOUT_SECONDS", "180")
        )

        if not 1 <= max_rows <= 1000:
            raise ValueError("MAX_ROWS must be between 1 and 1000.")

        if not 1 <= timeout_ms <= 60000:
            raise ValueError(
                "QUERY_TIMEOUT_MS must be between 1 and 60000."
            )

        if not 1 <= model_timeout <= 600:
            raise ValueError(
                "OLLAMA_TIMEOUT_SECONDS must be between 1 and 600."
            )

        schema = get_schema()

        print("Natural Language to SQL using Ollama")
        print(
            "Model:",
            os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b"),
        )
        print("Type exit to quit.")

        while True:
            question = input("\nYour question: ").strip()

            if question.lower() == "exit":
                print("Goodbye.")
                break

            if not question:
                continue

            if len(question) > 2000:
                print("Please keep questions under 2000 characters.")
                continue

            try:
                print("\nGenerating SQL...")

                generated = generate_sql(question, schema)

                print("\nGenerated SQL:")
                print(generated)

                # Never execute the model output without validation.
                sql = validate_sql(generated, max_rows)

                print("\nValidated SQL executed:")
                print(sql + ";")

                result = execute_query(
                    sql,
                    max_rows,
                    timeout_ms,
                )

                print("\nQuery Results:")

                if result.empty:
                    print("No matching records.")
                else:
                    print(result.to_string(index=False))

                print(
                    f"\n{len(result)} row(s); "
                    f"maximum {max_rows}."
                )

            except ValueError as exc:
                print(f"Validation error: {exc}")

            except RuntimeError as exc:
                print(f"Model error: {exc}")

            except mysql.connector.Error as exc:
                print(f"MySQL error {exc.errno}: {exc.msg}")

    except (ValueError, KeyError) as exc:
        print(f"Setup error: {exc}")

    except mysql.connector.Error as exc:
        print(f"MySQL setup error {exc.errno}: {exc.msg}")

    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")


if __name__ == "__main__":
    main()