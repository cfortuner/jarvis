"""Memory profiling tools.

https://pympler.readthedocs.io/en/latest/
https://docs.python.org/3.7/library/tracemalloc.html
https://stackify.com/top-5-python-memory-profilers/
https://pypi.org/project/memory-profiler/
https://pypi.org/project/filprofiler/
https://pypi.org/project/guppy3/


fil-profile run scratch/pympler_demo.py
python -m memory_profiler scratch/pympler_demo.py
"""
from dataclasses import dataclass
import pympler
from pympler import asizeof
from pympler import classtracker
from pympler import tracker


@dataclass
class SubDocument:
    name: str
    value: int


@dataclass
class Document:
    sub: SubDocument
    doc: str


def _create_doc(i: int):
    return Document(sub=SubDocument("brendan", i), doc=f"Hello Brendan {i}")


def _create_documents():
    docs = []
    for i in range(10000):
        docs.append(_create_doc(i))
    return docs


import time
from memory_profiler import profile


@profile
def run():
    docs = []
    for i in range(10):
        time.sleep(0.5)
        docs = _create_documents()


def inspect_object():
    obj = [1, 2, (3, 4), "text"]
    print(pympler.asizeof.asizeof(obj))
    print(asizeof.asized(obj, detail=1).format())


def track_leaks():
    # https://pympler.readthedocs.io/en/latest/tutorials/muppy_tutorial.html
    tr = tracker.SummaryTracker()
    docs = _create_documents()
    tr.print_diff()


def track_instance():
    tr = classtracker.ClassTracker()
    obj = _create_doc(0)
    tracker.track_object(obj)


def track_class():
    # Track all instances of a class
    tr = classtracker.ClassTracker()
    tr.track_class(Document)
    tr.create_snapshot()
    docs = _create_documents()
    tr.create_snapshot()
    tr.stats.print_summary()


if __name__ == "__main__":
    # track_leaks()
    # track_class()
    run()
