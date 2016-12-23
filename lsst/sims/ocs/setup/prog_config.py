try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os

from lsst.sims.ocs.utilities import expand_path

__all__ = ["apply_file_config", "read_file_config", "write_file_config"]

def apply_file_config(config, options):
    """Apply configuration file values to the command-line options.

    Parameters
    ----------
    config : configparser.ConfigParser
        The configuration file instance.
    options : argparse.Namespace
        The command-line options instance.
    """
    options.db_type = config["Database"]["type"]
    try:
        options.sqlite_save_dir = config[options.db_type]["save_directory"]
    except KeyError:
        pass
    try:
        options.session_id_start = int(config[options.db_type]["session_id_start"])
    except KeyError:
        pass
    try:
        options.mysql_config_path = config[options.db_type]["config_path"]
    except KeyError:
        pass
    try:
        options.track_session = config["tracking"] is not None
    except KeyError:
        pass
    try:
        options.tracking_db = config["tracking"]["tracking_db"]
    except KeyError:
        pass

def write_file_config(options, conf_dir=None):
    """Write a configuration file from the given options.

    Parameters
    ----------
    options : argparse.Namespace
        The options from ArgumentParser
    conf_dir : str, optional
        A directory for saving the configuration file in. Default is $HOME/.config/opsim4.
    """
    parser = configparser.SafeConfigParser()

    parser.add_section("Database")
    parser.set("Database", "type", options.type)
    parser.add_section(options.type)
    if options.type == "sqlite":
        parser.set(options.type, "save_directory", options.save_dir)
        if options.session_id_start is not None:
            parser.set(options.type, "session_id_start", options.session_id_start)
    if options.type == "mysql" and options.config_path is not None:
        parser.set(options.type, "config_path", options.config_path)

    if conf_dir is None:
        conf_dir = expand_path(os.path.join("$HOME", ".config"))
    with open(os.path.join(conf_dir, "opsim4"), 'w') as cfile:
        parser.write(cfile)

def read_file_config(conf_file=None, conf_dir=None):
    """Read in a configuration file.

    Parameters
    ----------
    conf_file : str, optional
        The name of the configuration file. Default is opsim4.
    conf_dir : str, optional
        The directory location of the configuration file. Default is $HOME/.config
    """
    if conf_file is None:
        conf_file = "opsim4"
    if conf_dir is None:
        conf_dir = expand_path(os.path.join("$HOME", ".config"))

    full_conf_file = os.path.join(conf_dir, conf_file)
    if not os.path.exists(full_conf_file):
        return None

    parser = configparser.SafeConfigParser()
    parser.read(full_conf_file)
    return parser
