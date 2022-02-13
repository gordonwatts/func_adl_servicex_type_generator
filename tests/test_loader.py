from pathlib import Path
from func_adl_servicex_type_generator.loader import load_yaml


def test_load_full_file():
    data = load_yaml(Path("./tests/xaod_r21_1.yaml"))

    collection_dict = {c.name: c for c in data.collections}
    classes_dict = {c.name: c for c in data.classes}

    assert "DiTauJets" in collection_dict
    assert "xAOD.Jet_v1" in classes_dict

    di_jets = collection_dict["DiTauJets"]
    jets = collection_dict["Jets"]
    jets_class = classes_dict["xAOD.Jet_v1"]
    btagging = classes_dict["xAOD.BTagging_v1"]
    truth = classes_dict["xAOD.TruthParticle_v1"]
    event_info = collection_dict["EventInfo"]
    element_link = classes_dict["ElementLink_DataVector_xAOD_BTagging_v1__"]

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

    assert len(element_link.behaviors) == 1
    assert element_link.behaviors[0] == "xAOD::BTagging_v1**"

    assert "sys_error_tool" in data.metadata
    m_sys = data.metadata["sys_error_tool"]
    assert isinstance(m_sys.data, list)

    assert len(jets.parameters) == 2
    jets_p = jets.parameters[0]
    assert jets_p.name == "calibration"
    assert jets_p.type == "str"
    assert jets_p.default_value == "'NOSYS'"
    assert len(jets_p.actions) == 2
    jets_a = jets_p.actions[1]
    assert jets_a.value == "'*Any*'"
    assert jets_a.md_names == [
        "sys_error_tool",
        "pileup_tool",
        "jet_corrections",
        "add_calibration_to_job",
    ]
    assert jets_a.bank_rename == "{bank_name}Calib_{calibration}"

    assert len(data.files) > 0
    trigger_list = [f for f in data.files if f.file_name == "trigger.py"]
    assert len(trigger_list) == 1
    trigger = trigger_list[0]

    assert len(trigger.init_lines) == 2
    assert len(trigger.contents) > 0
    assert trigger.contents[0].startswith("#")


def test_load_container_types():
    data = load_yaml(Path("./tests/xaod_r21_1.yaml"))
    classes_dict = {c.name: c for c in data.classes}

    non_container = classes_dict["xAOD.Jet_v1"]
    container = classes_dict["xAOD.JetConstituentVector"]

    assert non_container.cpp_container_type is None
    assert non_container.python_container_type is None

    assert container.cpp_container_type == "xAOD::JetConstituent*"
    assert container.python_container_type == "xAOD.JetConstituent"
