import datetime
import logging
import xml.etree.ElementTree as etree
import io
import warnings
import prov
import prov.identifier
from prov.model import DEFAULT_NAMESPACES, sorted_attributes
from prov.constants import *  # NOQA
from prov.serializers import Serializer


__author__ = "Lion Krischer"
__email__ = "krischer@geophysik.uni-muenchen.de"

logger = logging.getLogger(__name__)

# Create a dictionary containing all top-level PROV XML elements for an easy
# mapping.
FULL_NAMES_MAP = dict(PROV_N_MAP)
FULL_NAMES_MAP.update(ADDITIONAL_N_MAP)
# Inverse mapping.
FULL_PROV_RECORD_IDS_MAP = dict(
    (FULL_NAMES_MAP[rec_type_id], rec_type_id) for rec_type_id in FULL_NAMES_MAP
)

XML_XSD_URI = "http://www.w3.org/2001/XMLSchema"


class ProvXMLException(prov.Error):
    pass


class ProvXMLSerializer(Serializer):
    """PROV-XML serializer for :class:`~prov.model.ProvDocument`"""

    def serialize(self, stream, force_types=False, **kwargs):
        """
        Serializes a :class:`~prov.model.ProvDocument` instance to `PROV-XML
        <http://www.w3.org/TR/prov-xml/>`_.

        :param stream: Where to save the output.
        :type force_types: boolean, optional
        :param force_types: Will force xsd:types to be written for most
            attributes mainly PROV-"attributes", e.g. tags not in the
            PROV namespace. Off by default meaning xsd:type attributes will
            only be set for prov:type, prov:location, and prov:value as is
            done in the official PROV-XML specification. Furthermore the
            types will always be set if the Python type requires it. False
            is a good default and it should rarely require changing.
        """
        xml_root = self.serialize_bundle(bundle=self.document, force_types=force_types)
        for bundle in self.document.bundles:
            self.serialize_bundle(
                bundle=bundle, element=xml_root, force_types=force_types
            )
        # No encoding must be specified when writing to String object which
        # does not have the concept of an encoding as it should already
        # represent unicode code points.
        et = etree.ElementTree(xml_root)
        if isinstance(stream, io.TextIOBase):
            stream.write(
                map_namespaces(etree.tostring(et.getroot()).decode(
                    "utf-8"
                ),{n.prefix: n.uri for n in ([XSD,PROV,XSI]+[n for n in self.document.get_registered_namespaces()])})
            )
        else:
            et.write(stream, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    def serialize_bundle(self, bundle, element=None, force_types=False):
        """
        Serializes a bundle or document to PROV XML.

        :param bundle: The bundle or document.
        :param element: The XML element to write to. Will be created if None.
        :type force_types: boolean, optional
        :param force_types: Will force xsd:types to be written for most
            attributes mainly PROV-"attributes", e.g. tags not in the
            PROV namespace. Off by default meaning xsd:type attributes will
            only be set for prov:type, prov:location, and prov:value as is
            done in the official PROV-XML specification. Furthermore the
            types will always be set if the Python type requires it. False
            is a good default and it should rarely require changing.
        """
        # Build the namespace map for lxml and attach it to the root XML
        # element.
        nsmap = {
            ns.prefix: ns.uri
            for ns in self.document._namespaces.get_registered_namespaces()
        }
        if self.document._namespaces._default:
            nsmap[None] = self.document._namespaces._default.uri
        for namespace in bundle.namespaces:
            if namespace not in nsmap:
                nsmap[namespace.prefix] = namespace.uri

        for key, value in DEFAULT_NAMESPACES.items():
            uri = value.uri
            if value.prefix == "xsd":
                # The XSD namespace for some reason has no hash at the end
                # for PROV XML, but for all other serializations it does.
                uri = uri.rstrip("#")
            nsmap[value.prefix] = uri

        if element is not None:
            xml_bundle_root = etree.SubElement(
                element, _ns_prov("bundleContent")
            )
        else:
            xml_bundle_root = etree.Element(_ns_prov("document"))

        if bundle.identifier:
            xml_bundle_root.attrib[_ns_prov("id")] = str(bundle.identifier)

        for record in bundle._records:
            rec_type = record.get_type()
            identifier = str(record._identifier) if record._identifier else None

            if identifier:
                attrs = {_ns_prov("id"): identifier}
            else:
                attrs = None

            # Derive the record label from its attributes which is sometimes
            # needed.
            attributes = list(record.attributes)
            rec_label = self._derive_record_label(rec_type, attributes)

            elem = etree.SubElement(xml_bundle_root, _ns_prov(rec_label), attrs if attrs is not None else {})

            for attr, value in sorted_attributes(rec_type, attributes):
                subelem = etree.SubElement(
                    elem, _ns(attr.namespace.uri, attr.localpart)
                )
                if isinstance(value, prov.model.Literal):
                    if value.datatype not in [None, PROV["InternationalizedString"]]:
                        subelem.attrib[_ns_xsi("type")] = "%s:%s" % (
                            value.datatype.namespace.prefix,
                            value.datatype.localpart,
                        )
                    if value.langtag is not None:
                        subelem.attrib[_ns_xml("lang")] = value.langtag
                    v = value.value
                elif isinstance(value, prov.model.QualifiedName):
                    if attr not in PROV_ATTRIBUTE_QNAMES:
                        subelem.attrib[_ns_xsi("type")] = "xsd:QName"
                    v = str(value)
                elif isinstance(value, datetime.datetime):
                    v = value.isoformat()
                else:
                    v = str(value)

                # xsd type inference.
                #
                # This is a bit messy and there are all kinds of special
                # rules but it appears to get the job done.
                #
                # If it is a type element and does not yet have an
                # associated xsi type, try to infer it from the value.
                # The not startswith("prov:") check is a little bit hacky to
                # avoid type interference when the type is a standard prov
                # type.
                #
                # To enable a mapping of Python types to XML and back,
                # the XSD type must be written for these types.
                ALWAYS_CHECK = [
                    bool,
                    datetime.datetime,
                    float,
                    int,
                    prov.identifier.Identifier,
                ]
                ALWAYS_CHECK = tuple(ALWAYS_CHECK)
                if (
                    (
                        force_types
                        or type(value) in ALWAYS_CHECK
                        or attr in [PROV_TYPE, PROV_LOCATION, PROV_VALUE]
                    )
                    and _ns_xsi("type") not in subelem.attrib
                    and not str(value).startswith("prov:")
                    and not (attr in PROV_ATTRIBUTE_QNAMES and v)
                    and attr not in [PROV_ATTR_TIME, PROV_LABEL]
                ):
                    xsd_type = None
                    if isinstance(value, bool):
                        xsd_type = XSD_BOOLEAN
                        v = v.lower()
                    elif isinstance(value, str):
                        xsd_type = XSD_STRING
                    elif isinstance(value, float):
                        xsd_type = XSD_DOUBLE
                    elif isinstance(value, int):
                        xsd_type = XSD_INT
                    elif isinstance(value, datetime.datetime):
                        # Exception of the exception, while technically
                        # still correct, do not write XSD dateTime type for
                        # attributes in the PROV namespaces as the type is
                        # already declared in the XSD and PROV XML also does
                        # not specify it in the docs.
                        if (
                            attr.namespace.prefix != "prov"
                            or "time" not in attr.localpart.lower()
                        ):
                            xsd_type = XSD_DATETIME
                    elif isinstance(value, prov.identifier.Identifier):
                        xsd_type = XSD_ANYURI

                    if xsd_type is not None:
                        subelem.attrib[_ns_xsi("type")] = str(xsd_type)

                if attr in PROV_ATTRIBUTE_QNAMES and v:
                    subelem.attrib[_ns_prov("ref")] = v
                else:
                    subelem.text = v
        return xml_bundle_root

    def deserialize(self, stream, **kwargs):
        """
        Deserialize from `PROV-XML <http://www.w3.org/TR/prov-xml/>`_
        representation to a :class:`~prov.model.ProvDocument` instance.

        :param stream: Input data.
        """
        if isinstance(stream, io.TextIOBase):
            with io.BytesIO() as buf:
                buf.write(stream.read().encode("utf-8"))
                buf.seek(0, 0)
                xml_doc = etree.parse(buf).getroot()
        else:
            xml_doc = etree.parse(stream).getroot()

        # Remove all comments.
        for c in xml_doc.xpath("//comment()"):
            p = c.getparent()
            p.remove(c)

        document = prov.model.ProvDocument()
        self.deserialize_subtree(xml_doc, document)
        return document

    def deserialize_subtree(self, xml_doc, bundle):
        """
        Deserialize an etree element containing a PROV document or a bundle
        and write it to the provided internal object.

        :param xml_doc: An etree element containing the information to read.
        :param bundle: The bundle object to write to.
        """

        for element in xml_doc:
            qname = etree.QName(element)
            if qname.namespace != DEFAULT_NAMESPACES["prov"].uri:
                raise ProvXMLException(
                    "Non PROV element discovered in " "document or bundle."
                )
            # Ignore the <prov:other> element storing non-PROV information.
            if qname.localname == "other":
                warnings.warn(
                    "Document contains non-PROV information in "
                    "<prov:other>. It will be ignored in this package.",
                    UserWarning,
                )
                continue

            id_tag = _ns_prov("id")
            rec_id = element.attrib[id_tag] if id_tag in element.attrib else None

            if rec_id is not None:
                # Try to make a qualified name out of it!
                rec_id = xml_qname_to_QualifiedName(element, rec_id)

            # Recursively read bundles.
            if qname.localname == "bundleContent":
                b = bundle.bundle(identifier=rec_id)
                self.deserialize_subtree(element, b)
                continue

            attributes = _extract_attributes(element)

            # Map the record type to its base type.
            q_prov_name = FULL_PROV_RECORD_IDS_MAP[qname.localname]
            rec_type = PROV_BASE_CLS[q_prov_name]

            if _ns_xsi("type") in element.attrib:
                value = xml_qname_to_QualifiedName(
                    element, element.attrib[_ns_xsi("type")]
                )
                attributes.append((PROV["type"], value))

            rec = bundle.new_record(rec_type, rec_id, attributes)

            # Add the actual type in case a base type has been used.
            if rec_type != q_prov_name:
                rec.add_asserted_type(q_prov_name)
        return bundle

    def _derive_record_label(self, rec_type, attributes):
        """
        Helper function trying to derive the record label taking care of
        subtypes and what not. It will also remove the type declaration for
        the attributes if it was used to specialize the type.

        :param rec_type: The type of records.
        :param attributes: The attributes of the record.
        """
        rec_label = FULL_NAMES_MAP[rec_type]

        for key, value in list(attributes):
            if key != PROV_TYPE:
                continue
            if isinstance(value, prov.model.Literal):
                value = value.value
            if value in PROV_BASE_CLS and PROV_BASE_CLS[value] != value:
                attributes.remove((key, value))
                rec_label = FULL_NAMES_MAP[value]
                break
        return rec_label


def _extract_attributes(element):
    """
    Extract the PROV attributes from an etree element.

    :param element: The lxml.etree.Element instance.
    """
    attributes = []
    for subel in element:
        sqname = etree.QName(subel)
        _t = xml_qname_to_QualifiedName(
            subel, "%s:%s" % (subel.prefix, sqname.localname)
        )

        for key, value in subel.attrib.items():
            if key == _ns_xsi("type"):
                datatype = xml_qname_to_QualifiedName(subel, value)
                if datatype == XSD_QNAME:
                    _v = xml_qname_to_QualifiedName(subel, subel.text)
                else:
                    _v = prov.model.Literal(subel.text, datatype)
            elif key == _ns_prov("ref"):
                _v = xml_qname_to_QualifiedName(subel, value)
            elif key == _ns_xml("lang"):
                _v = prov.model.Literal(subel.text, langtag=value)
            else:
                warnings.warn(
                    "The element '%s' contains an attribute %s='%s' "
                    "which is not representable in the prov module's "
                    "internal data model and will thus be ignored."
                    % (_t, str(key), str(value)),
                    UserWarning,
                )

        if not subel.attrib:
            _v = subel.text

        attributes.append((_t, _v))

    return attributes


def xml_qname_to_QualifiedName(element, qname_str):
    if ":" in qname_str:
        prefix, localpart = qname_str.split(":", 1)
        if prefix in element.nsmap:
            ns_uri = element.nsmap[prefix]
            if ns_uri == XML_XSD_URI:
                ns = XSD  # use the standard xsd namespace (i.e. with #)
            elif ns_uri == PROV.uri:
                ns = PROV
            else:
                ns = Namespace(prefix, ns_uri)
            return ns[localpart]
    # case 1: no colon
    # case 2: unknown prefix
    if None in element.nsmap:
        ns_uri = element.nsmap[None]
        ns = Namespace("", ns_uri)
        return ns[qname_str]
    # no default namespace
    raise ProvXMLException(
        'Could not create a valid QualifiedName for "%s"' % qname_str
    )


def _ns(ns, tag):
    return "{%s}%s" % (ns, tag)


def _ns_prov(tag):
    return _ns(DEFAULT_NAMESPACES["prov"].uri, tag)


def _ns_xsi(tag):
    return _ns(DEFAULT_NAMESPACES["xsi"].uri, tag)


def _ns_xml(tag):
    NS_XML = "http://www.w3.org/XML/1998/namespace"
    return _ns(NS_XML, tag)

### INJECTED CODE HERE ###

import xml.sax
import xml.sax.saxutils
import xml.sax.xmlreader
from io import StringIO

def map_namespaces(xml_document, prefix_to_url):
    """
    Maps XML namespaces of a given XML document (as a string) to another.
    """
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = NamespaceReplacer(prefix_to_url)
    parser.setContentHandler(handler)
    parser.parse(StringIO(xml_document))
    return handler.tostring()


class NamespaceMapping():
    def __init__(self, base_mapping = None):
        self._base_mapping = base_mapping
        self._mappings = []

    def base(self):
        return self._base_mapping

    def map(self, prefix, uri):
        self._mappings.append( ( prefix, uri ) )

    def get_prefix_of(self, uri : str) -> str:
        for mapping in self._mappings:
            if mapping[1] == uri:
                return mapping[0]

        if self._base_mapping is not None:
            return self._base_mapping.get_prefix_of(uri)

        return None

    def get_uri_of(self, prefix : str) -> str:
        for mapping in self._mappings:
            if mapping[0] == prefix:
                return mapping[1]

        if self._base_mapping is not None:
            return self._base_mapping.get_uri_of(prefix)

        return None

class NamespaceReplacer(xml.sax.ContentHandler):
    def __init__(self, desired_mappings : dict):
        # desired mapping is { prefix: uri }
        self._output = StringIO()
        self._handler = xml.sax.saxutils.XMLGenerator(self._output, 'UTF-8')
        self._desired_mappings = desired_mappings

    def startDocument(self):
        """
        Receive notification of the beginning of a document.
        """
        self._mapping = None
        self._depth = 0
        self._declared_mappings = {}
        self._handler.startDocument()

    def startElement(self, name : str, attrs : xml.sax.xmlreader.AttributesImpl):
        """
        Signals the start of an element in non-namespace mode.
        """

        self._depth += 1

        # populate the namespace mappings of the source document.
        self._mapping = NamespaceMapping(self._mapping)
        for attribute_name in attrs.keys():
            if attribute_name == "xmlns":
                namespace_name = ""
            elif attribute_name.startswith("xmlns:"):
                namespace_name = attribute_name[len("xmlns:"):]
            else:
                continue
            attribute_value = attrs.getValue(attribute_name)
            self._mapping.map(namespace_name, attribute_value)

        # create a set of mapped attributes
        output_attribute_dict = {}

        # if this is the root element, add desired mappings.
        if self._depth == 1:
            for prefix in self._desired_mappings:
                attribute_value = self._desired_mappings[prefix]
                attribute_name = "xmlns" if len(prefix) == 0 else f"xmlns:{prefix}"
                output_attribute_dict[attribute_name] = attribute_value

        # map namespaces to other attributes.
        for attribute_name in attrs.keys():
            attribute_value = attrs.getValue(attribute_name)
            if attribute_name == "xmlns" or attribute_name.startswith("xmlns:"):
                # this is XML namespace declaration.
                # if the URI is already in the desired mappings, skip.
                if attribute_value in self._desired_mappings.values():
                    continue

                if attribute_name == "xmlns":
                    namespace_name = ""
                elif attribute_name.startswith("xmlns:"):
                    namespace_name = attribute_name[len("xmlns:"):]

                mapped_prefixes = [prefix for prefix, uri in self._declared_mappings.items() if uri == attribute_value]

                if len(mapped_prefixes) == 0:
                    mapped_prefixes = [ f"ns{len(self._declared_mappings) + 1}" ]
                    self._declared_mappings[ mapped_prefixes[0] ] = attribute_value

                attribute_name = "xmlns" if len(mapped_prefixes[0]) == 0 else f"xmlns:{mapped_prefixes[0]}"
                output_attribute_dict[attribute_name] = attribute_value
            else:
                mapped_attribute_name = self._translate_name(attribute_name)
                output_attribute_dict[mapped_attribute_name] = attribute_value

        mapped_name = self._translate_name(name)

        self._handler.startElement(mapped_name, xml.sax.xmlreader.AttributesImpl(output_attribute_dict))

    def endElement(self, name : str):
        """
        Signals the start of an element in non-namespace mode.
        """
        actual_name = self._translate_name(name)
        self._mapping = self._mapping.base()
        self._handler.endElement(actual_name)

    def endDocument(self):
        """
        Receive notification of the end of a document.
        """
        self._handler.endDocument()

    def tostring(self):
        return self._output.getvalue()

    def _translate_name(self, name : str) -> str:
        original_prefix = ''
        if ':' in name:
            index = name.index(':')
            original_prefix = name[0:index]
            name = name[index+1:]

        desired_uri = self._mapping.get_uri_of(original_prefix)

        mapped_prefixes = [prefix for prefix, uri in self._desired_mappings.items() if uri == desired_uri]
        if len(mapped_prefixes) == 0:
            mapped_prefixes = [prefix for prefix, uri in self._declared_mappings.items() if uri == desired_uri]

        prefix = "" if len(mapped_prefixes) == 0 else mapped_prefixes[0]

        return name if len(prefix) == 0 else f"{prefix}:{name}"
