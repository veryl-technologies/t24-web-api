import datetime
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

class BuiltinFunctions:
 
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    __version__ = '0.1'

    @staticmethod
    def num_to_short_alphanumeric(i):
        # Note that there is no Z, which is used for other purposes
        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXY'
        length = len(chars)

        result = ''
        while i:
            result = chars[i % length] + result
            i = i // length
        if not result:
            result = chars[0]
        return result

    def get_unique_new_customer_mnemonic(self):
        base = datetime.datetime(2016, 2, 1, 00, 00)
        secondsPassed = int((datetime.datetime.now() - base).total_seconds())
        code = self.num_to_short_alphanumeric(secondsPassed)
        result = code.rjust(8, 'Z')
        return result


class VariablesExporter:
    def add(self, name, value):
        output_file = BuiltIn().get_variable_value("${EXPORT_GLOBAL_VARS_TO_FILE}")
        if output_file and len(output_file) > 0:
            output_file_created = BuiltIn().get_variable_value("${EXPORT_GLOBAL_VARS_TO_FILE_CREATED}")
            if not output_file_created or len(output_file_created) <= 0:
                self._create_output_file(output_file)
                BuiltIn().set_global_variable("${EXPORT_GLOBAL_VARS_TO_FILE_CREATED}", output_file)
                output_file_created = output_file

        self._add_variable(output_file, name, value)

    @staticmethod
    def _add_variable(output_file, name, value):
        with open(output_file, "rb+") as f:
            f.seek(0, os.SEEK_END)
            f.write(name + " = " + VariablesExporter._format_value(value) + "\r\n")
    """ Old format using python method return value
        with open(output_file, "rb+") as f:
            # remove the last character '}'
            f.seek(-1, os.SEEK_END)
            f.truncate()
            f.write("\r\n")
            f.write("            \"" + name + "\": " + VariablesExporter._format_value(value) + ",}")
    """

    @staticmethod
    def _format_value(value):
        if value == "True" or value == "False" or str(value).isdigit():
            return value
        else:
            return "\"" + value + "\""

    @staticmethod
    def _create_output_file(outputFile):
        VariablesExporter._assure_directory_exists(outputFile)

        if os.path.isfile(outputFile):
            os.rename(outputFile, VariablesExporter._get_history_file_name(outputFile))

        """ Old format using python method return value
        with open(outputFile, "w+") as f:
            f.write("def get_variables():\r\n")
            f.write("    return {}")
        """
        with open(outputFile, "w+") as f:
            f.write("")

    @staticmethod
    def _assure_directory_exists(f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

    @staticmethod
    def _get_history_file_name(fileName):
        return fileName + time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime(os.path.getmtime(fileName)))
