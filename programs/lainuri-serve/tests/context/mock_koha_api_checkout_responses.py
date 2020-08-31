"""
These examples are copied from live scraper.log entries
"""

from bs4 import BeautifulSoup

def soupify(html_doc):
  soup = BeautifulSoup(html_doc, 'html.parser')
  for e in soup.select('script'): e.decompose() # Remove all script-tags
  return soup

def needs_confirmation_01():
  barcode = '1623220493'
  return (barcode, soupify("""
<!DOCTYPE html>
<!-- TEMPLATE FILE: circulation.tt -->
<html lang="default">
 <head>
  <title>
   Koha › Circulation
        › Checking out to Acevedo, Henry        23529000035676
  </title>
  <!-- local colors -->
  <!-- koha core js -->
 </head>
 <body class="circ" id="circ_circulation">
  <div class="navbar navbar-default" id="header">
   <div class="container-fluid">
    <ul class="nav navbar-nav" id="toplevelmenu">
     <li>
      <a href="/cgi-bin/koha/circ/circulation-home.pl">
       Circulation
      </a>
     </li>
     <li>
      <a href="/cgi-bin/koha/members/members-home.pl">
       Patrons
      </a>
     </li>
     <li class="dropdown">
      <a class="dropdown-toggle" data-toggle="dropdown" href="/cgi-bin/koha/catalogue/search.pl">
       Search
       <b class="caret">
       </b>
      </a>
      <ul class="dropdown-menu">
      </ul>
     </li>
     <li>
      <a href="#" id="cartmenulink">
       Cart
       <span id="basketcount">
       </span>
      </a>
     </li>
     <li class="dropdown">
      <a class="dropdown-toggle" data-toggle="dropdown" href="/cgi-bin/koha/mainpage.pl">
       More
       <b class="caret">
       </b>
      </a>
      <ul class="dropdown-menu">
       <li>
        <a href="/cgi-bin/koha/virtualshelves/shelves.pl">
         Lists
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/cataloguing/addbooks.pl">
         Cataloging
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/authorities/authorities-home.pl">
         Authorities
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/about.pl">
         About Koha
        </a>
       </li>
      </ul>
     </li>
    </ul>
    <ul class="nav navbar-nav pull-right">
     <li class="dropdown">
      <a class="dropdown-toggle" data-toggle="dropdown" href="#" id="drop3" role="button">
       <span class="loggedinusername">
        l-t-dev-good
       </span>
       <span class="separator">
        |
       </span>
       <strong>
        <span id="logged-in-branch-name">
         Midway
        </span>
        <span class="content_hidden" id="logged-in-branch-code">
         MPL
        </span>
       </strong>
       <b class="caret">
       </b>
      </a>
      <ul aria-labelledby="drop3" class="dropdown-menu" role="menu">
       <li>
        <a class="toplinks" href="/cgi-bin/koha/circ/selectbranchprinter.pl">
         Set library
        </a>
       </li>
       <li class="toplinks-myaccount">
        <a class="toplinks" href="/cgi-bin/koha/members/moremember.pl?borrowernumber=19">
         My account
        </a>
       </li>
       <li class="toplinks-mycheckouts">
        <a class="toplinks" href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=19">
         My checkouts
        </a>
       </li>
       <li>
        <a class="toplinks" href="/cgi-bin/koha/mainpage.pl?logout.x=1" id="logout">
         Log out
        </a>
       </li>
      </ul>
     </li>
     <li>
      <a class="toplinks" href="/cgi-bin/koha/help.pl" id="helper">
       Help
      </a>
     </li>
    </ul>
   </div>
   <div id="cartDetails">
    Your cart is empty.
   </div>
  </div>
  <div class="gradient">
   <h1 id="logo">
    <a href="/cgi-bin/koha/mainpage.pl">
    </a>
   </h1>
   <!-- Begin Circulation Resident Search Box -->
   <div id="header_search">
    <div class="residentsearch" id="circ_search">
     <p class="tip">
      Enter patron card number or partial name:
     </p>
     <form action="/cgi-bin/koha/circ/circulation.pl" id="patronsearch" method="post">
      <div class="autocomplete">
       <input autocomplete="off" class="head-searchbox focus" id="findborrower" name="findborrower" size="40" type="text"/>
       <input class="submit" id="autocsubmit" type="submit" value="Submit"/>
      </div>
     </form>
    </div>
    <div class="residentsearch" id="checkin_search">
     <p class="tip">
      Scan a barcode to check in:
     </p>
     <form action="/cgi-bin/koha/circ/returns.pl" autocomplete="off" method="post">
      <input accesskey="r" class="head-searchbox" id="ret_barcode" name="barcode" size="40"/>
      <input class="submit" type="submit" value="Submit"/>
     </form>
    </div>
    <div class="residentsearch" id="renew_search">
     <p class="tip">
      Scan a barcode to renew:
     </p>
     <form action="/cgi-bin/koha/circ/renew.pl" autocomplete="off" method="post">
      <input class="head-searchbox" id="ren_barcode" name="barcode" size="40"/>
      <input class="submit" type="submit" value="Submit"/>
     </form>
    </div>
    <ul>
     <li>
      <a class="keep_text" href="#circ_search">
       Check out
      </a>
     </li>
     <li>
      <a class="keep_text" href="#checkin_search">
       Check in
      </a>
     </li>
     <li>
      <a class="keep_text" href="#renew_search">
       Renew
      </a>
     </li>
    </ul>
   </div>
   <!-- /header_search -->
  </div>
  <!-- /gradient -->
  <!-- End Circulation Resident Search Box -->
  <div id="breadcrumbs">
   <a href="/cgi-bin/koha/mainpage.pl">
    Home
   </a>
   ›
   <a href="/cgi-bin/koha/circ/circulation-home.pl">
    Circulation
   </a>
   ›
   <a href="/cgi-bin/koha/circ/circulation.pl">
    Checkouts
   </a>
   › Henry Acevedo        23529000035676
  </div>
  <div class="yui-t2" id="doc3">
   <div id="bd">
    <div id="yui-main">
     <div class="yui-b">
      <div class="btn-toolbar" id="toolbar">
       <a class="btn btn-default btn-sm" href="/cgi-bin/koha/members/memberentry.pl?op=modify&amp;destination=circ&amp;borrowernumber=19&amp;categorycode=S" id="editpatron">
        <i class="fa fa-pencil">
        </i>
        Edit
       </a>
       <a class="btn btn-default btn-sm" href="/cgi-bin/koha/members/member-password.pl?member=19" id="changepassword">
        <i class="fa fa-lock">
        </i>
        Change password
       </a>
       <a class="btn btn-default btn-sm" href="/cgi-bin/koha/members/memberentry.pl?op=duplicate&amp;borrowernumber=19&amp;categorycode=S" id="duplicate">
        <i class="fa fa-copy">
        </i>
        Duplicate
       </a>
       <div class="btn-group">
        <button class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown">
         <i class="fa fa-print">
         </i>
         Print
         <span class="caret">
         </span>
        </button>
        <ul class="dropdown-menu">
         <li>
          <a href="#" id="printsummary">
           Print summary
          </a>
         </li>
         <li>
          <a href="#" id="printslip">
           Print slip
          </a>
         </li>
         <li>
          <a href="#" id="printquickslip">
           Print quick slip
          </a>
         </li>
         <li>
          <a href="#" id="printcheckinslip">
           Print checked-in today -slip
          </a>
         </li>
         <li>
          <a href="#" id="printfineslip">
           Print fines
          </a>
         </li>
        </ul>
       </div>
       <a class="btn btn-default btn-sm" data-toggle="modal" href="#add_message_form" id="addnewmessageLabel">
        <i class="fa fa-comment-o">
        </i>
        Add message
       </a>
       <div class="btn-group">
        <button class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown">
         More
         <span class="caret">
         </span>
        </button>
        <ul class="dropdown-menu">
         <li>
          <a href="/cgi-bin/koha/members/setstatus.pl?borrowernumber=19&amp;destination=circ&amp;reregistration=y" id="renewpatron">
           Renew patron
          </a>
         </li>
         <li class="disabled">
          <a data-placement="left" data-toggle="tooltip" href="#" id="patronflags" title="You are not authorized to set permissions">
           Set permissions
          </a>
         </li>
         <li class="disabled">
          <a data-placement="left" data-toggle="tooltip" href="#" id="apikeys" title="You are not authorized to manage API keys">
           Manage API keys
          </a>
         </li>
         <li>
          <a href="#" id="deletepatron">
           Delete
          </a>
         </li>
         <li class="disabled">
          <a data-placement="left" data-toggle="tooltip" href="#" id="updatechild" title="Patron is an adult">
           Update child to adult patron
          </a>
         </li>
        </ul>
       </div>
      </div>
     </div>
    </div>
   </div>
  </div>
 </body>
</html>
<li>
 <a href="#" id="exportcheckins">
  Export today's checked in barcodes
 </a>
</li>
<!-- Modal -->
<div aria-hidden="true" aria-labelledby="addnewmessageLabel" class="modal" id="add_message_form" role="dialog" tabindex="-1">
 <div class="modal-dialog">
  <div class="modal-content">
   <form action="/cgi-bin/koha/circ/add_message.pl" id="message_form" method="post" name="message_f">
    <div class="modal-header">
     <h3>
      Leave a message
     </h3>
    </div>
    <div class="modal-body">
     <div class="form-group">
      <label for="message_type">
       Add a message for:
      </label>
      <select id="message_type" name="message_type">
       <option value="L">
        Staff - Internal note
       </option>
       <option value="B">
        OPAC - Henry Acevedo
       </option>
      </select>
     </div>
     <div class="form-group">
      <label for="select_patron_messages">
       Predefined notes:
      </label>
      <select id="select_patron_messages" name="type">
       <option value="">
        Select note
       </option>
       <option value="Address Notes">
        Address Notes
       </option>
      </select>
     </div>
     <div class="form-group">
      <textarea class="modal-textarea" id="borrower_message" name="borrower_message" rows="3"></textarea>
     </div>
     <input name="borrowernumber" type="hidden" value="19"/>
     <input name="batch" type="hidden" value=""/>
     <input name="branchcode" type="hidden" value="MPL"/>
    </div>
    <div class="modal-footer">
     <button class="btn btn-default approve" type="submit">
      <i class="fa fa-check">
      </i>
      Save
     </button>
     <button aria-hidden="true" class="cancel" data-dismiss="modal" href="#">
      <i class="fa fa-times">
      </i>
      Cancel
     </button>
    </div>
   </form>
  </div>
 </div>
</div>
<!--  INITIAL BLOC : PARAMETERS & BORROWER INFO -->
<div class="yui-g">
 <div class="dialog alert audio-alert-action" id="circ_needsconfirmation">
  <h3>
   Cannot check out
  </h3>
  <ul>
  </ul>
  <form action="/cgi-bin/koha/circ/circulation.pl" method="get">
   <input name="borrowernumber" type="hidden" value="19"/>
   <input name="duedatespec" type="hidden" value=""/>
   <input name="restoreduedatespec" type="hidden"/>
   <input name="stickyduedate" type="hidden" value=""/>
   <button class="deny" type="submit">
    <i class="fa fa-times">
    </i>
    Continue
   </button>
  </form>
 </div>
</div>
<!-- NEEDSCONFIRMATION -->
<!-- /impossible -->
<span class="audio-alert-success">
</span>
<!-- BARCODE ENTRY -->
<div class="yui-g">
 <div class="yui-u first">
  <form action="/cgi-bin/koha/circ/circulation.pl" autocomplete="off" id="mainform" method="post" name="mainform">
   <input name="restoreduedatespec" type="hidden"/>
   <fieldset id="circ_circulation_issue">
    <label class="circ_barcode" for="barcode">
     Checking out to Henry Acevedo        23529000035676
    </label>
    <div class="hint">
     Enter item barcode:
    </div>
    <input class="barcode focus" disabled="disabled" id="barcode" name="barcode" size="14" type="text"/>
    <button class="btn btn-default" type="submit">
     Check out
    </button>
    <div id="show-checkout-settings">
     <a href="#">
      <i class="fa fa-caret-right checkout-settings-icon">
      </i>
      Checkout settings
     </a>
    </div>
    <div class="checkout-settings">
     <div class="checkout-setting" id="specify-due-date">
      <div class="hint">
       Specify due date (MM/DD/YYYY)
:
      </div>
      <input id="duedatespec" name="duedatespec" size="13" type="text" value=""/>
      <label for="stickyduedate">
       Remember for session:
      </label>
      <input id="stickyduedate" name="stickyduedate" onclick="this.form.barcode.focus();" type="checkbox"/>
      <button class="btn btn-default btn-sm action" id="cleardate" name="cleardate" onclick="this.checked = false; this.form.duedatespec.value = ''; this.form.stickyduedate.checked = false; this.form.barcode.focus(); return false;">
       Clear
      </button>
     </div>
     <div class="checkout-setting" id="set-automatic-renewal">
      <input disabled="disabled" id="auto_renew" name="auto_renew" type="checkbox" value="auto_renew"/>
      <label for="auto_renew">
       Automatic renewal
      </label>
     </div>
    </div>
    <!-- /.checkout-settings -->
    <input id="borrowernumber" name="borrowernumber" type="hidden" value="19"/>
    <input name="branch" type="hidden" value="MPL"/>
    <input name="print" type="hidden" value="maybe"/>
    <input name="debt_confirmed" type="hidden" value="0"/>
   </fieldset>
  </form>
 </div>
 <!-- /unless noissues -->
 <div class="yui-u">
  <div class="circmessage attention" id="circmessages">
   <h3>
    Attention:
   </h3>
   <ul>
    <div class="circmessage attention" id="ssbb-rootBlockSummary" style="color: rgb(153, 0, 0);">
    </div>
   </ul>
  </div>
  <div class="circmessage" id="messages">
   <h4>
    Messages:
   </h4>
   <ul>
   </ul>
   <a class="btn btn-link btn-sm" data-toggle="modal" href="#add_message_form" id="addnewmessageLabel">
    <i class="fa fa-plus">
    </i>
    Add a new message
   </a>
  </div>
 </div>
</div>
<div class="yui-g">
 <div class="toptabs" id="patronlists">
  <ul>
   <li>
    <a href="#checkouts">
     0 Checkouts
    </a>
   </li>
   <li>
    <a href="#reserves" id="holds-tab">
     0 Holds
    </a>
   </li>
   <li>
    <a href="#reldebarments" id="debarments-tab-link">
     Restrictions
    </a>
   </li>
  </ul>
  <!-- SUMMARY : TODAY & PREVIOUS ISSUES -->
  <div id="checkouts">
   <p>
    Patron has nothing checked out.
   </p>
  </div>
  <div id="reldebarments">
   <p>
    Patron is currently unrestricted.
   </p>
   <div class="" id="ssbb-rootTable" style="margin-bottom: 2em">
   </div>
  </div>
  <div id="reserves">
   <p>
    Patron has nothing on hold.
   </p>
  </div>
  <!-- reservesloop -->
  <!-- borrowernumber and borrower-->
 </div>
</div>
<div class="yui-b">
 <div class="patroninfo">
  <h5>
   Henry Acevedo        23529000035676
  </h5>
  <!--[if IE 6]>
<style type="tex/css">img { width: expression(this.width > 140 ? 140: true);
}</style>
<![endif]-->
  <ul class="patronbriefinfo">
   <li class="patronaddress1">
    4345 Library Rd.
   </li>
   <li class="patroncity">
    Springfield, MA
        44224
   </li>
   <li class="patronphone">
    <a href="tel:%28212%29%20555-1212">
     (212) 555-1212
    </a>
   </li>
   <li>
    <span class="empty">
     No email stored.
    </span>
   </li>
   <li class="patroncategory">
    Category: Staff (S)
   </li>
   <li class="patronlibrary">
    Home library: Midway
   </li>
  </ul>
 </div>
 <div id="menu">
  <ul>
   <li class="active">
    <a href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=19">
     Check out
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=19">
     Details
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/routing-lists.pl?borrowernumber=19">
     Routing lists
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/readingrec.pl?borrowernumber=19">
     Circulation history
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/holdshistory.pl?borrowernumber=19">
     Holds history
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/notices.pl?borrowernumber=19">
     Notices
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/statistics.pl?borrowernumber=19">
     Statistics
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/purchase-suggestions.pl?borrowernumber=19">
     Purchase suggestions
    </a>
   </li>
  </ul>
 </div>
</div>
<!-- Modal -->
<div aria-hidden="true" aria-labelledby="barcodeSubmittedModalLabel" class="modal fade" id="barcodeSubmittedModal" role="dialog" tabindex="-1">
 <div class="modal-dialog">
  <div class="modal-content">
   <div class="modal-header">
    <h3 id="barcodeSubmittedModalLabel">
     Barcode submitted
    </h3>
   </div>
   <div class="modal-body">
    <p>
     You have already submitted a barcode, please wait for the checkout to process...
    </p>
   </div>
  </div>
 </div>
</div>
<div class="navbar navbar-default navbar-fixed-bottom" id="changelanguage">
 <div class="container-fluid">
  <ul class="nav navbar-nav" id="i18nMenu">
   <li class="navbar-text">
    <span class="currentlanguage">
     English
    </span>
   </li>
   <li>
    <a href="/cgi-bin/koha/changelanguage.pl?language=fi-FI">
     Suomi
    </a>
   </li>
  </ul>
 </div>
</div>
<span id="audio-alert">
</span>
  """))

def issueconfirmed_01():
  barcode = '1620154429'
  return (barcode, soupify("""
<!DOCTYPE html>
<!-- TEMPLATE FILE: circulation.tt -->
<html lang="default">
 <head>
  <title>
   Koha › Circulation
        › Checking out to Acevedo, Henry        23529000035676
  </title>
  <!-- local colors -->
  <!-- koha core js -->
 </head>
 <body class="circ" id="circ_circulation">
  <div class="navbar navbar-default" id="header">
   <div class="container-fluid">
    <ul class="nav navbar-nav" id="toplevelmenu">
     <li>
      <a href="/cgi-bin/koha/circ/circulation-home.pl">
       Circulation
      </a>
     </li>
     <li>
      <a href="/cgi-bin/koha/members/members-home.pl">
       Patrons
      </a>
     </li>
     <li class="dropdown">
      <a class="dropdown-toggle" data-toggle="dropdown" href="/cgi-bin/koha/catalogue/search.pl">
       Search
       <b class="caret">
       </b>
      </a>
      <ul class="dropdown-menu">
      </ul>
     </li>
     <li>
      <a href="#" id="cartmenulink">
       Cart
       <span id="basketcount">
       </span>
      </a>
     </li>
     <li class="dropdown">
      <a class="dropdown-toggle" data-toggle="dropdown" href="/cgi-bin/koha/mainpage.pl">
       More
       <b class="caret">
       </b>
      </a>
      <ul class="dropdown-menu">
       <li>
        <a href="/cgi-bin/koha/virtualshelves/shelves.pl">
         Lists
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/cataloguing/addbooks.pl">
         Cataloging
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/authorities/authorities-home.pl">
         Authorities
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/about.pl">
         About Koha
        </a>
       </li>
      </ul>
     </li>
    </ul>
    <ul class="nav navbar-nav pull-right">
     <li class="dropdown">
      <a class="dropdown-toggle" data-toggle="dropdown" href="#" id="drop3" role="button">
       <span class="loggedinusername">
        l-t-dev-good
       </span>
       <span class="separator">
        |
       </span>
       <strong>
        <span id="logged-in-branch-name">
         Midway
        </span>
        <span class="content_hidden" id="logged-in-branch-code">
         MPL
        </span>
       </strong>
       <b class="caret">
       </b>
      </a>
      <ul aria-labelledby="drop3" class="dropdown-menu" role="menu">
       <li>
        <a class="toplinks" href="/cgi-bin/koha/circ/selectbranchprinter.pl">
         Set library
        </a>
       </li>
       <li class="toplinks-myaccount">
        <a class="toplinks" href="/cgi-bin/koha/members/moremember.pl?borrowernumber=19">
         My account
        </a>
       </li>
       <li class="toplinks-mycheckouts">
        <a class="toplinks" href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=19">
         My checkouts
        </a>
       </li>
       <li>
        <a class="toplinks" href="/cgi-bin/koha/mainpage.pl?logout.x=1" id="logout">
         Log out
        </a>
       </li>
      </ul>
     </li>
     <li>
      <a class="toplinks" href="/cgi-bin/koha/help.pl" id="helper">
       Help
      </a>
     </li>
    </ul>
   </div>
   <div id="cartDetails">
    Your cart is empty.
   </div>
  </div>
  <div class="gradient">
   <h1 id="logo">
    <a href="/cgi-bin/koha/mainpage.pl">
    </a>
   </h1>
   <!-- Begin Circulation Resident Search Box -->
   <div id="header_search">
    <div class="residentsearch" id="circ_search">
     <p class="tip">
      Enter patron card number or partial name:
     </p>
     <form action="/cgi-bin/koha/circ/circulation.pl" id="patronsearch" method="post">
      <div class="autocomplete">
       <input autocomplete="off" class="head-searchbox focus" id="findborrower" name="findborrower" size="40" type="text"/>
       <input class="submit" id="autocsubmit" type="submit" value="Submit"/>
      </div>
     </form>
    </div>
    <div class="residentsearch" id="checkin_search">
     <p class="tip">
      Scan a barcode to check in:
     </p>
     <form action="/cgi-bin/koha/circ/returns.pl" autocomplete="off" method="post">
      <input accesskey="r" class="head-searchbox" id="ret_barcode" name="barcode" size="40"/>
      <input class="submit" type="submit" value="Submit"/>
     </form>
    </div>
    <div class="residentsearch" id="renew_search">
     <p class="tip">
      Scan a barcode to renew:
     </p>
     <form action="/cgi-bin/koha/circ/renew.pl" autocomplete="off" method="post">
      <input class="head-searchbox" id="ren_barcode" name="barcode" size="40"/>
      <input class="submit" type="submit" value="Submit"/>
     </form>
    </div>
    <ul>
     <li>
      <a class="keep_text" href="#circ_search">
       Check out
      </a>
     </li>
     <li>
      <a class="keep_text" href="#checkin_search">
       Check in
      </a>
     </li>
     <li>
      <a class="keep_text" href="#renew_search">
       Renew
      </a>
     </li>
    </ul>
   </div>
   <!-- /header_search -->
  </div>
  <!-- /gradient -->
  <!-- End Circulation Resident Search Box -->
  <div id="breadcrumbs">
   <a href="/cgi-bin/koha/mainpage.pl">
    Home
   </a>
   ›
   <a href="/cgi-bin/koha/circ/circulation-home.pl">
    Circulation
   </a>
   ›
   <a href="/cgi-bin/koha/circ/circulation.pl">
    Checkouts
   </a>
   › Henry Acevedo        23529000035676
  </div>
  <div class="yui-t2" id="doc3">
   <div id="bd">
    <div id="yui-main">
     <div class="yui-b">
      <div class="btn-toolbar" id="toolbar">
       <a class="btn btn-default btn-sm" href="/cgi-bin/koha/members/memberentry.pl?op=modify&amp;destination=circ&amp;borrowernumber=19&amp;categorycode=S" id="editpatron">
        <i class="fa fa-pencil">
        </i>
        Edit
       </a>
       <a class="btn btn-default btn-sm" href="/cgi-bin/koha/members/member-password.pl?member=19" id="changepassword">
        <i class="fa fa-lock">
        </i>
        Change password
       </a>
       <a class="btn btn-default btn-sm" href="/cgi-bin/koha/members/memberentry.pl?op=duplicate&amp;borrowernumber=19&amp;categorycode=S" id="duplicate">
        <i class="fa fa-copy">
        </i>
        Duplicate
       </a>
       <div class="btn-group">
        <button class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown">
         <i class="fa fa-print">
         </i>
         Print
         <span class="caret">
         </span>
        </button>
        <ul class="dropdown-menu">
         <li>
          <a href="#" id="printsummary">
           Print summary
          </a>
         </li>
         <li>
          <a href="#" id="printslip">
           Print slip
          </a>
         </li>
         <li>
          <a href="#" id="printquickslip">
           Print quick slip
          </a>
         </li>
         <li>
          <a href="#" id="printcheckinslip">
           Print checked-in today -slip
          </a>
         </li>
         <li>
          <a href="#" id="printfineslip">
           Print fines
          </a>
         </li>
        </ul>
       </div>
       <a class="btn btn-default btn-sm" data-toggle="modal" href="#add_message_form" id="addnewmessageLabel">
        <i class="fa fa-comment-o">
        </i>
        Add message
       </a>
       <div class="btn-group">
        <button class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown">
         More
         <span class="caret">
         </span>
        </button>
        <ul class="dropdown-menu">
         <li>
          <a href="/cgi-bin/koha/members/setstatus.pl?borrowernumber=19&amp;destination=circ&amp;reregistration=y" id="renewpatron">
           Renew patron
          </a>
         </li>
         <li class="disabled">
          <a data-placement="left" data-toggle="tooltip" href="#" id="patronflags" title="You are not authorized to set permissions">
           Set permissions
          </a>
         </li>
         <li class="disabled">
          <a data-placement="left" data-toggle="tooltip" href="#" id="apikeys" title="You are not authorized to manage API keys">
           Manage API keys
          </a>
         </li>
         <li>
          <a href="#" id="deletepatron">
           Delete
          </a>
         </li>
         <li class="disabled">
          <a data-placement="left" data-toggle="tooltip" href="#" id="updatechild" title="Patron is an adult">
           Update child to adult patron
          </a>
         </li>
        </ul>
       </div>
      </div>
     </div>
    </div>
   </div>
  </div>
 </body>
</html>
<li>
 <a href="#" id="exportcheckins">
  Export today's checked in barcodes
 </a>
</li>
<!-- Modal -->
<div aria-hidden="true" aria-labelledby="addnewmessageLabel" class="modal" id="add_message_form" role="dialog" tabindex="-1">
 <div class="modal-dialog">
  <div class="modal-content">
   <form action="/cgi-bin/koha/circ/add_message.pl" id="message_form" method="post" name="message_f">
    <div class="modal-header">
     <h3>
      Leave a message
     </h3>
    </div>
    <div class="modal-body">
     <div class="form-group">
      <label for="message_type">
       Add a message for:
      </label>
      <select id="message_type" name="message_type">
       <option value="L">
        Staff - Internal note
       </option>
       <option value="B">
        OPAC - Henry Acevedo
       </option>
      </select>
     </div>
     <div class="form-group">
      <label for="select_patron_messages">
       Predefined notes:
      </label>
      <select id="select_patron_messages" name="type">
       <option value="">
        Select note
       </option>
       <option value="Address Notes">
        Address Notes
       </option>
      </select>
     </div>
     <div class="form-group">
      <textarea class="modal-textarea" id="borrower_message" name="borrower_message" rows="3"></textarea>
     </div>
     <input name="borrowernumber" type="hidden" value="19"/>
     <input name="batch" type="hidden" value=""/>
     <input name="branchcode" type="hidden" value="MPL"/>
    </div>
    <div class="modal-footer">
     <button class="btn btn-default approve" type="submit">
      <i class="fa fa-check">
      </i>
      Save
     </button>
     <button aria-hidden="true" class="cancel" data-dismiss="modal" href="#">
      <i class="fa fa-times">
      </i>
      Cancel
     </button>
    </div>
   </form>
  </div>
 </div>
</div>
<!--  INITIAL BLOC : PARAMETERS & BORROWER INFO -->
<!-- NEEDSCONFIRMATION -->
<!-- /impossible -->
<span class="audio-alert-success">
</span>
<!-- BARCODE ENTRY -->
<div class="yui-g">
 <div class="yui-u first">
  <form action="/cgi-bin/koha/circ/circulation.pl" autocomplete="off" id="mainform" method="post" name="mainform">
   <input name="restoreduedatespec" type="hidden"/>
   <fieldset class="lastchecked" id="circ_circulation_issue">
    <label class="circ_barcode" for="barcode">
     Checking out to Henry Acevedo        23529000035676
    </label>
    <div class="hint">
     Enter item barcode:
    </div>
    <input class="barcode focus" id="barcode" name="barcode" size="14" type="text"/>
    <button class="btn btn-default" type="submit">
     Check out
    </button>
    <div id="show-checkout-settings">
     <a href="#">
      <i class="fa fa-caret-right checkout-settings-icon">
      </i>
      Checkout settings
     </a>
    </div>
    <div class="checkout-settings">
     <div class="checkout-setting" id="specify-due-date">
      <div class="hint">
       Specify due date (MM/DD/YYYY)
:
      </div>
      <input id="duedatespec" name="duedatespec" size="13" type="text" value=""/>
      <label for="stickyduedate">
       Remember for session:
      </label>
      <input id="stickyduedate" name="stickyduedate" onclick="this.form.barcode.focus();" type="checkbox"/>
      <button class="btn btn-default btn-sm action" id="cleardate" name="cleardate" onclick="this.checked = false; this.form.duedatespec.value = ''; this.form.stickyduedate.checked = false; this.form.barcode.focus(); return false;">
       Clear
      </button>
     </div>
     <div class="checkout-setting" id="set-automatic-renewal">
      <input class="circ_setting" id="auto_renew" name="auto_renew" type="checkbox" value="auto_renew"/>
      <label for="auto_renew">
       Automatic renewal
      </label>
     </div>
    </div>
    <!-- /.checkout-settings -->
    <input id="borrowernumber" name="borrowernumber" type="hidden" value="19"/>
    <input name="branch" type="hidden" value="MPL"/>
    <input name="print" type="hidden" value="maybe"/>
    <input name="debt_confirmed" type="hidden" value="0"/>
   </fieldset>
   <div class="lastchecked">
    <p>
     <strong>
      Checked out:
     </strong>
     27 horas de estúdio. [Sound recording] (1620154429). Due on 10/02/2020
    </p>
   </div>
  </form>
 </div>
 <!-- /unless noissues -->
 <div class="yui-u">
  <div class="circmessage attention" id="circmessages">
   <h3>
    Attention:
   </h3>
   <ul>
    <div class="circmessage attention" id="ssbb-rootBlockSummary" style="color: rgb(153, 0, 0);">
    </div>
   </ul>
  </div>
  <div class="circmessage" id="messages">
   <h4>
    Messages:
   </h4>
   <ul>
   </ul>
   <a class="btn btn-link btn-sm" data-toggle="modal" href="#add_message_form" id="addnewmessageLabel">
    <i class="fa fa-plus">
    </i>
    Add a new message
   </a>
  </div>
 </div>
</div>
<div class="yui-g">
 <div class="toptabs" id="patronlists">
  <ul>
   <li>
    <a href="#checkouts">
     1 Checkout(s)
    </a>
   </li>
   <li>
    <a href="#reserves" id="holds-tab">
     0 Holds
    </a>
   </li>
   <li>
    <a href="#reldebarments" id="debarments-tab-link">
     Restrictions
    </a>
   </li>
  </ul>
  <!-- SUMMARY : TODAY & PREVIOUS ISSUES -->
  <div id="checkouts">
   <div id="issues-table-loading-message">
    <p>
     <a class="btn btn-default" href="#" id="issues-table-load-now-button">
      <i class="fa fa-book">
      </i>
      Show checkouts
     </a>
    </p>
   </div>
   <form action="/cgi-bin/koha/tools/export.pl" class="checkboxed" method="post" name="issues">
    <table id="issues-table" style="width: 100% !Important;">
     <thead>
      <tr>
       <th scope="col">
       </th>
       <th scope="col">
       </th>
       <th scope="col">
        Due date
       </th>
       <th scope="col">
        Due date
       </th>
       <th scope="col">
        Title
       </th>
       <th scope="col">
        Item type
       </th>
       <th scope="col">
        Location
       </th>
       <th scope="col">
        Home library
       </th>
       <th scope="col">
        Checked out on
       </th>
       <th scope="col">
        Checked out from
       </th>
       <th scope="col">
        Call no
       </th>
       <th scope="col">
        Charge
       </th>
       <th scope="col">
        Fine
       </th>
       <th scope="col">
        Price
       </th>
       <th scope="col">
        Renew
        <p class="column-tool">
         <a href="#" id="CheckAllRenewals">
          select all
         </a>
         |
         <a href="#" id="UncheckAllRenewals">
          none
         </a>
        </p>
       </th>
       <th scope="col">
        Check in
        <p class="column-tool">
         <a href="#" id="CheckAllCheckins">
          select all
         </a>
         |
         <a href="#" id="UncheckAllCheckins">
          none
         </a>
        </p>
       </th>
       <th scope="col">
        Export
        <p class="column-tool">
         <a href="#" id="CheckAllExports">
          select all
         </a>
         |
         <a href="#" id="UncheckAllExports">
          none
         </a>
        </p>
       </th>
      </tr>
     </thead>
     <tfoot>
      <tr>
       <td colspan="11" style="text-align: right; font-weight:bold;">
        Totals:
       </td>
       <td id="totaldue" style="text-align: right;">
        0.00
       </td>
       <td id="totalfine" style="text-align: right;">
        0.000000
       </td>
       <td id="totalprice" style="text-align: right;">
       </td>
       <td colspan="3">
        <div class="date-select">
         <p>
          <label for="newduedate">
           Renewal due date:
          </label>
          <input id="newduedate" name="newduedate" size="12" type="text" value=""/>
         </p>
         <p>
          <label for="exemptfine">
           Forgive fines on return:
           <input id="exemptfine" name="exemptfine" type="checkbox" value="1"/>
          </label>
         </p>
        </div>
       </td>
      </tr>
     </tfoot>
    </table>
    <label for="issues-table-load-immediately">
     Always show checkouts immediately
    </label>
    <input id="issues-table-load-immediately" type="checkbox"/>
    <div id="issues-table-actions">
     <fieldset class="action">
      <button class="btn btn-default" id="RenewCheckinChecked">
       <i class="fa fa-check">
       </i>
       Renew or check in selected items
      </button>
      <button class="btn btn-default" id="RenewAll">
       <i class="fa fa-book">
       </i>
       Renew all
      </button>
     </fieldset>
    </div>
   </form>
  </div>
  <div id="reldebarments">
   <p>
    Patron is currently unrestricted.
   </p>
   <div class="" id="ssbb-rootTable" style="margin-bottom: 2em">
   </div>
  </div>
  <div id="reserves">
   <p>
    Patron has nothing on hold.
   </p>
  </div>
  <!-- reservesloop -->
  <!-- borrowernumber and borrower-->
 </div>
</div>
<div class="yui-b">
 <div class="patroninfo">
  <h5>
   Henry Acevedo        23529000035676
  </h5>
  <!--[if IE 6]>
<style type="tex/css">img { width: expression(this.width > 140 ? 140: true);
}</style>
<![endif]-->
  <ul class="patronbriefinfo">
   <li class="patronaddress1">
    4345 Library Rd.
   </li>
   <li class="patroncity">
    Springfield, MA
        44224
   </li>
   <li class="patronphone">
    <a href="tel:%28212%29%20555-1212">
     (212) 555-1212
    </a>
   </li>
   <li>
    <span class="empty">
     No email stored.
    </span>
   </li>
   <li class="patroncategory">
    Category: Staff (S)
   </li>
   <li class="patronlibrary">
    Home library: Midway
   </li>
  </ul>
 </div>
 <div id="menu">
  <ul>
   <li class="active">
    <a href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=19">
     Check out
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=19">
     Details
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/routing-lists.pl?borrowernumber=19">
     Routing lists
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/readingrec.pl?borrowernumber=19">
     Circulation history
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/holdshistory.pl?borrowernumber=19">
     Holds history
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/notices.pl?borrowernumber=19">
     Notices
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/statistics.pl?borrowernumber=19">
     Statistics
    </a>
   </li>
   <li>
    <a href="/cgi-bin/koha/members/purchase-suggestions.pl?borrowernumber=19">
     Purchase suggestions
    </a>
   </li>
  </ul>
 </div>
</div>
<!-- Modal -->
<div aria-hidden="true" aria-labelledby="barcodeSubmittedModalLabel" class="modal fade" id="barcodeSubmittedModal" role="dialog" tabindex="-1">
 <div class="modal-dialog">
  <div class="modal-content">
   <div class="modal-header">
    <h3 id="barcodeSubmittedModalLabel">
     Barcode submitted
    </h3>
   </div>
   <div class="modal-body">
    <p>
     You have already submitted a barcode, please wait for the checkout to process...
    </p>
   </div>
  </div>
 </div>
</div>
<div class="navbar navbar-default navbar-fixed-bottom" id="changelanguage">
 <div class="container-fluid">
  <ul class="nav navbar-nav" id="i18nMenu">
   <li class="navbar-text">
    <span class="currentlanguage">
     English
    </span>
   </li>
   <li>
    <a href="/cgi-bin/koha/changelanguage.pl?language=fi-FI">
     Suomi
    </a>
   </li>
  </ul>
 </div>
</div>
<span id="audio-alert">
</span>
  """))
