import click
from lxml import etree

from xml_format.__about__ import __version__

# Default XSLT content
default_xslt_content = """\
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>

    <!-- Identity transform -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

    <!-- Template to sort attributes -->
    <xsl:template match="*">
        <xsl:copy>
            <!-- Apply the 'id' attribute first if it exists -->
            <xsl:apply-templates select="@id"/>
            <!-- Apply the 'name' attribute second if it exists -->
            <xsl:apply-templates select="@name"/>
            <!-- Apply the rest of the attributes sorted alphabetically -->
            <xsl:apply-templates select="@*[not(name() = 'id' or name() = 'name')]">
                <xsl:sort select="name()"/>
            </xsl:apply-templates>
            <!-- Apply child nodes -->
            <xsl:apply-templates select="node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>"""


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="XML Format")
@click.option(
    "--show-default-transform",
    is_flag=True,
    help="Show the default XSLT transform and exit",
)
@click.option(
    "-t",
    "--transform-file",
    type=click.Path(exists=True, readable=True),
    help="Path to a custom XSLT transform file.",
)
@click.option(
    "-w",
    "--write",
    is_flag=True,
    help="Persist the transformed content to the source file.",
)
@click.argument("filenames", type=click.Path(exists=True), nargs=-1)
def xml_format(transform_file, show_default_transform, write, filenames):
    if show_default_transform:
        click.echo(default_xslt_content)
        return

    if not filenames:
        click.echo("No XML files provided. Use --help for more information.")
        return

    # Load the XSLT content
    xslt_content = readfile(transform_file) if transform_file else default_xslt_content

    for xml_file in filenames:
        xml_content = readfile(xml_file)
        pretty_xml = format_xml_content(xml_content, xslt_content)

        # Write the transformed content back to the source file if --write is specified
        if write:
            writefile(xml_file, pretty_xml)
            click.echo(f"Formatted content of {xml_file}")
        else:
            # Print the transformed XML
            click.echo(f"Formatted content of {xml_file}:\n\n{pretty_xml}")
    return


def readfile(file_path):
    with open(file_path, encoding="utf-8") as f:
        return f.read()


def writefile(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def extract_frontmatter(xml_content):
    """Get the original XML declaration and doctype"""
    frontmatter = ""
    if xml_content.lstrip().startswith("<?xml"):
        xml_declaration_end = xml_content.find("?>") + 2
        frontmatter = xml_content[:xml_declaration_end].strip() + "\n"
        xml_content = xml_content[xml_declaration_end:]

    if xml_content.lstrip().startswith("<!DOCTYPE"):
        doctype_end = xml_content.find(">") + 1
        frontmatter += xml_content[:doctype_end].strip() + "\n"
        xml_content = xml_content[doctype_end:].strip()

    return frontmatter, xml_content


def format_xml_content(xml_content, xslt_content):
    """Format the XML content using XLST transform"""

    frontmatter, xml_content = extract_frontmatter(xml_content)

    parser = etree.XMLParser()
    xml_doc = etree.XML(xml_content, parser)

    xslt_doc = etree.fromstring(xslt_content)  # noqa: S320
    transform = etree.XSLT(xslt_doc)

    result = transform(xml_doc)

    pretty_result = etree.tostring(result, pretty_print=True)
    pretty_xml = pretty_result.decode(encoding="utf-8")

    if frontmatter:
        pretty_xml = frontmatter + pretty_xml

    return pretty_xml
