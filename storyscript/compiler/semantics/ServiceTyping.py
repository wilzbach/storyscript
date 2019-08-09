# -*- coding: utf-8 -*-
from storyscript.Hub import story_hub, type_class_mapping

from .types.Types import AnyType, BooleanType, FloatType, IntType, ListType, \
    MapType, NoneType, ObjectType, StringType


class ServiceTyping:
    """
    Handles interaction with the storyhub to grab typing
    information of services
    """
    def __init__(self):
        self.hub = story_hub()

    def get_service_data(self, service_name):
        service = self.hub.get(service_name, wrap_service=True)
        return service

    def check_get_service_data(self, tree, service_name):
        service_data = self.get_service_data(service_name)
        tree.expect(service_data, 'service_not_found', name=service_name)
        return service_data

    def get_action_from_config(self, service_config, action_name):
        action = service_config.action(action_name)
        return action

    def check_action_args(self, tree, action, args, service_name, action_name):
        required_args = [arg for arg in action.args() if arg.required()]
        for arg in required_args:
            arg_name = arg.name()
            tree.expect(args.get(arg_name, False), 'service_arg_required',
                        service=service_name, action=action_name, arg=arg_name)

        for arg, (sym, arg_node) in args.items():
            action_arg = action.arg(arg)
            tree.expect(action_arg is not None, 'service_arg_invalid',
                        service=service_name, action=action_name, arg=arg)
            target_type = action_arg.type()
            source_type = sym.type()
            action_arg_type_class = type_class_mapping(target_type)
            tree.expect(isinstance(source_type, action_arg_type_class),
                        'service_arg_type_mismatch', service=service_name,
                        action=action_name, arg=arg, target=target_type,
                        source=source_type)

    def resolve_service(self, tree,
                        service_name, action_name,
                        args, nested_block=False):
        tree.expect(len(tree.path.children) == 1, 'service_name')
        service_data = self.check_get_service_data(tree, service_name)
        config = service_data.configuration()
        action = self.get_action_from_config(config, action_name)
        tree.expect(action, 'service_action_not_found',
                    name=service_name, action=action_name)

        self.check_action_args(tree, action, args, service_name, action_name)

        if nested_block:
            return ObjectType(object=action)
        else:
            return self.get_service_output(action)

    def get_service_output(self, action):
        output = action.output()
        output_type = None
        if output is not None:
            type_class = type_class_mapping(output.type())
            if type_class == ObjectType:
                output_type = ObjectType(object=output)
            elif type_class == ListType:
                output_type = ListType(AnyType.instance())
            elif type_class == MapType:
                output_type = MapType(AnyType.instance(), AnyType.instance())
            else:
                assert type_class in (
                    AnyType, BooleanType, FloatType, IntType, StringType)
                output_type = type_class.instance()
        else:
            output_type = NoneType.instance()
        return output_type

    def resolve_service_event(self, tree, action_listener, event_name, args):
        event = action_listener.event(event_name)
        action_listener_name = action_listener.name()
        tree.expect(event, 'service_event_not_found',
                    name=action_listener_name, event=event_name)
        self.check_action_args(tree, event, args,
                               action_listener_name, event_name)
        return self.get_service_output(event)

    def resolve_service_output(self, tree,
                               output_name, action_name,
                               args, service_output):
        action = service_output.action(action_name)
        tree.expect(action, 'service_action_not_found',
                    name=output_name, action=action_name)
        self.check_action_args(tree, action, args, output_name, action_name)
        return NoneType.instance()
