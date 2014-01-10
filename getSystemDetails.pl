#!/usr/bin/perl
use Frontier::Client;
use Data::Dumper;

my $HOST = 'localhost';
my $user = 'testuser';
my $pass = 'qwas1234';
my $client = new Frontier::Client(url => "http://$HOST/rpc/api");
my $session = $client->call('auth.login',$user, $pass);
print "System Name\tBase Channel\tChild Channels\tConfig Channels\tSystemGroups\n";
my $systems = $client->call('system.listUserSystems', $session);
foreach my $system (@$systems) {
	$id = $system->{'id'};
	$name = $system->{'name'};
	
	# Get relevant data
	$baseChannelDetails = $client->call('system.getSubscribedBaseChannel', $session, $id);
	$childChannelDetails = $client->call('system.listSubscribedChildChannels', $session, $id);
	$configChannelDetails = $client->call('system.config.listChannels',$session,$id);
	$systemGroupDetails = $client->call('system.listGroups',$session,$id);
  	print $system->{'name'}."\t".$baseChannelDetails->{'label'}."\t";

	# Parse child channels
	$kids = "";
	foreach my $childChannel ($childChannelDetails) {
		foreach my $channelStuff (@$childChannel) {
		    if ($kids eq "") {
			    $kids = $channelStuff->{'label'};
			} else {
			    $kids = $kids . ":" . $channelStuff->{'label'} 
			}
		}
	}
	print $kids . "\t";	
	
	# Parse Config Channels
	$configs = "";
	foreach my $configChannel ($configChannelDetails) {
		foreach my $configStuff (@$configChannel) {
		    if ($configs eq "") {
				$configs = $configStuff->{'label'};
			} else {
				$configs = $configs . ":" . $configStuff->{'label'} 
			}
		}
	}
	print $configs . "\t";

	# Parse system groups
	foreach my $group (@$systemGroupDetails) {
		    if ($group->{'subscribed'} > 0) {
			## Look it up to get the id
			if ($configGroups eq "") {
				$configGroups = $group->{'system_group_name'};
			} else {
				$configGroups = $configGroups . ":" . $group->{'system_group_name'} 
			}
		}

	}
	print $configGroups . "\n";
	
}
$client->call('auth.logout', $session);

