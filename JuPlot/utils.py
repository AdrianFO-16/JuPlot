from functools import wraps

def inspect_dictionary_structure(base, dic, strict_typing = False, strict_structure = False):

    # TODO: TYPES DO NOT DISPLAY IN IPYTHON

    if not isinstance(dic, dict):
        raise ValueError(f"Expected dictionary, got {dic}") # ---->
    
    not_defined_keys = [key for key in dic.keys() if key not in base.keys()]
    if len(not_defined_keys) > 0:
        raise ValueError(f"{', '.join(not_defined_keys)} not defined in {base.keys()}")
    
    structure_undefined_keys = [key for key in base.keys() if key not in dic.keys()]
    if strict_structure and len(structure_undefined_keys) > 0:
        raise ValueError(f"Expected structure {base.keys()}, keys ({', '.join(structure_undefined_keys)}) are undefined")

    for key in dic:
        types = base[key]
        values = dic[key]
        if isinstance(types, dict):
            try:
                inspect_dictionary_structure(types, values)
            except ValueError as ex:
                raise ValueError(f"In key {key}: {ex.args[0]}") #<---- receive
        else:
            val_check = isinstance(values, types) or (values == None and not strict_typing)
            if not val_check:
                raise ValueError(f"In dictionary {dic}, {key}:{values} type does not coincide with {types}" + 
                                 (" or is None" if strict_typing else ""))
    return True

def apply_dict_rules(rules, dic):
    for key in rules:
        sub_keys = set(rules[key].keys()).intersection(set(dic[key].keys()))
        for sub_key in sub_keys:
            val = dic[key][sub_key]
            if isinstance(val, dict):
                apply_dict_rules(rules[key], dic[key])
            else:
                rules[key][sub_key](dic[key][sub_key])

class SAC:
    """ SAC (Semi abstract class) 
    Create abstract classes that can be derived without necessarily implementing abstract methods.
    """
    def __init__(self):
        class_type = type(self)
        bases = class_type.__bases__

        class_members = dir(self)

        if object in bases and len(bases) == 1:
            raise Exception(f"Cannot instantiate pure abstract class '{SAC.__name__}'")
        if SAC in bases:
            raise Exception(f"Cannot instantiate pure abstract based class '{class_type.__name__}'")

        abstract_methods = [member for member in class_members if "__is_semi_abstract__" in dir(getattr(self, member))]

        if len(abstract_methods) > 0:
            header = "SAC Warning: The following methods remain abstract: "
            methods = "\n".join(abstract_methods)
            delim = "-" * len(header)
            print(f"{delim}\n{header}\n{methods}\nin class {class_type.__name__}\n{delim}")

def semi_abstract_method(method):
    @wraps(method)
    def except_use(*_):
        raise NotImplementedError(f"Abstract method {method.__name__} was called.")
    
    setattr(except_use, "__is_semi_abstract__", True)
    return except_use

def method_wrapper(method):
    def outer_wrapper(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            method(self, *args, **kwargs)
            return func(self, *args, **kwargs)
        return wrapper
    return outer_wrapper