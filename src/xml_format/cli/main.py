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
    if transform_file:
        with open(transform_file) as xslt_file:
            xslt_content = xslt_file.read()
    else:
        xslt_content = default_xslt_content

    xslt_doc = etree.fromstring(xslt_content)  # noqa: S320
    transform = etree.XSLT(xslt_doc)

    for xml_file in filenames:
        xml_doc = etree.parse(xml_file)  # noqa: S320
        result = transform(xml_doc)

        pretty_result = etree.tostring(result, pretty_print=True)
        pretty_xml = pretty_result.decode(encoding="utf-8")

        frontmatter = extract_frontmatter(xml_file)
        if frontmatter:
            pretty_xml = frontmatter + pretty_xml

        # Write the transformed content back to the source file if --write is specified
        if write:
            with open(xml_file, "w", encoding="utf-8") as file:
                file.write(pretty_xml)
            click.echo(f"Formatted content of {xml_file}")
        else:
            # Print the transformed XML
            click.echo(f"Formatted content of {xml_file}:\n\n{pretty_xml}")
    return


def extract_frontmatter(xml_file):
    """Get the original XML declaration and doctype"""
    frontmatter = ""
    with open(xml_file, encoding="utf-8") as file:
        xml_content = file.read()

        if xml_content.lstrip().startswith("<?xml"):
            xml_declaration_end = xml_content.find("?>") + 2
            frontmatter = xml_content[:xml_declaration_end] + "\n"
            xml_content = xml_content[xml_declaration_end:].lstrip()

        if xml_content.lstrip().startswith("<!DOCTYPE"):
            doctype_end = xml_content.find(">") + 1
            frontmatter += xml_content[:doctype_end] + "\n"

    return frontmatter
