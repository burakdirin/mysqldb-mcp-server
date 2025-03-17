import json
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import mysql.connector
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP
from mysql.connector import Error as MySQLError
from mysql.connector.cursor import MySQLCursor


class MySQLServerError(Exception):
    """Base exception for MySQL server errors"""
    pass


class ConnectionError(MySQLServerError):
    """Raised when there's an issue with the database connection"""
    pass


class QueryError(MySQLServerError):
    """Raised when there's an issue executing a query"""
    pass


class QueryType(Enum):
    """Enum for different types of SQL queries"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    TRUNCATE = "TRUNCATE"
    USE = "USE"
    SHOW = "SHOW"
    DESCRIBE = "DESCRIBE"

    @classmethod
    def is_write_operation(cls, query_type: str) -> bool:
        """Check if the query type is a write operation"""
        write_operations = {
            cls.INSERT, cls.UPDATE, cls.DELETE,
            cls.CREATE, cls.DROP, cls.ALTER, cls.TRUNCATE
        }
        try:
            return cls(query_type.upper()) in write_operations
        except ValueError:
            return False


@dataclass
class MySQLContext:
    """Context for MySQL connection"""
    host: str
    user: str
    password: str
    database: Optional[str]
    readonly: bool
    connection: Optional[mysql.connector.MySQLConnection] = None

    def ensure_connected(self) -> None:
        """Ensure database connection is available, connecting lazily if needed"""
        if not self.connection or not self.connection.is_connected():
            config = {
                "host": self.host,
                "user": self.user,
                "password": self.password,
            }
            if self.database:
                config["database"] = self.database

            try:
                self.connection = mysql.connector.connect(**config)
            except MySQLError as e:
                raise ConnectionError(
                    f"Failed to connect to database: {str(e)}")


class QueryExecutor:
    """Handles MySQL query execution and result processing"""

    def __init__(self, context: MySQLContext):
        self.context = context

    def _format_datetime(self, value: Any) -> Any:
        """Format datetime values to string"""
        return value.strftime('%Y-%m-%d %H:%M:%S') if hasattr(value, 'strftime') else value

    def _process_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single row of results"""
        return {key: self._format_datetime(value) for key, value in row.items()}

    def _process_results(self, cursor: MySQLCursor) -> Union[List[Dict[str, Any]], Dict[str, int]]:
        """Process query results"""
        if cursor.with_rows:
            results = cursor.fetchall()
            return [self._process_row(row) for row in results]
        return {"affected_rows": cursor.rowcount}

    def execute_single_query(self, query: str) -> Dict[str, Any]:
        """Execute a single query and return results"""
        self.context.ensure_connected()
        cursor = None

        try:
            cursor = self.context.connection.cursor(dictionary=True)
            query_type = QueryType(query.strip().upper().split()[0])

            # Handle readonly mode
            if self.context.readonly and QueryType.is_write_operation(query_type.value):
                raise QueryError(
                    "Server is in read-only mode. Write operations are not allowed.")

            # Handle USE statements
            if query_type == QueryType.USE:
                db_name = query.strip().split()[-1].strip('`').strip()
                self.context.database = db_name
                cursor.execute(query)
                return {"message": f"Switched to database: {db_name}"}

            # Execute query
            cursor.execute(query)
            results = self._process_results(cursor)

            if not self.context.readonly:
                self.context.connection.commit()

            return results

        except MySQLError as e:
            raise QueryError(f"Error executing query: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def execute_multiple_queries(self, query: str) -> List[Dict[str, Any]]:
        """Execute multiple queries and return results"""
        queries = [q.strip() for q in query.split(';') if q.strip()]
        results = []

        for single_query in queries:
            try:
                result = self.execute_single_query(single_query)
                results.append(result)
            except QueryError as e:
                results.append({"error": str(e)})

        return results


def get_env_vars() -> tuple[str, str, str, Optional[str], bool]:
    """Get MySQL connection settings from environment variables

    Returns:
        Tuple of (host, user, password, database, readonly)
    """
    load_dotenv()

    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE")  # Optional
    readonly = os.getenv("MYSQL_READONLY", "0") in ("1", "true", "True")

    return host, user, password, database, readonly


@asynccontextmanager
async def mysql_lifespan(server: FastMCP) -> AsyncIterator[MySQLContext]:
    """MySQL connection lifecycle manager"""
    # Get connection settings from environment variables
    host, user, password, database, readonly = get_env_vars()

    # Initialize context without connecting
    ctx = MySQLContext(
        host=host,
        user=user,
        password=password,
        database=database,
        readonly=readonly,
        connection=None  # Don't connect immediately
    )

    try:
        yield ctx
    finally:
        if ctx.connection and ctx.connection.is_connected():
            ctx.connection.close()


# Create MCP server instance
mcp = FastMCP("MySQL Explorer", lifespan=mysql_lifespan)


def _get_executor(ctx: Context) -> QueryExecutor:
    """Helper function to get QueryExecutor from context"""
    mysql_ctx = ctx.request_context.lifespan_context
    return QueryExecutor(mysql_ctx)


@mcp.tool()
def connect_database(database: str, ctx: Context) -> str:
    """Connect to a specific MySQL database"""
    try:
        executor = _get_executor(ctx)
        result = executor.execute_single_query(f"USE `{database}`")
        return json.dumps(result, indent=2)
    except (ConnectionError, QueryError) as e:
        return str(e)


@mcp.tool()
def execute_query(query: str, ctx: Context) -> str:
    """Execute MySQL queries"""
    try:
        executor = _get_executor(ctx)
        results = executor.execute_multiple_queries(query)

        if len(results) == 1:
            return json.dumps(results[0], indent=2)
        return json.dumps(results, indent=2)
    except (ConnectionError, QueryError) as e:
        return str(e)


if __name__ == "__main__":
    mcp.run()
