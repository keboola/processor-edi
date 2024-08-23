import logging
import os
import subprocess
import csv
import xml.etree.ElementTree as ElT
from typing import List, Dict

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from configuration import Configuration # noqa

output_columns = [
    "filename", "element_Id", "segment_Id", "element_Composite", "element_text", "group_Control",
    "group_Date", "group_GroupType", "group_StandardCode",
    "group_StandardVersion", "group_Time", "interchange_AckRequest",
    "interchange_Authorization", "interchange_AuthorizationQual",
    "interchange_Control", "interchange_Date", "interchange_Security",
    "interchange_SecurityQual", "interchange_Standard",
    "interchange_TestIndicator", "interchange_Time", "interchange_Version",
    "loop_Id", "receiver_id", "subelement_Sequence",
    "subelement_text", "submitter_id", "transaction_Control",
    "transaction_DocType", "transaction_Name", "transaction_Version", "group_ApplReceiver", "group_ApplSender",
]


class Component(ComponentBase):

    def __init__(self):
        super().__init__()
        self.element_registry = []

    def run(self):
        """
        Main execution code
        """
        # params = Configuration(**self.configuration.parameters)
        temp_dir = os.path.join(self.data_folder_path, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        [os.remove(os.path.join(temp_dir, f)) for f in os.listdir(temp_dir) if
         os.path.isfile(os.path.join(temp_dir, f))]

        input_files = self.get_input_files_definitions()
        if len(input_files) == 0:
            raise UserException("No input files found")

        for in_file in input_files:
            logging.info(f'Processing input file: {in_file.name}')

            out_path = os.path.join(temp_dir, in_file.name)
            self.run_edireader(edi_input_file=in_file.full_path,
                               xml_output_file=out_path)

        out_t = self.create_out_table_definition("edi_processor_output.csv", columns=output_columns,
                                                 primary_key=["filename", "element_Id"])

        with open(out_t.full_path, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=output_columns)
            writer.writeheader()
            for row in self.parse_xml_folder_to_csv(temp_dir):
                writer.writerow(row)

        self.write_manifest(out_t)

    @staticmethod
    def run_edireader(edi_input_file, xml_output_file=None, acknowledgment_file=None,
                      include_namespace=False, recover_on_error=False, indent_xml=False):
        """
        Launches the EDItoXML Java executable with the given parameters.

        Args:
            edi_input_file (str): Path to the EDI input file to be converted to XML.
            xml_output_file (str, optional): Path to the desired XML output file. If not specified, output will be
             printed to stdout.
            acknowledgment_file (str, optional): Path to the acknowledgment file. Optional parameter.
            include_namespace (bool, optional): Whether to include namespace declarations in the XML. Defaults to False.
            recover_on_error (bool, optional): Whether to attempt recovery and continue parsing after an error in the
            EDI input. Defaults to False.
            indent_xml (bool, optional): Whether to indent the XML output for readability. Defaults to False.

        Returns:
            str: The standard output of the Java process if successful, or an error message if something went wrong.

        Raises:
            subprocess.CalledProcessError: If the Java process encounters an error.
        """
        # Base command
        command = ['java', '-jar', 'src/edireader-5.4.12.jar', edi_input_file]

        # Add optional parameters
        if xml_output_file:
            command.extend(['-o', xml_output_file])
        if acknowledgment_file:
            command.extend(['-a', acknowledgment_file])

        command.extend(['-n', str(include_namespace).lower()])
        command.extend(['-r', str(recover_on_error).lower()])
        command.extend(['-i', str(indent_xml).lower()])

        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise UserException(f"Error occurred: {e.stderr}")

    def parse_xml_to_rows(self, element: ElT.Element, parent_data: Dict[str, str] = None,
                          filename: str = "", submitter_id: str = "", receiver_id: str = "") -> List[Dict[str, str]]:
        current_data = self.initialize_current_data(parent_data, filename, submitter_id, receiver_id)

        self.process_element_attributes(element, current_data)
        self.process_element_text(element, current_data)

        rows = self.handle_children(element, current_data, filename, submitter_id, receiver_id)

        return rows

    @staticmethod
    def initialize_current_data(parent_data: Dict[str, str], filename: str,
                                submitter_id: str, receiver_id: str) -> Dict[str, str]:
        current_data = parent_data.copy() if parent_data else {}
        current_data["filename"] = filename
        current_data["submitter_id"] = submitter_id
        current_data["receiver_id"] = receiver_id
        return current_data

    def process_element_attributes(self, element: ElT.Element, current_data: Dict[str, str]) -> None:
        reference_keys = {'Id', 'Qual'}

        if element.attrib and set(element.attrib.keys()) != reference_keys:
            for k, v in element.attrib.items():
                key = f"{element.tag}_{k}"

                if key == "element_Id":
                    if v in self.element_registry:
                        current_data[key] = f"{v}_{self.element_registry.count(v)}"
                    self.element_registry.append(v)
                else:
                    current_data[key] = v

    @staticmethod
    def process_element_text(element: ElT.Element, current_data: Dict[str, str]) -> None:
        if element.text and element.text.strip():
            current_data[f"{element.tag}_text"] = element.text.strip()

    def handle_children(self, element: ElT.Element, current_data: Dict[str, str],
                        filename: str, submitter_id: str, receiver_id: str) -> List[Dict[str, str]]:
        rows = []
        children = list(element)
        if not children:
            rows.append(current_data)
        else:
            for child in children:
                rows.extend(self.parse_xml_to_rows(element=child, parent_data=current_data, filename=filename,
                                                   submitter_id=submitter_id, receiver_id=receiver_id))
        return rows

    def parse_xml_folder_to_csv(self, folder_path: str) -> dict:
        for filename in sorted(os.listdir(folder_path)):
            self.element_registry = []

            file_path = os.path.join(folder_path, filename)
            tree = ElT.parse(file_path)
            root = tree.getroot()
            submitter_id = root.find('.//sender/address').get('Qual')
            receiver_id = root.find('.//receiver/address').get('Qual')

            new_rows = self.parse_xml_to_rows(root, filename=filename, submitter_id=submitter_id,
                                              receiver_id=receiver_id)
            for row in new_rows:
                if "element_Id" in row:
                    yield row


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
