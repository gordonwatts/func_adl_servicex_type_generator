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

    assert di_jets.name == "DiTauJets"
    assert di_jets.collection_item_type == "xAOD.DiTauJet_v1"
    assert di_jets.collection_type == "Iterator[xAOD.DiTauJet_v1]"
    assert di_jets.collection_item_type_name == "DiTauJet_v1"

    assert jets_class.name == "xAOD.Jet_v1"
