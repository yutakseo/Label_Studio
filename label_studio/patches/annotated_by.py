"""Restore author-only attribution; editing/importing metadata is not authorship."""
from pathlib import Path
import argparse

REPLACEMENTS = (
    ("def add_user_filter(enabled, key, _filter, filter_expressions):\n", """def add_user_filter(enabled, key, _filter, filter_expressions):
    if enabled and key == 'annotations__completed_by':
        if _filter.operator in (Operator.CONTAINS, Operator.NOT_CONTAINS):
            actor = int(_filter.value)
            condition = Q(annotations__completed_by=actor) | Q(
                annotations__completed_by__isnull=True, annotations__updated_by=actor)
            filter_expressions.append(condition if _filter.operator == Operator.CONTAINS else ~condition)
            return 'continue'
        if _filter.operator == Operator.EMPTY:
            condition = Q(annotations__completed_by__isnull=True, annotations__updated_by__isnull=True)
            filter_expressions.append(condition if cast_bool_from_str(_filter.value) else ~condition)
            return 'continue'
"""),
    ("GroupConcat('annotations__completed_by')", "GroupConcat(Coalesce('annotations__completed_by', 'annotations__updated_by'))"),
    ("ArrayAgg('annotations__completed_by', distinct=True, default=Value([]))", "ArrayAgg(Coalesce('annotations__completed_by', 'annotations__updated_by'), distinct=True, default=Value([]))"),
)


def patch(source):
    for original, fallback in REPLACEMENTS:
        if source.count(fallback) == 1:
            source = source.replace(fallback, original)
        elif source.count(original) != 1:
            raise ValueError(f'Unsupported data manager: {original}')
    return source


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    source = args.source.read_text()
    result = patch(source)
    if result != source:
        args.source.write_text(result)
