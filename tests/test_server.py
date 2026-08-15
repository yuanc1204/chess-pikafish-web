import io
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import server


def fake_engine(*lines):
    engine = server.Engine.__new__(server.Engine)
    engine.p = SimpleNamespace(stdout=io.StringIO("\n".join(lines) + "\n"))
    return engine


class ReadSearchTests(unittest.TestCase):
    def test_reads_exact_score_and_search_stats(self):
        engine = fake_engine(
            "info depth 12 seldepth 18 score cp 23 wdl 105 800 95 "
            "nodes 1000 time 8",
            "bestmove a0a1",
        )

        result = engine._read_search()

        self.assertEqual(result["bestmove"], "a0a1")
        self.assertEqual(result["score"], 23)
        self.assertIsNone(result["mate"])
        self.assertEqual(result["wdl"], [105, 800, 95])
        self.assertEqual(result["eval_depth"], 12)
        self.assertEqual(result["nodes"], 1000)
        self.assertTrue(result["eval_exact"])

    def test_bound_does_not_overwrite_exact(self):
        for bound in ("upperbound", "lowerbound"):
            with self.subTest(bound=bound):
                engine = fake_engine(
                    "info depth 10 score cp 18 wdl 90 850 60 nodes 900",
                    f"info depth 11 score cp 52 {bound} wdl 200 700 100 "
                    "nodes 1200 time 10",
                    "bestmove b0c2",
                )

                result = engine._read_search()

                self.assertEqual(result["score"], 18)
                self.assertEqual(result["wdl"], [90, 850, 60])
                self.assertEqual(result["eval_depth"], 10)
                self.assertEqual(result["depth"], 11)
                self.assertEqual(result["nodes"], 1200)

    def test_bound_only_returns_no_evaluation(self):
        engine = fake_engine(
            "info depth 12 score cp -30 upperbound wdl 5 900 95",
            "bestmove h2e2",
        )

        result = engine._read_search()

        self.assertEqual(result["bestmove"], "h2e2")
        self.assertIsNone(result["score"])
        self.assertIsNone(result["mate"])
        self.assertIsNone(result["wdl"])
        self.assertFalse(result["eval_exact"])

    def test_exact_mate_replaces_previous_cp(self):
        engine = fake_engine(
            "info depth 8 score cp 300 wdl 800 150 50",
            "info depth 10 score mate 3 wdl 1000 0 0",
            "bestmove a0a1",
        )

        result = engine._read_search()

        self.assertIsNone(result["score"])
        self.assertEqual(result["mate"], 3)
        self.assertEqual(result["wdl"], [1000, 0, 0])

    def test_ignores_secondary_multipv_score(self):
        engine = fake_engine(
            "info depth 8 multipv 1 score cp 20 wdl 100 800 100",
            "info depth 8 multipv 2 score cp -80 wdl 1 500 499",
            "bestmove a0a1",
        )

        result = engine._read_search()

        self.assertEqual(result["score"], 20)
        self.assertEqual(result["wdl"], [100, 800, 100])


class LevelTests(unittest.TestCase):
    def test_analysis_ignores_random_move_probability(self):
        engine = server.Engine.__new__(server.Engine)
        engine.lock = threading.Lock()
        engine._set_threads = Mock()
        engine._set_position = Mock()
        engine._send = Mock()
        engine._read_search = Mock(return_value={"bestmove": "a0a1"})

        result = engine.analyze([], 1)

        engine._send.assert_called_once_with("go nodes 800")
        self.assertFalse(result["random"])

    def test_high_levels_use_increasing_time_and_no_random_moves(self):
        times = [server.LEVELS[n]["movetime"] for n in (5, 6, 7)]
        self.assertEqual(times, sorted(times))
        self.assertEqual(len(times), len(set(times)))
        for level in (4, 5, 6, 7):
            self.assertEqual(server.LEVELS[level]["rand"], 0)

    def test_expert_level_uses_old_level_four_node_budget(self):
        self.assertEqual(
            server.LEVELS[4],
            {"nodes": 150000, "threads": 2, "rand": 0.0, "name": "高手"},
        )

        engine = server.Engine.__new__(server.Engine)
        engine.lock = threading.Lock()
        engine._set_threads = Mock()
        engine._set_position = Mock()
        engine._send = Mock()
        engine._read_search = Mock(return_value={"bestmove": "a0a1"})

        engine.bestmove([], 4)

        engine._send.assert_called_once_with("go nodes 150000")

    def test_level_five_uses_configured_time(self):
        engine = server.Engine.__new__(server.Engine)
        engine.lock = threading.Lock()
        engine._set_threads = Mock()
        engine._set_position = Mock()
        engine._send = Mock()
        engine._read_search = Mock(return_value={"bestmove": "a0a1"})

        result = engine.bestmove([], 5)

        engine._send.assert_called_once_with(
            "go movetime %d" % server.LEVELS[5]["movetime"]
        )
        self.assertFalse(result["random"])

    def test_thread_count_is_capped_and_auto_resolved(self):
        engine = server.Engine.__new__(server.Engine)
        engine._max_threads = 6
        engine._cur_threads = 1
        engine._send = Mock()

        engine._set_threads(0)
        engine._set_threads(20)
        engine._set_threads(4)

        self.assertEqual(
            engine._send.call_args_list,
            [unittest.mock.call("setoption name Threads value 6"),
             unittest.mock.call("setoption name Threads value 4")],
        )


class HandlerGetTests(unittest.TestCase):
    def test_serves_bundled_audio(self):
        handler = server.Handler.__new__(server.Handler)
        handler.path = "/audio/move.wav"
        handler._file = Mock()
        handler.send_error = Mock()

        handler.do_GET()

        handler._file.assert_called_once_with(
            server.os.path.join(server.AUDIO_DIR, "move.wav"), "audio/wav"
        )
        handler.send_error.assert_not_called()

    def test_rejects_audio_path_traversal(self):
        handler = server.Handler.__new__(server.Handler)
        handler.path = "/audio/../move.wav"
        handler._file = Mock()
        handler.send_error = Mock()

        handler.do_GET()

        handler._file.assert_not_called()
        handler.send_error.assert_called_once_with(404)


if __name__ == "__main__":
    unittest.main()
