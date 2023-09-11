#!/usr/bin/env python
"""Convert an async module to a sync module.
"""

from __future__ import annotations

import os
import sys
from copy import deepcopy
from typing import Any
from pathlib import Path
from argparse import ArgumentParser, Namespace

import ast_comments as ast

# The ast_comment has an import:
#
#   from typing import Dict, List, Tuple, Union
#
# which shadows some of the types defined in ast.
#
# TODO: report the issue upstream
import ast as ast_orig

ast.Dict = ast_orig.Dict
ast.List = ast_orig.List
ast.Tuple = ast_orig.Tuple


def main() -> int:
    opt = parse_cmdline()
    with opt.filepath.open() as f:
        source = f.read()

    tree = ast.parse(source, filename=str(opt.filepath))
    tree = async_to_sync(tree, filepath=opt.filepath)
    output = tree_to_str(tree, opt.filepath)

    if opt.output:
        with open(opt.output, "w") as f:
            print(output, file=f)
    else:
        print(output)

    return 0


def async_to_sync(tree: ast.AST, filepath: Path | None = None) -> ast.AST:
    tree = BlanksInserter().visit(tree)
    tree = RenameAsyncToSync().visit(tree)
    tree = AsyncToSync().visit(tree)
    return tree


def tree_to_str(tree: ast.AST, filepath: Path) -> str:
    rv = f"""\
# WARNING: this file is auto-generated by '{os.path.basename(sys.argv[0])}'
# from the original file '{filepath.name}'
# DO NOT CHANGE! Change the original file instead.
"""
    rv += unparse(tree)
    return rv


# Hint: in order to explore the AST of a module you can run:
# python -m ast path/tp/module.py


class AsyncToSync(ast.NodeTransformer):
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        new_node = ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=node.decorator_list,
            returns=node.returns,
        )
        ast.copy_location(new_node, node)
        self.visit(new_node)
        return new_node

    def visit_AsyncFor(self, node: ast.AsyncFor) -> ast.AST:
        new_node = ast.For(
            target=node.target, iter=node.iter, body=node.body, orelse=node.orelse
        )
        ast.copy_location(new_node, node)
        self.visit(new_node)
        return new_node

    def visit_AsyncWith(self, node: ast.AsyncWith) -> ast.AST:
        new_node = ast.With(items=node.items, body=node.body)
        ast.copy_location(new_node, node)
        self.visit(new_node)
        return new_node

    def visit_Await(self, node: ast.Await) -> ast.AST:
        new_node = node.value
        self.visit(new_node)
        return new_node

    def visit_If(self, node: ast.If) -> ast.AST:
        # Drop `if is_async()` branch.
        #
        # Assume that the test guards an async object becoming sync and remove
        # the async side, because it will likely contain `await` constructs
        # illegal into a sync function.
        if self._is_async_call(node.test):
            for child in node.orelse:
                self.visit(child)
            return node.orelse

        # Manage `if True:  # ASYNC`
        # drop the unneeded branch
        if (stmts := self._async_test_statements(node)) is not None:
            for child in stmts:
                self.visit(child)
            return stmts

        self.generic_visit(node)
        return node

    def _is_async_call(self, test: ast.AST) -> bool:
        if not isinstance(test, ast.Call):
            return False
        if not isinstance(test.func, ast.Name):
            return False
        if test.func.id != "is_async":
            return False
        return True

    def _async_test_statements(self, node: ast.If) -> list[ast.AST] | None:
        if not (
            isinstance(node.test, ast.Constant) and isinstance(node.test.value, bool)
        ):
            return None

        if not (node.body and isinstance(node.body[0], ast.Comment)):
            return None

        comment = node.body[0].value

        if not comment.startswith("# ASYNC"):
            return None

        stmts: list[ast.AST]
        if node.test.value:
            stmts = node.orelse
        else:
            stmts = node.body[1:]  # skip the ASYNC comment
        return stmts


class RenameAsyncToSync(ast.NodeTransformer):
    names_map = {
        "AsyncClientCursor": "ClientCursor",
        "AsyncConnection": "Connection",
        "AsyncCopy": "Copy",
        "AsyncCopyWriter": "CopyWriter",
        "AsyncCursor": "Cursor",
        "AsyncFileWriter": "FileWriter",
        "AsyncGenerator": "Generator",
        "AsyncIterator": "Iterator",
        "AsyncLibpqWriter": "LibpqWriter",
        "AsyncPipeline": "Pipeline",
        "AsyncQueuedLibpqWriter": "QueuedLibpqWriter",
        "AsyncRawCursor": "RawCursor",
        "AsyncRowFactory": "RowFactory",
        "AsyncScheduler": "Scheduler",
        "AsyncServerCursor": "ServerCursor",
        "AsyncTransaction": "Transaction",
        "AsyncWriter": "Writer",
        "__aenter__": "__enter__",
        "__aexit__": "__exit__",
        "__aiter__": "__iter__",
        "aclose": "close",
        "aclosing": "closing",
        "acommands": "commands",
        "aconn": "conn",
        "aconn_cls": "conn_cls",
        "alist": "list",
        "anext": "next",
        "asleep": "sleep",
        "apipeline": "pipeline",
        "asynccontextmanager": "contextmanager",
        "connection_async": "connection",
        "cursor_async": "cursor",
        "ensure_table_async": "ensure_table",
        "find_insert_problem_async": "find_insert_problem",
        "psycopg_pool.sched_async": "psycopg_pool.sched",
        "wait_async": "wait",
        "wait_conn_async": "wait_conn",
    }
    _skip_imports = {
        "utils": {"alist", "anext"},
    }

    def visit_Module(self, node: ast.Module) -> ast.AST:
        self._fix_docstring(node.body)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        self._fix_docstring(node.body)
        node.name = self.names_map.get(node.name, node.name)
        for arg in node.args.args:
            arg.arg = self.names_map.get(arg.arg, arg.arg)
        for arg in node.args.args:
            ann = arg.annotation
            if not ann:
                continue
            if isinstance(ann, ast.Subscript):
                # Remove the [] from the type
                ann = ann.value
            if isinstance(ann, ast.Attribute):
                ann.attr = self.names_map.get(ann.attr, ann.attr)

        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self._fix_docstring(node.body)
        self.generic_visit(node)
        return node

    def _fix_docstring(self, body: list[ast.AST]) -> None:
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body[0].value.value = body[0].value.value.replace("Async", "")

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "TypeVar":
            node = self._visit_Call_TypeVar(node)

        self.generic_visit(node)
        return node

    def _visit_Call_TypeVar(self, node: ast.Call) -> ast.AST:
        for kw in node.keywords:
            if kw.arg != "bound":
                continue
            if not isinstance(kw.value, ast.Constant):
                continue
            if not isinstance(kw.value.value, str):
                continue
            kw.value.value = self._visit_type_string(kw.value.value)

        return node

    def _visit_type_string(self, source: str) -> str:
        # Convert the string to tree, visit, and convert it back to string
        tree = ast.parse(source, type_comments=False)
        tree = async_to_sync(tree)
        rv = unparse(tree)
        return rv

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        self._fix_docstring(node.body)
        node.name = self.names_map.get(node.name, node.name)
        node = self._fix_base_params(node)
        self.generic_visit(node)
        return node

    def _fix_base_params(self, node: ast.ClassDef) -> ast.AST:
        # Handle :
        #   class AsyncCursor(BaseCursor["AsyncConnection[Any]", Row]):
        # the base cannot be a token, even with __future__ annotation.
        for base in node.bases:
            if not isinstance(base, ast.Subscript):
                continue
            if not isinstance(base.slice, ast.Tuple):
                continue
            for elt in base.slice.elts:
                if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str)):
                    continue
                elt.value = self._visit_type_string(elt.value)

        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST | None:
        # Remove import of async utils eclypsing builtins
        if skips := self._skip_imports.get(node.module):
            node.names = [n for n in node.names if n.name not in skips]
            if not node.names:
                return None

        node.module = self.names_map.get(node.module, node.module)
        for n in node.names:
            n.name = self.names_map.get(n.name, n.name)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in self.names_map:
            node.id = self.names_map[node.id]
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        if node.attr in self.names_map:
            node.attr = self.names_map[node.attr]
        self.generic_visit(node)
        return node

    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        # Manage AsyncGenerator[X, Y] -> Generator[X, None, Y]
        self._manage_async_generator(node)
        # # Won't result in a recursion because we change the args number
        # self.visit(node)
        # return node

        self.generic_visit(node)
        return node

    def _manage_async_generator(self, node: ast.Subscript) -> ast.AST | None:
        if not (isinstance(node.value, ast.Name) and node.value.id == "AsyncGenerator"):
            return None

        if not (isinstance(node.slice, ast.Tuple) and len(node.slice.elts) == 2):
            return None

        node.slice.elts.insert(1, deepcopy(node.slice.elts[1]))
        self.generic_visit(node)
        return node


class BlanksInserter(ast.NodeTransformer):
    """
    Restore the missing spaces in the source (or something similar)
    """

    def generic_visit(self, node: ast.AST) -> ast.AST:
        if isinstance(getattr(node, "body", None), list):
            node.body = self._inject_blanks(node.body)
        super().generic_visit(node)
        return node

    def _inject_blanks(self, body: list[ast.Node]) -> list[ast.AST]:
        if not body:
            return body

        new_body = []
        before = body[0]
        new_body.append(before)
        for i in range(1, len(body)):
            after = body[i]
            nblanks = after.lineno - before.end_lineno - 1
            if nblanks > 0:
                # Inserting one blank is enough.
                blank = ast.Comment(
                    value="",
                    inline=False,
                    lineno=before.end_lineno + 1,
                    end_lineno=before.end_lineno + 1,
                    col_offset=0,
                    end_col_offset=0,
                )
                new_body.append(blank)
            new_body.append(after)
            before = after

        return new_body


def unparse(tree: ast.AST) -> str:
    rv: str = Unparser().visit(tree)
    rv = _fix_comment_on_decorators(rv)
    return rv


def _fix_comment_on_decorators(source: str) -> str:
    """
    Re-associate comments to decorators.

    In a case like:

        1  @deco  # comment
        2  def func(x):
        3     pass

    it seems that Function lineno is 2 instead of 1 (Python 3.10). Because
    the Comment lineno is 1, it ends up printed above the function, instead
    of inline. This is a problem for '# type: ignore' comments.

    Maybe the problem could be fixed in the tree, but this solution is a
    simpler way to start.
    """
    lines = source.splitlines()

    comment_at = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            comment_at = i
        elif not line.strip():
            pass
        elif line.lstrip().startswith("@classmethod"):
            if comment_at is not None:
                lines[i] = lines[i] + "  " + lines[comment_at].lstrip()
                lines[comment_at] = ""
        else:
            comment_at = None

    return "\n".join(lines)


class Unparser(ast._Unparser):
    """
    Try to emit long strings as multiline.

    The normal class only tries to emit docstrings as multiline,
    but the resulting source doesn't pass flake8.
    """

    # Beware: private method. Tested with in Python 3.10.
    def _write_constant(self, value: Any) -> None:
        if isinstance(value, str) and len(value) > 50:
            self._write_str_avoiding_backslashes(value)
        else:
            super()._write_constant(value)


def parse_cmdline() -> Namespace:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "filepath", metavar="FILE", type=Path, help="the file to process"
    )
    parser.add_argument(
        "output", metavar="OUTPUT", nargs="?", help="file where to write (or stdout)"
    )
    opt = parser.parse_args()

    return opt


if __name__ == "__main__":
    sys.exit(main())
