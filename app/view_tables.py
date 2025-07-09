#!/usr/bin/env python3

import argparse
import psycopg2
from tabulate import tabulate
import shutil
import sys

def truncate(val, width):
    val = str(val)
    return val if len(val) <= width else val[:width - 3] + '...'

def print_help():
    print("""\
Usage: pretty_psql.py -d DBNAME -U USER -t TABLE [options]

Pretty-print a PostgreSQL table with fixed-width ellipsized cells.

Required arguments:
  -d, --database DBNAME     Database name
  -U, --user USER           Username
  -t, --table TABLE         Table name

Optional arguments:
      --host HOST           Host to connect to (default: localhost)
      --port PORT           Port to connect to (default: 5432)
      --width N             Maximum column width (default: 30)
      --limit N             Limit number of rows (default: 20)
  -h, --help                Show this help message and exit

Examples:
  ./pretty_psql.py -d mydb -U myuser -t logs
  ./pretty_psql.py -d mydb -U myuser -t tickets --width 40 --limit 50

Notes:
  • Any field longer than the width limit is truncated and ends with "..."
  • Output is aligned using tabulate and fits standard terminal sizes
""")

def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-d", "--database", help="Database name")
    parser.add_argument("-U", "--user", help="Username")
    parser.add_argument("-t", "--table", help="Table name")
    parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
    parser.add_argument("--port", default=5432, type=int, help="Port (default: 5432)")
    parser.add_argument("--width", type=int, default=30, help="Max width per cell (default: 30)")
    parser.add_argument("--limit", type=int, default=20, help="Max number of rows (default: 20)")
    parser.add_argument("-h", "--help", action="store_true", help="Show help and exit")
    return parser.parse_args()

def main():
    args = parse_args()

    if args.help or not (args.database and args.user and args.table):
        print_help()
        sys.exit(0 if args.help else 1)

    try:
        conn = psycopg2.connect(
            dbname=args.database,
            user=args.user,
            host=args.host,
            port=args.port
        )
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {args.table} LIMIT {args.limit};")
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]

        term_width = shutil.get_terminal_size((80, 20)).columns
        col_width = min(args.width, max(10, term_width // len(colnames)))

        truncated_rows = [
            [truncate(cell, col_width) for cell in row]
            for row in rows
        ]
        print(tabulate(truncated_rows, headers=colnames, tablefmt="grid"))

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

