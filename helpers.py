import os
import yaml
from typing import Dict, Literal

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, MetaData

IfExists = Literal["fail", "replace", "append"]


def dataframes_to_excel(
        dataframes: Dict[str, pd.DataFrame], excel_full_path: str
) -> None:
    """
    Export DataFrames to an Excel file from a dict like keys=sheet names and values=DataFrame
    :param dataframes: DataFrames as Dict[sheet_name, data]
    :param excel_full_path: full path of the Excel File
    :return: None
    """
    os.makedirs(os.path.dirname(excel_full_path), exist_ok=True)

    with pd.ExcelWriter(excel_full_path) as writer:
        for sheet, df in dataframes.items():
            if isinstance(df, pd.Series):
                df.to_frame().to_excel(writer, sheet_name=sheet, merge_cells=False, index=True)
            elif isinstance(df.columns, pd.MultiIndex):
                df.to_excel(writer, sheet_name=sheet, merge_cells=False)
            elif df.index.dtype == np.int64 and df.index.nlevels == 1:
                df.to_excel(writer, sheet_name=sheet, merge_cells=False, index=False)
            else:
                df.to_excel(writer, sheet_name=sheet, merge_cells=False, index=True)


def dataframes_to_db(
        dataframes: Dict[str, pd.DataFrame],
        db_path: str,
        drop_all_tables: bool = False,
        append_data: bool = False,
):
    """
    Create a SQLite database from a dict like keys=sheet names and values=DataFrame
    If the SQLite database already exists, current data (before this new insertion) could be kept or erased with the
    drop_all_tables parameter
    :param dataframes: DataFrames as Dict(sheet_name, Data)
    :param db_path: full database path
    :param drop_all_tables: if true, all tables will be deleted
    :param append_data: if True, data will be added to the current table. If False, current data will be erased before
    the insertion
    :return: None
    """
    path, _ = os.path.split(db_path)
    os.makedirs(path, exist_ok=True)

    engine = create_engine(f"sqlite:///{db_path}", echo=True)
    con = engine.connect()
    meta = MetaData()

    if drop_all_tables:
        meta.drop_all(con)

    if append_data:
        if_exists: IfExists = "append"
    else:
        if_exists: IfExists = "replace"

    for sh, df in dataframes.items():
        df.to_sql(name=sh, con=con, if_exists=if_exists, index=False)


def to_db_format(name: str) -> str:
    """
    Format a column name to a database column name - no space and lower case
    :param name:
    :return:
    """
    return name.strip().lower().replace(" ", "_")

def get_serialized_data(path: str) -> Dict:
    """
    Reads and deserializes data from a file based on its extension. Supported formats are YAML, JSON, and TOML.

    This function opens the file at the specified path, identifies its extension, and deserializes its content
    into a Python dictionary or list (depending on the format). The following file extensions are supported:
    - `.yaml` or `.yml` (YAML format)
    - `.json` (JSON format)
    - `.toml` (TOML format)

    If the file extension is unsupported, a `ValueError` is raised.

    :param path: The file path of the serialized data to be loaded.
                  This must be a valid path to a file with a supported extension (.yaml, .json, or .toml).
    :return: A Python dictionary or list containing the deserialized data.
             The return type depends on the content of the file (e.g., a dictionary for JSON and TOML, a list or dictionary for YAML).
    :raises ValueError: If the file extension is not supported or the file cannot be opened.
    """
    _, extension = os.path.splitext(path)

    with open(path, mode="r", encoding="utf-8") as file:
        if extension == ".yaml":
            return yaml.safe_load(file)
        elif extension == ".json":
            return json.load(file)
        elif extension == ".toml":
            return toml.load(file)

        raise ValueError(f"Unsupported file extension {extension} | file={path}")

