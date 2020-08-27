from bs4 import BeautifulSoup

def soupify(html_doc):
  return BeautifulSoup(html_doc, 'html.parser')

def transfer_with_outstanding_fines_01():
  barcode = '1623220493'
  return (barcode, soupify("""
<body class="circ" id="circ_returns">
 <span class="audio-alert-success">
 </span>
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
       MIK2
      </span>
      <span class="separator">
       |
      </span>
      <strong>
       <span id="logged-in-branch-name">
        Mikkelin kampuskirjasto
       </span>
       <span class="content_hidden" id="logged-in-branch-code">
        MIK
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
       <a class="toplinks" href="/cgi-bin/koha/members/moremember.pl?borrowernumber=39586">
        My account
       </a>
      </li>
      <li class="toplinks-mycheckouts">
       <a class="toplinks" href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=39586">
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
    Xamk
   </a>
  </h1>
  <!-- Begin Checkin Resident Search Box -->
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
     <a class="keep_text" href="#renew_search">
      Renew
     </a>
    </li>
   </ul>
  </div>
 </div>
 <!-- /gradient -->
 <!-- End Checkin Resident Search Box -->
 <div id="breadcrumbs">
  <a href="/cgi-bin/koha/mainpage.pl">
   Home
  </a>
  ›
  <a href="/cgi-bin/koha/circ/circulation-home.pl">
   Circulation
  </a>
  › Check in
 </div>
 <div class="yui-t2" id="doc3">
  <div id="bd">
   <div id="yui-main">
    <div class="yui-b">
     <div class="yui-g">
      <!-- Patron has added an issue note -->
      <!-- Patron has fines -->
      <div class="dialog alert">
       <h3>
        Patron has outstanding fines of 4.00.
       </h3>
       <p>
        <a href="/cgi-bin/koha/members/pay.pl?borrowernumber=7905">
         Make payment
        </a>
        .
       </p>
      </div>
      <!-- Patron has waiting holds -->
      <!-- Patron is restricted and checkin was backdated -->
      <!-- case of a mistake in transfer loop -->
      <!-- transfer: item with no reservation, must be returned according to home library circulation rules -->
      <div class="dialog message audio-alert-action" id="return1">
       <h3>
        Please return item to: Kouvolan kampuskirjasto
       </h3>
       <p>
        <a href="/cgi-bin/koha/catalogue/detail.pl?type=intra&amp;biblionumber=185357">
         1623220493: Buenas migas.
        </a>
       </p>
       <p>
        <button class="openWin" data-url="transfer-slip.pl?transferitem=88583&amp;branchcode=KOU&amp;op=slip" type="button">
         <i class="fa fa-print">
         </i>
         Print slip
        </button>
       </p>
      </div>
      <!-- case of simple return no issue or transfer but with a reservation  -->
      <div class="dialog message" id="exemptfines" style="display:none;">
       <p>
        Fines for returned items are forgiven.
       </p>
      </div>
      <div class="dialog message" id="forgivemanualholdsexpire-alert" style="display:none;">
       <p>
        Fines are not charged for manually cancelled holds.
       </p>
      </div>
      <div class="dialog message" id="dropboxmode" style="display:none;">
       <p>
        Book drop mode.  (Effective checkin date is 26.08.2020 13:01 ).
       </p>
      </div>
     </div>
     <div class="yui-g">
      <form action="/cgi-bin/koha/circ/returns.pl" autocomplete="off" id="checkin-form" method="post">
       <div class="yui-u first">
        <fieldset>
         <legend>
          Check in
         </legend>
         <label for="barcode">
          Enter item barcode:
         </label>
         <input class="focus" id="barcode" name="barcode" size="14"/>
         <input class="submit" type="submit" value="Submit"/>
         <div class="date-select" id="return_date_override_fields">
          <div class="hint">
           Specify return date (DD.MM.YYYY)
:
          </div>
          <input id="return_date_override" name="return_date_override" size="13" type="text" value=""/>
          <label for="return_date_override_remember">
           Remember for next check in:
          </label>
          <input id="return_date_override_remember" name="return_date_override_remember" onclick="this.form.barcode.focus();" type="checkbox"/>
          <input class="action" id="cleardate" name="cleardate" onclick="this.checked = false; this.form.return_date_override.value = ''; this.form.return_date_override_remember.checked = false; this.form.barcode.focus(); return false;" type="button" value="Clear"/>
         </div>
         <input name="ri-0" type="hidden" value="1623220493"/>
         <input name="dd-0" type="hidden" value="2020-09-24 23:59"/>
         <input name="bn-0" type="hidden" value="7905"/>
        </fieldset>
       </div>
       <div class="yui-u">
        <fieldset id="checkin_options">
         <legend>
          Options
         </legend>
         <!-- overduecharges -->
         <p>
          <input id="dropboxcheck" name="dropboxmode" type="checkbox" value="dropboxmode"/>
          <label for="dropboxcheck">
           Book drop mode
          </label>
         </p>
         <p>
          <input id="forgivemanualholdsexpire" name="forgivemanualholdsexpire" type="checkbox" value="forgivemanualholdsexpire"/>
          <label for="forgivemanualholdsexpire">
           Forgive fees for manually expired holds
          </label>
         </p>
        </fieldset>
       </div>
      </form>
     </div>
     <h2>
      Checked-in items
     </h2>
     <table id="checkedintable">
      <thead>
       <tr>
        <th class="ci-duedate">
         Due date
        </th>
        <th class="ci-title">
         Title
        </th>
        <th class="ci-author">
         Author
        </th>
        <th class="ci-barcode">
         Barcode
        </th>
        <th class="ci-homelibrary">
         Home library
        </th>
        <th class="ci-holdinglibrary">
         Holding library
        </th>
        <th class="ci-shelvinglocation">
         Shelving location
        </th>
        <th class="ci-callnumber">
         Call number
        </th>
        <th class="ci-dateaccessioned">
         Date acquired
        </th>
        <th class="ci-type">
         Type
        </th>
        <th class="ci-patron">
         Patron
        </th>
        <th class="ci-note">
         Note
        </th>
       </tr>
      </thead>
      <tr>
       <td class="ci-duedate">
        24.09.2020 23:59
       </td>
       <td class="ci-title">
        <a href="/cgi-bin/koha/catalogue/detail.pl?biblionumber=185357">
         Buenas migas.
        </a>
       </td>
       <td class="ci-author">
       </td>
       <td class="ci-barcode">
        <a href="/cgi-bin/koha/catalogue/moredetail.pl?biblionumber=185357&amp;itemnumber=88583#item88583">
         1623220493
        </a>
       </td>
       <td class="ci-homelibrary">
        Kouvolan kampuskirjasto
       </td>
       <td class="ci-holdinglibrary">
        Kouvolan kampuskirjasto
       </td>
       <td class="ci-shelvinglocation">
        Lainattavat
       </td>
       <td class="ci-callnumber">
        89.6307 BUENAS
       </td>
       <td class="ci-dateaccessioned">
        25.08.2014
       </td>
       <td class="ci-type">
        Laina14
       </td>
       <td class="ci-patron">
        <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=7905">
         Koehenkilö, Erkki Ilmari (XAMKOPISK)
        </a>
        <span class="results_summary nowrap">
         <span class="label">
          Checkouts:
         </span>
         <span class="number_box">
          <a href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=7905">
           3
          </a>
         </span>
        </span>
       </td>
       <td class="ci-note">
       </td>
      </tr>
     </table>
    </div>
   </div>
   <div class="yui-b noprint">
    <div id="navmenu">
     <div id="navmenulist">
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/circulation-home.pl">
         Circulation home
        </a>
       </li>
      </ul>
      <h5>
       Circulation
      </h5>
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/circulation.pl">
         Check out
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/returns.pl">
         Check in
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/renew.pl">
         Renew
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/branchtransfers.pl">
         Transfer
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/selectbranchprinter.pl">
         Set library
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/cataloguing/addbiblio.pl?frameworkcode=FA">
         Fast cataloging
        </a>
       </li>
      </ul>
      <h5>
       Circulation reports
      </h5>
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/view_holdsqueue.pl">
         Holds queue
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/pendingreserves2.pl">
         Holds to pull
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/waitingreserves.pl">
         Holds awaiting pickup
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/reserveratios.pl">
         Hold ratios
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/transferstoreceive.pl">
         Transfers to receive
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/branchoverdues.pl">
         Overdues with fines
        </a>
       </li>
      </ul>
     </div>
    </div>
   </div>
  </div>
 </div>
</body>
  """))

def hold_transfer_with_outstanding_fines_01():
  barcode = '1620161108'
  return (barcode, soupify("""
<body class="circ" id="circ_returns">
 <span class="audio-alert-success">
 </span>
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
       MIK2
      </span>
      <span class="separator">
       |
      </span>
      <strong>
       <span id="logged-in-branch-name">
        Mikkelin kampuskirjasto
       </span>
       <span class="content_hidden" id="logged-in-branch-code">
        MIK
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
       <a class="toplinks" href="/cgi-bin/koha/members/moremember.pl?borrowernumber=39586">
        My account
       </a>
      </li>
      <li class="toplinks-mycheckouts">
       <a class="toplinks" href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=39586">
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
    Xamk
   </a>
  </h1>
  <!-- Begin Checkin Resident Search Box -->
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
     <a class="keep_text" href="#renew_search">
      Renew
     </a>
    </li>
   </ul>
  </div>
 </div>
 <!-- /gradient -->
 <!-- End Checkin Resident Search Box -->
 <div id="breadcrumbs">
  <a href="/cgi-bin/koha/mainpage.pl">
   Home
  </a>
  ›
  <a href="/cgi-bin/koha/circ/circulation-home.pl">
   Circulation
  </a>
  › Check in
 </div>
 <div class="yui-t2" id="doc3">
  <div id="bd">
   <div id="yui-main">
    <div class="yui-b">
     <div class="yui-g">
      <!-- Patron has added an issue note -->
      <!-- Patron has fines -->
      <div class="dialog alert">
       <h3>
        Patron has outstanding fines of 4.00.
       </h3>
       <p>
        <a href="/cgi-bin/koha/members/pay.pl?borrowernumber=7905">
         Make payment
        </a>
        .
       </p>
      </div>
      <!-- Patron has waiting holds -->
      <!-- Patron is restricted and checkin was backdated -->
      <!-- case of a mistake in transfer loop -->
      <!-- case of simple return no issue or transfer but with a reservation  -->
      <!--  reserved  -->
      <div class="modal fade audio-alert-action" id="hold-found2">
       <div class="modal-dialog">
        <div class="modal-content">
         <form action="returns.pl" class="confirm" method="post">
          <div class="modal-header">
           <h3>
            Hold found:
            <br/>
            <a href="/cgi-bin/koha/catalogue/detail.pl?type=intra&amp;biblionumber=224247">
             1620161108: Venäjän-kaupan opas /
            </a>
           </h3>
          </div>
          <div class="modal-body">
           <h4>
            Hold for:
            <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=1266">
             1579-1604-6602
            </a>
           </h4>
           <li>
            <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=1266">
             Hanhisalo, Katariina Laura Maria
             <span class="patron-category">
              - Xamk henkilökunta
             </span>
            </a>
           </li>
           <li class="patronaddress1">
            Vesitorninkatu 9 A 7
           </li>
           <li class="patroncity">
            50130 MIKKELI
           </li>
           <li>
            0503477351
           </li>
           <li>
            katariinaha@gmail.com
           </li>
           <h4>
            <strong>
             Transfer to:
            </strong>
            Savonlinnan kampuskirjasto
           </h4>
           <input name="print_slip" type="hidden" value="0"/>
           <input name="transfer_slip" type="hidden" value="0"/>
           <input name="ri-0" type="hidden" value="1620161108"/>
           <input name="dd-0" type="hidden" value="2020-09-24 23:59"/>
           <input name="bn-0" type="hidden" value="7905"/>
           <input name="itemnumber" type="hidden" value="9834"/>
           <input name="borrowernumber" type="hidden" value="1266"/>
           <input name="biblionumber" type="hidden" value="224247"/>
           <input name="reserve_id" type="hidden" value="19601"/>
           <input name="diffBranch" type="hidden" value="SAV"/>
           <input name="exemptfine" type="hidden" value=""/>
           <input name="dropboxmode" type="hidden" value=""/>
           <input name="forgivemanualholdsexpire" type="hidden" value=""/>
           <input name="return_date_override" type="hidden" value=""/>
           <input name="return_date_override_remember" type="hidden" value=""/>
          </div>
          <div class="modal-footer">
           <button class="btn btn-default approve" type="submit">
            <i class="fa fa-check">
            </i>
            Confirm hold and transfer
           </button>
           <button class="btn btn-default print" onclick="this.form.transfer_slip.value = 1; this.form.submit()" type="submit">
            <i class="fa fa-print">
            </i>
            Print slip, transfer, and confirm
           </button>
           <button aria-hidden="true" class="btn btn-danger deny" data-dismiss="modal" onclick="$('#barcode').focus(); return false;" type="submit">
            <i class="fa fa-times">
            </i>
            Ignore
           </button>
          </div>
         </form>
        </div>
       </div>
      </div>
      <div class="dialog message" id="exemptfines" style="display:none;">
       <p>
        Fines for returned items are forgiven.
       </p>
      </div>
      <div class="dialog message" id="forgivemanualholdsexpire-alert" style="display:none;">
       <p>
        Fines are not charged for manually cancelled holds.
       </p>
      </div>
      <div class="dialog message" id="dropboxmode" style="display:none;">
       <p>
        Book drop mode.  (Effective checkin date is 26.08.2020 13:02 ).
       </p>
      </div>
     </div>
     <div class="yui-g">
      <form action="/cgi-bin/koha/circ/returns.pl" autocomplete="off" id="checkin-form" method="post">
       <div class="yui-u first">
        <fieldset>
         <legend>
          Check in
         </legend>
         <label for="barcode">
          Enter item barcode:
         </label>
         <input class="focus" id="barcode" name="barcode" size="14"/>
         <input class="submit" type="submit" value="Submit"/>
         <div class="date-select" id="return_date_override_fields">
          <div class="hint">
           Specify return date (DD.MM.YYYY)
:
          </div>
          <input id="return_date_override" name="return_date_override" size="13" type="text" value=""/>
          <label for="return_date_override_remember">
           Remember for next check in:
          </label>
          <input id="return_date_override_remember" name="return_date_override_remember" onclick="this.form.barcode.focus();" type="checkbox"/>
          <input class="action" id="cleardate" name="cleardate" onclick="this.checked = false; this.form.return_date_override.value = ''; this.form.return_date_override_remember.checked = false; this.form.barcode.focus(); return false;" type="button" value="Clear"/>
         </div>
         <input name="ri-0" type="hidden" value="1620161108"/>
         <input name="dd-0" type="hidden" value="2020-09-24 23:59"/>
         <input name="bn-0" type="hidden" value="7905"/>
        </fieldset>
       </div>
       <div class="yui-u">
        <fieldset id="checkin_options">
         <legend>
          Options
         </legend>
         <!-- overduecharges -->
         <p>
          <input id="dropboxcheck" name="dropboxmode" type="checkbox" value="dropboxmode"/>
          <label for="dropboxcheck">
           Book drop mode
          </label>
         </p>
         <p>
          <input id="forgivemanualholdsexpire" name="forgivemanualholdsexpire" type="checkbox" value="forgivemanualholdsexpire"/>
          <label for="forgivemanualholdsexpire">
           Forgive fees for manually expired holds
          </label>
         </p>
        </fieldset>
       </div>
      </form>
     </div>
     <h2>
      Checked-in items
     </h2>
     <table id="checkedintable">
      <thead>
       <tr>
        <th class="ci-duedate">
         Due date
        </th>
        <th class="ci-title">
         Title
        </th>
        <th class="ci-author">
         Author
        </th>
        <th class="ci-barcode">
         Barcode
        </th>
        <th class="ci-homelibrary">
         Home library
        </th>
        <th class="ci-holdinglibrary">
         Holding library
        </th>
        <th class="ci-shelvinglocation">
         Shelving location
        </th>
        <th class="ci-callnumber">
         Call number
        </th>
        <th class="ci-dateaccessioned">
         Date acquired
        </th>
        <th class="ci-type">
         Type
        </th>
        <th class="ci-patron">
         Patron
        </th>
        <th class="ci-note">
         Note
        </th>
       </tr>
      </thead>
      <tr>
       <td class="ci-duedate">
        24.09.2020 23:59
       </td>
       <td class="ci-title">
        <a href="/cgi-bin/koha/catalogue/detail.pl?biblionumber=224247">
         Venäjän-kaupan opas /
        </a>
       </td>
       <td class="ci-author">
       </td>
       <td class="ci-barcode">
        <a href="/cgi-bin/koha/catalogue/moredetail.pl?biblionumber=224247&amp;itemnumber=9834#item9834">
         1620161108
        </a>
       </td>
       <td class="ci-homelibrary">
        Kotkan kampuskirjasto
       </td>
       <td class="ci-holdinglibrary">
        Mikkelin kampuskirjasto
       </td>
       <td class="ci-shelvinglocation">
        Lainattavat
       </td>
       <td class="ci-callnumber">
        339 VENÄJÄN
       </td>
       <td class="ci-dateaccessioned">
        24.01.2019
       </td>
       <td class="ci-type">
        Laina14
       </td>
       <td class="ci-patron">
        <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=7905">
         Koehenkilö, Erkki Ilmari (XAMKOPISK)
        </a>
        <span class="results_summary nowrap">
         <span class="label">
          Checkouts:
         </span>
         <span class="number_box">
          <a href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=7905">
           2
          </a>
         </span>
        </span>
       </td>
       <td class="ci-note">
       </td>
      </tr>
     </table>
    </div>
   </div>
   <div class="yui-b noprint">
    <div id="navmenu">
     <div id="navmenulist">
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/circulation-home.pl">
         Circulation home
        </a>
       </li>
      </ul>
      <h5>
       Circulation
      </h5>
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/circulation.pl">
         Check out
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/returns.pl">
         Check in
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/renew.pl">
         Renew
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/branchtransfers.pl">
         Transfer
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/selectbranchprinter.pl">
         Set library
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/cataloguing/addbiblio.pl?frameworkcode=FA">
         Fast cataloging
        </a>
       </li>
      </ul>
      <h5>
       Circulation reports
      </h5>
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/view_holdsqueue.pl">
         Holds queue
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/pendingreserves2.pl">
         Holds to pull
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/waitingreserves.pl">
         Holds awaiting pickup
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/reserveratios.pl">
         Hold ratios
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/transferstoreceive.pl">
         Transfers to receive
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/branchoverdues.pl">
         Overdues with fines
        </a>
       </li>
      </ul>
     </div>
    </div>
   </div>
  </div>
 </div>
</body>
  """))

def hold_with_outstanding_fines_01():
  barcode = '1623176764'
  return (barcode, soupify("""
<body class="circ" id="circ_returns">
 <span class="audio-alert-success">
 </span>
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
       MIK2
      </span>
      <span class="separator">
       |
      </span>
      <strong>
       <span id="logged-in-branch-name">
        Mikkelin kampuskirjasto
       </span>
       <span class="content_hidden" id="logged-in-branch-code">
        MIK
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
       <a class="toplinks" href="/cgi-bin/koha/members/moremember.pl?borrowernumber=39586">
        My account
       </a>
      </li>
      <li class="toplinks-mycheckouts">
       <a class="toplinks" href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=39586">
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
    Xamk
   </a>
  </h1>
  <!-- Begin Checkin Resident Search Box -->
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
     <a class="keep_text" href="#renew_search">
      Renew
     </a>
    </li>
   </ul>
  </div>
 </div>
 <!-- /gradient -->
 <!-- End Checkin Resident Search Box -->
 <div id="breadcrumbs">
  <a href="/cgi-bin/koha/mainpage.pl">
   Home
  </a>
  ›
  <a href="/cgi-bin/koha/circ/circulation-home.pl">
   Circulation
  </a>
  › Check in
 </div>
 <div class="yui-t2" id="doc3">
  <div id="bd">
   <div id="yui-main">
    <div class="yui-b">
     <div class="yui-g">
      <!-- Patron has added an issue note -->
      <!-- Patron has fines -->
      <div class="dialog alert">
       <h3>
        Patron has outstanding fines of 4.00.
       </h3>
       <p>
        <a href="/cgi-bin/koha/members/pay.pl?borrowernumber=7905">
         Make payment
        </a>
        .
       </p>
      </div>
      <!-- Patron has waiting holds -->
      <!-- Patron is restricted and checkin was backdated -->
      <!-- case of a mistake in transfer loop -->
      <!-- case of simple return no issue or transfer but with a reservation  -->
      <!--  reserved  -->
      <div class="modal fade audio-alert-action" id="hold-found2">
       <div class="modal-dialog">
        <div class="modal-content">
         <form action="returns.pl" class="confirm" method="post">
          <div class="modal-header">
           <h3>
            Hold found:
            <br/>
            <a href="/cgi-bin/koha/catalogue/detail.pl?type=intra&amp;biblionumber=142261">
             1623176764: Tietoisesti paras :
            </a>
           </h3>
          </div>
          <div class="modal-body">
           <h4>
            Hold for:
            <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=1266">
             1579-1604-6602
            </a>
           </h4>
           <li>
            <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=1266">
             Hanhisalo, Katariina Laura Maria
             <span class="patron-category">
              - Xamk henkilökunta
             </span>
            </a>
           </li>
           <li class="patronaddress1">
            Vesitorninkatu 9 A 7
           </li>
           <li class="patroncity">
            50130 MIKKELI
           </li>
           <li>
            0503477351
           </li>
           <li>
            <a href="mailto:katariinaha@gmail.com" id="boremail">
             katariinaha@gmail.com
            </a>
           </li>
           <li>
            Patron notification:
             Email.
           </li>
           <h4>
            <strong>
             Hold at
            </strong>
            Mikkelin kampuskirjasto
           </h4>
           <input name="print_slip" type="hidden" value="0"/>
           <input name="transfer_slip" type="hidden" value="0"/>
           <input name="ri-0" type="hidden" value="1623176764"/>
           <input name="dd-0" type="hidden" value="2020-09-24 23:59"/>
           <input name="bn-0" type="hidden" value="7905"/>
           <input name="itemnumber" type="hidden" value="71711"/>
           <input name="borrowernumber" type="hidden" value="1266"/>
           <input name="biblionumber" type="hidden" value="142261"/>
           <input name="reserve_id" type="hidden" value="19602"/>
           <input name="diffBranch" type="hidden" value="MIK"/>
           <input name="exemptfine" type="hidden" value=""/>
           <input name="dropboxmode" type="hidden" value=""/>
           <input name="forgivemanualholdsexpire" type="hidden" value=""/>
           <input name="return_date_override" type="hidden" value=""/>
           <input name="return_date_override_remember" type="hidden" value=""/>
          </div>
          <div class="modal-footer">
           <button class="btn btn-default approve" type="submit">
            <i class="fa fa-check">
            </i>
            Confirm hold
           </button>
           <button class="btn btn-default print" onclick="this.form.print_slip.value = 1; this.form.submit();" type="submit">
            <i class="fa fa-print">
            </i>
            Print slip and confirm
           </button>
           <button aria-hidden="true" class="btn btn-danger deny" data-dismiss="modal" onclick="$('#barcode').focus(); return false;" type="submit">
            <i class="fa fa-times">
            </i>
            Ignore
           </button>
          </div>
         </form>
        </div>
       </div>
      </div>
      <div class="dialog message" id="exemptfines" style="display:none;">
       <p>
        Fines for returned items are forgiven.
       </p>
      </div>
      <div class="dialog message" id="forgivemanualholdsexpire-alert" style="display:none;">
       <p>
        Fines are not charged for manually cancelled holds.
       </p>
      </div>
      <div class="dialog message" id="dropboxmode" style="display:none;">
       <p>
        Book drop mode.  (Effective checkin date is 26.08.2020 13:02 ).
       </p>
      </div>
     </div>
     <div class="yui-g">
      <form action="/cgi-bin/koha/circ/returns.pl" autocomplete="off" id="checkin-form" method="post">
       <div class="yui-u first">
        <fieldset>
         <legend>
          Check in
         </legend>
         <label for="barcode">
          Enter item barcode:
         </label>
         <input class="focus" id="barcode" name="barcode" size="14"/>
         <input class="submit" type="submit" value="Submit"/>
         <div class="date-select" id="return_date_override_fields">
          <div class="hint">
           Specify return date (DD.MM.YYYY)
:
          </div>
          <input id="return_date_override" name="return_date_override" size="13" type="text" value=""/>
          <label for="return_date_override_remember">
           Remember for next check in:
          </label>
          <input id="return_date_override_remember" name="return_date_override_remember" onclick="this.form.barcode.focus();" type="checkbox"/>
          <input class="action" id="cleardate" name="cleardate" onclick="this.checked = false; this.form.return_date_override.value = ''; this.form.return_date_override_remember.checked = false; this.form.barcode.focus(); return false;" type="button" value="Clear"/>
         </div>
         <input name="ri-0" type="hidden" value="1623176764"/>
         <input name="dd-0" type="hidden" value="2020-09-24 23:59"/>
         <input name="bn-0" type="hidden" value="7905"/>
        </fieldset>
       </div>
       <div class="yui-u">
        <fieldset id="checkin_options">
         <legend>
          Options
         </legend>
         <!-- overduecharges -->
         <p>
          <input id="dropboxcheck" name="dropboxmode" type="checkbox" value="dropboxmode"/>
          <label for="dropboxcheck">
           Book drop mode
          </label>
         </p>
         <p>
          <input id="forgivemanualholdsexpire" name="forgivemanualholdsexpire" type="checkbox" value="forgivemanualholdsexpire"/>
          <label for="forgivemanualholdsexpire">
           Forgive fees for manually expired holds
          </label>
         </p>
        </fieldset>
       </div>
      </form>
     </div>
     <h2>
      Checked-in items
     </h2>
     <table id="checkedintable">
      <thead>
       <tr>
        <th class="ci-duedate">
         Due date
        </th>
        <th class="ci-title">
         Title
        </th>
        <th class="ci-author">
         Author
        </th>
        <th class="ci-barcode">
         Barcode
        </th>
        <th class="ci-homelibrary">
         Home library
        </th>
        <th class="ci-holdinglibrary">
         Holding library
        </th>
        <th class="ci-shelvinglocation">
         Shelving location
        </th>
        <th class="ci-callnumber">
         Call number
        </th>
        <th class="ci-dateaccessioned">
         Date acquired
        </th>
        <th class="ci-type">
         Type
        </th>
        <th class="ci-patron">
         Patron
        </th>
        <th class="ci-note">
         Note
        </th>
       </tr>
      </thead>
      <tr>
       <td class="ci-duedate">
        24.09.2020 23:59
       </td>
       <td class="ci-title">
        <a href="/cgi-bin/koha/catalogue/detail.pl?biblionumber=142261">
         Tietoisesti paras :
        </a>
       </td>
       <td class="ci-author">
        Collins, Jim.
       </td>
       <td class="ci-barcode">
        <a href="/cgi-bin/koha/catalogue/moredetail.pl?biblionumber=142261&amp;itemnumber=71711#item71711">
         1623176764
        </a>
       </td>
       <td class="ci-homelibrary">
        Kouvolan kampuskirjasto
       </td>
       <td class="ci-holdinglibrary">
        Mikkelin kampuskirjasto
       </td>
       <td class="ci-shelvinglocation">
        Lainattavat
       </td>
       <td class="ci-callnumber">
        69.11 COLLINS
       </td>
       <td class="ci-dateaccessioned">
        04.02.2014
       </td>
       <td class="ci-type">
        Laina14
       </td>
       <td class="ci-patron">
        <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=7905">
         Koehenkilö, Erkki Ilmari (XAMKOPISK)
        </a>
        <span class="results_summary nowrap">
         <span class="label">
          Checkouts:
         </span>
         <span class="number_box">
          <a href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=7905">
           1
          </a>
         </span>
        </span>
       </td>
       <td class="ci-note">
       </td>
      </tr>
     </table>
    </div>
   </div>
   <div class="yui-b noprint">
    <div id="navmenu">
     <div id="navmenulist">
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/circulation-home.pl">
         Circulation home
        </a>
       </li>
      </ul>
      <h5>
       Circulation
      </h5>
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/circulation.pl">
         Check out
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/returns.pl">
         Check in
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/renew.pl">
         Renew
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/branchtransfers.pl">
         Transfer
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/selectbranchprinter.pl">
         Set library
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/cataloguing/addbiblio.pl?frameworkcode=FA">
         Fast cataloging
        </a>
       </li>
      </ul>
      <h5>
       Circulation reports
      </h5>
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/view_holdsqueue.pl">
         Holds queue
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/pendingreserves2.pl">
         Holds to pull
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/waitingreserves.pl">
         Holds awaiting pickup
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/reserveratios.pl">
         Hold ratios
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/transferstoreceive.pl">
         Transfers to receive
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/branchoverdues.pl">
         Overdues with fines
        </a>
       </li>
      </ul>
     </div>
    </div>
   </div>
  </div>
 </div>
</body>
  """))

def simple_checkin_01():
  barcode = '1620027464'
  return (barcode, soupify("""
<body class="circ" id="circ_returns">
 <span class="audio-alert-success">
 </span>
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
       MIK2
      </span>
      <span class="separator">
       |
      </span>
      <strong>
       <span id="logged-in-branch-name">
        Mikkelin kampuskirjasto
       </span>
       <span class="content_hidden" id="logged-in-branch-code">
        MIK
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
       <a class="toplinks" href="/cgi-bin/koha/members/moremember.pl?borrowernumber=39586">
        My account
       </a>
      </li>
      <li class="toplinks-mycheckouts">
       <a class="toplinks" href="/cgi-bin/koha/circ/circulation.pl?borrowernumber=39586">
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
    Xamk
   </a>
  </h1>
  <!-- Begin Checkin Resident Search Box -->
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
     <a class="keep_text" href="#renew_search">
      Renew
     </a>
    </li>
   </ul>
  </div>
 </div>
 <!-- /gradient -->
 <!-- End Checkin Resident Search Box -->
 <div id="breadcrumbs">
  <a href="/cgi-bin/koha/mainpage.pl">
   Home
  </a>
  ›
  <a href="/cgi-bin/koha/circ/circulation-home.pl">
   Circulation
  </a>
  › Check in
 </div>
 <div class="yui-t2" id="doc3">
  <div id="bd">
   <div id="yui-main">
    <div class="yui-b">
     <div class="yui-g">
      <!-- Patron has added an issue note -->
      <!-- Patron has waiting holds -->
      <!-- Patron is restricted and checkin was backdated -->
      <!-- case of a mistake in transfer loop -->
      <div class="dialog message" id="exemptfines" style="display:none;">
       <p>
        Fines for returned items are forgiven.
       </p>
      </div>
      <div class="dialog message" id="forgivemanualholdsexpire-alert" style="display:none;">
       <p>
        Fines are not charged for manually cancelled holds.
       </p>
      </div>
      <div class="dialog message" id="dropboxmode" style="display:none;">
       <p>
        Book drop mode.  (Effective checkin date is 26.08.2020 13:02 ).
       </p>
      </div>
     </div>
     <div class="yui-g">
      <form action="/cgi-bin/koha/circ/returns.pl" autocomplete="off" id="checkin-form" method="post">
       <div class="yui-u first">
        <fieldset>
         <legend>
          Check in
         </legend>
         <label for="barcode">
          Enter item barcode:
         </label>
         <input class="focus" id="barcode" name="barcode" size="14"/>
         <input class="submit" type="submit" value="Submit"/>
         <div class="date-select" id="return_date_override_fields">
          <div class="hint">
           Specify return date (DD.MM.YYYY)
:
          </div>
          <input id="return_date_override" name="return_date_override" size="13" type="text" value=""/>
          <label for="return_date_override_remember">
           Remember for next check in:
          </label>
          <input id="return_date_override_remember" name="return_date_override_remember" onclick="this.form.barcode.focus();" type="checkbox"/>
          <input class="action" id="cleardate" name="cleardate" onclick="this.checked = false; this.form.return_date_override.value = ''; this.form.return_date_override_remember.checked = false; this.form.barcode.focus(); return false;" type="button" value="Clear"/>
         </div>
         <input name="ri-0" type="hidden" value="1620027464"/>
         <input name="dd-0" type="hidden" value="2020-09-24 23:59"/>
         <input name="bn-0" type="hidden" value="7905"/>
        </fieldset>
       </div>
       <div class="yui-u">
        <fieldset id="checkin_options">
         <legend>
          Options
         </legend>
         <!-- overduecharges -->
         <p>
          <input id="dropboxcheck" name="dropboxmode" type="checkbox" value="dropboxmode"/>
          <label for="dropboxcheck">
           Book drop mode
          </label>
         </p>
         <p>
          <input id="forgivemanualholdsexpire" name="forgivemanualholdsexpire" type="checkbox" value="forgivemanualholdsexpire"/>
          <label for="forgivemanualholdsexpire">
           Forgive fees for manually expired holds
          </label>
         </p>
        </fieldset>
       </div>
      </form>
     </div>
     <h2>
      Checked-in items
     </h2>
     <table id="checkedintable">
      <thead>
       <tr>
        <th class="ci-duedate">
         Due date
        </th>
        <th class="ci-title">
         Title
        </th>
        <th class="ci-author">
         Author
        </th>
        <th class="ci-barcode">
         Barcode
        </th>
        <th class="ci-homelibrary">
         Home library
        </th>
        <th class="ci-holdinglibrary">
         Holding library
        </th>
        <th class="ci-shelvinglocation">
         Shelving location
        </th>
        <th class="ci-callnumber">
         Call number
        </th>
        <th class="ci-dateaccessioned">
         Date acquired
        </th>
        <th class="ci-type">
         Type
        </th>
        <th class="ci-patron">
         Patron
        </th>
        <th class="ci-note">
         Note
        </th>
       </tr>
      </thead>
      <tr>
       <td class="ci-duedate">
        24.09.2020 23:59
       </td>
       <td class="ci-title">
        <a href="/cgi-bin/koha/catalogue/detail.pl?biblionumber=119736">
         Lapsekas parisuhde /
        </a>
       </td>
       <td class="ci-author">
       </td>
       <td class="ci-barcode">
        <a href="/cgi-bin/koha/catalogue/moredetail.pl?biblionumber=119736&amp;itemnumber=21843#item21843">
         1620027464
        </a>
       </td>
       <td class="ci-homelibrary">
        Mikkelin kampuskirjasto
       </td>
       <td class="ci-holdinglibrary">
        Mikkelin kampuskirjasto
       </td>
       <td class="ci-shelvinglocation">
        Lainattavat
       </td>
       <td class="ci-callnumber">
        159.9 REISER
       </td>
       <td class="ci-dateaccessioned">
        04.02.2014
       </td>
       <td class="ci-type">
        Laina14
       </td>
       <td class="ci-patron">
        <a href="/cgi-bin/koha/members/moremember.pl?borrowernumber=7905">
         Koehenkilö, Erkki Ilmari (XAMKOPISK)
        </a>
       </td>
       <td class="ci-note">
       </td>
      </tr>
     </table>
    </div>
   </div>
   <div class="yui-b noprint">
    <div id="navmenu">
     <div id="navmenulist">
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/circulation-home.pl">
         Circulation home
        </a>
       </li>
      </ul>
      <h5>
       Circulation
      </h5>
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/circulation.pl">
         Check out
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/returns.pl">
         Check in
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/renew.pl">
         Renew
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/branchtransfers.pl">
         Transfer
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/selectbranchprinter.pl">
         Set library
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/cataloguing/addbiblio.pl?frameworkcode=FA">
         Fast cataloging
        </a>
       </li>
      </ul>
      <h5>
       Circulation reports
      </h5>
      <ul>
       <li>
        <a href="/cgi-bin/koha/circ/view_holdsqueue.pl">
         Holds queue
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/pendingreserves2.pl">
         Holds to pull
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/waitingreserves.pl">
         Holds awaiting pickup
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/reserveratios.pl">
         Hold ratios
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/transferstoreceive.pl">
         Transfers to receive
        </a>
       </li>
       <li>
        <a href="/cgi-bin/koha/circ/branchoverdues.pl">
         Overdues with fines
        </a>
       </li>
      </ul>
     </div>
    </div>
   </div>
  </div>
 </div>
</body>
  """))