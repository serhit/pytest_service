from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


class ConfigType(str, Enum):
    file_type_1 = 'file-type-1'
    file_type_2 = 'file-type-2'


class TestResult(BaseModel):
    id: str
    outcome: str
    rule: str
    line_no: Optional[int] = None
    field_name: Optional[str] = None
    ref: Optional[str] = None


class FileValidationResult(BaseModel):
    file_name: str
    result: int
    passed_cnt: int
    failed_cnt: int
    xfailed_cnt: int
    skipped_cnt: int
    total_duration_sec: float
    failed_tests: List[TestResult]
    version: str = None
