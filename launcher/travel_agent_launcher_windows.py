import os
import platform
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _base_dir()
APP_DIR = BASE_DIR / "app"
VENV_DIR = BASE_DIR / ".venv"
TRAVEL_AGENT = APP_DIR / "travel_agent.py"

COLORS = {
    "bg": "#0f1115",
    "panel": "#161a22",
    "panel_alt": "#1c2230",
    "text": "#e6eaf2",
    "muted": "#9aa4b2",
    "accent": "#35c2ff",
    "accent_hover": "#60d1ff",
    "danger": "#ff6b6b",
}


class TravelAgentApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Travel Agent")
        self.root.geometry("860x600")
        self.root.minsize(760, 520)
        self.root.configure(bg=COLORS["bg"])

        self.main = tk.Frame(root, bg=COLORS["bg"])
        self.main.pack(fill="both", expand=True, padx=18, pady=18)

        self._build_header()
        self._build_controls()
        self._build_output()

        self.destination_entry.bind("<Return>", lambda _: self.run_agent())
        self.destination_entry.focus_set()

    def _build_header(self) -> None:
        header = tk.Frame(self.main, bg=COLORS["panel"], highlightthickness=1, highlightbackground="#262f41")
        header.pack(fill="x")

        tk.Label(
            header,
            text="Dynamic Travel Packing Assistant",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 15),
            anchor="w",
            padx=14,
            pady=12,
        ).pack(fill="x")

        tk.Label(
            header,
            text="Enter a destination and get an AI-generated packing list based on live weather.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
            padx=14,
            pady=0,
        ).pack(fill="x", pady=(0, 12))

    def _build_controls(self) -> None:
        controls = tk.Frame(self.main, bg=COLORS["panel_alt"], highlightthickness=1, highlightbackground="#2a3448")
        controls.pack(fill="x", pady=(12, 10))

        row = tk.Frame(controls, bg=COLORS["panel_alt"])
        row.pack(fill="x", padx=12, pady=12)

        tk.Label(
            row,
            text="Destination",
            bg=COLORS["panel_alt"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        self.destination_entry = tk.Entry(
            row,
            bg="#0e141e",
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            font=("Segoe UI", 10),
            width=35,
        )
        self.destination_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=7)

        self.run_button = tk.Button(
            row,
            text="Run Agent",
            command=self.run_agent,
            bg=COLORS["accent"],
            activebackground=COLORS["accent_hover"],
            fg="#00121a",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=7,
        )
        self.run_button.pack(side="right")

        self.clear_button = tk.Button(
            row,
            text="Clear",
            command=self.clear_output,
            bg="#2a3244",
            activebackground="#3a4660",
            fg=COLORS["text"],
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10),
            padx=12,
            pady=7,
        )
        self.clear_button.pack(side="right", padx=(0, 8))

        token_row = tk.Frame(controls, bg=COLORS["panel_alt"])
        token_row.pack(fill="x", padx=12, pady=(0, 10))

        tk.Label(
            token_row,
            text="HF Token",
            bg=COLORS["panel_alt"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        self.token_entry = tk.Entry(
            token_row,
            bg="#0e141e",
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            font=("Segoe UI", 10),
            show="*",
        )
        self.token_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=7)

        self.show_token_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            token_row,
            text="Show",
            variable=self.show_token_var,
            command=self._toggle_token_visibility,
            bg=COLORS["panel_alt"],
            activebackground=COLORS["panel_alt"],
            fg=COLORS["muted"],
            selectcolor=COLORS["panel_alt"],
            font=("Segoe UI", 9),
            cursor="hand2",
        ).pack(side="right")

        self.save_token_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            token_row,
            text="Save to .env",
            variable=self.save_token_var,
            bg=COLORS["panel_alt"],
            activebackground=COLORS["panel_alt"],
            fg=COLORS["muted"],
            selectcolor=COLORS["panel_alt"],
            font=("Segoe UI", 9),
            cursor="hand2",
        ).pack(side="right", padx=(0, 10))

        status_row = tk.Frame(controls, bg=COLORS["panel_alt"])
        status_row.pack(fill="x", padx=12, pady=(0, 10))

        tk.Label(
            status_row,
            text="Status:",
            bg=COLORS["panel_alt"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            status_row,
            textvariable=self.status_var,
            bg="#202a3a",
            fg=COLORS["accent"],
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=3,
        )
        self.status_label.pack(side="left", padx=(8, 0))

    def _build_output(self) -> None:
        output_panel = tk.Frame(self.main, bg=COLORS["panel"], highlightthickness=1, highlightbackground="#2a3448")
        output_panel.pack(fill="both", expand=True)

        tk.Label(
            output_panel,
            text="Output",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            padx=12,
            pady=10,
        ).pack(fill="x")

        self.output = scrolledtext.ScrolledText(
            output_panel,
            wrap=tk.WORD,
            font=("Cascadia Mono", 10),
            state="disabled",
            bg="#0c111a",
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
        )
        self.output.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def append_output(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def clear_output(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.configure(state="disabled")

    def set_status(self, text: str, color: str | None = None) -> None:
        self.status_var.set(text)
        self.status_label.configure(fg=color or COLORS["accent"])

    def _toggle_token_visibility(self) -> None:
        self.token_entry.configure(show="" if self.show_token_var.get() else "*")

    def run_agent(self) -> None:
        destination = self.destination_entry.get().strip()
        if not destination:
            messagebox.showwarning("Missing destination", "Enter a destination first.")
            return

        self.run_button.configure(state="disabled")
        self.set_status("Preparing environment...", COLORS["accent"])
        self.clear_output()
        self.append_output(f"Destination: {destination}\n\n")

        token_input = self.token_entry.get().strip()
        worker = threading.Thread(
            target=self._run_agent_worker, args=(destination, token_input), daemon=True
        )
        worker.start()

    def _run_agent_worker(self, destination: str, token_input: str) -> None:
        try:
            if platform.system().lower() != "windows":
                self._ui_error("This launcher is for Windows only.")
                return
            if not TRAVEL_AGENT.exists():
                self._ui_error("Could not find travel_agent.py next to this executable.")
                return

            venv_python = self._ensure_venv()
            self._ensure_dependencies(venv_python)
            token = self._resolve_token(token_input)

            self.root.after(0, lambda: self.set_status("Running...", COLORS["accent"]))
            stdout, stderr, returncode = self._execute_agent(venv_python, destination, token)

            if stdout:
                self.root.after(0, lambda: self.append_output(stdout))
            if stderr:
                self.root.after(0, lambda: self.append_output("\n[stderr]\n" + stderr))

            if returncode == 0:
                self.root.after(0, lambda: self.set_status("Completed", "#7ddf9e"))
            else:
                self.root.after(0, lambda: self.set_status(f"Failed ({returncode})", COLORS["danger"]))
        except Exception as exc:
            self._ui_error(str(exc))
        finally:
            self.root.after(0, lambda: self.run_button.configure(state="normal"))

    def _run(self, cmd: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            text=True,
            capture_output=True,
            check=False,
        )

    def _find_base_python(self) -> str:
        if shutil.which("py"):
            return "py"
        if shutil.which("python"):
            return "python"
        raise RuntimeError("Python is not installed or not in PATH. Install Python 3.10+.")

    def _venv_python(self) -> Path:
        return VENV_DIR / "Scripts" / "python.exe"

    def _ensure_venv(self) -> Path:
        venv_python = self._venv_python()
        if venv_python.exists():
            return venv_python

        self.root.after(0, lambda: self.append_output("Creating .venv...\n"))
        base_python = self._find_base_python()
        created = self._run([base_python, "-m", "venv", str(VENV_DIR)])
        if created.returncode != 0:
            raise RuntimeError(created.stderr or created.stdout or "Failed to create .venv.")
        return venv_python

    def _ensure_dependencies(self, venv_python: Path) -> None:
        probe = self._run(
            [
                str(venv_python),
                "-c",
                "import smolagents,requests,dotenv,ddgs; from smolagents import DuckDuckGoSearchTool",
            ]
        )
        if probe.returncode == 0:
            return

        self.root.after(0, lambda: self.append_output("Installing required packages...\n"))
        upgrade = self._run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
        if upgrade.returncode != 0:
            raise RuntimeError(upgrade.stderr or upgrade.stdout or "Failed to upgrade pip.")

        install = self._run(
            [
                str(venv_python),
                "-m",
                "pip",
                "install",
                "smolagents[openai]",
                "python-dotenv",
                "requests",
                "ddgs",
            ]
        )
        if install.returncode != 0:
            raise RuntimeError(install.stderr or install.stdout or "Failed to install dependencies.")

    def _read_token_from_env_file(self) -> str:
        env_file = APP_DIR / ".env"
        if not env_file.exists():
            return ""

        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("HUGGINGFACE_HUB_TOKEN=") and line.split("=", 1)[1].strip():
                return line.split("=", 1)[1].strip()
        return ""

    def _write_token_to_env(self, token: str) -> None:
        env_file = APP_DIR / ".env"
        lines = []
        if env_file.exists():
            lines = env_file.read_text(encoding="utf-8", errors="ignore").splitlines()

        replaced = False
        output_lines = []
        for line in lines:
            if line.strip().startswith("HUGGINGFACE_HUB_TOKEN="):
                output_lines.append(f"HUGGINGFACE_HUB_TOKEN={token}")
                replaced = True
            else:
                output_lines.append(line)
        if not replaced:
            output_lines.append(f"HUGGINGFACE_HUB_TOKEN={token}")
        env_file.write_text("\n".join(output_lines).strip() + "\n", encoding="utf-8")

    def _resolve_token(self, token_input: str) -> str:
        if token_input:
            if self.save_token_var.get():
                self._write_token_to_env(token_input)
            return token_input

        env_token = os.getenv("HUGGINGFACE_HUB_TOKEN", "").strip()
        if env_token:
            return env_token

        file_token = self._read_token_from_env_file()
        if file_token:
            return file_token

        raise RuntimeError(
            "Missing token.\nPaste your Hugging Face token in the UI field or create .env with:\n"
            "HUGGINGFACE_HUB_TOKEN=hf_your_token_here"
        )

    def _execute_agent(self, venv_python: Path, destination: str, token: str) -> tuple[str, str, int]:
        proc_env = os.environ.copy()
        proc_env["HUGGINGFACE_HUB_TOKEN"] = token
        proc = subprocess.Popen(
            [str(venv_python), str(TRAVEL_AGENT)],
            cwd=str(BASE_DIR),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=proc_env,
            text=True,
        )
        stdout, stderr = proc.communicate(input=destination + "\n")
        return stdout or "", stderr or "", proc.returncode or 0

    def _ui_error(self, message: str) -> None:
        self.root.after(0, lambda: self.set_status("Failed", COLORS["danger"]))
        self.root.after(0, lambda: self.append_output("\n[error]\n" + message + "\n"))
        self.root.after(0, lambda: messagebox.showerror("Travel Agent", message))


def main() -> None:
    root = tk.Tk()
    TravelAgentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
