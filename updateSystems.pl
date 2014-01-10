#!/usr/bin/perl
use Frontier::Client;
use Data::Dumper;

my $HOST = 'localhost';
my $user = 'testuser';
my $pass = 'password';
my $client = new Frontier::Client(url => "http://$HOST/rpc/api");
my $session = $client->call('auth.login',$user, $pass);
my $i=0;

## Get an array of the group details
my $groups = $client->call('systemgroup.listAllGroups', $session);
foreach $group (@$groups) {
	$gname = $group->{'name'};
	$newGroups->{$gname} = $group->{'id'};
}

open (FILE, 'output2.csv');
 while (<FILE>) {
 chomp;
 ($systemName, $baseChannel, $childChannels,$configChannels,$systemGroups) = split("\t");

## Ignore the column headers if they exist
next if ($systemName eq "System Name");
 $i++;

## Get the systemId
my $systemDetails = $client->call('system.getId', $session, $systemName);
foreach my $sysDets (@$systemDetails) {
	$systemId = $sysDets->{'id'};
}
 print "System Name: $systemName\n";
 print "System ID: $systemId\n";
 print "Base Channel: $baseChannel\n";
 print "Child Channels: $childChannels\n";
 print "Config Channels: $configChannels\n";
 print "System Groups: $systemGroups\n\n";

## Split child channels (if exists)
if ($childChannels ne "") {
	$addChildChannels=1;
	@kids = split(':',$childChannels);
	} else {
	$addChildChannels=0;
}

## Split config channels (if exists)
if ($configChannels ne "") {
	$addConfigChannels=1;
	@configs = split(':',$configChannels);
	} else {
	$addConfigChannels=0;
}

## Split system groups (if exists)
if ($systemGroups ne "") {
	$addSystemGroups=1;
	@sysGroups = split(':',$systemGroups);
	foreach $g  (@sysGroups) {
	push(@groupsToAdd,$newGroups->{'g'});
		$groupToAdd = $newGroups->{'$g'};
		print "Adding $groupToAdd \n";	
	}
	} else {
	$addSystemGroups=0;
}
print Dumper($groupsToAdd);
## Set the base channel
$rc = $client->call('system.setBaseChannel',$session,$systemId,$baseChannel);
&checkRetVal("Set Base Channel",$rc);

## Set child channels
if ($addChildChannels eq "1") {
	$klist = join(', ',@kids);
	$rc = $client->call('system.setChildChannels',$session,$systemId,\@kids);
	&checkRetVal("Set Child Channel (s): $klist",$rc);
	} else {
	print " - No child channels to add\n";
	}

## Set config channels
########################################################
##    ** NOTE **                                      ##
## You need to enable config management on the system ##
## to add config channels via the API                 ##
########################################################
if ($addConfigChannels eq "1") {
	$clist = join(', ',@configs);
	@sysId = split(' ',$systemId);
	$rc = $client->call('system.config.addChannels',$session,@sysId,\@configs,"true");
	&checkRetVal("Set Config Channel (s): $clist",$rc);
	} else {
	print " - No config channels to add\n";
	}
}

## Set SystemGroups
## TOTO - Not required at the mo
#if ($addSystemGroups eq "1") {
#	$syslist = join(', ',@configs);
#	@sysId = split(' ',$systemId);
#	$rc = $client->call('system.setGroupMembership',$session,@sysId,\@configs,"true");
#	&checkRetVal("Set System Groups(s): $clist",$rc);
#	} else {
#	print " - No System Groups to add\n";
#	}

$client->call('auth.logout', $session);

print "\nFinished - $i systems updated\n";

## Subs
sub checkRetVal {
($op, $val) = ($_[0], $_[1]);
if ($val ne "1") {
	print " - $op failed with return code $val\n";
	exit();
	} else {
	print " - $op : [OK]\n";
	}
}

