from xml_format.cli.main import default_xslt_content, format_xml_content

xml_content = """\
<?xml version="1.0" encoding="utf-8" ?>
<example z="last" name="exampleName" id="123" a="first" b="second">
    <child name="childName" id="456" z="lastChild" a="firstChild" />
</example>
"""

expected_output_xml = """\
<?xml version="1.0" encoding="utf-8" ?>
<example id="123" name="exampleName" a="first" b="second" z="last">
    <child id="456" name="childName" a="firstChild" z="lastChild"/>
</example>
"""


def test_xml_format():
    formatted = format_xml_content(xml_content, default_xslt_content)

    assert (
        formatted == expected_output_xml
    ), f"Test failed. Expected output:\n{expected_output_xml}\n\nGot:\n{formatted}"
