from dataclasses import dataclass
from typing import List

import pandas as pd

from RCS.google.schema import RCSDataForCheck


@dataclass(frozen=True, slots=True)
class CountryMsisdn:
    country: str
    msisdns: List[str]


@dataclass(slots=True)
class SummaryRecord:
    country: str
    checked_msisdn: int
    totalRandomSampleUserCount: int
    reachableRandomSampleUserCount: int


class ExcellReader:

    def __init__(self, in_file):
        self.book = pd.read_excel(in_file, sheet_name=None)

    def get_data_for_check(self) -> List[RCSDataForCheck]:
        sheet_names = self.book.keys()
        data = []
        for sheet_name in sheet_names:
            msisdns = []
            df = self.book[sheet_name]
            for _, row in df.iterrows():
                for _, phone in row.items():
                    if not str(phone).startswith('+'):
                        phone = f'+{phone}'

                    msisdns.append(phone)

            data.append(RCSDataForCheck(country=sheet_name, msisdns=msisdns))

        return data


class ExcellWriter:

    def __init__(self, in_file) -> None:
        self.writer = pd.ExcelWriter(in_file, engine="xlsxwriter")

    def add_sheet(self, df: pd.DataFrame, sheet_name) -> None:
        df.to_excel(excel_writer=self.writer, sheet_name=sheet_name, index=False)

    def close_writer(self) -> None:
        self.writer.close()
