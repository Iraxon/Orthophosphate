import src.orthophosphate.compiler.datapack_generator.datapack_directory_management as ddm

def test_namespacing():
    for k,v in {
        "My very cool DATAPACK": "my_very_cool_datapack",
        "Maiestas": "maiestas",
        "This.thing+" : "this.thing",
        "Name Space 99": "name_space_99"
        }.items():
        assert ddm.namespace_from_str(k) == v
