#!/usr/bin/perl

use DBI;
use Date::Manip;

$db=DBI->connect('DBI:mysql:test', 'test', 'secret');


# Doug@Apley.com 2005-10-22

print "Content-Type: Text/HTML\n\n";
&GetQueryString;
($thisprogram)=$ENV{'SCRIPT_NAME'}=~m/([\w\-_]*\.cgi)/;

if ($QString{'d1'}) {$d1=&UnixDate(&ParseDate($QString{'d1'}), '%Y-%m-%d');}


unless ($d1) {$d1_error='<SPAN CLASS=error>Not understood</SPAN>';}

print "<HTML>\n";
print "  <HEAD>\n";
print "    <TITLE>Calendar</TITLE>\n";
print "    <STYLE>\n";
print "      BODY {font-family: arial, helvetica}\n";
print "      .month {width: 95%; border-style: solid; border-color: blue; border-width: thin; font-size: 8pt;}\n";
print "      .month TH {background-color: black; color: white}\n";
print "      .month TD {background-color: grey; padding: 5px; height: 60px;}\n";
print "      TD.no_day {background-color: white}\n";
print "      TD.day {border: thin solid gray; background: #D0D0D0; width: 14%; vertical-align: top; overflow: hidden;}\n";
print "      .day_num {color: red; float: left; vertical-align: top}\n";
print "      .error {color: red;}\n";
print "      .event {clear: left; color: black;}\n";
print "    </STYLE>\n";

print "
    <SCRIPT LANGUAGE='JavaScript'>
      function RoundedTop(selector,bk,color,size) {
        var i;
        var v=getElementsBySelector(selector);
        for (i=0; i<v.length; i++)
        AddTop (v[i],bk,color,size);
        }

      function AddTop(el,bk,color,size){
        var i;
        var d=document.createElement(\"b\");
        var cn=\"r\";
        var lim=4;
        if (size && size==\"small\") { cn=\"rs\"; lim=2}
        d.className=\"rtop\";
        d.style.backgroundColor=bk;
        for (i=1; i<=lim; i++) {
          var x=document.createElement(\"b\");
          x.className=cn + i;
          x.style.backgroundColor=color;
          d.appendChild(x);
          }
        el.insertBefore(d,el.firstChild);
        }

      function getElementsBySelector(selector){
        var i;
        var s=[];
        var selid=\"\";
        var selclass=\"\";
        var tag=selector;
        var objlist=[];
        if (selector.indexOf(\" \")>0){  //descendant selector like \"tag#id tag\"
        s=selector.split(\" \");
        var fs=s[0].split(\"#\");
        if (fs.length==1) return(objlist);
          return(document.getElementById(fs[1]).getElementsByTagName(s[1]));
          }
        if (selector.indexOf(\"#\")>0){ //id selector like \"tag#id\"
          s=selector.split(\"#\");
          tag=s[0];
          selid=s[1];
          }
        if (selid!=\"\") {
          objlist.push(document.getElementById(selid));
          return(objlist);
          }
        if (selector.indexOf(\".\")>0){  //class selector like \"tag.class\"
          s=selector.split(\".\");
          tag=s[0];
          selclass=s[1];
          }
        var v=document.getElementsByTagName(tag);  // tag selector like \"tag\"
        if (selclass==\"\")
          return (v);
          for (i=0; i<v.length; i++) {
            if (v[i].className==selclass) {
            objlist.push(v[i]);
            }
         }
         return(objlist);
       }

    </SCRIPT>\n";

print "  </HEAD>\n";
print "</HTML>\n";

print "<BODY ONLOAD='RoundedTop(\"TD.day\",\"#FFF\",\"#e7e7e7\");'>\n";
print "<FORM METHOD=GET ACTION=$thisprogram>\n";
print "<TABLE>\n";
print "  <TR>\n";
print "    <TD>\n";
print "      Date: <INPUT TYPE=TEXT NAME='d1' VALUE='".($d1||$QString{'d1'})."'><BR>\n";
print "    </TD>\n";

print "    <TD>\n";
print "      <INPUT TYPE=RADIO NAME=table VALUE='timecard' ".($QString{'table'} eq 'timecard'?' CHECKED':'')."> Time cards<BR>\n";
print "      <INPUT TYPE=RADIO NAME=table VALUE='transaction' ".($QString{'table'} ne 'timecard'?' CHECKED':'')."> Transactions<BR>\n";
print "    </TD>\n";

print "    <TD>\n";
print "      <INPUT TYPE=RADIO NAME=granularity VALUE='day' ".($QString{'granularity'} eq 'day'?' CHECKED':'')."> Day<BR>\n";
print "      <INPUT TYPE=RADIO NAME=granularity VALUE='week' ".(($QString{'granularity'} ne 'day') && ($QString{'granularity'} ne 'month')?' CHECKED':'')."> Week<BR>\n";
print "      <INPUT TYPE=RADIO NAME=granularity VALUE='month' ".(($QString{'granularity'} ne 'day') && ($QString{'granularity'} ne 'week')?' CHECKED':'')."> Month<BR>\n";
print "    </TD>\n";

print "    <TD>\n";
print "      <INPUT TYPE=SUBMIT VALUE='Refresh'>\n";
print "    <TD>\n";

print "  </TR>\n";
print "</TABLE>\n";
print "</FORM>\n";

if ($d1) {&Calendar($d1, $d2);}
  


#------------------- Day of Week ---------------
# Given a date yyyy-mm-dd from 1700-2200 A.D., returns an integer between 0 and 6 indicating day of week.  (0=Sun, 1=Mon, ... 6=Sat)
# Based upon algorithm: http://www.quincunx.org/calendar/index.htm
sub DayOfWeek {
  my ($Y,$M,$D)=$_[0]=~/(\d{4})-(\d{1,2})-(\d{1,2})/;
  return ((int(($Y%100)*1.25)+(6,2,2,5,0,3,5,1,4,6,2,4)[$M-1]+$D+(5,3,1,0,-2,-4)[int($Y/100)-17]-(($Y%4==0 && ($Y%100!=0 || $Y%400==0 )) && $M<=2))%7);
  }


#------------------ IsLeapYear ------------------
# Given a year yyyy from 1700-2200 A.D., returns true if it's a leap year or false if not.
# A leap year is a year evenly divisible by four which does not end in 00 unless it's evenly divisible by 400.
sub IsLeapYear {
  return ($_[0]%4==0 && ($_[0]%100!=0 || $_[0]%400==0 ));
  }


#------------------- DaysInMonth -------------------
# Given a year yyyy and month mm returns the number of days in the month.
sub DaysInMonth {
  return (31,28,31,30,31,30,31,31,30,31,30,31)[$_[1]-1]+($_[1]==1 && &IsLeapYear($_[0]));
  }


#------------------- Calendar --------------
# Given a date yyyy-mm-dd as the first parameter
sub Calendar {
  my ($Date,$Y,$M,$D)=$_[0]=~/((\d{4})-(\d{1,2})-(\d{1,2}))/;
  my $dow=&DayOfWeek("$Y-$M-01");
  my $daysinmonth=&DaysInMonth($Y,$M);

#  if ($QString{'table'} eq 'timecard') {$sth=$db->prepare("SELECT id, start, CONCAT_WS(' ', employee, hours) FROM apley.hours WHERE start BETWEEN ".$db->quote("$Y-$M-01")." AND DATE_ADD(".$db->quote("$Y-$M-01").", INTERVAL 1 MONTH)" ." ORDER BY start");}
#  else {$sth=$db->prepare("SELECT id, date_xact, CONCAT_WS(' ', MIN(trans_to), MIN(trans_for), MAX(amount)) FROM apley.transactions WHERE date_xact BETWEEN ".$db->quote("$Y-$M-01")." AND DATE_ADD(".$db->quote("$Y-$M-01").", INTERVAL 1 MONTH)" ." GROUP BY trans_group ORDER BY date_xact");}
  $sth=$db->prepare('SELECT id, dayoff, name FROM test.test WHERE dayoff BETWEEN '.$db->quote("$Y-$M-01").' AND DATE_ADD('.$db->quote("$Y-$M-01").', INTERVAL 1 MONTH) ORDER BY dayoff');

  $sth->execute;
  ($id, $eventdate, $name)=$sth->fetchrow;
  print "<CENTER>\n";
  print "<H2>".(('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')[$M-1])." $Y</H2>\n";
  print "<A HREF=$thisprogram?d1=".(($M>1?$Y:$Y-1).'-'.($M>1?$M-1:12).'-01').">&lt;&lt; previous</A> &nbsp; &nbsp; &nbsp; <A HREF=$thisprogram?d1=".(($M==12?$Y+1:$Y).'-'.($M==12?1:$M+1).'-01').">next &gt;&gt;</A>\n";
  print "<TABLE CLASS='month'>\n";
  print "  <TR><TH>Sun<TH>Mon<TH>Tue<TH>Wed<TH>Thu<TH>Fri<TH>Sat\n";
  print "  <TR>".($dow>0?"<TD COLSPAN=$dow CLASS='no_day'>":'')."\n";
  foreach $day(1..$daysinmonth) {
    if (!(($day+$dow-1)%7)) {print "  <TR>\n";}
    print "    <TD CLASS='day'><SPAN CLASS='day_num'>".($day||'&nbsp;')."</SPAN>\n";
#  print "Next event is $id, $eventdate, $name<BR>\n";
    while ($eventdate && &DateBefore($eventdate, "$Y-$M-$day")) {($id, $eventdate, $name)=$sth->fetchrow;}
    while (&DateEqual("$Y-$M-$day", $eventdate)) {
      print "      <DIV CLASS=event>$name</DIV>\n";
      ($id, $eventdate, $name)=$sth->fetchrow;}
    }
  unless (($dow+$daysinmonth)%7==0) {print "  <TD COLSPAN=".(7-(($dow+$daysinmonth)%7))." CLASS='no_day'>&nbsp;\n";}
  print "</TABLE>\n";
  }


#------------------- GetQueryString ---------------
sub GetQueryString {
  my ($pair, $name, $value);
  foreach $pair (split(/\&/, $ENV{QUERY_STRING})) {
    $pair =~ tr/+/ /;
    $pair =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    ($name, $value) = split(/=/, $pair);
    $QString{$name}=$value;
    }
  }


#------------------------ DateBefore ------------------------
# Returns true if the first parameter is a date which is before the date given in the second parameter
sub DateBefore {
#print "In DateBefore: $_[0] and $_[1] <BR>\n";
  my ($y1, $m1, $d1)=($_[0]=~/^(\d{4})\D(\d{1,2})\D(\d{1,2})/);
  my ($y2, $m2, $d2)=($_[1]=~/^(\d{4})\D(\d{1,2})\D(\d{1,2})/);
  return ($y1<$y2 || ($y1==$y2 && ($m1<$m2 || ($m1==$m2 && $d1<$d2))));
  }


#------------------------ DateEqual ------------------------
# Returns true if the first parameter is a date which is the same day as the date given in the second parameter
sub DateEqual {
#print "In DateEqual: $_[0] and $_[1] <BR>\n";
  my ($y1, $m1, $d1)=($_[0]=~/^(\d{4})\D(\d{1,2})\D(\d{1,2})/);
  my ($y2, $m2, $d2)=($_[1]=~/^(\d{4})\D(\d{1,2})\D(\d{1,2})/);
  return ($y1==$y2 && $m1==$m2 && $d1==$d2);
  }


#------------------------ DateBetween ------------------------
# Returns true if the first parameter is a date which is on or after the second parameter and before the third parameter.
sub DateBetween {
  my ($y1, $m1, $d1)=($_[0]=~/(\d{4})\D(\d{1,2})\D(\d{1,2})/);
  my ($y2, $m2, $d2)=($_[1]=~/(\d{4})\D(\d{1,2})\D(\d{1,2})/);
  my ($y3, $m3, $d3)=($_[2]=~/(\d{4})\D(\d{1,2})\D(\d{1,2})/);
  return (($y1>$y2 || ($y1==$y2 && ($m1>$m2 || ($m1==$m2 && $d1>=$d2)))) && ($y1<$y3 || ($y1==$y3 && ($m1<$m3 || ($m1==$m3 && $d1<$d3)))));
  }


