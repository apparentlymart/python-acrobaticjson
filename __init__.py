
import simplejson

def dumps(obj):
    r = Root.for_value(obj)
    return simplejson.dumps(r.struct, separators = (',', ':'))

class Root(object):
    """
    Wrapper for a raw Acrobatic JSON structure that
    can produce wrapper objects that provide dict-
    and list-like interfaces to the original
    data structure.
    """

    def __init__(self,struct):
        self.primitive_ids = {}
        self.other_ids = {}
        self.struct = struct
        self.next_id = len(struct)
        self.wrapped = {}
        self.modified = False

    def for_value(cls, value):
        """
        Create a root for an Acrobatic JSON structure
        created from the provided value. The provided
        value must be either a list or a dict containing
        only numbers, booleans, strings, lists or dicts.
        """
        self = cls([])
        id = self.__acrobatic_value(value)
        assert id == 0
        self.modified = False
        return self
    for_value = classmethod(for_value)

    def new_object(cls):
        """
        Create a root for an Acrobatic JSON structure
        representing an empty object.
        """
        return cls.for_value([])
    new_object = classmethod(new_object)

    def new_array(cls):
        """
        Create a root for an Acrobatic JSON structure
        representing an empty array.
        """
        return cls.for_value({})
    new_array = classmethod(new_array)

    def get_value(self):
        return self.get_wrapped_value_by_index(0)

    def get_wrapped_value_by_index(self, index):

        # Do we already have a wrapper for this?
        if (index in self.wrapped):
            return self.wrapped[index]

        acrobatic_value = self.struct[index]

        if (isinstance(acrobatic_value, list)):
            return ArrayWrapper(self, index)
        elif (isinstance(acrobatic_value, dict)):
            return ObjectWrapper(self, index)
        else:
            return acrobatic_value

    def __acrobatic_value(self, value):

        # nulls don't get pointerized
        if (value is None):
            return None

        # booleans don't get pointerized
        if (value is True or value is False):
            return value

        # if we've been given back one of our own wrapper objects,
        # just return the id it already has.
        if (isinstance(value, Wrapper) and value.root is self):
            return value.index

        id_table = None
        id_table_index = None
        if (isinstance(value, str) or isinstance(value,int) or isinstance(value,float) or isinstance(value,bool)):
            id_table = self.primitive_ids
            id_table_index = value
        else:
            id_table = self.other_ids
            id_table_index = id(value)

        index = None
        if (id_table_index in id_table):
            return id_table[id_table_index]
        else:
            id_table[id_table_index] = self.next_id
            self.next_id = self.next_id + 1
            index = id_table[id_table_index]

        # Do we already have this object in our struct?
        if (index < len(self.struct)):
            return index
        else:
            # Grow the struct to accomodate this new value
            self.struct.append(None)

        value_to_store = None

        if (isinstance(value, dict) or isinstance(value, ObjectWrapper)):
            value_to_store = {}
            for key in value:
                value_to_store[key] = self.__acrobatic_value(value[key])
        elif (isinstance(value, list) or isinstance(value, ArrayWrapper)):
            value_to_store = map(lambda v : self.__acrobatic_value(v), value)
        else:
            # Anything else just gets stored verbatim, though it
            # might later blow up the JSON encoder if it's something
            # weird.
            value_to_store = value

        assert(value_to_store is not None)

        self.struct[index] = value_to_store

        self.modified = True

        return index

class Wrapper(object):
    def __init__(self, root, index):
        self.root = root
        self.index = index
        self.ref = root.struct[index]

class ArrayWrapper(Wrapper):
    pass

class ObjectWrapper(Wrapper):
    pass

