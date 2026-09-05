# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""The .dat control file (manual §4.1): scalar keywords, the ATOMS line, and
keyword blocks whose items start with '>'. Round trip must preserve order."""

import pytest

import rmcprofile_tools as rt

DAT = """TITLE :: NaCl test
MATERIAL :: NaCl
TEMPERATURE :: 300K

NUMBER_DENSITY ::   0.044646 Angstrom^(-3)
MINIMUM_DISTANCES ::   3.5  2.4  3.5 Angstrom
MAXIMUM_MOVES ::   0.05  0.05 Angstrom
R_SPACING ::  0.0200 Angstrom
PRINT_PERIOD :: 100
TIME_LIMIT ::     1.00 MINUTES
SAVE_PERIOD ::     0.50 MINUTES

ATOMS :: Na Cl

FLAGS ::
  > NO_MOVEOUT
  > NO_SAVE_CONFIGURATIONS

INPUT_CONFIGURATION_FORMAT ::  rmc6f
SAVE_CONFIGURATION_FORMAT  ::  rmc6f

NEUTRON_REAL_SPACE_DATA :: 1
  > FILENAME :: nacl_gr.dat
  > DATA_TYPE :: G(r)
  > FIT_TYPE :: G(r)
  > START_POINT :: 1
  > END_POINT :: 1500
  > CONSTANT_OFFSET ::   0.0000
  > WEIGHT ::   0.0500
  > NO_FITTED_OFFSET

BRAGG ::
  > BRAGG_SHAPE :: gsas2                   %% Which peakprofile to use
  > SUPERCELL ::  3 3 3
  > RECALCULATE
  > WEIGHT ::   0.0100

END ::
"""


@pytest.fixture
def dat_path(tmp_path):
    p = tmp_path / "nacl.dat"
    p.write_text(DAT, encoding="utf-8")
    return p


def test_scalars_atoms_and_blocks(dat_path):
    d = rt.read_dat(dat_path)
    assert d.scalars["TITLE"] == "NaCl test"
    assert d.scalars["NUMBER_DENSITY"] == "0.044646 Angstrom^(-3)"
    assert d.atoms == ["Na", "Cl"]
    assert [b.name for b in d.blocks] == ["FLAGS", "NEUTRON_REAL_SPACE_DATA", "BRAGG"]
    nrs = d.blocks[1]
    assert nrs.arg == "1"
    assert nrs.items[0] == ("FILENAME", "nacl_gr.dat")
    assert ("NO_FITTED_OFFSET", None) in nrs.items          # bare flag: no "::"
    assert d.get("BRAGG", "BRAGG_SHAPE") == "gsas2"          # the %% comment is stripped
    assert d.get("BRAGG", "SUPERCELL") == "3 3 3"
    assert ("RECALCULATE", None) in d.blocks[2].items
    assert d.get("FLAGS", "NO_MOVEOUT") is None
    assert d.get("BRAGG", "NOT_THERE", "dflt") == "dflt"


def test_helpers(dat_path):
    d = rt.read_dat(dat_path)
    assert [b.name for b in d.data_blocks()] == ["NEUTRON_REAL_SPACE_DATA"]
    assert d.filenames() == ["nacl_gr.dat"]
    assert d.minimum_distances() == [3.5, 2.4, 3.5]
    assert d.time_limit_minutes() == 1.0


def test_write_then_read_preserves_everything(dat_path, tmp_path):
    d = rt.read_dat(dat_path)
    out = tmp_path / "copy.dat"
    d.write(out)
    again = rt.read_dat(out)
    assert again.scalars == d.scalars and again.atoms == d.atoms
    assert [(b.name, b.arg, b.items) for b in again.blocks] == [(b.name, b.arg, b.items) for b in d.blocks]
    text = out.read_text(encoding="utf-8")
    assert text.rstrip().endswith("END ::")
    assert "  > FILENAME :: nacl_gr.dat" in text and "  > NO_FITTED_OFFSET\n" in text


def test_edit_a_value_and_write(dat_path, tmp_path):
    d = rt.read_dat(dat_path)
    d.set("NEUTRON_REAL_SPACE_DATA", "WEIGHT", "0.0200")
    d.scalars["TIME_LIMIT"] = "5.00 MINUTES"
    out = tmp_path / "edited.dat"
    d.write(out)
    again = rt.read_dat(out)
    assert again.get("NEUTRON_REAL_SPACE_DATA", "WEIGHT") == "0.0200"
    assert again.time_limit_minutes() == 5.0


def test_shipped_shapes_of_blocks(tmp_path):
    """Shapes seen in the package's own exercises: a block with no items
    (POLYHEDRAL_RESTRAINT :: 5), a scalar with an empty value
    (IGNORE_HISTORY_FILE ::), a block with an empty argument
    (XRAY_RECIPROCAL_SPACE_DATA ::), an EXAFS block, WEIGHT_OPTIMIZATION ::."""
    p = tmp_path / "shapes.dat"
    p.write_text("TITLE :: x\nATOMS :: Ga P O\nIGNORE_HISTORY_FILE ::\nBOX_SIZE :: 8 8 8\nWEIGHT_OPTIMIZATION ::\n"
                 "XRAY_RECIPROCAL_SPACE_DATA ::\n  > FILENAME :: g.fq\n  > DATA_TYPE :: F(Q)\n"
                 "POLYHEDRAL_RESTRAINT :: 5\nEXAFS ::\n  > FILENAME ::Nb_EXAFS(k).dat\nEND ::\n", encoding="utf-8")
    d = rt.read_dat(p)
    assert d.scalars["IGNORE_HISTORY_FILE"] == "" and d.scalars["BOX_SIZE"] == "8 8 8"
    assert [b.name for b in d.blocks] == ["WEIGHT_OPTIMIZATION", "XRAY_RECIPROCAL_SPACE_DATA", "POLYHEDRAL_RESTRAINT", "EXAFS"]
    assert d.blocks[2].arg == "5" and d.blocks[2].items == []
    assert d.get("EXAFS", "FILENAME") == "Nb_EXAFS(k).dat"
    assert [b.name for b in d.data_blocks()] == ["XRAY_RECIPROCAL_SPACE_DATA", "EXAFS"]


def test_missing_end_is_an_error(tmp_path):
    p = tmp_path / "noend.dat"
    p.write_text(DAT.replace("END ::\n", ""), encoding="utf-8")
    with pytest.raises(ValueError, match="END ::"):
        rt.read_dat(p)


def test_convolve_keeps_its_double_colon(tmp_path):
    """RMCProfile's own files write '> CONVOLVE ::' but '> NO_FITTED_OFFSET'; a writer that
    dropped the '::' silently disabled the convolution (chapter 4, 2026-09-05)."""
    p = tmp_path / "c.dat"
    p.write_text("TITLE :: x\nNEUTRON_RECIPROCAL_SPACE_DATA :: 1\n  > FILENAME :: f.dat\n  > CONVOLVE ::\n"
                 "  > NO_FITTED_SCALE\nEND ::\n", encoding="utf-8")
    d = rt.read_dat(p)
    assert d.get("NEUTRON_RECIPROCAL_SPACE_DATA", "CONVOLVE") == ""
    assert d.get("NEUTRON_RECIPROCAL_SPACE_DATA", "NO_FITTED_SCALE") is None
    d.write(p)
    text = p.read_text(encoding="utf-8")
    assert "  > CONVOLVE ::\n" in text and "  > NO_FITTED_SCALE\n" in text
