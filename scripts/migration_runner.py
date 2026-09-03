#!/usr/bin/env python3
"""Validate and plan reversible SQL migrations for a Duple schema."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


MIGRATION_NAME = re.compile(r"^(?P<version>\d{4})_(?P<name>[a-z0-9_]+)\.sql$")
SECTION_MARKER = "-- DOWN"


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path
    up_sql: str
    down_sql: str


def load_migrations(directory: Path) -> list[Migration]:
    """Load, validate, and sort all reversible migration files."""
    migrations: list[Migration] = []
    seen_versions: set[int] = set()
    for path in sorted(directory.glob("*.sql")):
        match = MIGRATION_NAME.match(path.name)
        if not match:
            raise ValueError(f"invalid migration filename: {path.name}")
        version = int(match.group("version"))
        if version in seen_versions:
            raise ValueError(f"duplicate migration version: {version:04d}")
        seen_versions.add(version)
        text = path.read_text(encoding="utf-8")
        if text.count(SECTION_MARKER) != 1:
            raise ValueError(f"migration must contain exactly one {SECTION_MARKER}: {path.name}")
        up_sql, down_sql = text.split(SECTION_MARKER, 1)
        if not up_sql.strip() or not down_sql.strip():
            raise ValueError(f"migration has an empty up/down section: {path.name}")
        migrations.append(Migration(version, match.group("name"), path, up_sql.strip(), down_sql.strip()))
    return sorted(migrations, key=lambda migration: migration.version)


def render_sql(sql: str, schema: str, duple_id: str) -> str:
    """Render only the placeholders supported by the creator-kit contract."""
    if not re.fullmatch(r"[a-z][a-z0-9_]{1,29}_ai", schema):
        raise ValueError("schema must be a safe Duple schema name ending in _ai")
    if not re.fullmatch(r"[a-z][a-z0-9_]{1,29}", duple_id):
        raise ValueError("duple_id must be lowercase letters, digits, or underscores")
    return sql.replace("__SCHEMA__", schema).replace("__DUPLE_ID__", duple_id)


def plan(migrations: list[Migration], applied: set[int], target: int | None = None) -> list[tuple[str, Migration]]:
    """Return ordered apply/rollback operations without executing SQL."""
    versions = {migration.version for migration in migrations}
    unknown = applied - versions
    if unknown:
        raise ValueError(f"applied versions are absent from manifest: {sorted(unknown)}")
    target = target if target is not None else (migrations[-1].version if migrations else 0)
    if target not in {0, *versions}:
        raise ValueError(f"target version is absent from manifest: {target:04d}")
    operations: list[tuple[str, Migration]] = []
    for migration in migrations:
        if migration.version <= target and migration.version not in applied:
            operations.append(("apply", migration))
    for migration in reversed(migrations):
        if migration.version > target and migration.version in applied:
            operations.append(("rollback", migration))
    return operations


def _parse_versions(raw: str) -> set[int]:
    return {int(value) for value in raw.split(",")} if raw.strip() else set()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("list", "plan"))
    parser.add_argument("--directory", type=Path, default=Path("scripts/migrations"))
    parser.add_argument("--applied", default="", help="comma-separated applied migration versions")
    parser.add_argument("--target", type=int)
    parser.add_argument("--schema", default="tawan_ai")
    parser.add_argument("--duple-id", default="tawan")
    args = parser.parse_args()
    migrations = load_migrations(args.directory)
    if args.command == "list":
        for migration in migrations:
            print(f"{migration.version:04d} {migration.name}")
        return
    for action, migration in plan(migrations, _parse_versions(args.applied), args.target):
        sql = migration.up_sql if action == "apply" else migration.down_sql
        print(f"{action.upper()} {migration.version:04d}_{migration.name}")
        print(render_sql(sql, args.schema, args.duple_id))


if __name__ == "__main__":
    main()
