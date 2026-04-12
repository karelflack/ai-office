"""
Tests for the ai-office core/ module.

All tests use tmp_path and monkeypatch to redirect filesystem roots so they
never touch the real projects/, tasks/, runs/, or memory/ directories.

Patching strategy:
  - core.tasks.BASE_DIR  — used by _get_task_dirs() for project-scoped paths
  - core.projects.BASE_DIR + core.projects.PROJECTS_DIR — used by every
    projects.py function
  - core.memory.RUNS_DIR + core.memory.MEMORY_FILE — used by memory.py
"""

import json
import sys
from pathlib import Path
from datetime import date

import pytest

# Ensure the repo root is on sys.path so "import core.*" works when pytest
# is invoked from any working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import core.tasks as tasks_mod
import core.projects as projects_mod
import core.memory as memory_mod
import core.agents as agents_mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project_dirs(base: Path, slug: str) -> dict:
    """Create the four task bucket directories for a project and return them."""
    dirs = {
        "backlog":   base / "projects" / slug / "tasks" / "backlog",
        "active":    base / "projects" / slug / "tasks" / "active",
        "completed": base / "projects" / slug / "tasks" / "completed",
        "failed":    base / "projects" / slug / "tasks" / "failed",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def _task_file(content_lines: list[str]) -> str:
    """Join lines with newlines."""
    return "\n".join(content_lines)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def fake_base(tmp_path: Path) -> Path:
    """Return a tmp directory that will serve as the fake BASE_DIR."""
    return tmp_path


@pytest.fixture()
def patched_tasks(fake_base: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect core.tasks so it operates inside fake_base."""
    monkeypatch.setattr(tasks_mod, "BASE_DIR", fake_base)
    tasks_dir = fake_base / "tasks"
    # Also patch the module-level TASK_DIRS constant (used by non-project paths)
    monkeypatch.setattr(tasks_mod, "TASKS_DIR", tasks_dir)
    monkeypatch.setattr(tasks_mod, "TASK_DIRS", {
        "backlog":   tasks_dir / "backlog",
        "active":    tasks_dir / "active",
        "completed": tasks_dir / "completed",
    })
    return fake_base


@pytest.fixture()
def patched_projects(fake_base: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect core.projects so it operates inside fake_base."""
    monkeypatch.setattr(projects_mod, "BASE_DIR", fake_base)
    monkeypatch.setattr(projects_mod, "PROJECTS_DIR", fake_base / "projects")
    # projects.py calls core.tasks.slugify — no patching needed there (pure fn)
    return fake_base


@pytest.fixture()
def patched_memory(fake_base: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect core.memory so it operates inside fake_base."""
    memory_dir = fake_base / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    memory_file = memory_dir / "team_memory.json"
    memory_file.write_text(json.dumps({"agents": {}, "projects": {}}), encoding="utf-8")

    monkeypatch.setattr(memory_mod, "BASE_DIR", fake_base)
    monkeypatch.setattr(memory_mod, "MEMORY_FILE", memory_file)
    monkeypatch.setattr(memory_mod, "RUNS_DIR", fake_base / "runs")
    return fake_base


# ---------------------------------------------------------------------------
# 1. slugify()
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_normal_string(self):
        assert tasks_mod.slugify("Hello World") == "hello-world"

    def test_special_chars_stripped(self):
        # Non-alphanumeric/space/underscore/dash chars are stripped
        assert tasks_mod.slugify("Foo & Bar! (2024)") == "foo-bar-2024"

    def test_spaces_become_dashes(self):
        assert tasks_mod.slugify("one two three") == "one-two-three"

    def test_multiple_spaces_collapse(self):
        assert tasks_mod.slugify("a   b") == "a-b"

    def test_underscores_become_dashes(self):
        assert tasks_mod.slugify("hello_world") == "hello-world"

    def test_leading_trailing_dashes_stripped(self):
        # Special chars at boundaries become dashes that must be stripped
        assert tasks_mod.slugify("!hello world!") == "hello-world"

    def test_already_slug(self):
        assert tasks_mod.slugify("my-slug") == "my-slug"

    def test_numbers_preserved(self):
        assert tasks_mod.slugify("Version 2.0") == "version-20"

    def test_empty_string(self):
        assert tasks_mod.slugify("") == ""


# ---------------------------------------------------------------------------
# 2. create_project()
# ---------------------------------------------------------------------------

class TestCreateProject:
    def test_returns_slug(self, patched_projects):
        slug = projects_mod.create_project("My Project")
        assert slug == "my-project"

    def test_project_json_exists(self, patched_projects):
        slug = projects_mod.create_project("Alpha")
        p = patched_projects / "projects" / slug / "project.json"
        assert p.exists()
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["slug"] == slug
        assert data["name"] == "Alpha"

    def test_task_subdirs_created(self, patched_projects):
        slug = projects_mod.create_project("Beta")
        base = patched_projects / "projects" / slug / "tasks"
        for bucket in ("backlog", "active", "completed", "failed"):
            assert (base / bucket).is_dir(), f"missing tasks/{bucket}"

    def test_memory_dir_created(self, patched_projects):
        slug = projects_mod.create_project("Gamma")
        assert (patched_projects / "projects" / slug / "memory").is_dir()

    def test_decisions_dir_created(self, patched_projects):
        slug = projects_mod.create_project("Delta")
        assert (patched_projects / "projects" / slug / "memory" / "decisions").is_dir()

    def test_five_category_decision_files(self, patched_projects):
        slug = projects_mod.create_project("Epsilon")
        decisions_dir = patched_projects / "projects" / slug / "memory" / "decisions"
        expected = {"architecture.md", "implementation.md", "compliance.md", "brand.md", "strategy.md"}
        actual = {f.name for f in decisions_dir.glob("*.md")}
        assert actual == expected

    def test_decision_files_have_header(self, patched_projects):
        slug = projects_mod.create_project("Zeta")
        decisions_dir = patched_projects / "projects" / slug / "memory" / "decisions"
        arch = (decisions_dir / "architecture.md").read_text(encoding="utf-8")
        assert arch.startswith("# Architecture Decisions")

    def test_project_memory_json_created(self, patched_projects):
        slug = projects_mod.create_project("Eta")
        mem = patched_projects / "projects" / slug / "memory" / "project_memory.json"
        assert mem.exists()
        data = json.loads(mem.read_text(encoding="utf-8"))
        assert data["slug"] == slug

    def test_raises_on_duplicate(self, patched_projects):
        projects_mod.create_project("Theta")
        with pytest.raises(ValueError, match="already exists"):
            projects_mod.create_project("Theta")

    def test_description_stored(self, patched_projects):
        slug = projects_mod.create_project("Iota", description="A test project")
        p = patched_projects / "projects" / slug / "project.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["description"] == "A test project"

    def test_output_dirs_created(self, patched_projects):
        slug = projects_mod.create_project("Kappa")
        output_base = patched_projects / "output" / slug
        assert output_base.is_dir()
        # At least one known subdir must exist
        assert (output_base / "architecture").is_dir()


# ---------------------------------------------------------------------------
# 3. project_task_dirs()
# ---------------------------------------------------------------------------

class TestProjectTaskDirs:
    def test_returns_four_buckets(self, patched_projects):
        result = projects_mod.project_task_dirs("my-proj")
        assert set(result.keys()) == {"backlog", "active", "completed", "failed"}

    def test_paths_under_project(self, patched_projects):
        result = projects_mod.project_task_dirs("my-proj")
        for bucket, path in result.items():
            # Each path must be inside projects/my-proj/tasks/<bucket>
            assert str(path).endswith(f"tasks/{bucket}")
            assert "my-proj" in str(path)


# ---------------------------------------------------------------------------
# 4. list_projects()
# ---------------------------------------------------------------------------

class TestListProjects:
    def test_empty_when_dir_missing(self, patched_projects):
        # PROJECTS_DIR does not exist yet
        assert projects_mod.list_projects() == []

    def test_empty_when_dir_exists_but_no_projects(self, patched_projects):
        (patched_projects / "projects").mkdir(parents=True, exist_ok=True)
        assert projects_mod.list_projects() == []

    def test_returns_created_projects(self, patched_projects):
        projects_mod.create_project("Apple")
        projects_mod.create_project("Banana")
        result = projects_mod.list_projects()
        slugs = [p["slug"] for p in result]
        assert "apple" in slugs
        assert "banana" in slugs

    def test_sorted_alphabetically(self, patched_projects):
        projects_mod.create_project("Zebra")
        projects_mod.create_project("Ant")
        projects_mod.create_project("Mango")
        result = projects_mod.list_projects()
        slugs = [p["slug"] for p in result]
        assert slugs == sorted(slugs)

    def test_dirs_without_project_json_are_skipped(self, patched_projects):
        (patched_projects / "projects" / "orphan").mkdir(parents=True)
        result = projects_mod.list_projects()
        assert all(p.get("slug") != "orphan" for p in result)


# ---------------------------------------------------------------------------
# 5. create_task()
# ---------------------------------------------------------------------------

class TestCreateTask:
    def test_creates_file_in_backlog(self, patched_tasks):
        slug = "my-proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Do Something", "arve", project_slug=slug)
        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        assert (backlog / filename).exists()

    def test_filename_contains_title_slug(self, patched_tasks):
        slug = "my-proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Build API", "bjorn", project_slug=slug)
        assert "build-api" in filename

    def test_filename_starts_with_date(self, patched_tasks):
        slug = "my-proj"
        _make_project_dirs(patched_tasks, slug)
        today = date.today().isoformat()
        filename = tasks_mod.create_task("Build API", "bjorn", project_slug=slug)
        assert filename.startswith(today)

    def test_content_has_agent_field(self, patched_tasks):
        slug = "my-proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Fix Bug", "arve", project_slug=slug)
        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        content = (backlog / filename).read_text(encoding="utf-8")
        assert "**Agent:** arve" in content

    def test_content_has_status_backlog(self, patched_tasks):
        slug = "my-proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Fix Bug", "arve", project_slug=slug)
        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        content = (backlog / filename).read_text(encoding="utf-8")
        assert "**Status:** backlog" in content

    def test_content_includes_description(self, patched_tasks):
        slug = "my-proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Fix Bug", "arve", description="Detailed desc", project_slug=slug)
        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        content = (backlog / filename).read_text(encoding="utf-8")
        assert "Detailed desc" in content

    def test_depends_on_written(self, patched_tasks):
        slug = "my-proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task(
            "Follow-up", "dag", depends_on="2026-01-01-upstream.md", project_slug=slug
        )
        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        content = (backlog / filename).read_text(encoding="utf-8")
        assert "**depends_on:** 2026-01-01-upstream.md" in content

    def test_model_field_written_when_provided(self, patched_tasks):
        slug = "my-proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("LLM Task", "arve", model="claude-opus-4", project_slug=slug)
        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        content = (backlog / filename).read_text(encoding="utf-8")
        assert "**Model:** claude-opus-4" in content

    def test_model_field_absent_when_not_provided(self, patched_tasks):
        slug = "my-proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Plain Task", "arve", project_slug=slug)
        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        content = (backlog / filename).read_text(encoding="utf-8")
        assert "**Model:**" not in content


# ---------------------------------------------------------------------------
# 6. assign_task()
# ---------------------------------------------------------------------------

class TestAssignTask:
    def _create_task(self, base: Path, slug: str, title: str = "My Task", agent: str = "arve") -> str:
        dirs = _make_project_dirs(base, slug)
        filename = tasks_mod.create_task(title, agent, project_slug=slug)
        return filename

    def test_moves_to_active(self, patched_tasks):
        slug = "proj"
        filename = self._create_task(patched_tasks, slug)
        tasks_mod.assign_task(filename, "bjorn", project_slug=slug)
        active = patched_tasks / "projects" / slug / "tasks" / "active"
        assert (active / filename).exists()

    def test_removes_from_backlog(self, patched_tasks):
        slug = "proj"
        filename = self._create_task(patched_tasks, slug)
        tasks_mod.assign_task(filename, "bjorn", project_slug=slug)
        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        assert not (backlog / filename).exists()

    def test_updates_agent_field(self, patched_tasks):
        slug = "proj"
        filename = self._create_task(patched_tasks, slug, agent="arve")
        tasks_mod.assign_task(filename, "bjorn", project_slug=slug)
        active = patched_tasks / "projects" / slug / "tasks" / "active"
        content = (active / filename).read_text(encoding="utf-8")
        assert "**Agent:** bjorn" in content

    def test_updates_status_to_active(self, patched_tasks):
        slug = "proj"
        filename = self._create_task(patched_tasks, slug)
        tasks_mod.assign_task(filename, "bjorn", project_slug=slug)
        active = patched_tasks / "projects" / slug / "tasks" / "active"
        content = (active / filename).read_text(encoding="utf-8")
        assert "**Status:** active" in content

    def test_raises_if_task_not_found(self, patched_tasks):
        _make_project_dirs(patched_tasks, "proj")
        with pytest.raises(FileNotFoundError):
            tasks_mod.assign_task("nonexistent.md", "arve", project_slug="proj")


# ---------------------------------------------------------------------------
# 7. complete_task()
# ---------------------------------------------------------------------------

class TestCompleteTask:
    def test_moves_to_completed(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Finish Me", "arve", project_slug=slug)
        tasks_mod.assign_task(filename, "arve", project_slug=slug)
        tasks_mod.complete_task(filename, project_slug=slug)
        completed = patched_tasks / "projects" / slug / "tasks" / "completed"
        assert (completed / filename).exists()

    def test_removes_from_active(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Finish Me", "arve", project_slug=slug)
        tasks_mod.assign_task(filename, "arve", project_slug=slug)
        tasks_mod.complete_task(filename, project_slug=slug)
        active = patched_tasks / "projects" / slug / "tasks" / "active"
        assert not (active / filename).exists()

    def test_updates_status_to_completed(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Finish Me", "arve", project_slug=slug)
        tasks_mod.assign_task(filename, "arve", project_slug=slug)
        tasks_mod.complete_task(filename, project_slug=slug)
        completed = patched_tasks / "projects" / slug / "tasks" / "completed"
        content = (completed / filename).read_text(encoding="utf-8")
        assert "**Status:** completed" in content

    def test_raises_if_task_not_found(self, patched_tasks):
        _make_project_dirs(patched_tasks, "proj")
        with pytest.raises(FileNotFoundError):
            tasks_mod.complete_task("ghost.md", project_slug="proj")


# ---------------------------------------------------------------------------
# 8. fail_task()
# ---------------------------------------------------------------------------

class TestFailTask:
    def test_moves_to_failed(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Risky Task", "dag", project_slug=slug)
        tasks_mod.fail_task(filename, project_slug=slug)
        failed = patched_tasks / "projects" / slug / "tasks" / "failed"
        assert (failed / filename).exists()

    def test_removes_from_backlog(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Risky Task", "dag", project_slug=slug)
        tasks_mod.fail_task(filename, project_slug=slug)
        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        assert not (backlog / filename).exists()

    def test_updates_status_to_failed(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Risky Task", "dag", project_slug=slug)
        tasks_mod.fail_task(filename, project_slug=slug)
        failed = patched_tasks / "projects" / slug / "tasks" / "failed"
        content = (failed / filename).read_text(encoding="utf-8")
        assert "**Status:** failed" in content

    def test_appends_reason(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Risky Task", "dag", project_slug=slug)
        tasks_mod.fail_task(filename, reason="Timeout exceeded", project_slug=slug)
        failed = patched_tasks / "projects" / slug / "tasks" / "failed"
        content = (failed / filename).read_text(encoding="utf-8")
        assert "Timeout exceeded" in content
        assert "## Failure Reason" in content

    def test_no_reason_no_failure_section(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        filename = tasks_mod.create_task("Quiet Fail", "dag", project_slug=slug)
        tasks_mod.fail_task(filename, project_slug=slug)
        failed = patched_tasks / "projects" / slug / "tasks" / "failed"
        content = (failed / filename).read_text(encoding="utf-8")
        assert "## Failure Reason" not in content

    def test_noop_when_task_does_not_exist(self, patched_tasks):
        """fail_task on a non-existent filename should not raise."""
        _make_project_dirs(patched_tasks, "proj")
        # Should not raise; nothing to fail
        tasks_mod.fail_task("totally-missing.md", project_slug="proj")


# ---------------------------------------------------------------------------
# 9. cascade_fail()
# ---------------------------------------------------------------------------

class TestCascadeFail:
    def test_direct_dependant_marked_failed(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        # Create a root task and a dependent
        root = tasks_mod.create_task("Root Task", "arve", project_slug=slug)
        dep = tasks_mod.create_task("Dep Task", "bjorn", depends_on=root, project_slug=slug)

        cascaded = tasks_mod.cascade_fail(root, project_slug=slug)
        assert dep in cascaded

        failed = patched_tasks / "projects" / slug / "tasks" / "failed"
        assert (failed / dep).exists()

    def test_cascade_is_recursive(self, patched_tasks):
        """A -> B -> C: failing A should cascade to both B and C."""
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        task_a = tasks_mod.create_task("Task A", "arve", project_slug=slug)
        task_b = tasks_mod.create_task("Task B", "bjorn", depends_on=task_a, project_slug=slug)
        task_c = tasks_mod.create_task("Task C", "dag", depends_on=task_b, project_slug=slug)

        cascaded = tasks_mod.cascade_fail(task_a, project_slug=slug)
        assert task_b in cascaded
        assert task_c in cascaded

    def test_unrelated_task_not_cascaded(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        task_a = tasks_mod.create_task("Task A", "arve", project_slug=slug)
        task_b = tasks_mod.create_task("Task B", "bjorn", project_slug=slug)  # no depends_on

        cascaded = tasks_mod.cascade_fail(task_a, project_slug=slug)
        assert task_b not in cascaded

        backlog = patched_tasks / "projects" / slug / "tasks" / "backlog"
        assert (backlog / task_b).exists()

    def test_cascade_fail_reason_mentions_dependency(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        task_a = tasks_mod.create_task("Root", "arve", project_slug=slug)
        task_b = tasks_mod.create_task("Child", "bjorn", depends_on=task_a, project_slug=slug)

        tasks_mod.cascade_fail(task_a, project_slug=slug)
        failed = patched_tasks / "projects" / slug / "tasks" / "failed"
        content = (failed / task_b).read_text(encoding="utf-8")
        assert task_a in content

    def test_returns_empty_when_no_dependants(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        task_a = tasks_mod.create_task("Lone Wolf", "arve", project_slug=slug)
        cascaded = tasks_mod.cascade_fail(task_a, project_slug=slug)
        assert cascaded == []


# ---------------------------------------------------------------------------
# 10. resolve_handoffs()
# ---------------------------------------------------------------------------

class TestResolveHandoffs:
    def test_activates_waiting_task(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        upstream = tasks_mod.create_task("Upstream", "arve", project_slug=slug)
        waiting = tasks_mod.create_task(
            "Waiting", "bjorn", depends_on=upstream, project_slug=slug
        )

        # Simulate upstream completing
        tasks_mod.assign_task(upstream, "arve", project_slug=slug)
        tasks_mod.complete_task(upstream, project_slug=slug)

        activated = tasks_mod.resolve_handoffs(upstream, project_slug=slug)
        assert waiting in activated

        active = patched_tasks / "projects" / slug / "tasks" / "active"
        assert (active / waiting).exists()

    def test_does_not_activate_unrelated_tasks(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        upstream = tasks_mod.create_task("Upstream", "arve", project_slug=slug)
        unrelated = tasks_mod.create_task("Unrelated", "dag", project_slug=slug)

        tasks_mod.assign_task(upstream, "arve", project_slug=slug)
        tasks_mod.complete_task(upstream, project_slug=slug)

        activated = tasks_mod.resolve_handoffs(upstream, project_slug=slug)
        assert unrelated not in activated

    def test_returns_empty_when_no_backlog(self, patched_tasks):
        """resolve_handoffs on a non-existent backlog returns []."""
        slug = "proj"
        # Don't create directories; backlog won't exist
        result = tasks_mod.resolve_handoffs("some-task.md", project_slug=slug)
        assert result == []

    def test_waiting_task_gets_correct_agent(self, patched_tasks):
        """The activated task should retain its original agent."""
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        upstream = tasks_mod.create_task("Up", "arve", project_slug=slug)
        waiting = tasks_mod.create_task(
            "Down", "magnus", depends_on=upstream, project_slug=slug
        )

        tasks_mod.assign_task(upstream, "arve", project_slug=slug)
        tasks_mod.complete_task(upstream, project_slug=slug)
        tasks_mod.resolve_handoffs(upstream, project_slug=slug)

        active = patched_tasks / "projects" / slug / "tasks" / "active"
        content = (active / waiting).read_text(encoding="utf-8")
        assert "**Agent:** magnus" in content

    def test_multiple_waiters_all_activated(self, patched_tasks):
        slug = "proj"
        _make_project_dirs(patched_tasks, slug)
        upstream = tasks_mod.create_task("Gate", "arve", project_slug=slug)
        w1 = tasks_mod.create_task("Waiter 1", "bjorn", depends_on=upstream, project_slug=slug)
        w2 = tasks_mod.create_task("Waiter 2", "dag",   depends_on=upstream, project_slug=slug)

        tasks_mod.assign_task(upstream, "arve", project_slug=slug)
        tasks_mod.complete_task(upstream, project_slug=slug)
        activated = tasks_mod.resolve_handoffs(upstream, project_slug=slug)

        assert w1 in activated
        assert w2 in activated


# ---------------------------------------------------------------------------
# 11. write_run() / read_run()
# ---------------------------------------------------------------------------

class TestWriteReadRun:
    def test_round_trip(self, patched_memory):
        lines = ["Starting...", "Step 1 done", "Step 2 done"]
        memory_mod.write_run("task-abc", lines, done=False)
        result = memory_mod.read_run("task-abc")
        assert result["lines"] == lines
        assert result["done"] is False

    def test_done_flag_round_trip(self, patched_memory):
        memory_mod.write_run("task-xyz", ["output line"], done=True)
        result = memory_mod.read_run("task-xyz")
        assert result["done"] is True

    def test_missing_run_returns_defaults(self, patched_memory):
        result = memory_mod.read_run("never-written")
        assert result == {"lines": [], "done": False}

    def test_project_scoped_write_read(self, patched_memory):
        lines = ["proj line 1"]
        memory_mod.write_run("task-proj", lines, done=True, project_slug="my-proj")
        result = memory_mod.read_run("task-proj", project_slug="my-proj")
        assert result["lines"] == lines
        assert result["done"] is True

    def test_project_scoped_does_not_bleed_into_global(self, patched_memory):
        memory_mod.write_run("shared-id", ["scoped"], done=True, project_slug="proj-a")
        # Reading without project_slug should return defaults (file is in a subdir)
        result = memory_mod.read_run("shared-id")
        assert result == {"lines": [], "done": False}

    def test_overwrite_updates_content(self, patched_memory):
        memory_mod.write_run("task-upd", ["v1"], done=False)
        memory_mod.write_run("task-upd", ["v1", "v2"], done=True)
        result = memory_mod.read_run("task-upd")
        assert result["lines"] == ["v1", "v2"]
        assert result["done"] is True


# ---------------------------------------------------------------------------
# 12. list_runs()
# ---------------------------------------------------------------------------

class TestListRuns:
    def test_empty_when_no_runs(self, patched_memory):
        result = memory_mod.list_runs()
        assert result == {"running": [], "done": [], "web_search": []}

    def test_running_vs_done_split(self, patched_memory):
        memory_mod.write_run("task-run", ["line"], done=False)
        memory_mod.write_run("task-done", ["line"], done=True)
        result = memory_mod.list_runs()
        assert "task-run" in result["running"]
        assert "task-done" in result["done"]
        assert "task-run" not in result["done"]
        assert "task-done" not in result["running"]

    def test_web_search_flag_for_running_with_openai_line(self, patched_memory):
        memory_mod.write_run("ws-task", ["Processing...", "[OpenAI] search result"], done=False)
        result = memory_mod.list_runs()
        assert "ws-task" in result["web_search"]
        assert "ws-task" in result["running"]

    def test_done_task_not_in_web_search(self, patched_memory):
        """Completed tasks with [OpenAI] lines should NOT appear in web_search."""
        memory_mod.write_run("ws-done", ["[OpenAI] something"], done=True)
        result = memory_mod.list_runs()
        assert "ws-done" not in result["web_search"]

    def test_running_without_openai_not_in_web_search(self, patched_memory):
        memory_mod.write_run("plain-run", ["normal output"], done=False)
        result = memory_mod.list_runs()
        assert "plain-run" not in result["web_search"]

    def test_project_scoped_list(self, patched_memory):
        memory_mod.write_run("p-task-1", ["x"], done=False, project_slug="proj-x")
        memory_mod.write_run("p-task-2", ["y"], done=True,  project_slug="proj-x")
        result = memory_mod.list_runs(project_slug="proj-x")
        assert "p-task-1" in result["running"]
        assert "p-task-2" in result["done"]

    def test_global_runs_not_mixed_with_project_runs(self, patched_memory):
        memory_mod.write_run("global-task", ["g"], done=False)
        memory_mod.write_run("proj-task",   ["p"], done=False, project_slug="proj-y")
        global_result = memory_mod.list_runs()
        proj_result   = memory_mod.list_runs(project_slug="proj-y")
        assert "global-task" in global_result["running"]
        assert "proj-task"   not in global_result["running"]
        assert "proj-task"   in proj_result["running"]
        assert "global-task" not in proj_result["running"]

    def test_multiple_runs_all_listed(self, patched_memory):
        for i in range(5):
            memory_mod.write_run(f"task-{i}", [f"line {i}"], done=(i % 2 == 0))
        result = memory_mod.list_runs()
        all_ids = result["running"] + result["done"]
        for i in range(5):
            assert f"task-{i}" in all_ids


# ---------------------------------------------------------------------------
# Agents module (bonus — simple, no filesystem)
# ---------------------------------------------------------------------------

class TestAgents:
    def test_known_agents_are_valid(self):
        for agent in ("orchestrator", "arve", "bjorn", "dag", "magnus"):
            assert agents_mod.is_valid(agent)

    def test_unknown_agent_is_invalid(self):
        assert not agents_mod.is_valid("nobody")
        assert not agents_mod.is_valid("")
        assert not agents_mod.is_valid("ARVE")  # case-sensitive

    def test_valid_agents_set_is_not_empty(self):
        assert len(agents_mod.VALID_AGENTS) > 0

    def test_all_expected_agents_present(self):
        expected = {
            "orchestrator", "arve", "bjorn", "dag", "else", "frode",
            "halvard", "guro", "jorunn", "ingrid", "knut", "laila",
            "magnus", "nora", "odd", "per",
        }
        assert expected == agents_mod.VALID_AGENTS
