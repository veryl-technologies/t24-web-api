import time
import os
from robot.libraries.BuiltIn import BuiltIn


class Config:

    @staticmethod
    def get_t24_version():
        version = BuiltIn().get_variable_value("${T24_VERSION}")
        if not version:
            return 11
        else:
            return version

class VariablesExporter:

    def add_global(self, name, value):
        output_file = self._get_output_file("EXPORT_GLOBAL_VARS_TO_FILE")
        self._add_variable(output_file, name, value)

    def add_module(self, name, value):
        output_file = self._get_output_file("EXPORT_MODULE_VARS_TO_FILE")
        self._add_variable(output_file, name, value)

    def _get_output_file(self, var_name):
        output_file = BuiltIn().get_variable_value("${" + var_name + "}")
        if not output_file:
            raise Exception(var_name + ' not defined.')

        # within the RF execution session, make sure that the previous variables file is backed up and a new one started
        output_file_created = BuiltIn().get_variable_value("${" + var_name + "_CREATED}")
        if not output_file_created:
            self._backup_previous_and_create_new_file(output_file)
            BuiltIn().set_global_variable("${" + var_name + "_CREATED}", output_file)  # just sth non-empty

        return output_file

    @staticmethod
    def _add_variable(output_file, name, value):
        with open(output_file, "rb+") as f:
            f.seek(0, os.SEEK_END)
            f.write(name + " = " + VariablesExporter._format_value(value) + "\r\n")

    @staticmethod
    def _format_value(value):
        if value == "True" or value == "False" or str(value).isdigit():
            return value
        else:
            return "\"" + value + "\""

    @staticmethod
    def _backup_previous_and_create_new_file(path):
        VariablesExporter._assure_directory_exists(path)
        if os.path.isfile(path):
            os.rename(path, VariablesExporter._get_history_file_name(path))
        with open(path, "w+") as f:
            f.write("")

    @staticmethod
    def _assure_directory_exists(f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

    @staticmethod
    def _get_history_file_name(path):
        return path + time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime(os.path.getmtime(path)))
