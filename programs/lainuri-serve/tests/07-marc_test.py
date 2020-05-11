#!/usr/bin/python3

import context

from lainuri.koha_api import MARCRecord


def test_marc_record_parsing(subtests):
  rec = MARCRecord(record_xml)
  assert rec.author() == ""
  assert rec.title() == "12 princess stories."
  assert rec.edition() == "1st ed."
  assert rec.book_cover_url() == "https://topdocumentaryfilms.com/wp-content/uploads/2013/05/this-is-what-winning-looks-like-150x198.jpg"


record_xml = """
<record xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
 <leader>02496cam a2200337 a 4500</leader>
 <controlfield tag="001">13734414</controlfield>
 <controlfield tag="008">040928s2006 nyua j 000 1 eng d</controlfield>
 <datafield tag="010" ind1=" " ind2=" ">
  <subfield code="a"> 2004114274</subfield>
 </datafield>
 <datafield tag="020" ind1=" " ind2=" ">
  <subfield code="a">9780736423519</subfield>
 </datafield>
 <datafield tag="020" ind1=" " ind2=" ">
  <subfield code="a">0736423516</subfield>
 </datafield>
 <datafield tag="035" ind1=" " ind2=" ">
  <subfield code="a">(OCoLC)ocm70833242</subfield>
 </datafield>
 <datafield tag="040" ind1=" " ind2=" ">
  <subfield code="a">OCO</subfield>
  <subfield code="c">OCO</subfield>
  <subfield code="d">BAKER</subfield>
  <subfield code="d">BTCTA</subfield>
  <subfield code="d">DLC</subfield>
 </datafield>
 <datafield tag="042" ind1=" " ind2=" ">
  <subfield code="a">lccopycat</subfield>
 </datafield>
 <datafield tag="050" ind1="0" ind2="0">
  <subfield code="a">PZ7</subfield>
  <subfield code="b">.A1017 2006</subfield>
 </datafield>
 <datafield tag="245" ind1="0" ind2="0">
  <subfield code="a">12 princess stories.</subfield>
 </datafield>
 <datafield tag="246" ind1="3" ind2="0">
  <subfield code="a">Twelve princess stories</subfield>
 </datafield>
 <datafield tag="250" ind1=" " ind2=" ">
  <subfield code="a">1st ed.</subfield>
 </datafield>
 <datafield tag="260" ind1=" " ind2=" ">
  <subfield code="a">[New York :</subfield>
  <subfield code="b">Golden Books,</subfield>
  <subfield code="c">c2006].</subfield>
 </datafield>
 <datafield tag="300" ind1=" " ind2=" ">
  <subfield code="a">1 v. (unpaged) :</subfield>
  <subfield code="b">ill. ;</subfield>
  <subfield code="c">29 cm.</subfield>
 </datafield>
 <datafield tag="490" ind1="0" ind2=" ">
  <subfield code="a">Disney princess</subfield>
 </datafield>
 <datafield tag="500" ind1=" " ind2=" ">
  <subfield code="a">"A Golden tall treasury"--P. [1] of cover.</subfield>
 </datafield>
 <datafield tag="505" ind1="0" ind2=" ">
  <subfield code="a">Disney's Aladdin / [illustrated by Phil Ortiz and Serge Michaels] -- Disney's Beauty and the Beast / [illustrated by the Disney Storybook Artists] -- Disney's Cinderella / [adapted by Nikki Grimes ; illustrated by Don Williams, Jim Story, and H.R. Russell] -- Disney's The little mermaid / [adapted by Stephanie Calmenson ; illustrated by Francesc Mateu] -- Disney's Sleeping Beauty / [adapted by Michael Teitelbaum ; illustrated by Sue DiCicco] -- Disney's Snow White and the Seven Dwarfs / [illustrated by Guell] -- Disney's Beauty and the Beast. Getting to know you / [by Lisa Ann Marsoli ; illustrated by the Disney Storybook Artists] -- Disney's The little mermaid. A whale of a time / [by Irene Trimble ; illustrated by Darryl Goudreau] -- Disney's Mulan / [adapted by Katherine Poindexter ; illustrated by José Cardona and Don Williams] -- Disney's The little mermaid. Make-believe bride / [by K. Emily Hutta ; illustrated by the Disney Storybook Artists] -- Disney's Beauty and the Beast. Friends are sweet / [by Jennifer Liberts ; illustrated by Darrell Baker] -- Disney's Aladdin. One true love / [by Annie Auerbach ; illustrated by the Disney Storybook Artists].</subfield>
 </datafield>
 <datafield tag="710" ind1="2" ind2=" ">
  <subfield code="a">Disney Storybook Artists.</subfield>
 </datafield>
 <datafield tag="856" ind1="4" ind2="2">
  <subfield code="3">Publisher description</subfield>
  <subfield code="u">http://www.loc.gov/catdir/enhancements/fy0620/2004114274-d.html</subfield>
 </datafield>
 <datafield tag="856" ind1="4" ind2="0">
  <subfield code="u">https://topdocumentaryfilms.com/wp-content/uploads/2013/05/this-is-what-winning-looks-like-150x198.jpg</subfield>
  <subfield code="y">IMAGE</subfield>
 </datafield>
 <datafield tag="906" ind1=" " ind2=" ">
  <subfield code="a">7</subfield>
  <subfield code="b">cbc</subfield>
  <subfield code="c">copycat</subfield>
  <subfield code="d">2</subfield>
  <subfield code="e">epcn</subfield>
  <subfield code="f">20</subfield>
  <subfield code="g">y-gencatlg</subfield>
 </datafield>
 <datafield tag="942" ind1=" " ind2=" ">
  <subfield code="2">ddc</subfield>
  <subfield code="c">BK</subfield>
  <subfield code="1">2019-05-13 17:04:57</subfield>
 </datafield>
 <datafield tag="955" ind1=" " ind2=" ">
  <subfield code="a">pc14 2004-09-28</subfield>
  <subfield code="a">lc15 2007-08-29 z-processor</subfield>
  <subfield code="a">xc00 2009-03-02 to USPL/CL</subfield>
  <subfield code="i">xc17 2010-12-23 (Telework) (Out of scope for AC treatment (derivative)) to Rev.</subfield>
  <subfield code="c">xc17 2011-02-01 (Telework) (modify 490) to Rev.</subfield>
  <subfield code="a">xc05 2011-02-07 rev. to BCCD</subfield>
 </datafield>
</record>
"""
