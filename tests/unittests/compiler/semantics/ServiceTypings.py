from storyscript.compiler.semantics.ServiceTyping import ServiceTyping
from storyscript.compiler.semantics.types.Types import NoneType
from storyscript.hub.TypeMappings import TypeMappings


def test_service_output(patch, magic):
    patch.init(ServiceTyping)
    patch.object(TypeMappings, 'get_type_instance')
    action = magic()
    typings = ServiceTyping()
    res = typings.get_service_output(action)
    TypeMappings.get_type_instance.assert_called_with(
        ty=action.output().type(),
    )
    assert res == TypeMappings.get_type_instance()


def test_service_output_none(patch, magic):
    patch.init(ServiceTyping)
    patch.object(TypeMappings, 'get_type_instance')
    action = magic()
    action.output.return_value = None
    typings = ServiceTyping()
    res = typings.get_service_output(action)
    TypeMappings.get_type_instance.assert_not_called()
    assert res == NoneType.instance()
