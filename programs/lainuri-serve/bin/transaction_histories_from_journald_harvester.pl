# IN THIS FILE
#
# Extract transaction information from journald and create transaction_history-rows from the data.
#
#

use strict;
use warnings;


open(my $fh, '>:encoding(UTF-8)', 'out');


sub process_checkout {
  my $in = $_[0];
  print($in . "\n");
  $in =~ /(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)/gsm || die("NO TS ON '$in'");
  my $ts = $1;
  $in =~ /'event': '(.+?)'/gsm || die("NO EVENT!");
  my $ev = $1;
  $in =~ /'item_barcode':\s+'(.+?)'/gsm || die("NO IBC ON '$in'");
  my $ibc = $1;
  $in =~ /'status': '(.+?)',/gsm || die("NO STATUS ON '$in'");
  my $st = $1;
  $in =~ /'user_barcode':\s+'(.+?)'/gsm || die("NO UBC ON '$in'");
  my $ubc = $1;

  if ($st ne "SUCCESS") {
    print("ST: " . $st . " EV: " . $ev . " IBC: " . $ibc . " UBC: " . $ubc . " TS: " . $ts . "\n");
  }
  else {
    print("ST: " . $st . " EV: " . $ev . " IBC: " . $ibc . " UBC: " . $ubc . " TS: " . $ts . "\n");
    print $fh ("ST: " . $st . " EV: " . $ev . " IBC: " . $ibc . " UBC: " . $ubc . " TS: " . $ts . "\n");
  }
}
sub process_checkin {
  my $in = $_[0];
  print($in . "\n");
  $in =~ /(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)/gsm || die("NO TS ON '$in'");
  my $ts = $1;
  $in =~ /'event': '(.+?)'/gsm || die("NO EVENT!");
  my $ev = $1;
  $in =~ /'item_barcode':\s+'(.+?)'/gsm || die("NO IBC ON '$in'");
  my $ibc = $1;
  $in =~ /'status': '(.+?)',/gsm || die("NO STATUS ON '$in'");
  my $st = $1;

  if ($st ne "SUCCESS") {
    print("ST: " . $st . " EV: " . $ev . " IBC: " . $ibc . " TS: " . $ts . "\n");
  }
  else {
    print("ST: " . $st . " EV: " . $ev . " IBC: " . $ibc . " TS: " . $ts . "\n");
    print $fh ("ST: " . $st . " EV: " . $ev . " IBC: " . $ibc . " TS: " . $ts . "\n");
  }
}


$/ = '--';
open(my $in1, "journalctl -u lainuri-serve | grep -P -A8 -B1 \"'event': 'check-out-complete',\" |");
while (<$in1>) {
  process_checkout($_);
}
open(my $in2, "journalctl -u lainuri-serve | grep -P -A8 -B1 \"'event': 'check-in-complete',\" |");
while (<$in2>) {
  process_checkin($_);
}
