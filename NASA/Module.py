from model_config import type_dict, ACTION

import sys
sys.path.append('../Analyzer')
from type_constructor import create_action

class Module():
    def __init__(self, name, inputs, arguments, defines, rules, sub_action_generator = None):
        self.argument_list = arguments
        self.name = name
        self.instances = {}
        self.inputs = inputs
        self.defines = defines
        self.construct_rule = rules
        if sub_action_generator is not None:
            self.sub_action_generator = sub_action_generator
        else:
            self.sub_action_generator =lambda name: []

    def define_constraints(self):
        constraints = []
        for instance in self.instances.values():
            for rule in self.construct_rule:
                constraints.append(rule(instance))
        return constraints

    def create_instance(self, name=""):
        if name == "":
            id = len(self.instances) + 1
            name = "{}{}".format(self.name, id)
        instance = create_action(name, self.argument_list, type_dict, sub_actions=self.sub_action_generator(name), defines=self.defines, inputs=self.inputs)
        self.instances[name] = instance
        ACTION.append(instance)
        return instance
