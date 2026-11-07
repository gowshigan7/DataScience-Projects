"""
test_merger.py
==============
Tests du moteur de fusion, de l'analyse des plages et de la CLI.

Description :
    Les PDF de test sont générés à la volée dans le dossier temporaire de pytest.
    Chaque page a une largeur unique, ce qui permet de vérifier l'ordre des pages.

Cas d'usage :
    - pytest pdf_merger/tests/ -v

Entrée  : Aucune
Sortie  : résultats des tests
"""

import pytest
from pypdf import PdfReader, PdfWriter

from pdf_merger.cli import main, parse_item
from pdf_merger.merger import MergeError, MergeItem, count_pages, merge_pdfs
from pdf_merger.page_range import parse_page_range


def make_pdf(path, widths):
    """
    Crée un PDF dont la page i a la largeur widths[i].

    Args:
        path: chemin de sortie.
        widths (list[int]): largeur de chaque page.

    Returns:
        str: chemin du fichier créé.
    """
    writer = PdfWriter()
    for width in widths:
        writer.add_blank_page(width=width, height=100)
    with open(path, "wb") as handle:
        writer.write(handle)
    return str(path)


def widths_of(path):
    """
    Lit la largeur de chaque page d'un PDF.

    Args:
        path (str): chemin du PDF.

    Returns:
        list[int]: largeurs, dans l'ordre des pages.
    """
    return [int(page.mediabox.width) for page in PdfReader(path).pages]


@pytest.fixture
def pdfs(tmp_path):
    """
    Deux PDF : a.pdf (3 pages : 101-103) et b.pdf (2 pages : 201-202).

    Args:
        tmp_path: dossier temporaire pytest.

    Returns:
        tuple[str, str, str]: (a.pdf, b.pdf, chemin de sortie)
    """
    a = make_pdf(tmp_path / "a.pdf", [101, 102, 103])
    b = make_pdf(tmp_path / "b.pdf", [201, 202])
    return a, b, str(tmp_path / "out.pdf")


# ---------------------------------------------------------------- page_range
@pytest.mark.parametrize("spec, expected", [
    (None, [0, 1, 2, 3, 4]),
    ("", [0, 1, 2, 3, 4]),
    ("toutes", [0, 1, 2, 3, 4]),
    ("2", [1]),
    ("1-3", [0, 1, 2]),
    ("1-2, 5", [0, 1, 4]),
    ("4-", [3, 4]),
    ("-2", [0, 1]),
    ("3-1", [2, 1, 0]),
    (" 1 , ,2 ", [0, 1]),
])
def test_parse_page_range(spec, expected):
    assert parse_page_range(spec, 5) == expected


@pytest.mark.parametrize("spec", ["abc", "0", "6", "1-9", "2-x"])
def test_parse_page_range_invalid(spec):
    with pytest.raises(ValueError):
        parse_page_range(spec, 5)


# ------------------------------------------------------------------- merger
def test_merge_keeps_order(pdfs):
    a, b, out = pdfs
    assert merge_pdfs([b, a], out) == 5
    assert widths_of(out) == [201, 202, 101, 102, 103]


def test_merge_with_ranges(pdfs):
    a, b, out = pdfs
    merge_pdfs([MergeItem(a, "3, 1"), MergeItem(b, "2")], out)
    assert widths_of(out) == [103, 101, 202]


def test_merge_bookmarks(pdfs):
    a, b, out = pdfs
    merge_pdfs([a, b], out, add_bookmarks=True)
    reader = PdfReader(out)
    titles = [o.title for o in reader.outline]
    pages = [reader.get_destination_page_number(o) for o in reader.outline]
    assert titles == ["a", "b"] and pages == [0, 3]


def test_merge_without_bookmarks(pdfs):
    a, b, out = pdfs
    merge_pdfs([a, b], out, add_bookmarks=False)
    assert PdfReader(out).outline == []


def test_merge_same_file_twice(pdfs):
    a, _, out = pdfs
    assert merge_pdfs([a, a], out) == 6


def test_merge_empty_list(pdfs):
    with pytest.raises(MergeError):
        merge_pdfs([], pdfs[2])


def test_merge_missing_file(pdfs, tmp_path):
    with pytest.raises(MergeError, match="introuvable"):
        merge_pdfs([pdfs[0], str(tmp_path / "absent.pdf")], pdfs[2])


def test_merge_not_a_pdf(pdfs, tmp_path):
    fake = tmp_path / "fake.pdf"
    fake.write_text("pas un pdf")
    with pytest.raises(MergeError, match="lisible"):
        merge_pdfs([pdfs[0], str(fake)], pdfs[2])


def test_merge_bad_range(pdfs):
    a, _, out = pdfs
    with pytest.raises(MergeError, match="a.pdf"):
        merge_pdfs([MergeItem(a, "1-10")], out)


def test_merge_refuses_overwriting_input(pdfs):
    a, b, _ = pdfs
    with pytest.raises(MergeError):
        merge_pdfs([a, b], a)
    assert count_pages(a) == 3


def test_merge_encrypted_pdf(pdfs, tmp_path):
    writer = PdfWriter(clone_from=pdfs[0])
    writer.encrypt("secret")
    locked = tmp_path / "locked.pdf"
    with open(locked, "wb") as handle:
        writer.write(handle)
    with pytest.raises(MergeError, match="mot de passe"):
        merge_pdfs([str(locked)], pdfs[2])


def test_merge_encrypted_without_user_password(pdfs, tmp_path):
    writer = PdfWriter(clone_from=pdfs[1])
    writer.encrypt(user_password="", owner_password="owner")
    locked = tmp_path / "owner_only.pdf"
    with open(locked, "wb") as handle:
        writer.write(handle)
    assert merge_pdfs([str(locked)], pdfs[2]) == 2


# ---------------------------------------------------------------------- cli
def test_cli_merge(pdfs, capsys):
    a, b, out = pdfs
    assert main([f"{a}:2-3", b, "-o", out]) == 0
    assert widths_of(out) == [102, 103, 201, 202]
    assert "4 pages" in capsys.readouterr().out


def test_cli_error_exit_code(pdfs, capsys):
    assert main(["absent.pdf", "-o", pdfs[2]]) == 1
    assert "introuvable" in capsys.readouterr().err


def test_parse_item_windows_drive_letter():
    assert parse_item(r"C:\docs\a.pdf") == MergeItem(r"C:\docs\a.pdf")
    assert parse_item(r"C:\docs\a.pdf:1-3") == MergeItem(r"C:\docs\a.pdf", "1-3")
