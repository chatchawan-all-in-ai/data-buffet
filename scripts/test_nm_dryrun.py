import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import nm_dryrun


class DefaultCredentialsError(Exception):
    pass


class DryRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.google = types.ModuleType("google")
        self.auth = types.ModuleType("google.auth")
        self.exceptions = types.ModuleType("google.auth.exceptions")
        self.cloud = types.ModuleType("google.cloud")
        self.bigquery = types.ModuleType("google.cloud.bigquery")
        self.google.auth = self.auth
        self.google.cloud = self.cloud
        self.auth.exceptions = self.exceptions
        self.cloud.bigquery = self.bigquery
        self.exceptions.DefaultCredentialsError = DefaultCredentialsError
        self.auth.default = Mock(return_value=(object(), "ignored-default-project"))
        self.client = Mock()
        self.client.query.return_value = types.SimpleNamespace(total_bytes_processed=42)
        self.bigquery.Client = Mock(return_value=self.client)
        self.bigquery.QueryJobConfig = Mock(side_effect=lambda **kw: types.SimpleNamespace(**kw))
        self.modules = {
            "google": self.google,
            "google.auth": self.auth,
            "google.auth.exceptions": self.exceptions,
            "google.cloud": self.cloud,
            "google.cloud.bigquery": self.bigquery,
        }

    def action(self, name="consumer", **fields):
        return {
            "fileName": f"definitions/{name}.sqlx",
            "target": {"database": nm_dryrun.PROJECT, "schema": "mart", "name": name},
            **fields,
        }

    def run_main(self, graph=None, changed=(), mode="all"):
        compiled = self.root / "compile.json"
        changed_file = self.root / "changed.txt"
        compiled.write_text(json.dumps(graph or {"tables": [self.action(query="SELECT 1")]}))
        changed_file.write_text("\n".join(changed))
        argv = ["nm_dryrun.py", "--compile", str(compiled), "--changed", str(changed_file), "--mode", mode]
        output = io.StringIO()
        with patch.dict(sys.modules, self.modules), patch.object(sys, "argv", argv), contextlib.redirect_stdout(output):
            code = nm_dryrun.main()
        return code, output.getvalue()

    def test_missing_client_fails(self):
        self.modules["google.cloud"] = None
        code, output = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("FAIL dry run", output)
        self.auth.default.assert_not_called()

    def test_absent_adc_is_the_only_credential_skip(self):
        self.auth.default.side_effect = DefaultCredentialsError("Your default credentials were not found. To set up ADC...")
        code, output = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("WARNING: SKIP", output)
        self.assertIn("UNVERIFIED", output)
        self.bigquery.Client.assert_not_called()

    def test_invalid_adc_and_discovery_errors_fail(self):
        for error in (DefaultCredentialsError("File credentials.json was not found."), RuntimeError("credential refresh failed")):
            with self.subTest(error=error):
                self.auth.default.side_effect = error
                code, output = self.run_main()
                self.assertEqual(code, 1)
                self.assertIn("FAIL dry run", output)
                self.assertNotIn("SKIP", output)

    def test_client_creation_error_never_skips(self):
        self.bigquery.Client.side_effect = DefaultCredentialsError("Your default credentials were not found.")
        code, output = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("client creation failed", output)
        self.assertNotIn("SKIP", output)

    def test_dry_run_uses_the_pinned_project_and_does_not_execute(self):
        code, output = self.run_main()
        self.assertEqual(code, 0)
        self.bigquery.Client.assert_called_once_with(project=nm_dryrun.PROJECT, credentials=self.auth.default.return_value[0])
        args, kwargs = self.client.query.call_args
        self.assertEqual(args, ("SELECT 1",))
        self.assertEqual(kwargs["project"], nm_dryrun.PROJECT)
        self.assertTrue(kwargs["job_config"].dry_run)
        self.assertFalse(kwargs["job_config"].use_query_cache)
        self.assertIn("1 ok", output)
        self.assertIn("42 bytes total", output)

    def test_only_exact_action_targets_allow_missing_object_warnings(self):
        graph = {"tables": [self.action(query="SELECT * FROM source"), self.action("dependency", query="SELECT 1")]}
        for path in ("databuffet-nonprd:mart.dependency", "databuffet-nonprd.mart.dependency"):
            with self.subTest(path=path):
                self.client.query.side_effect = RuntimeError(f"Not found: Table {path} was not found in location US")
                code, output = self.run_main(graph, changed=["definitions/consumer.sqlx"], mode="changed")
                self.assertEqual(code, 0)
                self.assertIn("1 skipped with warning", output)
                self.assertIn("0 ok", output)
        for message in (
            "Not found: Table databuffet-nonprd:mart.mds_data_company_mastr was not found in location US",
            "Not found: Table other-project:mart.dependency was not found in location US",
            "Not found: Table databuffet-nonprd:other_dataset.dependency was not found in location US",
            "Not found: Dataset databuffet-nonprd:mart",
            "Not found: Routine databuffet-nonprd:mart.dependency",
            "Access denied",
        ):
            with self.subTest(message=message):
                self.client.query.side_effect = RuntimeError(message)
                code, output = self.run_main(graph, changed=["definitions/consumer.sqlx"], mode="changed")
                self.assertEqual(code, 1)
                self.assertIn("1 failed", output)
                self.assertIn("0 skipped with warning", output)

    def test_declared_sources_are_not_undeployed_actions(self):
        graph = {"tables": [self.action(query="SELECT * FROM source")], "declarations": [self.action("source")]}
        self.client.query.side_effect = RuntimeError("Not found: Table databuffet-nonprd:mart.source was not found in location US")
        code, output = self.run_main(graph)
        self.assertEqual(code, 1)
        self.assertIn("0 skipped with warning", output)

    def test_operation_and_assertion_targets_are_in_the_complete_graph(self):
        for key in ("operations", "assertions"):
            with self.subTest(key=key):
                graph = {"tables": [self.action(query="SELECT * FROM dependency")], key: [self.action("dependency")]}
                self.client.query.side_effect = RuntimeError("Not found: View databuffet-nonprd:mart.dependency was not found in location US")
                code, output = self.run_main(graph, changed=["definitions/consumer.sqlx"], mode="changed")
                self.assertEqual(code, 0)
                self.assertIn("1 skipped with warning", output)

    def test_each_mode_keeps_its_own_complete_sequence(self):
        action = self.action(
            query="SELECT 1", incrementalQuery="SELECT 1",
            preOps=["SELECT 'full pre'"], postOps=["SELECT 'full post'"],
            incrementalPreOps=["SELECT 'incremental pre'"], incrementalPostOps=["SELECT 'incremental post'"],
        )
        self.assertEqual(nm_dryrun.action_queries(action, False), [
            ("query", "SELECT 'full pre';\nSELECT 1;\nSELECT 'full post'", True),
            ("incremental", "SELECT 'incremental pre';\nSELECT 1;\nSELECT 'incremental post'", True),
        ])

    def test_deduplication_compares_pre_body_and_post_together(self):
        action = self.action(query="SELECT 1", incrementalQuery="SELECT 1", postOps=["SELECT 2"], incrementalPostOps=["SELECT 2"])
        self.assertEqual(nm_dryrun.action_queries(action, False), [("query", "SELECT 1;\nSELECT 2", True)])
        action["incrementalPostOps"] = ["SELECT 3"]
        self.assertEqual(nm_dryrun.action_queries(action, False), [("query", "SELECT 1;\nSELECT 2", True), ("incremental", "SELECT 1;\nSELECT 3", True)])

    def test_deduplication_keeps_materialization_context(self):
        action = self.action(query="SELECT 2", preOps=["SELECT 1"], incrementalQuery="SELECT 1", incrementalPostOps=["SELECT 2"])
        self.assertEqual(nm_dryrun.action_queries(action, False), [
            ("query", "SELECT 1;\nSELECT 2", False),
            ("incremental", "SELECT 1;\nSELECT 2", True),
        ])
        code, output = self.run_main({"tables": [action]})
        self.assertEqual(code, 0)
        self.assertEqual(self.client.query.call_count, 1)
        self.assertIn("1 ok", output)
        self.assertIn("1 unverified", output)

    def test_scripts_are_listed_without_being_counted_or_submitted_as_ok(self):
        graph = {
            "tables": [self.action(query="SELECT * FROM temp", preOps=["CREATE TEMP TABLE temp AS SELECT 1"], incrementalQuery="SELECT * FROM temp", incrementalPreOps=["CREATE TEMP TABLE temp AS SELECT 2"], postOps=["SELECT 3"])],
            "operations": [self.action("operation", queries=["CREATE TABLE target AS SELECT 1; DELETE FROM target WHERE TRUE;"])],
        }
        code, output = self.run_main(graph)
        self.assertEqual(code, 0)
        self.assertIn("3 unverified", output)
        self.assertIn("0 ok, 0 failed", output)
        self.assertIn("[incremental]", output)
        self.assertIn("[operation]", output)
        self.client.query.assert_not_called()

    def test_post_operations_in_both_modes_are_unverified_against_deployed_schema(self):
        action = self.action(
            query="SELECT 1 AS prdSku", incrementalQuery="SELECT 1 AS prdSku",
            postOps=["UPDATE target SET prdSize = 'large' WHERE TRUE"],
            incrementalPostOps=["UPDATE target SET prdSize = 'small' WHERE TRUE"],
        )
        code, output = self.run_main({"tables": [action]})
        self.assertEqual(code, 0)
        self.client.query.assert_not_called()
        self.assertIn("2 unverified", output)
        self.assertIn("0 ok, 0 failed", output)
        self.assertIn("newly materialized target", output)

    def test_only_the_mode_with_post_operations_is_unverified(self):
        for post_key in ("postOps", "incrementalPostOps"):
            with self.subTest(post_key=post_key):
                self.client.query.reset_mock()
                action = self.action(query="SELECT 1", incrementalQuery="SELECT 2", **{post_key: ["UPDATE target SET id = 1 WHERE TRUE"]})
                code, output = self.run_main({"tables": [action]})
                self.assertEqual(code, 0)
                self.assertEqual(self.client.query.call_count, 1)
                self.assertIn("1 ok", output)
                self.assertIn("1 unverified", output)

    def test_empty_post_operations_do_not_require_materialization(self):
        action = self.action(query="SELECT 1", incrementalQuery="SELECT 2", postOps=["", " \n"], incrementalPostOps=[])
        code, output = self.run_main({"tables": [action]})
        self.assertEqual(code, 0)
        self.assertEqual(self.client.query.call_count, 2)
        self.assertIn("2 ok", output)
        self.assertIn("0 unverified", output)

    def test_script_detection_preserves_single_statement_literals_and_comments(self):
        for sql in (
            "SELECT ';'; -- extra ; in a comment",
            'SELECT "a; b"; /* ; */',
            "SELECT '''line;\nline''';",
            'SELECT """line;\nline""";',
            "SELECT `field;name` FROM `project.dataset.table`;",
            "SELECT r'\\;'; # comment ;",
            "SELECT 1; SELECT 2;",
            "SELECT 1; UPDATE target SET id = 1 WHERE TRUE;",
            "SELECT 1; CREATE TABLE target AS SELECT 2;",
        ):
            with self.subTest(sql=sql):
                self.assertFalse(nm_dryrun.is_unverified_script(sql))
        for sql in (
            "CREATE TABLE target AS SELECT 1; DELETE FROM target WHERE TRUE;",
            "BEGIN SELECT 1; END;", "CALL procedure()", "EXECUTE IMMEDIATE 'SELECT 1'",
            "SELECT 1; EXECUTE IMMEDIATE 'SELECT 2';", "IF TRUE THEN SELECT 1; END IF;",
            "CREATE TEMP TABLE target AS SELECT 1;", "CREATE/* comment */TEMP TABLE target AS SELECT 1;",
        ):
            with self.subTest(sql=sql):
                self.assertTrue(nm_dryrun.is_unverified_script(sql))

    def test_shared_configuration_changes_widen_the_selected_actions(self):
        graph = {"tables": [self.action(query="SELECT 1"), self.action("sibling", query="SELECT 2")]}
        for changed in ("includes/settings.js", "workflow_settings.yaml"):
            with self.subTest(changed=changed):
                self.client.query.reset_mock()
                code, output = self.run_main(graph, changed=[changed], mode="changed")
                self.assertEqual(code, 0)
                self.assertEqual(self.client.query.call_count, 2)
                self.assertIn("2 ok", output)

    def test_other_projects_are_refused(self):
        action = self.action(query="SELECT 1")
        action["target"]["database"] = "other-project"
        code, output = self.run_main({"tables": [action]})
        self.assertEqual(code, 1)
        self.assertIn("REFUSED", output)
        self.client.query.assert_not_called()


if __name__ == "__main__":
    unittest.main()
