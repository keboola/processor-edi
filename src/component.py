import csv
import logging
import os
from badx12.parser import Parser

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from configuration import Configuration # noqa


class Component(ComponentBase):

    def __init__(self):
        super().__init__()

    def run(self):
        """
        Main execution code
        """
        # params = Configuration(**self.configuration.parameters)

        input_files = self.get_input_files_definitions()

        if len(input_files) == 0:
            raise UserException("No input tables found")

        for in_file in input_files:
            logging.info(f'Processing input file: {in_file.name}')
            parser = Parser()
            document = parser.parse_document(in_file.full_path).to_dict()

            out_table_name = self.remove_suffix(in_file.name)
            table = self.create_out_table_definition(out_table_name, incremental=True, primary_key=[])
            interchange = document.get("document", {}).get("interchange", {})

            with open(table.full_path, 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=["name", "required", "description", "content",
                                                                  "max_length", "min_length"])
                csv_writer.writeheader()
                for field in self.process_interchange(interchange):
                    csv_writer.writerow(field)

            self.write_manifest(table)

    @staticmethod
    def yield_fields(fields) -> dict:
        if fields:
            for field in fields:
                yield field

    def process_interchange(self, interchange):
        header_fields = interchange.get("header", {}).get("fields")
        yield from self.yield_fields(header_fields)

        trailer_fields = interchange.get("trailer", {}).get("fields")
        yield from self.yield_fields(trailer_fields)

        body = interchange.get("body")
        if body:
            body = body[0]
            body_header_fields = body.get("header", {}).get("fields")
            yield from self.yield_fields(body_header_fields)

            body_trailer_fields = body.get("trailer", {}).get("fields")
            yield from self.yield_fields(body_trailer_fields)

            body_body = body.get("body", [{}])[0]
            body_body_fields = body_body.get("fields")
            yield from self.yield_fields(body_body_fields)

            transaction_sets = body.get("transaction_sets", [{}])
            transaction_set_fields = transaction_sets[0].get("fields")
            yield from self.yield_fields(transaction_set_fields)

        groups = interchange.get("groups")
        if groups:
            groups = groups[0]
            group_header_fields = groups.get("header", {}).get("fields")
            yield from self.yield_fields(group_header_fields)

            group_trailer_fields = groups.get("trailer", {}).get("fields")
            yield from self.yield_fields(group_trailer_fields)

            group_body = groups.get("body", [{}])[0]
            group_body_fields = group_body.get("fields")
            yield from self.yield_fields(group_body_fields)

            group_transaction_sets = group_body.get("transaction_sets", [{}])
            group_transaction_set_fields = group_transaction_sets[0].get("fields")
            yield from self.yield_fields(group_transaction_set_fields)

    @staticmethod
    def remove_suffix(filename: str) -> str:
        """Removes the suffix from a filename."""
        return os.path.splitext(filename)[0]


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
