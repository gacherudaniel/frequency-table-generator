"""
core.py
-------
All the "business logic" for reading a Stata (.dta) file, classifying
variables, computing weighted/unweighted frequency tables, and exporting a
formatted Excel workbook.

This module has NO Flask code in it on purpose — it can be tested and reused
independently of the web app.
"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import xlsxwriter


# ---------------------------------------------------------------------------
# Reading the dataset
# ---------------------------------------------------------------------------
def load_stata_dataset(filepath: Path):
    """Load a .dta file, returning (df, meta). Raises RuntimeError on failure."""
    try:
        df, meta = pyreadstat.read_dta(str(filepath), apply_value_formats=False)
    except Exception as exc:
        raise RuntimeError(
            f"Could not read '{filepath.name}' as a Stata file. "
            f"Please make sure it is a valid .dta file.\nDetails: {exc}"
        )
    return df, meta


def build_variable_overview(df: pd.DataFrame, meta) -> list[dict]:
    """Return a list of {index, name, dtype, label} for display in the UI."""
    var_labels = dict(zip(meta.column_names, meta.column_labels)) if meta.column_labels else {}
    overview = []
    for i, col in enumerate(df.columns, start=1):
        overview.append({
            "index": i,
            "name": col,
            "dtype": str(df[col].dtype),
            "label": var_labels.get(col, "") or "",
            "n_unique": int(df[col].nunique(dropna=True)),
        })
    return overview


# ---------------------------------------------------------------------------
# Variable classification
# ---------------------------------------------------------------------------
def is_id_variable(series: pd.Series, varname: str) -> bool:
    name = varname.lower()
    name_suggests_id = (
        name in {"id"} or name.endswith("_id") or name.endswith("id") or name.startswith("id_")
    )
    non_missing = series.dropna()
    is_fully_unique = len(non_missing) > 0 and non_missing.is_unique and len(non_missing) == len(series)
    return name_suggests_id or is_fully_unique


def is_continuous_variable(series: pd.Series, varname: str, meta, max_categories: int) -> bool:
    if not pd.api.types.is_numeric_dtype(series):
        return False
    has_value_labels = varname in (meta.variable_to_label or {})
    n_unique = series.nunique(dropna=True)
    return (not has_value_labels) and (n_unique > max_categories)


def classify_variable(series: pd.Series, varname: str, meta, options: dict) -> str:
    """Returns 'include', 'skip_id', 'skip_continuous', or 'skip_too_many_categories'."""
    if options["exclude_id_vars"] and is_id_variable(series, varname):
        return "skip_id"
    if (options["exclude_continuous"] or options["categorical_only"]) and \
            is_continuous_variable(series, varname, meta, options["max_categories"]):
        return "skip_continuous"
    if series.nunique(dropna=True) > options["max_categories"]:
        return "skip_too_many_categories"
    return "include"


# ---------------------------------------------------------------------------
# Frequency table computation
# ---------------------------------------------------------------------------
def get_value_labels_for(varname: str, meta) -> dict:
    label_set_name = (meta.variable_to_label or {}).get(varname)
    if not label_set_name:
        return {}
    return (meta.value_labels or {}).get(label_set_name, {})


def build_weight_series(df: pd.DataFrame, weight_var, weight_value):
    """
    Build the weight series to apply to every row, plus a human-readable label
    describing where the weight came from.

    A weight can come from either:
      - `weight_var`: the name of a column already present in the dataset
        (e.g. a survey design weight computed elsewhere), or
      - `weight_value`: a single constant number (e.g. 1/p) typed in by the
        user, applied uniformly to every observation. This is useful when the
        dataset does not contain a weight variable but the sampling fraction
        (and therefore the design weight) is known.

    Returns (weight_series_or_None, label_or_None).
    """
    if weight_var:
        return df[weight_var].astype(float), f"Variable: {weight_var}"
    if weight_value is not None:
        return pd.Series(float(weight_value), index=df.index), f"Constant value: {weight_value}"
    return None, None


def compute_frequency_table(df: pd.DataFrame, varname: str, weight_series, meta) -> pd.DataFrame:
    series = df[varname]
    value_labels = get_value_labels_for(varname, meta)

    working = pd.DataFrame({"value": series})
    working["value_display"] = working["value"].map(
        lambda v: value_labels.get(v, v) if pd.notna(v) else "Missing"
    )

    if weight_series is not None:
        working["weight"] = weight_series.values
        grouped = working.groupby("value_display", dropna=False)["weight"].sum()
        freq_col_name = "Weighted Frequency"
    else:
        grouped = working.groupby("value_display", dropna=False).size()
        freq_col_name = "Frequency"

    total = grouped.sum()
    result = grouped.reset_index()
    result.columns = ["Category", freq_col_name]

    percent_col_name = "Weighted Percent" if weight_series is not None else "Percent"
    result[percent_col_name] = (result[freq_col_name] / total * 100) if total else 0.0

    result["_is_missing"] = (result["Category"] == "Missing").astype(int)
    result = result.sort_values(["_is_missing"]).drop(columns="_is_missing").reset_index(drop=True)
    return result


def generate_all_frequency_tables(df: pd.DataFrame, meta, weight_series, options: dict,
                                   progress_callback=None):
    """
    Loop through every variable, classify it, and compute a frequency table
    for included variables.

    progress_callback(done, total, varname) is called after each variable, if given.
    """
    results = {}
    skipped = []

    skip_reason_text = {
        "skip_id": "Identified as an ID variable",
        "skip_continuous": "Identified as a continuous numeric variable",
        "skip_too_many_categories": f"More than {options['max_categories']} distinct categories",
    }

    total = len(df.columns)
    for i, varname in enumerate(df.columns, start=1):
        decision = classify_variable(df[varname], varname, meta, options)

        if decision != "include":
            skipped.append({"Variable": varname, "Reason": skip_reason_text[decision]})
        else:
            try:
                results[varname] = compute_frequency_table(df, varname, weight_series, meta)
            except Exception as exc:
                skipped.append({"Variable": varname, "Reason": f"Error during processing: {exc}"})

        if progress_callback:
            progress_callback(i, total, varname)

    return results, skipped


# ---------------------------------------------------------------------------
# Excel export
# ---------------------------------------------------------------------------
def sanitize_sheet_name(name: str, used_names: set) -> str:
    invalid_chars = ["[", "]", ":", "*", "?", "/", "\\"]
    clean = name
    for ch in invalid_chars:
        clean = clean.replace(ch, "_")
    clean = clean[:31] if clean else "Variable"

    original_clean = clean
    counter = 1
    while clean in used_names:
        suffix = f"_{counter}"
        clean = original_clean[: 31 - len(suffix)] + suffix
        counter += 1

    used_names.add(clean)
    return clean


def write_variable_sheet(worksheet, varname, table: pd.DataFrame, meta, weight_label, formats):
    var_labels = dict(zip(meta.column_names, meta.column_labels)) if meta.column_labels else {}
    label = var_labels.get(varname, "") or "(no label)"

    row = 0
    worksheet.write(row, 0, "Variable Name:", formats["bold"])
    worksheet.write(row, 1, varname, formats["bold"])
    row += 1

    worksheet.write(row, 0, "Variable Label:", formats["bold"])
    worksheet.write(row, 1, label)
    row += 1

    worksheet.write(row, 0, "Analysis Type:", formats["bold"])
    worksheet.write(row, 1, "Weighted" if weight_label else "Unweighted")
    row += 1

    if weight_label:
        worksheet.write(row, 0, "Weight Source:", formats["bold"])
        worksheet.write(row, 1, weight_label)
        row += 1

    row += 1
    table_start_row = row

    for col_idx, col_name in enumerate(table.columns):
        worksheet.write(table_start_row, col_idx, col_name, formats["header"])

    percent_col_idx = list(table.columns).index(
        "Weighted Percent" if "Weighted Percent" in table.columns else "Percent"
    )
    for r_idx, (_, data_row) in enumerate(table.iterrows(), start=1):
        for c_idx, col_name in enumerate(table.columns):
            value = data_row[col_name]
            if c_idx == percent_col_idx:
                worksheet.write_number(table_start_row + r_idx, c_idx, float(value), formats["percent"])
            elif isinstance(value, (int, float, np.integer, np.floating)):
                worksheet.write_number(table_start_row + r_idx, c_idx, float(value), formats["number"])
            else:
                worksheet.write(table_start_row + r_idx, c_idx, str(value))

    worksheet.freeze_panes(table_start_row + 1, 0)

    for c_idx, col_name in enumerate(table.columns):
        max_len = max([len(str(col_name))] + [len(str(v)) for v in table[col_name].astype(str)])
        worksheet.set_column(c_idx, c_idx, max_len + 4)
    worksheet.set_column(1, 1, 20)


def write_summary_sheet(worksheet, summary_info: dict, skipped: list, formats):
    worksheet.write(0, 0, "Frequency Table Generation — Summary", formats["title"])

    row = 2
    for key, value in summary_info.items():
        worksheet.write(row, 0, key, formats["bold"])
        worksheet.write(row, 1, value)
        row += 1

    row += 1
    worksheet.write(row, 0, "Skipped Variables", formats["bold"])
    row += 1

    if skipped:
        worksheet.write(row, 0, "Variable", formats["header"])
        worksheet.write(row, 1, "Reason Skipped", formats["header"])
        row += 1
        for item in skipped:
            worksheet.write(row, 0, item["Variable"])
            worksheet.write(row, 1, item["Reason"])
            row += 1
    else:
        worksheet.write(row, 0, "None — all variables were processed successfully.")

    worksheet.set_column(0, 0, 30)
    worksheet.set_column(1, 1, 50)
    worksheet.freeze_panes(1, 0)


def export_to_excel(output_path: Path, tables: dict, meta, weight_label,
                     summary_info: dict, skipped: list) -> Path:
    workbook = xlsxwriter.Workbook(str(output_path))

    formats = {
        "title": workbook.add_format({"bold": True, "font_size": 14}),
        "bold": workbook.add_format({"bold": True}),
        "header": workbook.add_format({
            "bold": True, "bg_color": "#4472C4", "font_color": "white",
            "border": 1, "align": "center",
        }),
        "percent": workbook.add_format({"num_format": "0.00"}),
        "number": workbook.add_format({"num_format": "#,##0"}),
    }

    summary_ws = workbook.add_worksheet("Summary")
    write_summary_sheet(summary_ws, summary_info, skipped, formats)

    used_names = {"Summary"}
    for varname, table in tables.items():
        sheet_name = sanitize_sheet_name(varname, used_names)
        worksheet = workbook.add_worksheet(sheet_name)
        write_variable_sheet(worksheet, varname, table, meta, weight_label, formats)

    workbook.close()
    return output_path


# ---------------------------------------------------------------------------
# End-to-end convenience function used by the Flask route
# ---------------------------------------------------------------------------
def run_full_pipeline(dta_path: Path, output_path: Path, dataset_name: str,
                       weight_var, weight_value, options: dict, progress_callback=None):
    """Read dataset, generate tables, export to Excel. Returns a summary dict.

    `weight_var` is the name of a weight column already present in the
    dataset. `weight_value` is a constant numeric weight (e.g. 1/p, the
    design weight) to apply to every observation when the dataset itself has
    no weight column. At most one of the two should be set.
    """
    start = time.time()
    df, meta = load_stata_dataset(dta_path)

    weight_series, weight_label = build_weight_series(df, weight_var, weight_value)

    tables, skipped = generate_all_frequency_tables(
        df, meta, weight_series, options, progress_callback=progress_callback
    )

    summary_info = {
        "Dataset Name": dataset_name,
        "Date Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Number of Variables": df.shape[1],
        "Number of Observations": len(df),
        "Weight Source Used": weight_label if weight_label else "None (unweighted)",
        "Analysis Type": "Weighted" if weight_label else "Unweighted",
        "Variables Successfully Processed": len(tables),
        "Variables Skipped": len(skipped),
    }
    elapsed = time.time() - start
    summary_info["Execution Time"] = f"{elapsed:.2f} seconds"

    export_to_excel(output_path, tables, meta, weight_label, summary_info, skipped)

    return {
        "summary": summary_info,
        "skipped": skipped,
        "n_processed": len(tables),
        "n_skipped": len(skipped),
        "elapsed": elapsed,
    }
