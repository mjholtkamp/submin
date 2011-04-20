# This sshd was compiled with PATH=/usr/bin:/bin:/usr/sbin:/sbin

Port PORT
Protocol 2
#AddressFamily any
ListenAddress 127.0.0.1
#ListenAddress ::

# HostKey for protocol version 1
#HostKey /etc/ssh_host_key
# HostKeys for protocol version 2
#HostKey /etc/ssh_host_rsa_key
#HostKey /etc/ssh_host_dsa_key
HostKey CONF_DIR/ssh_host_dsa_key

# Logging
# obsoletes QuietMode and FascistLogging
#SyslogFacility AUTHPRIV
#LogLevel QUIET

# Authentication:

#LoginGraceTime 2m
PermitRootLogin no

# environment may have loose modes, don't care.
StrictModes no
#MaxAuthTries 6

#RSAAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile AUTH_KEYFILE

# For this to work you will also need host keys in /etc/ssh_known_hosts
#RhostsRSAAuthentication no
# similar for protocol version 2
#HostbasedAuthentication no
# Change to yes if you don't trust ~/.ssh/known_hosts for
# RhostsRSAAuthentication and HostbasedAuthentication
#IgnoreUserKnownHosts no
# Don't read the user's ~/.rhosts and ~/.shosts files
#IgnoreRhosts yes

# To disable tunneled clear text passwords, change to no here! Also,
# remember to set the UsePAM setting to 'no'.
#PasswordAuthentication no
#PermitEmptyPasswords no

UsePam no

#AllowTcpForwarding yes
#GatewayPorts no
#X11Forwarding no
#X11DisplayOffset 10
#X11UseLocalhost yes
#PrintMotd yes
#PrintLastLog yes
#TCPKeepAlive yes
#UseLogin no
#UsePrivilegeSeparation yes
PermitUserEnvironment yes
#Compression delayed
#ClientAliveInterval 0
#ClientAliveCountMax 3
#UseDNS yes
PidFile CONF_DIR/sshd.pid
#MaxStartups 10
#PermitTunnel no

# SACL options
SACLSupport no

# Change to no to disable s/key passwords
#ChallengeResponseAuthentication yes

# Kerberos options
#KerberosAuthentication no
KerberosOrLocalPasswd no
KerberosTicketCleanup no
#KerberosGetAFSToken no

# GSSAPI options
#GSSAPIAuthentication no
GSSAPICleanupCredentials no
GSSAPIStrictAcceptorCheck no
#GSSAPIKeyExchange no

