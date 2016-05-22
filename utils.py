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

class VariablesExporter():
    def add(self, name, value):
        try:
            outputFile = BuiltIn().get_variable_value("${EXPORT_GLOBAL_VARS_TO_FILE}")
            if outputFile and len(outputFile) > 0:
                outputFileCreated = BuiltIn().get_variable_value("${EXPORT_GLOBAL_VARS_TO_FILE_CREATED}")
                if not outputFileCreated or len(outputFileCreated) <= 0:
                    self._create_output_file(outputFile)
                    BuiltIn().set_global_variable("${EXPORT_GLOBAL_VARS_TO_FILE_CREATED}", outputFile)
                    outputFileCreated = outputFile

                self._add_variable(outputFile, name, value)
        except:
            pass

    def _add_variable(self, outputFile, name, value):
        with open(outputFile,"rb+") as f:
            # remove the last character '}'
            f.seek(-1, os.SEEK_END)
            f.truncate()
            f.write("\r\n")
            f.write("            \"" + name + "\": " + self._format_value(value) + ",}")

    def _format_value(self, value):
        if value == "True" or value == "False" or str(value).isdigit():
            return value
        else:
            return "\"" + value + "\""

    def _create_output_file(self, outputFile):
        self._assure_directory_exists(outputFile)

        if os.path.isfile(outputFile):
            os.rename(outputFile, self._get_history_file_name(outputFile))

        with open(outputFile,"w+") as f:
            f.write("def get_variables():\r\n")
            f.write("    return {}")

    def _assure_directory_exists(self, f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

    def _get_history_file_name(self, fileName):
        return fileName + time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime(os.path.getmtime(fileName)))