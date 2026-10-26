"""Conservative SELECT-only validation for this small employee demo."""
import re
import sqlglot
from sqlglot import exp

SAFE_FUNCTIONS = {
    'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ROUND', 'ABS', 'LOWER', 'UPPER',
    'LENGTH', 'CHAR_LENGTH', 'COALESCE', 'IFNULL', 'NULLIF', 'YEAR', 'MONTH',
    'DAY', 'CURRENT_DATE', 'CURDATE', 'DATEDIFF', 'DATE', 'CAST', 'CONCAT',
}


def validate_sql(sql: str, max_rows: int = 100) -> str:
    if not 1 <= max_rows <= 1000:
        raise ValueError('MAX_ROWS must be between 1 and 1000.')
    if not sql or len(sql) > 10000:
        raise ValueError('Empty or oversized SQL response.')
    # Comments can carry MySQL executable directives; reject them before parsing.
    if any(token in sql for token in ('/*', '--', '#', '@', ':=')):
        raise ValueError('Comments and variables are not allowed.')
    try:
        statements = sqlglot.parse(sql, read='mysql')
    except sqlglot.errors.ParseError as exc:
        raise ValueError('GPT returned invalid MySQL SQL.') from exc
    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise ValueError('Exactly one SELECT query is required.')
    tree = statements[0]
    # Intentionally omit CTEs, unions, locks, hints and SELECT INTO in this demo.
    forbidden = {'Into', 'Lock', 'Hint', 'With', 'Union', 'Intersect', 'Except',
                 'Command', 'Insert', 'Update', 'Delete', 'Create', 'Drop', 'Alter'}
    if any(type(node).__name__ in forbidden for node in tree.walk()):
        raise ValueError('Only simple read-only SELECT queries are supported.')
    tables = list(tree.find_all(exp.Table))
    if not tables or any(t.name.lower() != 'employees' or t.db or t.catalog for t in tables):
        raise ValueError('Queries may only read the local employees table.')
    for function in tree.find_all(exp.Func):
        name = function.name if isinstance(function, exp.Anonymous) else function.sql_name()
        if name.upper() not in SAFE_FUNCTIONS:
            raise ValueError(f'Unsupported SQL function: {name}')
    for select in tree.find_all(exp.Select):
        limit = select.args.get('limit')
        if limit:
            value = limit.expression
            if not isinstance(value, exp.Literal) or not re.fullmatch(r'\d+', str(value.this)):
                raise ValueError('LIMIT must be a non-negative integer.')
    limit = tree.args.get('limit')
    requested = int(limit.expression.this) if limit else max_rows
    tree = tree.limit(min(requested, max_rows), copy=False)
    # Regenerate SQL from the validated tree; never execute the original text.
    return tree.sql(dialect='mysql')
