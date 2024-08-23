EDI Files Processor
=============

This processor allows you to convert EDI files into CSV files. It uses edireader library under the hood.
https://github.com/BerryWorksSoftware/edireader

Configuration
=============

The processor currently has no configuration options. It converts EDI files into CSV files with predefined columns.

Sample configuration:
```
  "parameters": {
  }
```

Output
======

### Processor Output Columns

1. filename PK
2. element_Id PK
3. segment_Id
4. element_Composite
5. element_text
6. group_Control
7. group_Date
8. group_GroupType
9. group_StandardCode
10. group_StandardVersion
11. group_Time
12. interchange_AckRequest
13. interchange_Authorization
14. interchange_AuthorizationQual
15. interchange_Control
16. interchange_Date
17. interchange_Security
18. interchange_SecurityQual
19. interchange_Standard
20. interchange_TestIndicator
21. interchange_Time
22. interchange_Version
23. loop_Id
24. receiver_id
25. subelement_Sequence
26. subelement_text
27. submitter_id
28. transaction_Control
29. transaction_DocType
30. transaction_Name
31. transaction_Version
32. group_ApplReceiver
33. group_ApplSender


Development
-----------

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to
your custom path in the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, init the workspace and run the component with following
command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone https://github.com/keboola/processor-edi keboola.processor-edi
cd keboola.processor-edi
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint check using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration
===========

For information about deployment and integration with KBC, please refer to the
[deployment section of developers
documentation](https://developers.keboola.com/extend/component/deployment/)
