#!/usr/bin/perl
use Frontier::Client;
use Data::Dumper;
use Scalar::Util qw(reftype);
use POSIX qw(strftime);

## config.pl contains the host, username and password
## In the format:
## $HOST="localhost";
## $USER="username";
## $PASS="password";

require('config.pl');

@keys = ();
@systems = ();
@packageList = ();
$packages = {};
my $date = strftime "%Y_%m_%d_%H_%m_%S", localtime;
$outputFile = "output_" . $date . ".csv";

## connect to the satellite server
my $client = new Frontier::Client(url => "http://$HOST/rpc/api");
my $session = $client->call('auth.login',$USER, $PASS);

## Get a list of relevant activation keys
$aa = $client->call('activationkey.listActivationKeys',$session);
foreach $akey (@$aa) {
  $key = $akey->{'key'};
  ## Alter the regex below as required ##
  ## i.e:
  ## /.*server-5\.*/)
  ## /.*server-6\.4.*/)
#  if ($key =~ /.*rhel-6-4.*/) {
#    if ($key != /desktopserver/) {
      push(@keys,$key);
#    }
#  }
}

## Open a main file to log results in
open my $fhmain, '>', $outputFile or die("Can't open file $!\n");
#print $hfmain "Vendor\tPackage\tVersion\tRelease\tArchitecture";

## Get the active systems for each activation key
for $key (@keys) {
  $bb = $client->call('activationkey.listActivatedSystems',$session,$key);
  ## Loop through each system and check packages
  foreach $activeSystems (@$bb) {
    $sysId =  $activeSystems->{'id'};
    $sysName =  $activeSystems->{'hostname'};
    print " - Checking packages on $sysName \n";
    push(@systems,$sysName);

    ## Get the packages on that system
    $cc = $client->call('system.listPackages',$session,$sysId);
    foreach $pkge (@$cc) {
        ## Check if AMD64 and change
        if ($pkge->{'arch'} eq 'AMD64') {
              $newArch = "x86_64";
        } else {
               $newArch = $pkge->{'arch'};
        }

      ## Add to the packagelist hash (if the id isn't already there)
      if (!grep { $_->{id} == $pkge->{'id'} } @packageList) {

      ## Get the *REAL* package id
      $dd = $client->call('packages.findByNvrea',$session,$pkge->{'name'},$pkge->{'version'},$pkge->{'release'},'',$newArch);
      foreach $results (@$dd) {
      $realId = $results->{'id'};
      }

      ## Get the vendor details
      $ee = $client->call('packages.getDetails',$session,$realId);
      $vendor = $ee->{'vendor'};
        push @packageList, { 'version' => $pkge->{'version'},
                          'name' =>  $pkge->{'name'},
                          'id' =>  $pkge->{'id'},
                          'epoch' =>  $pkge->{'epoch'},
                          'release' => $pkge->{'release'},
                          'summary' => $ee->{'summary'},
                          'vendor' => $vendor,
                          'arch' => $newArch};
#        print $fh $pkge->{'id'} . "\t" . $pkge->{'name'} . "\t" . $pkge->{'version'} . "\t" . $pkge->{'release'} . "\t" . $pkge->{'arch'} . "\n";
        print $fhmain $vendor . "\t" . $pkge->{'name'} . "\t" . $pkge->{'version'} . "\t" . $pkge->{'release'} . "\t" . $newArch . "\t" . $ee->{'summary'} . "\n";
#        print $fh $pkge->{'name'} . "\t" . $pkge->{'version'} . "\t" . $pkge->{'release'} . "\t" . $newArch . "\n";
        }
      }
#  close $fh;
  }
}

close $fhmain;

##print Dumper @packageList;
print " - Output file is: $outputFile\n";

## Logout
$client->call('auth.logout', $session);
exit();
