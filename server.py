# -*- coding: utf-8 -*-
"""
本地象棋对弈服务 —— 用 Pikafish 引擎做对手。
纯 Python 标准库，无需联网安装任何依赖。
启动后浏览器访问 http://127.0.0.1:8899
"""
import json
import os
import random
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(BASE, "Pikafish", "pikafish.exe")
WEBDIR = os.path.join(BASE, "web")
AUDIO_DIR = os.path.join(WEBDIR, "audio")
PORT = 8899

# 难度档位：nodes=节点上限，movetime=思考毫秒，rand=走随机合法着法的概率。
# 高档使用时间而不是很小的固定节点数，避免在高速 CPU 上几十毫秒就落子。
LEVELS = {
    1: {"nodes": 800,    "threads": 1, "rand": 0.50, "name": "新手"},
    2: {"nodes": 4000,   "threads": 1, "rand": 0.25, "name": "入门"},
    3: {"nodes": 25000,  "threads": 1, "rand": 0.08, "name": "业余"},
    4: {"nodes": 150000, "threads": 2, "rand": 0.00, "name": "高手"},
    5: {"movetime": 800,  "threads": 4, "rand": 0.00, "name": "棋手"},
    6: {"movetime": 2500, "threads": 8, "rand": 0.00, "name": "大师"},
    7: {"movetime": 8000, "threads": 0, "rand": 0.00, "name": "大神"},
}

HASH_MB = 512


class Engine:
    def __init__(self, path):
        self.lock = threading.Lock()
        self.p = subprocess.Popen(
            [path], cwd=os.path.dirname(path),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            text=True, encoding="utf-8", bufsize=1,
        )
        self._cur_threads = 1
        self._max_threads = max(1, (os.cpu_count() or 2) - 2)
        self._send("uci")
        self._wait("uciok")
        self._send("setoption name Hash value %d" % HASH_MB)
        self._send("setoption name Threads value 1")
        self._send("setoption name UCI_ShowWDL value true")  # 输出胜/和/负概率
        self._send("isready")
        self._wait("readyok")

    def _send(self, cmd):
        self.p.stdin.write(cmd + "\n")
        self.p.stdin.flush()

    def _wait(self, token):
        while True:
            line = self.p.stdout.readline()
            if line == "":
                raise RuntimeError("engine exited")
            if line.strip().startswith(token):
                return

    def _set_threads(self, n):
        # 0 表示自动使用大部分逻辑处理器；始终给系统和浏览器留出余量。
        n = self._max_threads if n <= 0 else min(n, self._max_threads)
        if n != self._cur_threads:
            self._send("setoption name Threads value %d" % n)
            self._cur_threads = n

    def legal_moves(self, moves):
        """返回当前局面（startpos + moves）轮到方的全部合法着法。"""
        with self.lock:
            self._set_position(moves)
            self._send("go perft 1")
            out = []
            while True:
                line = self.p.stdout.readline()
                if line == "":
                    raise RuntimeError("engine exited")
                line = line.strip()
                if line.startswith("Nodes searched"):
                    break
                if len(line) >= 4 and line[0] in "abcdefghi" and ":" in line:
                    mv = line.split(":")[0].strip()
                    if len(mv) == 4:
                        out.append(mv)
            return out

    def _set_position(self, moves):
        if moves:
            self._send("position startpos moves " + " ".join(moves))
        else:
            self._send("position startpos")

    def _read_search(self):
        """读取到 bestmove；只把无上下界标记的评估当作精确值。"""
        exact = None
        stats = {"depth": None, "seldepth": None, "nodes": None,
                 "search_ms": None}
        while True:
            line = self.p.stdout.readline()
            if line == "":
                raise RuntimeError("engine exited")
            line = line.strip()
            if line.startswith("info"):
                tok = line.split()
                for key, out_key in (("depth", "depth"),
                                     ("seldepth", "seldepth"),
                                     ("nodes", "nodes"), ("time", "search_ms")):
                    if key in tok:
                        try:
                            stats[out_key] = int(tok[tok.index(key) + 1])
                        except (ValueError, IndexError):
                            pass

                # 节点/时间恰好耗尽时，最后一行常是 upperbound/lowerbound；
                # 它不是精确评估，不能覆盖上一轮完整迭代的 WDL。
                is_primary = "multipv" not in tok
                if "multipv" in tok:
                    try:
                        is_primary = int(tok[tok.index("multipv") + 1]) == 1
                    except (ValueError, IndexError):
                        is_primary = False
                if ("score" in tok and is_primary and "upperbound" not in tok
                        and "lowerbound" not in tok):
                    score = mate = None
                    wdl = None
                    try:
                        if "cp" in tok:
                            score = int(tok[tok.index("cp") + 1])
                        elif "mate" in tok:
                            mate = int(tok[tok.index("mate") + 1])
                        if "wdl" in tok:
                            i = tok.index("wdl")
                            wdl = [int(tok[i + 1]), int(tok[i + 2]),
                                   int(tok[i + 3])]
                        exact = {"score": score, "mate": mate, "wdl": wdl,
                                 "eval_depth": stats["depth"]}
                    except (ValueError, IndexError):
                        pass
            if line.startswith("bestmove"):
                parts = line.split()
                result = exact or {"score": None, "mate": None, "wdl": None,
                                   "eval_depth": None}
                result.update(stats)
                result["bestmove"] = parts[1] if len(parts) > 1 else "(none)"
                result["eval_exact"] = exact is not None
                return result

    def bestmove(self, moves, level):
        cfg = LEVELS.get(level, LEVELS[4])
        # 低档：按概率直接走随机合法着法，封顶棋力、增加变化
        if cfg["rand"] > 0 and random.random() < cfg["rand"]:
            legal = self.legal_moves(moves)
            if legal:
                return {"bestmove": random.choice(legal), "random": True,
                        "score": None, "mate": None, "wdl": None}
        return self.analyze(moves, level)

    def analyze(self, moves, level):
        """按指定档位搜索当前局面，不应用低档的随机走子概率。"""
        cfg = LEVELS.get(level, LEVELS[4])
        with self.lock:
            self._set_threads(cfg["threads"])
            self._set_position(moves)
            if "movetime" in cfg:
                self._send("go movetime %d" % cfg["movetime"])
            else:
                self._send("go nodes %d" % cfg["nodes"])
            result = self._read_search()
            result["random"] = False
            return result

    def fen(self, moves):
        """返回 startpos+moves 局面的 FEN（用于重复局面检测）。"""
        with self.lock:
            self._set_position(moves)
            self._send("d"); self._send("isready")
            f = None
            while True:
                l = self.p.stdout.readline()
                if l == "":
                    raise RuntimeError("engine exited")
                if l.startswith("Fen:"):
                    f = l[4:].strip()
                if l.strip() == "readyok":
                    return f

    def quit(self):
        try:
            self._send("quit"); self.p.wait(timeout=5)
        except Exception:
            self.p.kill()


engine = None   # 作为服务运行时在 __main__ 中创建；被 import 时不启动引擎


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass  # 安静

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, ctype):
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._file(os.path.join(WEBDIR, "index.html"), "text/html; charset=utf-8")
        elif path.startswith("/audio/"):
            name = path[len("/audio/"):]
            audio_path = os.path.join(AUDIO_DIR, name)
            if (name == os.path.basename(name) and name.endswith(".wav")
                    and os.path.isfile(audio_path)):
                self._file(audio_path, "audio/wav")
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")
        moves = data.get("moves", [])
        try:
            if self.path == "/api/legal":
                self._json({"moves": engine.legal_moves(moves)})
            elif self.path == "/api/engine":
                self._json(engine.bestmove(moves, int(data.get("level", 4))))
            elif self.path == "/api/analyze":
                self._json(engine.analyze(moves, int(data.get("level", 4))))
            else:
                self.send_error(404)
        except Exception as e:
            self._json({"error": str(e)}, 500)


if __name__ == "__main__":
    engine = Engine(ENGINE)
    print("=" * 48)
    print("  象棋对弈服务已启动 (Pikafish 引擎)")
    print("  请用浏览器打开:  http://127.0.0.1:%d" % PORT)
    print("  关闭本窗口即可结束程序")
    print("=" * 48)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
