import types
import cgi
import string

##########################################################################
#
# This module is a generic purpose XML formatter
#
# Six functions are defined:
#  class2string - converts a class or a dictionary into an XML string
#                 class fields or dictionary keys are used as XML tags
#  dict2string  - converts a dictionary or a list (or tuple) into an XML string
#                 keys or indexes are used as parameters, not tags
#  list2string  - converts a list or a dictionary into an XML string
#                 no indexes here, only the values are used
#                 in case of a dictionary, keys are used and the values are ignored
#
#  class2file - write a class or a dictionary into an open file as an XML string
#               class fields or dictionary keys are used as XML tags
#  dict2file  - write a dictionary or a list (or tuple) into an open file as an XML string
#               keys or indexes are used as parameters, not tags
#  list2file  - write a list or a dictionary into an open file as an XML string
#               no indexes here, only the values are used
#               in case of a dictionary, keys are used and the values are ignored
#
##########################################################################


######################################################################
def complete_class_params(class_params):
    res = class_params.copy()
    if not ("subclass_params" in res.keys()):
        res["subclass_params"] = {}
    if not ("dicts_params" in res.keys()):
        res["dicts_params"] = {}
    if not ("lists_params" in res.keys()):
        res["lists_params"] = {}
    if not ("tree_params" in res.keys()):
        res["tree_params"] = {}
    if not ("text_params" in res.keys()):
        res["text_params"] = []
    return res

# internal, get header of a class


def class2head(inst, inst_name, params, dicts_params, lists_params,
               tree_params, text_params, leading_tab, debug_str):
    inst_attrs = []
    dict_attrs = []
    list_attrs = []
    tree_attrs = []
    text_attrs = []
    head_arr = []
    head_arr.append(leading_tab + ('<%s' % inst_name))
    for attr in params.keys():
        el = params[attr]
        if type(el) in (types.IntType, types.LongType):
            head_arr.append(' %s="%i"' % (attr, el))
        elif isinstance(el, types.FloatType):
            head_arr.append(' %s="%.12g"' % (attr, el))
        elif isinstance(el, types.StringType):
            head_arr.append(' %s="%s"' % (attr, cgi.escape(el, 1)))
        elif el is None:
            head_arr.append(' %s="None"' % attr)
        else:
            raise RuntimeError("Param attr %s is not a simple type (%s)" % (
                attr, debug_str))

    if isinstance(inst, types.DictType):
        keys = inst.keys()  # dictionaries can be use like classes
    else:
        keys = dir(inst)
    for attr in keys:
        el = inst[attr]
        if type(el) in (types.IntType, types.LongType):
            head_arr.append(' %s="%i"' % (attr, el))
        elif isinstance(el, types.FloatType):
            head_arr.append(' %s="%.12g"' % (attr, el))
        elif isinstance(el, types.StringType):
            if attr in text_params:
                text_attrs.append(attr)
            else:
                head_arr.append(' %s="%s"' % (attr, cgi.escape(el, 1)))
        elif type(el) in (types.ListType, types.TupleType):
            if attr in lists_params.keys():
                list_attrs.append(attr)
            elif attr in dicts_params.keys():
                dict_attrs.append(attr)
            else:
                raise RuntimeError("No params for list attr %s (%s)" % (
                    attr, debug_str))
        elif isinstance(el, types.DictType):
            if attr in dicts_params.keys():
                # print "%s is dict" % attr
                dict_attrs.append(attr)
            elif attr in lists_params.keys():
                # print "%s is list" % attr
                list_attrs.append(attr)
            elif attr in tree_params.keys():
                # print "%s is tree" % attr
                tree_attrs.append(attr)
            else:
                # print "%s is class" % attr
                inst_attrs.append(attr)
        elif isinstance(el, types.InstanceType):
            inst_attrs.append(attr)
        elif el is None:
            head_arr.append(' %s="None"' % attr)
        else:
            raise RuntimeError("Unsupported type (%s) for attr %s (%s)" % (
                type(el), attr, debug_str))
    if (len(inst_attrs) == 0) and (len(dict_attrs) == 0) and (
            len(list_attrs) == 0) and (len(tree_attrs) == 0) and (len(text_attrs) == 0):
        head_arr.append('/>')
        is_complete = 1
    else:
        head_arr.append('>')
        is_complete = 0
    head_str = string.join(head_arr, '')

    return (head_str, is_complete, inst_attrs, dict_attrs,
            list_attrs, tree_attrs, text_attrs)


# Convert a class into an XML string
# all the simple attributes will be put in the header
# other dictionaries will be put into the body
def class2string(inst, inst_name, params={}, subclass_params={}, dicts_params={}, lists_params={
}, tree_params={}, text_params=[], indent_tab="   ", leading_tab="", debug_str=""):
    # return a pair (new_subclass_params,new_dict2list_params)
    def get_subclass_param(subclass_params, attr):
        if attr in subclass_params.keys():
            return complete_class_params(subclass_params[attr])
        else:  # if attr not explicitly specified, use default behaviour
            return complete_class_params({})

    head_str, is_complete, inst_attrs, dict_attrs, list_attrs, tree_attrs, text_attrs = class2head(
        inst, inst_name, params, dicts_params, lists_params, tree_params, text_params, leading_tab, debug_str)
    if is_complete:
        return head_str

    res_arr = []
    res_arr.append(head_str)
    for attr in text_attrs:
        res_arr.append(leading_tab + indent_tab + "<%s>\n%s\n</%s>" %
                       (attr, cgi.escape(inst[attr], 1), attr))

    for attr in inst_attrs:
        c = get_subclass_param(subclass_params, attr)
        res_arr.append(class2string(inst[attr], attr, {}, c["subclass_params"], c["dicts_params"], c["lists_params"], c[
                       "tree_params"], c["text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (inst_name, attr))))
    for attr in dict_attrs:
        sp = complete_dict_params(dicts_params[attr])
        res_arr.append(dict2string(inst[attr], attr, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {}, sp[
                       "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (inst_name, attr))))
    for attr in list_attrs:
        sp = complete_list_params(lists_params[attr])
        res_arr.append(list2string(inst[attr], attr, sp["el_name"], sp["el_attr_name"], {}, sp[
                       "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (inst_name, attr))))
    for attr in tree_attrs:
        t = tree_params[attr]
        res_arr.append(tree2string(inst[attr], attr, t[
                       "child_element"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (inst_name, attr))))
    res_arr.append(leading_tab + ('</%s>' % inst_name))
    return string.join(res_arr, '\n')

# Write a class as XML into an open file
# all the simple attributes will be put in the header
# other dictionaries will be put into the body


def class2file(fd, inst, inst_name, params={}, subclass_params={}, dicts_params={}, lists_params={
}, tree_params={}, text_params=[], indent_tab="   ", leading_tab="", debug_str=""):
    # return a pair (new_subclass_params,new_dict2list_params)
    def get_subclass_param(subclass_params, attr):
        if attr in subclass_params.keys():
            return complete_class_params(subclass_params[attr])
        else:  # if attr not explicitly specified, use default behaviour
            return complete_class_params({})

    head_str, is_complete, inst_attrs, dict_attrs, list_attrs, tree_attrs, text_attrs = class2head(
        inst, inst_name, params, dicts_params, lists_params, tree_params, text_params, leading_tab, debug_str)
    fd.write(head_str + "\n")
    if is_complete:
        return fd

    for attr in text_attrs:
        fd.write(leading_tab + indent_tab + "<%s>\n%s\n</%s>\n" %
                 (attr, cgi.escape(inst[attr], 1), attr))
    for attr in inst_attrs:
        c = get_subclass_param(subclass_params, attr)
        class2file(fd, inst[attr], attr, {}, c["subclass_params"], c["dicts_params"], c["lists_params"], c["tree_params"], c[
                   "text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (inst_name, attr)))
    for attr in dict_attrs:
        sp = complete_dict_params(dicts_params[attr])
        dict2file(fd, inst[attr], attr, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {}, sp[
                  "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (inst_name, attr)))
    for attr in list_attrs:
        sp = complete_list_params(lists_params[attr])
        list2file(fd, inst[attr], attr, sp["el_name"], sp["el_attr_name"], {}, sp[
                  "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (inst_name, attr)))
    for attr in tree_attrs:
        t = tree_params[attr]
        tree2file(fd, inst[attr], attr, t["child_element"], indent_tab,
                  leading_tab + indent_tab, debug_str + ("%s[%s]." % (inst_name, attr)))
    fd.write(leading_tab + ('</%s>\n' % inst_name))
    return fd

######################################################################


def complete_dict_params(dict_params):
    res = dict_params.copy()
    if not ("dict_attr_name" in res.keys()):
        res["dict_attr_name"] = "name"
    if not ("el_attr_name" in res.keys()):
        res["el_attr_name"] = "val"
    if not ("subtypes_params" in res.keys()):
        res["subtypes_params"] = {}
    return res

# Convert a dictionary into an XML string
# all elements should be of the same type, although this is not enforced


def dict2string(dict, dict_name, el_name, dict_attr_name="name", el_attr_name="val", params={
}, subtypes_params={}, indent_tab="   ", leading_tab="", debug_str=""):
    res_arr = []

    head_arr = []
    head_arr.append(leading_tab + ('<%s' % dict_name))
    for attr in params.keys():
        el = params[attr]
        if type(el) in (types.IntType, types.LongType):
            head_arr.append(' %s="%i"' % (attr, el))
        elif isinstance(el, types.FloatType):
            head_arr.append(' %s="%.12g"' % (attr, el))
        elif isinstance(el, types.StringType):
            head_arr.append(' %s="%s"' % (attr, cgi.escape(el, 1)))
        elif el is None:
            head_arr.append(' %s="None"' % attr)
        else:
            raise RuntimeError("Param attr %s is not a simple type (%s) (%s)" % (
                attr, type(el), debug_str))
    head_arr.append('>')
    head_str = string.join(head_arr, '')
    res_arr.append(head_str)
    # print head_str

    if isinstance(dict, types.DictType):
        keys = dict.keys()
    else:
        keys = range(len(dict))  # allow lists to be used as dictionaries

    for idx in keys:
        el = dict[idx]
        if ((type(el) in (types.IntType, types.LongType, types.FloatType, types.StringType)) or
                (el is None)):
            if el is None:
                val = "None"
            elif isinstance(el, types.StringType):
                val = cgi.escape(el, 1)
            elif isinstance(el, types.FloatType):
                val = "%.12g" % el
            else:
                val = "%i" % el
            res_arr.append(leading_tab + indent_tab + ('<%s %s="%s" %s="%s"/>' %
                                                       (el_name, dict_attr_name, idx, el_attr_name, val)))
        elif isinstance(el, types.InstanceType):
            if "class" in subtypes_params.keys():
                c = complete_class_params(subtypes_params["class"])
                res_arr.append(class2string(el, el_name, {dict_attr_name: idx}, c["subclass_params"], c["dicts_params"], c["lists_params"], c[
                               "tree_params"], c["text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx))))
            else:
                raise RuntimeError("No params for class (at idx %s) (%s)" % (
                    idx, debug_str))
        elif isinstance(el, types.DictType):
            #print (idx,subtypes_params.keys())
            if "dict" in subtypes_params.keys():
                sp = complete_dict_params(subtypes_params["dict"])
                res_arr.append(dict2string(el, el_name, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {dict_attr_name: idx}, sp[
                               "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx))))
            elif "list" in subtypes_params.keys():
                sp = complete_list_params(subtypes_params["list"])
                res_arr.append(list2string(el, el_name, sp["el_name"], sp["el_attr_name"], {dict_attr_name: idx}, sp[
                               "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx))))
            elif "class" in subtypes_params.keys():
                c = complete_class_params(subtypes_params["class"])
                res_arr.append(class2string(el, el_name, {dict_attr_name: idx}, c["subclass_params"], c["dicts_params"], c["lists_params"], c[
                               "tree_params"], c["text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx))))
            else:
                raise RuntimeError("No params for dict (at idx %s) (%s)" % (
                    idx, debug_str))
        elif type(el) in (types.ListType, types.TupleType):
            if "list" in subtypes_params.keys():
                sp = complete_list_params(subtypes_params["list"])
                res_arr.append(list2string(el, el_name, sp["el_name"], sp["el_attr_name"], {dict_attr_name: idx}, sp[
                               "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx))))
            elif "dict" in subtypes_params.keys():
                sp = complete_dict_params(subtypes_params["dict"])
                res_arr.append(dict2string(el, el_name, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {dict_attr_name: idx}, sp[
                               "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx))))
            else:
                raise RuntimeError("No params for list (at idx %s) (%s)" % (
                    idx, debug_str))
        else:
            raise RuntimeError("Unsupported type(%s) at idx %s (%s)" % (
                type(el), idx, debug_str))

    res_arr.append(leading_tab + ('</%s>' % dict_name))

    return string.join(res_arr, '\n')

# Write a dictionary formatted as XML into an open file
# all elements should be of the same type, although this is not enforced


def dict2file(fd, dict, dict_name, el_name, dict_attr_name="name", el_attr_name="val",
              params={}, subtypes_params={}, indent_tab="   ", leading_tab="", debug_str=""):
    head_arr = []
    head_arr.append(leading_tab + ('<%s' % dict_name))
    for attr in params.keys():
        el = params[attr]
        if type(el) in (types.IntType, types.LongType):
            head_arr.append(' %s="%i"' % (attr, el))
        elif isinstance(el, types.FloatType):
            head_arr.append(' %s="%.12g"' % (attr, el))
        elif isinstance(el, types.StringType):
            head_arr.append(' %s="%s"' % (attr, cgi.escape(el, 1)))
        elif el is None:
            head_arr.append(' %s="None"' % attr)
        else:
            raise RuntimeError("Param attr %s is not a simple type (%s) (%s)" % (
                attr, type(el), debug_str))
    head_arr.append('>\n')
    head_str = string.join(head_arr, '')
    fd.write(head_str)
    # print head_str

    if isinstance(dict, types.DictType):
        keys = dict.keys()
    else:
        keys = range(len(dict))  # allow lists to be used as dictionaries

    for idx in keys:
        el = dict[idx]
        if ((type(el) in (types.IntType, types.LongType, types.FloatType, types.StringType)) or
                (el is None)):
            if el is None:
                val = "None"
            elif isinstance(el, types.StringType):
                val = cgi.escape(el, 1)
            elif isinstance(el, types.FloatType):
                val = "%.12g" % el
            else:
                val = "%i" % el
            fd.write(leading_tab + indent_tab + ('<%s %s="%s" %s="%s"/>\n' %
                                                 (el_name, dict_attr_name, idx, el_attr_name, val)))
        elif isinstance(el, types.InstanceType):
            if "class" in subtypes_params.keys():
                c = complete_class_params(subtypes_params["class"])
                class2file(fd, el, el_name, {dict_attr_name: idx}, c["subclass_params"], c["dicts_params"], c["lists_params"], c[
                           "tree_params"], c["text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx)))
            else:
                raise RuntimeError("No params for class (at idx %s) (%s)" % (
                    idx, debug_str))
        elif isinstance(el, types.DictType):
            #print (idx,subtypes_params.keys())
            if "dict" in subtypes_params.keys():
                sp = complete_dict_params(subtypes_params["dict"])
                dict2file(fd, el, el_name, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {dict_attr_name: idx}, sp[
                          "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx)))
            elif "list" in subtypes_params.keys():
                sp = complete_list_params(subtypes_params["list"])
                list2file(fd, el, el_name, sp["el_name"], sp["el_attr_name"], {dict_attr_name: idx}, sp[
                          "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx)))
            elif "class" in subtypes_params.keys():
                c = complete_class_params(subtypes_params["class"])
                class2file(fd, el, el_name, {dict_attr_name: idx}, c["subclass_params"], c["dicts_params"], c["lists_params"], c[
                           "tree_params"], c["text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx)))
            else:
                raise RuntimeError("No params for dict (at idx %s) (%s)" % (
                    idx, debug_str))
        elif type(el) in (types.ListType, types.TupleType):
            if "list" in subtypes_params.keys():
                sp = complete_list_params(subtypes_params["list"])
                list2file(fd, el, el_name, sp["el_name"], sp["el_attr_name"], {dict_attr_name: idx}, sp[
                          "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx)))
            elif "dict" in subtypes_params.keys():
                sp = complete_dict_params(subtypes_params["dict"])
                dict2file(fd, el, el_name, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {dict_attr_name: idx}, sp[
                          "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s[%s]." % (dict_name, idx)))
            else:
                raise RuntimeError("No params for list (at idx %s) (%s)" % (
                    idx, debug_str))
        else:
            raise RuntimeError("Unsupported type(%s) at idx %s (%s)" % (
                type(el), idx, debug_str))

    fd.write(leading_tab + ('</%s>\n' % dict_name))

    return

######################################################################


def complete_list_params(list_params):
    res = list_params.copy()
    if not ("el_attr_name" in res.keys()):
        res["el_attr_name"] = "val"
    if not ("subtypes_params" in res.keys()):
        res["subtypes_params"] = {}
    return res

# Convert a list into an XML string
# Do not show the indexes, use dict2string if that is needed
# all elements should be of the same type, although this is not enforced


def list2string(list, list_name, el_name, el_attr_name="val", params={
}, subtypes_params={}, indent_tab="   ", leading_tab="", debug_str=""):
    res_arr = []

    head_arr = []
    head_arr.append(leading_tab + ('<%s' % list_name))
    for attr in params.keys():
        el = params[attr]
        if type(el) in (types.IntType, types.LongType):
            head_arr.append(' %s="%i"' % (attr, el))
        elif isinstance(el, types.FloatType):
            head_arr.append(' %s="%.12g"' % (attr, el))
        elif isinstance(el, types.StringType):
            head_arr.append(' %s="%s"' % (attr, cgi.escape(el, 1)))
        elif el is None:
            head_arr.append(' %s="None"' % attr)
        else:
            raise RuntimeError("Param attr %s is not a simple type (%s) (%s)" % (
                attr, type(el), debug_str))
    head_arr.append('>')
    head_str = string.join(head_arr, '')
    res_arr.append(head_str)

    # print head_str

    if isinstance(list, types.DictType):
        els = list.keys()  # Use only the keys of the dictionary
    else:
        els = list

    for el in els:
        if ((type(el) in (types.IntType, types.LongType, types.FloatType, types.StringType)) or
                (el is None)):
            if el is None:
                val = "None"
            if isinstance(el, types.StringType):
                val = cgi.escape(el, 1)
            elif isinstance(el, types.FloatType):
                val = "%.12g" % el
            else:
                val = "%i" % el
            res_arr.append(leading_tab + indent_tab +
                           ('<%s %s="%s"/>' % (el_name, el_attr_name, val)))
        elif isinstance(el, types.InstanceType):
            if "class" in subtypes_params.keys():
                c = complete_class_params(subtypes_params["class"])
                res_arr.append(class2string(el, el_name, {}, c["subclass_params"], c["dicts_params"], c["lists_params"], c[
                               "tree_params"], c["text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name)))
            else:
                raise RuntimeError(
                    "No params for class in list (%s)" %
                    debug_str)
        elif isinstance(el, types.DictType):
            if "dict" in subtypes_params.keys():
                sp = complete_dict_params(subtypes_params["dict"])
                res_arr.append(dict2string(el, el_name, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {}, sp[
                               "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name)))
            elif "list" in subtypes_params.keys():
                sp = complete_list_params(subtypes_params["list"])
                res_arr.append(list2string(el, el_name, sp["el_name"], sp["el_attr_name"], {}, sp[
                               "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name)))
            elif "class" in subtypes_params.keys():
                c = complete_class_params(subtypes_params["class"])
                res_arr.append(class2string(el, el_name, {}, c["subclass_params"], c["dicts_params"], c["lists_params"], c[
                               "tree_params"], c["text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name)))
            else:
                raise RuntimeError(
                    "No params for dict in list (%s)" %
                    debug_str)
        elif type(el) in (types.ListType, types.TupleType):
            if "list" in subtypes_params.keys():
                sp = complete_list_params(subtypes_params["list"])
                res_arr.append(list2string(el, el_name, sp["el_name"], sp["el_attr_name"], {}, sp[
                               "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name)))
            elif "dict" in subtypes_params.keys():
                sp = complete_dict_params(subtypes_params["dict"])
                res_arr.append(dict2string(el, el_name, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {}, sp[
                               "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name)))
            else:
                raise RuntimeError(
                    "No params for list in list (%s)" %
                    debug_str)
        else:
            raise RuntimeError("Unsupported type(%s) in list (%s)" % (
                type(el), debug_str))

    res_arr.append(leading_tab + ('</%s>' % list_name))

    return string.join(res_arr, '\n')

# Write a list formatted as XML in an open file
# Do not show the indexes, use dict2file if that is needed
# all elements should be of the same type, although this is not enforced


def list2file(fd, list, list_name, el_name, el_attr_name="val", params={
}, subtypes_params={}, indent_tab="   ", leading_tab="", debug_str=""):
    head_arr = []
    head_arr.append(leading_tab + ('<%s' % list_name))
    for attr in params.keys():
        el = params[attr]
        if type(el) in (types.IntType, types.LongType):
            head_arr.append(' %s="%i"' % (attr, el))
        elif isinstance(el, types.FloatType):
            head_arr.append(' %s="%.12g"' % (attr, el))
        elif isinstance(el, types.StringType):
            head_arr.append(' %s="%s"' % (attr, cgi.escape(el, 1)))
        elif el is None:
            head_arr.append(' %s="None"' % attr)
        else:
            raise RuntimeError("Param attr %s is not a simple type (%s) (%s)" % (
                attr, type(el), debug_str))
    head_arr.append('>\n')
    head_str = string.join(head_arr, '')
    fd.write(head_str)

    # print head_str

    if isinstance(list, types.DictType):
        els = list.keys()  # Use only the keys of the dictionary
    else:
        els = list

    for el in els:
        if ((type(el) in (types.IntType, types.LongType, types.FloatType, types.StringType)) or
                (el is None)):
            if el is None:
                val = "None"
            elif isinstance(el, types.StringType):
                val = cgi.escape(el, 1)
            elif isinstance(el, types.FloatType):
                val = "%.12g" % el
            else:
                val = "%i" % el
            fd.write(leading_tab + indent_tab + ('<%s %s="%s"/>\n' %
                                                 (el_name, el_attr_name, val)))
        elif isinstance(el, types.InstanceType):
            if "class" in subtypes_params.keys():
                c = complete_class_params(subtypes_params["class"])
                class2file(fd, el, el_name, {}, c["subclass_params"], c["dicts_params"], c["lists_params"], c[
                           "tree_params"], c["text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name))
            else:
                raise RuntimeError(
                    "No params for class in list (%s)" %
                    debug_str)
        elif isinstance(el, types.DictType):
            if "dict" in subtypes_params.keys():
                sp = complete_dict_params(subtypes_params["dict"])
                dict2file(fd, el, el_name, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {}, sp[
                          "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name))
            elif "list" in subtypes_params.keys():
                sp = complete_list_params(subtypes_params["list"])
                list2file(fd, el, el_name, sp["el_name"], sp["el_attr_name"], {}, sp[
                          "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name))
            elif "class" in subtypes_params.keys():
                c = complete_class_params(subtypes_params["class"])
                class2file(fd, el, el_name, {}, c["subclass_params"], c["dicts_params"], c["lists_params"], c[
                           "tree_params"], c["text_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name))
            else:
                raise RuntimeError(
                    "No params for dict in list (%s)" %
                    debug_str)
        elif type(el) in (types.ListType, types.TupleType):
            if "list" in subtypes_params.keys():
                sp = complete_list_params(subtypes_params["list"])
                list2file(fd, el, el_name, sp["el_name"], sp["el_attr_name"], {}, sp[
                          "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name))
            elif "dict" in subtypes_params.keys():
                sp = complete_dict_params(subtypes_params["dict"])
                dict2file(fd, el, el_name, sp["el_name"], sp["dict_attr_name"], sp["el_attr_name"], {}, sp[
                          "subtypes_params"], indent_tab, leading_tab + indent_tab, debug_str + ("%s." % list_name))
            else:
                raise RuntimeError(
                    "No params for list in list (%s)" %
                    debug_str)
        else:
            raise RuntimeError("Unsupported type(%s) in list (%s)" % (
                type(el), debug_str))

    fd.write(leading_tab + ('</%s>\n' % list_name))

    return

######################################################################
# Convert a tree into an XML string
# a tree is a dictionary that have inside other dictionaries of the same type
# all the clients are contained in an element of list type
# only simple attributes are allowed and will be put in the header


def tree2string(tree, tree_name, child_element,
                indent_tab="   ", leading_tab="", debug_str=""):
    res = []
    line = leading_tab + '<' + tree_name
    for key in tree.keys():
        if key == child_element:
            continue  # do it later
        line = line + (' %s="%s"' % (key, tree[key]))

    nr_childs = 0
    if child_element in tree:
        nr_childs = len(tree[child_element])

    if nr_childs > 0:
        res.append(line + ">")
        for child in tree[child_element]:
            res.append(tree2string(child, tree_name, child_element, indent_tab,
                                   leading_tab + indent_tab, debug_str + tree_name + "."))
        res.append(leading_tab + "</" + tree_name + ">")
    else:
        res.append(line + "/>")

    return string.join(res, "\n")

# Write a tree as XML into an open file
# a tree is a dictionary that have inside other dictionaries of the same type
# all the clients are contained in an element of list type
# only simple attributes are allowed and will be put in the header


def tree2file(fd, tree, tree_name, child_element,
              indent_tab="   ", leading_tab="", debug_str=""):
    line = leading_tab + '<' + tree_name
    for key in tree.keys():
        if key == child_element:
            continue  # do it later
        line = line + (' %s="%s"' % (key, tree[key]))

    nr_childs = 0
    if child_element in tree:
        nr_childs = len(tree[child_element])

    if nr_childs > 0:
        fd.write(line + ">\n")
        for child in tree[child_element]:
            tree2file(fd, child, tree_name, child_element, indent_tab,
                      leading_tab + indent_tab, debug_str + tree_name + ".")
        fd.write(leading_tab + "</" + tree_name + ">\n")
    else:
        fd.write(line + "/>\n")

    return fd
