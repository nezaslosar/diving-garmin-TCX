from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

LJUBLJANA_TZ = ZoneInfo("Europe/Ljubljana")
UTC_TZ = ZoneInfo("UTC")


TEXTS = {
    "sl": {
        "lang_name": "Slovenščina",
        "select_language": "Izberi jezik",
        "continue": "Naprej",
        "title": "Potapljanje → Garmin TCX",
        "basic_data": "Osnovni podatki",
        "met_section": "Poraba / MET",
        "date": "Datum",
        "date_hint": "izberi v koledarju",
        "start": "Začetek",
        "time_hint": "HH:MM",
        "duration": "Trajanje",
        "duration_unit": "min",
        "weight": "Teža",
        "weight_hint": "kg (brez opreme)",
        "base_met": "Osnovni MET",
        "current": "Tok",
        "extra_conditions": "Dodatni pogoji",
        "cold": "hladna voda / mraz (+0.4)",
        "effort": "več plavanja / napor (+0.4)",
        "generate": "Ustvari TCX datoteko",
        "done": "Končano",
        "saved": "Shranjeno",
        "duration_line": "Trajanje",
        "calories_line": "Kalorije",
        "base_met_line": "Osnovni MET",
        "current_adj_line": "Popravek za tok",
        "extra_adj_line": "Dodatni popravek",
        "final_met_line": "Končni MET",
        "error": "Napaka",
        "select_valid": "Izberi veljaven MET in tok.",
        "duration_error": "Trajanje mora biti celo število med 1 in 600.",
        "weight_error": "Teža mora biti pozitivno število.",
        "datetime_error": "Datum ali ura nista veljavna.",
        "met_options": [
            ("6.0 – zelo miren potop", 6.0),
            ("6.5 – miren potop", 6.5),
            ("6.8 – normalen potop", 6.8),
            ("7.5 – bolj naporen potop", 7.5),
            ("8.0 – naporen potop", 8.0),
        ],
        "current_options": [
            ("brez toka", 0.0),
            ("srednje močan tok (+0.4)", 0.4),
            ("močan tok (+0.8)", 0.8),
        ],
        "output_folder": "Potapljanje_TCX",
    },
    "en": {
        "lang_name": "English",
        "select_language": "Select language",
        "continue": "Continue",
        "title": "Diving → Garmin TCX",
        "basic_data": "Basic data",
        "met_section": "Energy / MET",
        "date": "Date",
        "date_hint": "choose from calendar",
        "start": "Start",
        "time_hint": "HH:MM",
        "duration": "Duration",
        "duration_unit": "min",
        "weight": "Weight",
        "weight_hint": "kg (without gear)",
        "base_met": "Base MET",
        "current": "Current",
        "extra_conditions": "Additional conditions",
        "cold": "cold water / cold (+0.4)",
        "effort": "more swimming / effort (+0.4)",
        "generate": "Create TCX file",
        "done": "Done",
        "saved": "Saved",
        "duration_line": "Duration",
        "calories_line": "Calories",
        "base_met_line": "Base MET",
        "current_adj_line": "Current adjustment",
        "extra_adj_line": "Additional adjustment",
        "final_met_line": "Final MET",
        "error": "Error",
        "select_valid": "Select a valid MET and current option.",
        "duration_error": "Duration must be an integer between 1 and 600.",
        "weight_error": "Weight must be a positive number.",
        "datetime_error": "Date or time is not valid.",
        "met_options": [
            ("6.0 – very calm dive", 6.0),
            ("6.5 – calm dive", 6.5),
            ("6.8 – normal dive", 6.8),
            ("7.5 – more demanding dive", 7.5),
            ("8.0 – demanding dive", 8.0),
        ],
        "current_options": [
            ("no current", 0.0),
            ("moderate current (+0.4)", 0.4),
            ("strong current (+0.8)", 0.8),
        ],
        "output_folder": "Diving_TCX",
    },
}


@dataclass
class DiveEntry:
    start_dt: datetime
    duration_min: int
    weight_kg: float
    met: float

    @property
    def end_dt(self) -> datetime:
        return self.start_dt + timedelta(minutes=self.duration_min)

    @property
    def calories(self) -> int:
        return max(0, int(round(self.met * self.weight_kg * (self.duration_min / 60.0))))


def build_tcx(entry: DiveEntry) -> ET.ElementTree:
    ET.register_namespace("", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

    start_utc = entry.start_dt.astimezone(UTC_TZ)
    start_str = start_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    root = ET.Element(
        "{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}TrainingCenterDatabase",
        {
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation":
                "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 "
                "http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
        },
    )

    activities = ET.SubElement(root, "Activities")
    activity = ET.SubElement(activities, "Activity", {"Sport": "Other"})
    ET.SubElement(activity, "Id").text = start_str

    lap = ET.SubElement(activity, "Lap", {"StartTime": start_str})
    ET.SubElement(lap, "TotalTimeSeconds").text = str(entry.duration_min * 60)
    ET.SubElement(lap, "DistanceMeters").text = "0.0"
    ET.SubElement(lap, "Calories").text = str(entry.calories)
    ET.SubElement(lap, "Intensity").text = "Active"
    ET.SubElement(lap, "TriggerMethod").text = "Manual"

    return ET.ElementTree(root)


class LanguageSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Language / Jezik")
        self.resizable(False, False)

        self.selected_language = tk.StringVar(value="sl")

        frame = ttk.Frame(self, padding=16)
        frame.grid(row=0, column=0)

        ttk.Label(frame, text="Izberi jezik / Select language", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        ttk.Radiobutton(
            frame, text=TEXTS["sl"]["lang_name"], variable=self.selected_language, value="sl"
        ).grid(row=1, column=0, sticky="w", pady=4)

        ttk.Radiobutton(
            frame, text=TEXTS["en"]["lang_name"], variable=self.selected_language, value="en"
        ).grid(row=2, column=0, sticky="w", pady=4)

        ttk.Button(frame, text="OK", command=self.finish).grid(row=3, column=0, sticky="ew", pady=(12, 0))

        self.result = None

    def finish(self):
        self.result = self.selected_language.get()
        self.destroy()


class App(tk.Tk):
    def __init__(self, lang: str):
        super().__init__()
        self.lang = lang
        self.t = TEXTS[lang]

        self.title(self.t["title"])
        self.resizable(False, False)

        self._build_style()

        outer = ttk.Frame(self, padding=16)
        outer.grid(row=0, column=0, sticky="nsew")

        title = ttk.Label(
            outer,
            text=self.t["title"],
            style="Title.TLabel"
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))

        now = datetime.now(LJUBLJANA_TZ)

        self.var_duration = tk.StringVar(value="50")
        self.var_weight = tk.StringVar(value="65")
        self.var_hour = tk.StringVar(value=now.strftime("%H"))
        self.var_minute = tk.StringVar(value=now.strftime("%M"))
        self.var_met_label = tk.StringVar(value=self.t["met_options"][2][0])
        self.var_current_label = tk.StringVar(value=self.t["current_options"][0][0])

        self.var_cold = tk.BooleanVar(value=False)
        self.var_effort = tk.BooleanVar(value=False)

        basic_frame = ttk.LabelFrame(outer, text=self.t["basic_data"], padding=12)
        basic_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        ttk.Label(basic_frame, text=self.t["date"]).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=4)
        self.date_entry = DateEntry(
            basic_frame,
            width=18,
            date_pattern="dd-mm-y"
        )
        self.date_entry.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(basic_frame, text=self.t["date_hint"]).grid(row=0, column=2, sticky="w", padx=(12, 0), pady=4)

        ttk.Label(basic_frame, text=self.t["start"]).grid(row=1, column=0, sticky="w", padx=(0, 12), pady=4)
        time_frame = ttk.Frame(basic_frame)
        time_frame.grid(row=1, column=1, sticky="w", pady=4)

        tk.Spinbox(
            time_frame,
            from_=0,
            to=23,
            width=3,
            format="%02.0f",
            textvariable=self.var_hour
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(time_frame, text=":").grid(row=0, column=1, padx=4)

        tk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=3,
            format="%02.0f",
            textvariable=self.var_minute
        ).grid(row=0, column=2, sticky="w")

        ttk.Label(basic_frame, text=self.t["time_hint"]).grid(row=1, column=2, sticky="w", padx=(12, 0), pady=4)

        ttk.Label(basic_frame, text=self.t["duration"]).grid(row=2, column=0, sticky="w", padx=(0, 12), pady=4)
        ttk.Entry(basic_frame, textvariable=self.var_duration, width=22).grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(basic_frame, text=self.t["duration_unit"]).grid(row=2, column=2, sticky="w", padx=(12, 0), pady=4)

        ttk.Label(basic_frame, text=self.t["weight"]).grid(row=3, column=0, sticky="w", padx=(0, 12), pady=4)
        ttk.Entry(basic_frame, textvariable=self.var_weight, width=22).grid(row=3, column=1, sticky="w", pady=4)
        ttk.Label(basic_frame, text=self.t["weight_hint"]).grid(row=3, column=2, sticky="w", padx=(12, 0), pady=4)

        met_frame = ttk.LabelFrame(outer, text=self.t["met_section"], padding=12)
        met_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        ttk.Label(met_frame, text=self.t["base_met"]).grid(row=0, column=0, sticky="nw", padx=(0, 12), pady=4)
        self.met_combo = ttk.Combobox(
            met_frame,
            textvariable=self.var_met_label,
            values=[label for label, _ in self.t["met_options"]],
            width=42,
            state="readonly",
        )
        self.met_combo.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(met_frame, text=self.t["current"]).grid(row=1, column=0, sticky="w", padx=(0, 12), pady=4)
        self.current_combo = ttk.Combobox(
            met_frame,
            textvariable=self.var_current_label,
            values=[label for label, _ in self.t["current_options"]],
            width=42,
            state="readonly",
        )
        self.current_combo.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(met_frame, text=self.t["extra_conditions"]).grid(row=2, column=0, sticky="nw", padx=(0, 12), pady=4)

        cond = ttk.Frame(met_frame)
        cond.grid(row=2, column=1, sticky="w", pady=4)

        ttk.Checkbutton(
            cond,
            text=self.t["cold"],
            variable=self.var_cold
        ).grid(row=0, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            cond,
            text=self.t["effort"],
            variable=self.var_effort
        ).grid(row=1, column=0, sticky="w", pady=2)

        button_frame = ttk.Frame(outer)
        button_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(4, 0))

        self.generate_button = ttk.Button(
            button_frame,
            text=self.t["generate"],
            command=self.generate
        )
        self.generate_button.grid(row=0, column=0, sticky="ew")

        self.lbl_out = ttk.Label(
            outer,
            text="",
            wraplength=620,
            justify="left"
        )
        self.lbl_out.grid(row=4, column=0, columnspan=3, sticky="w", pady=(12, 0))

    def _build_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", padding=(10, 6))

    def generate(self):
        try:
            date_s = self.date_entry.get().strip()
            time_s = f"{self.var_hour.get().strip()}:{self.var_minute.get().strip()}"

            duration = int(self.var_duration.get().strip())
            if not (1 <= duration <= 600):
                raise ValueError(self.t["duration_error"])

            weight = float(self.var_weight.get().strip().replace(",", "."))
            if weight <= 0:
                raise ValueError(self.t["weight_error"])

            base_met = next(v for l, v in self.t["met_options"] if l == self.var_met_label.get())
            current_adj = next(v for l, v in self.t["current_options"] if l == self.var_current_label.get())

            extra_adj = 0.0
            if self.var_cold.get():
                extra_adj += 0.4
            if self.var_effort.get():
                extra_adj += 0.4

            final_met = base_met + current_adj + extra_adj

            start_dt = datetime.strptime(f"{date_s} {time_s}", "%d-%m-%Y %H:%M").replace(tzinfo=LJUBLJANA_TZ)

            entry = DiveEntry(
                start_dt=start_dt,
                duration_min=duration,
                weight_kg=weight,
                met=final_met
            )

            tree = build_tcx(entry)

            out_dir = Path.home() / "Downloads" / self.t["output_folder"]
            out_dir.mkdir(parents=True, exist_ok=True)

            file = out_dir / f"diving_{start_dt.strftime('%Y%m%d_%H%M')}.tcx"
            tree.write(file, encoding="utf-8", xml_declaration=True)

            msg = (
                f"{self.t['saved']}:\n{file}\n\n"
                f"{self.t['duration_line']}: {entry.duration_min} {self.t['duration_unit']}\n"
                f"{self.t['calories_line']}: {entry.calories} kcal\n"
                f"{self.t['base_met_line']}: {base_met:.1f}\n"
                f"{self.t['current_adj_line']}: +{current_adj:.1f}\n"
                f"{self.t['extra_adj_line']}: +{extra_adj:.1f}\n"
                f"{self.t['final_met_line']}: {final_met:.1f}"
            )

            self.lbl_out.config(text=msg)
            messagebox.showinfo(self.t["done"], msg)

        except StopIteration:
            messagebox.showerror(self.t["error"], self.t["select_valid"])
        except ValueError as e:
            messagebox.showerror(self.t["error"], str(e))
        except Exception:
            messagebox.showerror(self.t["error"], self.t["datetime_error"])


def main():
    selector = LanguageSelector()
    selector.mainloop()

    selected_lang = selector.result or "sl"

    app = App(selected_lang)
    app.mainloop()


if __name__ == "__main__":
    main()
