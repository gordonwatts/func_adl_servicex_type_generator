from pathlib import Path
from func_adl_servicex_type_generator.loader import load_yaml


def test_load_full_file():
    collections, classes = load_yaml(Path("./tests/xaod_r21_1.yaml"))

    collection_dict = {c.name: c for c in collections}
    classes_dict = {c.name: c for c in classes}

    assert "DiTauJets" in collection_dict
    assert "xAOD.Jet_v1" in classes_dict

    di_jets = collection_dict["DiTauJets"]
    jets_class = classes_dict["xAOD.Jet_v1"]
    btagging = classes_dict["xAOD.BTagging_v1"]
    truth = classes_dict["xAOD.TruthParticle_v1"]
    event_info = collection_dict["EventInfo"]

    assert di_jets.name == "DiTauJets"
    assert di_jets.collection_item_type == "xAOD.DiTauJet_v1"
    assert di_jets.collection_type == "Iterable[xAOD.DiTauJet_v1]"
    assert di_jets.collection_item_type_name == "DiTauJet_v1"
    assert di_jets.cpp_item_type == "xAOD::DiTauJet_v1"
    assert di_jets.cpp_collection_type == "DataVector<xAOD::DiTauJet_v1>"

    assert jets_class.name == "xAOD.Jet_v1"
    assert len(jets_class.methods) > 0
    pt_methods = [m for m in jets_class.methods if m.name == "pt"]
    assert len(pt_methods) == 1
    assert pt_methods[0].return_type == "double"
    assert len(pt_methods[0].arguments) == 0

    calc_llr = [m for m in btagging.methods if m.name == "calcLLR"]
    assert len(calc_llr) == 1
    assert len(calc_llr[0].arguments) == 2
    assert calc_llr[0].arguments[0].arg_type == "float"

    assert len(event_info.cpp_include_file) == 1
    assert event_info.link_libraries == ["xAODEventInfo"]

    decayVtx = [m for m in truth.methods if m.name == "decayVtx"]
    assert len(decayVtx) == 1
    assert decayVtx[0].return_type == "const xAOD::TruthVertex_v1*"


def test_load_container_types():
    _, classes = load_yaml(Path("./tests/xaod_r21_1.yaml"))
    classes_dict = {c.name: c for c in classes}

    non_container = classes_dict["xAOD.Jet_v1"]
    container = classes_dict["xAOD.JetConstituentVector"]

    assert non_container.cpp_container_type is None
    assert non_container.python_container_type is None

    assert container.cpp_container_type == "xAOD::JetConstituent"
    assert container.python_container_type == "xAOD.JetConstituent"
