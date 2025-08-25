import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, ttk
import requests
import json
import math
import random
from typing import List, Dict, Any
import os

# Automatically get path relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
js_file_path = os.path.join(script_dir, "gformjs.js")

# Read the JavaScript snippet
try:
    with open(js_file_path, "r", encoding="utf-8") as f:
        JS_SNIPPET = f.read()
except FileNotFoundError:
    JS_SNIPPET = "// JavaScript snippet not found. Make sure google_forms_snippet.js is in the same folder."


# ===================== Instruction Window =====================
def show_instructions(root: tk.Tk):
    instr = tk.Toplevel(root)
    instr.title("Instructions")
    instr.geometry("820x580")
    instr.resizable(False, False)

    tk.Label(instr, text="📌 GOOGLE FORMS BOT — INSTRUCTIONS", font=("Arial", 15, "bold")).pack(pady=10)

    text = scrolledtext.ScrolledText(instr, width=96, height=24)
    text.pack(padx=10, pady=5)
    text.insert(tk.END, "1) Open your Google Form (the 'viewform' URL) in your browser.\n")
    text.insert(tk.END, "2) Open the Developer Console (Right-click → Inspect → Console).\n")
    text.insert(tk.END, "3) Paste the JavaScript below and press Enter. Copy the JSON it prints.\n\n")
    text.insert(tk.END, JS_SNIPPET + "\n\n")
    text.insert(tk.END, "4) In this app, click 'Import JSON', paste the JSON, & follow prompts.\n")
    text.config(state="disabled")

    def copy_js():
        root.clipboard_clear()
        root.clipboard_append(JS_SNIPPET)
        root.update()
        messagebox.showinfo("Copied", "JavaScript snippet copied to clipboard!")

    btns = tk.Frame(instr)
    btns.pack(pady=8)
    tk.Button(btns, text="📋 Copy JavaScript", command=copy_js).pack(side="left", padx=6)
    tk.Button(btns, text="✅ Got it, start", command=instr.destroy).pack(side="left", padx=6)
    instr.grab_set()
    instr.focus_set()


# ===================== Helper UI Dialogs =====================
def prompt_multiline(title: str, initial_text: str = "") -> str:
    dlg = tk.Toplevel()
    dlg.title(title)
    dlg.geometry("560x360")
    dlg.resizable(True, True)
    txt = scrolledtext.ScrolledText(dlg, width=66, height=16)
    txt.pack(padx=10, pady=10, fill="both", expand=True)
    if initial_text: txt.insert("1.0", initial_text)
    result = {"text": ""}

    def on_ok():
        result["text"] = txt.get("1.0", "end-1c")
        dlg.destroy()

    def on_cancel():
        result["text"] = ""
        dlg.destroy()

    btns = tk.Frame(dlg)
    btns.pack(pady=6)
    tk.Button(btns, text="Save", command=on_ok).pack(side="left", padx=6)
    tk.Button(btns, text="Cancel", command=on_cancel).pack(side="left", padx=6)
    dlg.grab_set()
    dlg.focus_set()
    dlg.wait_window()
    return result["text"]


# ===== NEW: Percentage Chooser with Sliders =====
class PercentageChooser(tk.Toplevel):
    def __init__(self, title: str, options: List[str]):
        super().__init__()
        self.title(title)
        self.geometry("500x300")
        self.resizable(False, False)

        self.options = options
        self.values = [0] * len(options)
        self.sliders = []
        self.entries = []

        for i, opt in enumerate(options):
            frame = ttk.Frame(self)
            frame.pack(fill="x", padx=10, pady=5)

            label = ttk.Label(frame, text=opt, width=20)
            label.pack(side="left")

            slider = ttk.Scale(frame, from_=0, to=100, orient="horizontal",
                               command=lambda val, idx=i: self.update_from_slider(idx, val))
            slider.pack(side="left", fill="x", expand=True, padx=5)
            self.sliders.append(slider)

            entry = ttk.Entry(frame, width=5)
            entry.insert(0, "0")
            entry.bind("<Return>", lambda e, idx=i: self.update_from_entry(idx))
            entry.pack(side="right")
            self.entries.append(entry)

        btn = ttk.Button(self, text="Done", command=self.finish)
        btn.pack(pady=10)

        self.result = None
        self.grab_set()
        self.focus_set()

    def update_from_slider(self, idx, val):
        val = round(float(val))
        self.entries[idx].delete(0, tk.END)
        self.entries[idx].insert(0, str(val))
        self.values[idx] = val
        self.correct_total(idx)

    def update_from_entry(self, idx):
        try:
            val = int(self.entries[idx].get())
        except ValueError:
            val = 0
        self.sliders[idx].set(val)
        self.values[idx] = val
        self.correct_total(idx)

    def correct_total(self, idx):
        total = sum(self.values)
        if total > 100:
            overflow = total - 100
            self.values[idx] -= overflow
            if self.values[idx] < 0:
                self.values[idx] = 0
            self.sliders[idx].set(self.values[idx])
            self.entries[idx].delete(0, tk.END)
            self.entries[idx].insert(0, str(self.values[idx]))

    def finish(self):
        if sum(self.values) != 100:
            messagebox.showerror("Error", "Percentages must sum to 100.")
            return
        self.result = self.values
        self.destroy()


# ===================== Percentage Logic =====================
def parse_percent_list(s: str, expected_len: int) -> List[int]:
    parts = [p.strip() for p in s.replace('%','').split(',') if p.strip() != ""]
    vals = []
    for p in parts:
        if not p.isdigit():
            raise ValueError(f"'{p}' is not an integer percentage")
        v = int(p)
        if v < 0 or v > 100:
            raise ValueError(f"Percentage out of range: {v}")
        vals.append(v)
    if len(vals) != expected_len:
        raise ValueError(f"Expected {expected_len} values, got {len(vals)}")
    if sum(vals) != 100:
        raise ValueError(f"Percentages must sum to 100 (got {sum(vals)})")
    return vals


def largest_remainder_counts(percentages: List[int], total: int) -> List[int]:
    quotas = [p * total / 100.0 for p in percentages]
    floors = [int(math.floor(q)) for q in quotas]
    rem = total - sum(floors)
    remainders = [(quotas[i]-floors[i], i) for i in range(len(percentages))]
    remainders.sort(reverse=True)
    counts = floors[:]
    i=0
    while rem>0 and i<len(remainders):
        _, idx = remainders[i]
        counts[idx] += 1
        rem -=1
        i+=1
    return counts


def deterministic_assignment(options: List[str], percentages: List[int], total_subs: int, seed_key: str) -> List[str]:
    counts = largest_remainder_counts(percentages, total_subs)
    bucket = []
    for opt, c in zip(options, counts):
        bucket.extend([opt]*c)
    rnd = random.Random(abs(hash(seed_key)) & 0xFFFFFFFF)
    rnd.shuffle(bucket)
    while len(bucket)<total_subs:
        bucket.append(options[0])
    return bucket[:total_subs]


# ===================== Main App =====================
class GoogleFormsBotApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Google Forms Bot")
        self.root.geometry("840x680")
        self.root.resizable(False, False)

        # Structure: { qid: {"open_ended": bool, "options": [{"text":str,"perc":int}], "responses":[str]}}
        self.questions: Dict[str, Dict[str, Any]] = {}

        # URL
        tk.Label(root, text="Google Form URL (viewform):", font=("Arial", 12)).pack(pady=(8,4))
        self.url_entry = tk.Entry(root, width=100)
        self.url_entry.pack(pady=4)

        # Buttons row
        btns = tk.Frame(root)
        btns.pack(pady=6)
        tk.Button(btns, text="📥 Import JSON", command=self.import_json).pack(side="left", padx=5)
        tk.Button(btns, text="➕ Add Question", command=self.add_question).pack(side="left", padx=5)
        tk.Button(btns, text="✏️ Edit Question", command=self.edit_question).pack(side="left", padx=5)
        tk.Button(btns, text="🗑️ Delete Question", command=self.delete_question).pack(side="left", padx=5)

        # Display
        self.display = scrolledtext.ScrolledText(root, width=100, height=26, state="disabled")
        self.display.pack(pady=10)

        # Submissions
        bottom = tk.Frame(root)
        bottom.pack(pady=6)
        tk.Label(bottom, text="Number of submissions:", font=("Arial",12)).pack(side="left")
        self.submissions_entry = tk.Entry(bottom,width=10)
        self.submissions_entry.pack(side="left", padx=6)
        tk.Button(bottom,text="🚀 Start Submissions",command=self.start_submissions).pack(side="left", padx=12)

        # Progress bar
        self.progress = ttk.Progressbar(root,length=800,mode='determinate')
        self.progress.pack(pady=(6,2))

        # Watermark
        tk.Label(root,text="Copyright https://github.com/zaaccha-ry V 1.0 (Aug 2025)", font=("Arial",9), fg="gray").pack(side="bottom", pady=6)

    # ---------- Display ----------
    def update_display(self):
        self.display.config(state="normal")
        self.display.delete("1.0", tk.END)
        for qid, q in self.questions.items():
            if q.get("open_ended"):
                self.display.insert(tk.END,f"QID {qid} — Open-ended\n")
                self.display.insert(tk.END,f" Responses ({len(q.get('responses',[]))}): {q.get('responses',[])}\n")
            else:
                self.display.insert(tk.END,f"QID {qid} — Closed (percentages)\n")
                for opt in q["options"]:
                    self.display.insert(tk.END,f" {opt['text']} — {opt['perc']}%\n")
        self.display.config(state="disabled")

    # ---------- Import JSON ----------
    def import_json(self):
        raw = simpledialog.askstring("Import JSON","Paste the JSON from the JS snippet:")
        if not raw: return
        try:
            data = json.loads(raw)
        except Exception as e:
            messagebox.showerror("Error",f"Invalid JSON:\n{e}")
            return
        # Parse each question
        for qid, meta in data.items():
            open_ended = bool(meta.get("open_ended"))
            if open_ended:
                resp_text = prompt_multiline(f"Open-ended responses for {qid}")
                responses = [line.strip() for line in resp_text.splitlines() if line.strip() and not line.startswith('Enter one') and not line.startswith('(')]
                self.questions[qid] = {"open_ended": True, "responses": responses, "options": []}
            else:
                raw_options = meta.get("options",[])
                if not raw_options:
                    self.questions[qid] = {"open_ended": True, "responses": [], "options": []}
                    continue

                # ==== NEW: Use Slider Chooser instead of text entry ====
                chooser = PercentageChooser(f"Set percentages for {qid}", raw_options)
                chooser.wait_window()
                if chooser.result is None:
                    continue
                options = [{"text": t,"perc":p} for t,p in zip(raw_options,chooser.result)]
                self.questions[qid] = {"open_ended": False,"options":options,"responses":[]}
        self.update_display()

    # ---------- Add / Edit / Delete ----------
    def add_question(self):
        qid = simpledialog.askstring("Add Question","Enter QID (e.g., entry.123456):")
        if not qid: return
        is_open = messagebox.askyesno("Question Type","Is this question open-ended?")
        if is_open:
            txt = prompt_multiline("Open-ended responses","")
            responses = [line.strip() for line in txt.splitlines() if line.strip()]
            self.questions[qid] = {"open_ended":True,"responses":responses,"options":[]}
        else:
            n = simpledialog.askinteger("Closed Options","How many options?",minvalue=1)
            if not n: return
            opts = []
            for i in range(n):
                t = simpledialog.askstring("Option Text",f"Text for option {i+1}:")
                if t is None: return
                opts.append(t.strip())

            chooser = PercentageChooser(f"Set percentages for {qid}", opts)
            chooser.wait_window()
            if chooser.result is None:
                return
            self.questions[qid] = {"open_ended":False,"options":[{"text":t,"perc":p} for t,p in zip(opts,chooser.result)],"responses":[]}
        self.update_display()

    def edit_question(self):
        if not self.questions:
            messagebox.showwarning("Warning","No questions to edit.")
            return
        qid = simpledialog.askstring("Edit Question","Enter QID to edit:")
        if not qid or qid not in self.questions:
            messagebox.showerror("Error","QID not found.")
            return
        q = self.questions[qid]
        if q.get("open_ended"):
            txt = prompt_multiline(f"Edit open-ended responses for {qid}","\n".join(q.get("responses",[])))
            if txt != "":
                q["responses"] = [line.strip() for line in txt.splitlines() if line.strip()]
        else:
            new_opts = [o["text"] for o in q["options"]]
            chooser = PercentageChooser(f"Edit percentages for {qid}", new_opts)
            chooser.wait_window()
            if chooser.result is not None:
                q["options"] = [{"text":t,"perc":p} for t,p in zip(new_opts,chooser.result)]
        self.update_display()

    def delete_question(self):
        if not self.questions:
            messagebox.showwarning("Warning","No questions to delete.")
            return
        qid = simpledialog.askstring("Delete Question","Enter QID to delete:")
        if qid in self.questions:
            del self.questions[qid]
            self.update_display()
        else:
            messagebox.showerror("Error","QID not found.")

    # ---------- Submissions ----------
    def start_submissions(self):
        url = self.url_entry.get().strip()
        if not url or "viewform" not in url:
            messagebox.showerror("Error","Enter a valid Google Form viewform URL.")
            return
        try:
            total = int(self.submissions_entry.get())
            if total <= 0: raise ValueError
        except Exception:
            messagebox.showerror("Error","Enter a valid positive integer for submissions.")
            return
        if not self.questions:
            messagebox.showerror("Error","No questions added.")
            return
        form_url = url.rsplit('/',1)[0] + '/formResponse'

        closed_assignments: Dict[str,List[str]] = {}
        for qid,q in self.questions.items():
            if not q.get("open_ended"):
                options = [o["text"] for o in q["options"]]
                pcts = [o["perc"] for o in q["options"]]
                closed_assignments[qid] = deterministic_assignment(options,pcts,total,seed_key=qid)

        self.progress["maximum"] = total
        self.progress["value"] = 0
        self.root.update_idletasks()

        session = requests.Session()
        success = 0
        for i in range(total):
            data = {}
            for qid,q in self.questions.items():
                if q.get("open_ended"):
                    responses = q.get("responses",[])
                    data[qid] = random.choice(responses) if responses else ""
                else:
                    data[qid] = closed_assignments[qid][i]
            try:
                r = session.post(form_url,data=data,timeout=10)
                if r.status_code == 200: success+=1
            except Exception:
                pass
            self.progress["value"] = i+1
            self.root.update_idletasks()
        messagebox.showinfo("Done",f"Submitted {success}/{total} responses successfully!")


# ===================== Run App =====================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    show_instructions(root)
    root.deiconify()
    app = GoogleFormsBotApp(root)
    root.mainloop()
