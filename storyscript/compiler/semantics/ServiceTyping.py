# -*- coding: utf-8 -*-
from storyhub.sdk.service.ServiceOutput import ServiceOutput

from storyscript.compiler.semantics.types.Casting import implicit_type_cast
from storyscript.hub.Hub import story_hub
from storyscript.hub.TypeMappings import TypeMappings

from .types.Types import NoneType, ObjectType


class ServiceTyping:
    """
    Handles interaction with the storyhub to grab typing
    information of services
    """
    def __init__(self):
        self.hub = story_hub()

    def enforce_service_data(self, tree, service_name):
        """
        This function is responsible for using the storyhub sdk to
        retrieve service data for a given service name and return it
        after doing a check for its existence.
        """
        service_data = self.hub.get(service_name)
        tree.expect(service_data is not None,
                    'service_not_found', name=service_name)
        return service_data

    def get_action_from_config(self, service_config, action_name):
        action = service_config.action(action_name)
        return action

    def check_action_args(self, tree, action, args, service_name, action_name):
        required_args = (arg for arg in action.args() if arg.required())
        for arg in required_args:
            arg_name = arg.name()
            tree.expect(args.get(arg_name) is not None, 'service_arg_required',
                        service=service_name, action=action_name, arg=arg_name)

        for arg, (sym, arg_node) in args.items():
            action_arg = action.arg(arg)
            tree.expect(action_arg is not None, 'service_arg_invalid',
                        service=service_name, action=action_name, arg=arg)
            target_type = TypeMappings.get_type_instance(ty=action_arg.type())
            source_type = sym.type()

            implicit_type_cast(tree, source_type, target_type,
                               service_name, action_name, arg, arg_node)

    def resolve_service(self, tree, service_name, action_name, args,
                        nested_block=False):
        """
        Resolve a service via the storyhub sdk.
            - check `service_name` existence
            - check service `action_name` existence
            - check service `action_name` arguments with `args`
        Returns:
            Service action return type
        """
        tree.expect(len(tree.path.children) == 1, 'service_name')
        service_data = self.enforce_service_data(tree, service_name)
        config = service_data.configuration()
        action = self.get_action_from_config(config, action_name)
        tree.expect(action, 'service_action_not_found',
                    name=service_name, action=action_name)

        self.check_action_args(tree, action, args, service_name, action_name)

        if nested_block:
            tree.expect(action.events() != [], 'service_event_expected',
                        service=service_name, action=action_name)
            return ObjectType(obj={}, action=action)
        else:
            tree.expect(action.events() == [], 'expression_no_event',
                        service=service_name, action=action_name)
            return self.get_service_output(action)

    def get_service_output(self, action):
        output = action.output()
        if output is not None:
            output_type = TypeMappings.get_type_instance(ty=output.type())
            if isinstance(output_type, ObjectType):
                output_type.set_action(output)
        else:
            output_type = NoneType.instance()
        return output_type

    def resolve_service_event(self, tree, action_listener, event_name, args):
        event = action_listener.event(event_name)
        action_listener_name = action_listener.name()
        tree.expect(event is not None, 'service_event_not_found',
                    name=action_listener_name, event=event_name)
        self.check_action_args(tree, event, args,
                               action_listener_name, event_name)
        return self.get_service_output(event)

    def resolve_service_output_object(self, tree, output_name, action_name,
                                      args, service_symbol):
        """
        Handles event-based service output objects which define actions.
        The object output originates from when block listening on an event.
        """
        service_output = service_symbol.type().action()
        tree.expect(isinstance(service_output, ServiceOutput),
                    'service_action_without_output',
                    object=output_name)

        action = service_output.action(action_name)
        tree.expect(action is not None, 'service_action_not_found',
                    name=output_name, action=action_name)
        self.check_action_args(tree, action, args, output_name, action_name)
        return NoneType.instance()
