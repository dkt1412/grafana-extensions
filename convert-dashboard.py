from argparse import ArgumentParser,ArgumentTypeError
import json
import os

"""
Edits a Grafana JSON dashboard for specific conversions
Outputs an importable Grafana JSON dashboard.

TODO:
	* Import basic graphite JSON
	* Convert to basic graphite JSON
	* Replace print with logging
	* Deal with invalid templating after datasource change.
"""


def valid_file(arg):
    if not os.path.exists(arg):
        raise ArgumentTypeError("The file %s does not exist!" % arg)
    else:
        return arg

def _load_json_blob(json_file_path):
    """Loads a dictionary from a json_blob

        Keyword arguments:
        json_file_path -- path to json file

        Returns:
        dictionary containing loaded json data
    """
    print "Loading from " + json_file_path
    with open(json_file_path, 'r') as fp:
        return json.load(fp)


def _replace_key_in_dict(a_dict, key, replacement_value):
    """ Given a dictionary, recursively replace any values with key=<key> with <replacement_value>

        Keyword arguments:
        a_dict -- dictionary to apply recursion on
        key -- the key to replace its value
        replacement_value -- value to replace a_dict[key] with

        Returns:
        dictionary containing modified a_dict
    """
    for k in a_dict.keys():
        if key == k:
            print "Found a match with %sand replacing with %s" % (key, replacement_value)
            a_dict[k] = _sanitize_for_json(replacement_value)
        elif type(a_dict[k]) is dict:
            _replace_key_in_dict(a_dict[k], key, replacement_value)
        elif type(a_dict[k]) is list:
            [_replace_key_in_dict(d, key, replacement_value) for d in a_dict[k] if type(d) is dict]

    return a_dict


def _sanitize_for_json(value):
    return   value


def _results_filename(json_file_with_extension, file_suffix):
    return json_file_with_extension.strip(".json") + file_suffix + ".json"

def _write_to_file(a_dict, json_file_name):
    print "Writing to " + json_file_name
    with open(json_file_name, 'w') as fp:
        json.dump(a_dict, fp)


def replace_key(args):
    """ Given a json file, replace all values of the <key> with <replacement_value>
            and writes to a new json file

        Keyword arguments:
        args: should contain the following
            - json_file
            - key
            - replacement_value
    """
    json_dict = _load_json_blob(args.json_file)
    mod_json_dict = _replace_key_in_dict(json_dict, args.key, args.replacement_value)
    _write_to_file(mod_json_dict_results_filename(args.json_file, "_mod_with_" + args.key))


def change_datasource(args):
    """ Given a json file, replace all values of "datasource" with <new_datasource>
            and writes to a new json file

        Keyword arguments:
        args: should contain the following
            - json_file
            - new_datasource
    """
    json_dict = _load_json_blob(args.json_file)
    mod_json_dict = _replace_key_in_dict(json_dict, "datasource", args.new_datasource)
    _write_to_file(mod_json_dict, _results_filename(args.json_file, "_datasource_" + args.new_datasource))


if __name__ == "__main__":
    parser = ArgumentParser(description="Execute various conversions from a Grafana JSON dashboard")
    parser.add_argument("json_file", type=valid_file, metavar="JSON_FILE", help="Path to a Grafana JSON dashboard to use for conversions")

    subcommand_parser = parser.add_subparsers()

    change_datasource_parser = subcommand_parser.add_parser("change-datasource", help="Change dashboard to use new datasource")
    change_datasource_parser.add_argument("new_datasource", metavar="NEW_DATASOURCE", help = "New datasource to use")
    change_datasource_parser.set_defaults(func=change_datasource)

    replace_key_parser = subcommand_parser.add_parser("replace_key", help="Replace ALL values of given key in dashboard")
    replace_key_parser.add_argument("key", metavar="KEY", help = "Number of users to generate")
    replace_key_parser.add_argument("replacement_value", metavar="REPLACEMENT_VALUE", help = "")
    replace_key_parser.set_defaults(func=replace_key)

    args = parser.parse_args()
    args.func(args)
