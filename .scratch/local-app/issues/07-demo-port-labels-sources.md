# Sources for segowl/defaults/port_labels.csv

Vendor documentation, IETF RFCs and the IANA registry only; nothing taken from nmap-services.

Markers:
- `[checked]` = the port values were read on the vendor page during ticket 07 (page fetched, or the vendor page's own text quoted by web search), and the CSV row matches it.
- `[unverified: …]` = no public vendor page could be read; the reason is given. Check these by hand before relying on them.
- `[convention]` = not vendor-documented on purpose (common alternate ports).

## Standard protocols
- Rows tagged "(RFC NNNN)" in the product column → https://www.rfc-editor.org/rfc/rfcNNNN (the RFC named on the row) [checked: RFC numbers match the protocol]
- IANA-registered ports without an RFC on the row (rsync 873, AFP 548, r-services 512-514, X11 6000-6063, OpenVPN 1194, SSDP 1900, sFlow 6343, Oracle TTC 2483/2484, NDMP 10000, Smart Install 4786, Aruba PAPI 8211, Docker 2375-2377, etcd 2379-2380, Puppet 8140, Zabbix 10050/10051, NRPE 5666, NetApp 11104/11105, Microsoft vmrdp 2179, HSRP 1985, OpenFlow 6653, PDL datastream 9100) → https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml [checked against the IANA CSV export]
- WireGuard udp:51820 [checked: the port used in the official quick start; WireGuard has no fixed default] → https://www.wireguard.com/quickstart/
- IPMI RMCP udp:623 → IANA (asf-rmcp) [checked], plus the BMC vendor pages below.

## Microsoft
- Windows / AD service ports (RPC 135, 49152-65535, SMB 445, NetBIOS 137-139, LDAP/CLDAP 389, LDAPS 636, GC 3268/3269, Kerberos 88/464, DNS 53, ADWS 9389, WinRM 5985/5986, RDP 3389 TCP/UDP, WDS/BINL udp:4011, RPC over HTTP 593, legacy RADIUS udp:1645/1646, RADIUS 1812/1813, SNMP 161/162, TFTP 69, NTP 123, DHCP 67, Hyper-V live migration 6600) [checked] → https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/service-overview-and-network-port-requirements
- Hyper-V VMConnect 2179 [checked] → https://learn.microsoft.com/en-us/archive/blogs/mpsc_dynamic_it/system-center-virtual-machine-manager-network-communications-ports-udptcp (Microsoft archive; also IANA "vmrdp")
- RD Gateway udp:3391 [checked] → https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/ports-used-by-rds
- KMS 1688 [checked] → https://learn.microsoft.com/windows-server/get-started/activation-troubleshoot-kms-general
- AD FS certificate authentication 49443 [checked] → https://learn.microsoft.com/en-us/powershell/module/adfs/set-adfsalternatetlsclientbinding
- LLMNR udp:5355 → RFC 4795 [checked]
- Configuration Manager 2701, 10123, WSUS 8530/8531, PXE udp:4011, multicast udp:63000-64000, Service Broker 4022 [checked] → https://learn.microsoft.com/en-us/intune/configmgr/core/plan-design/hierarchy/ports
- SQL Server 1433, udp:1434, 4022 and 5022 (both "conventional": Books Online examples, no fixed default) [checked] → https://learn.microsoft.com/en-us/sql/sql-server/install/configure-the-windows-firewall-to-allow-sql-server-access

## Out-of-band
- HPE iLO 443, 17988 (virtual media), 17990 (remote console) [checked] → HPE iLO 5 2.98 User Guide, "Ports used by iLO features" (HPE part number 30-DFF5B33E-015; copy fetched from https://itpfdoc.hitachi.co.jp/manuals/ha8000v/hard/Gen10/iLO/30-DFF5B33E-015.pdf, canonical on support.hpe.com). Removed 3002 (not in the guide).
- Dell iDRAC 443, 5900, 5901 [checked] → iDRAC9 User's Guide v3.4, "iDRAC port information", https://dl.dell.com/topicspdf/idrac9-lifecycle-controller-v34-series_Users-Guide_en-us.pdf. Removed 3668 (not in the table).
- Supermicro BMC TCP 623 virtual media [checked] → https://www.supermicro.com/en/support/security_BMC_virtual_media ; 5900 iKVM [checked] → https://www.supermicro.com/white_paper/IPMI_white_paper.pdf. Removed 5120/5123 (no Supermicro source).
- Lenovo XClarity Controller 3900 [checked] → https://pubs.lenovo.com/xcc/NN1ia_c_configuringportassignments
- Cisco IMC KVM 2068 [checked] → https://www.cisco.com/c/fr_ca/support/docs/servers-unified-computing/ucs-manager/115958-ucsm-kvm-troubleshooting-00.html

## Virtualization
- VMware ESXi 443, 902 TCP/UDP, 427 TCP, 5988, 8000, 8182 TCP/UDP, vSAN 2233 [checked] → https://knowledge.broadcom.com/external/article/318895/port-requirements-for-vmware-vsphere-esx.html (5989 replaced by 5988 as listed there; udp:427 removed, KB lists TCP only)
- VMware vCenter 443 [checked, same KB]; VAMI 5480 [checked] → https://docs.vmware.com/en/VMware-vSphere/7.0/vsphere-vcenter-appliance-management-api-programming-guide/GUID-ABE3C8C9-9000-4989-BE40-0F464D09C132.html ; 9443, 7444, 6501, 6502 (vSphere 6.x table) [checked] → https://knowledge.broadcom.com/external/article/326184/tcp-and-udp-ports-required-to-access-vmw.html . The current tool https://ports.broadcom.com/ is a JS app and was not readable.
- Omnissa (VMware) Horizon 4172 TCP/UDP, 8443, 22443 [checked] → https://techzone.omnissa.com/resource/network-ports-horizon-8 and https://docs.omnissa.com/Horizon-Security/FirewallRulesforHorizonAgent
- Proxmox VE 8006, 3128, 5900-5999, udp:5405-5412, 60000-60050 [checked] → https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html
- Proxmox Backup Server 8007 [checked] → https://pbs.proxmox.com/docs/installation.html
- Nutanix Prism 9440 [checked] → https://next.nutanix.com/installation-configuration-23/ports-and-protocols-reference-chart-40249 (Nutanix-hosted copy of https://portal.nutanix.com/page/documents/details?targetId=Port-Reference:tem-AHV_port_auto_r.html)
- libvirt 16509/16514 [checked] → https://libvirt.org/remote.html
- Citrix ICA 1494, CGP 2598 [checked] → https://docs.citrix.com/en-us/linux-virtual-delivery-agent/current-release/configure/administration/network-port-matrix and https://support.citrix.com/external/article/CTX696838/citrix-unable-to-connect-to-windows-vda.html

## Backup and storage
- Veeam B&R v13 (9419, 9420, 10443, 6160, 6161, 6162, 2500-3300, 6170) [checked] → https://helpcenter.veeam.com/docs/vbr/userguide/used_ports.html
- Veeam B&R v12 (9392, 9396, 9401, 9394) [checked] → https://helpcenter.veeam.com/docs/backup/vsphere/used_ports.html?ver=120
- Veeam Backup Enterprise Manager 9443 (IIS-based releases), 9394 [checked] → https://helpcenter.veeam.com/archive/backup/95u4/em/used_ports.html and https://helpcenter.veeam.com/docs/backup/em/used_ports.html
- Commvault 8400, 8401, 8403 [checked] → https://documentation.commvault.com/2024e/commcell-console/tcp_ports_used_for_services.html (labels corrected: 8401 = Event Manager, 8403 = GxFWD tunnel)
- Veritas NetBackup 1556, 13724, 13782 [checked] → https://www.veritas.com/support/en_US/doc/80731497-165998031-0/v124789546-165998031
- Veritas Backup Exec 6101, 10000 [checked] → https://docs.backupexec.com/us/en/backupexec-userdocs/product-guides/all-platforms/backup-exec-administrators-guide/20-0/configuration-and-settings/using-backup-exec-with-firewalls.html
- Bacula / Bareos 9101-9103 [checked] → https://docs.baculasystems.com/BEInstallation/BEInstallationOnLinux/LinuxInstallationWithPackageManager/FirewallSettings/index.html
- IBM Storage Protect 1500, 1581 [checked] → https://www.ibm.com/support/knowledgecenter/SSEQVQ_8.1.4/client/t_cfg_firewall.html and https://www.ibm.com/docs/ko/storage-protect/8.2.2?topic=reference-httpport
- Acronis Cyber Protect 9877, 7780 [checked] → https://www.acronis.com/en/support/documentation/AcronisCyberProtect_15/network-connection-diagram.html (Cyber Protect 15 page; no 16-specific page found)
- NetApp ONTAP SnapMirror 11104/11105 [checked] → https://docs.netapp.com/us-en/ontap/networking/ontap_port_usage_on_a_storage_system_overview.html
- Dell Data Domain 3009 [checked] → https://www.dell.com/support/kbdoc/en-sg/000205800/datadomain-ca-certificate-erros-when-creating-replication-contexts . Removed 2051 (only community/third-party sources).
- Synology DSM 5000/5001 [checked] → https://kb.synology.com/en-global/DSM/tutorial/What_network_ports_are_used_by_Synology_services
- QNAP QTS 8080 [checked] → https://www.qnap.com/en/how-to/faq/article/what-network-ports-are-used-by-qts-quts-hero-and-qutscloud-systems
- Ceph 3300, 6789, 6800-7568 [checked] → https://docs.ceph.com/en/latest/rados/configuration/network-config-ref/ (range corrected from 6800-7300)
- GlusterFS 24007 [checked] → https://docs.redhat.com/en/documentation/red_hat_gluster_storage/3.1/html/administration_guide/chap-getting_started
- MinIO 9000, console 9001 when pinned [checked] → https://min.io/docs/minio/linux/administration/minio-console.html

## Network and security appliances
- Fortinet FortiGate 443, 541, 514 (OFTP), 703 TCP/UDP, 1000, 1003, 8008, 8010 [checked] → https://docs.fortinet.com/document/fortigate/6.0.0/fortinet-communication-ports-and-protocols/534827/fortigate-open-ports (8008 corrected: policy override authentication, not FSSO)
- Fortinet FortiClient EMS 8013, 8014, 10443 [checked] → https://docs.fortinet.com/document/forticlient/7.2.13/ems-quickstart-guide/439480 and https://docs.fortinet.com/document/fortigate/6.2.0/ports-and-protocols/788212 (10443 corrected: EMS package download, not SSL VPN)
- Palo Alto PAN-OS management (443, 4443, 6080-6082) [checked] → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-management-functions
- Palo Alto Panorama 3978, 28443, HA 28769/28260 [checked] → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-panorama and .../ports-used-for-ha
- Palo Alto User-ID 5007 [checked] → .../ports-used-for-user-id ; GlobalProtect udp:4501 [checked] → .../ports-used-for-globalprotect
- Cisco Smart Install 4786 [checked] → https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20180328-smi2
- Cisco Secure Firewall FMC 8305 [checked] → https://docs.manage.security.cisco.com/c_communication_port_requirements.html
- Cisco ISE portals 8443, posture 8905 [checked] → https://www3-realm.cisco.com/en/US/docs/security/ise/1.2/user_guide/ise_webportals.pdf (ISE 1.2 guide; the 3.3 ports chapter was not readable) ; pxGrid 8910 [checked] → https://bxin.cisco.com/c/en/us/support/docs/security/identity-services-engine-33/221570-configure-ciphers-in-ise-3-3-and-later.pdf
- Cisco IOS reverse Telnet 2001-2016 [checked] → https://www3-realm.cisco.com/en/US/tech/tk801/tk36/technologies_configuration_example09186a008014f8e7.shtml (2000 + line number; 1-16 is the example's line range)
- Check Point 256, 257, 18190-18192, 18264 → https://support.checkpoint.com/results/sk/sk52421 [unverified: sk52421 needs a Check Point login; values corroborated only on community.checkpoint.com]
- Sophos Firewall 4444 [checked] → https://docs.sophos.com/nsg/sophos-firewall/21.0/api/system/administration/adminsettings/operations/webadminsettings.html
- MikroTik Winbox 8291, API 8728/8729, MNDP udp:5678 [checked] → https://help.mikrotik.com/docs/display/ROS/Services
- F5 BIG-IP iQuery 4353 [checked] → https://techdocs.f5.com/en-us/bigip-17-5-0/big-ip-dns-implementations/integrating-big-ip-dns-into-a-network-with-big-ip-ltm-systems.html ; failover udp:1026 [checked] → https://techdocs.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-device-service-clustering-administration-12-1-1/6.html ; single-NIC config utility 8443 [checked] → https://clouddocs.f5.com/cloud/public/v1/aws/AWS_singleNIC.html
- Ubiquiti UniFi udp:3478, udp:10001 [checked via search extract]; 8443, 8080 → https://help.ui.com/hc/en-us/articles/218506997 [unverified: help.ui.com returns 403 to automated fetch; 8080/8443 corroborated only by third parties]
- HPE Aruba udp:8211 PAPI [checked: IANA aruba-papi] ; 4343 → https://arubanetworking.hpe.com/techdocs/centralonprem/2.5.7/content/getting_started/opening_comm_ports.htm [checked for "device bootstrap to controllers"; WebUI use only confirmed on airheads.hpe.com]
- Juniper Junos XML protocol 3220/3221 [checked] → https://www.juniper.net/documentation/us/en/software/junos/junos-xml-protocol/topics/task/remote-access-junoscript-client-applications-clear-text-ssl.html
- NetFlow udp:2055 [convention: common collector port, no vendor default; Cisco exporters require an explicit port]

## Databases and caches
- Oracle Database 1521, Connection Manager 1630 (clients) and 1830 (admin), 2483/2484 [checked] → https://docs.oracle.com/en/database/oracle/oracle-database/19/ladbi/oracle-database-component-port-numbers-and-protocols.html and https://docs.oracle.com/en/database/oracle/oracle-database/26/netrf/protocol-address-configuration.html
- MySQL 3306, 33060 [checked] → https://dev.mysql.com/doc/mysql-port-reference/en/mysql-port-reference-tables.html
- PostgreSQL 5432 [checked] → https://www.postgresql.org/docs/current/runtime-config-connection.html
- SAP ASE 5000 → removed (no SAP page found; conflicts with Synology/Docker Registry 5000)
- IBM Db2 50000 → https://www.ibm.com/docs/en/db2/11.5?topic=ports-default [unverified: IBM page not readable; IBM Support notes say instances created on 11.5.6+ default to 25000, 50000 stays the legacy default]
- Firebird 3050 [checked] → https://raw.githubusercontent.com/FirebirdSQL/firebird/master/builds/install/misc/firebird.conf (RemoteServicePort = 3050) and IANA gds_db
- MongoDB 27017 [checked] → https://www.mongodb.com/docs/manual/reference/default-mongodb-port/
- Redis 6379, Sentinel 26379 [checked] → https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/
- Memcached 11211, UDP off since 1.5.6 [checked] → https://github.com/memcached/memcached/wiki/ConfiguringServer
- Apache Cassandra 9042, 7000, 7001 [checked] → https://cassandra.apache.org/doc/latest/cassandra/managing/configuration/cass_yaml_file.html ; JMX 7199 [checked] → https://github.com/apache/cassandra/blob/trunk/conf/cassandra-env.sh
- Elasticsearch 9200/9300 [checked] → https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-network.html
- CouchDB 5984 [checked] → https://docs.couchdb.org/en/stable/setup/cluster.html
- Couchbase 8091 [checked] → https://docs.couchbase.com/server/current/install/install-ports.html
- InfluxDB 8086 [checked] → https://docs.influxdata.com/influxdb/v2/reference/config-options/
- ClickHouse 8123, 9000 [checked] → https://clickhouse.com/docs/en/guides/sre/network-ports
- Neo4j 7474, 7687 [checked] → https://neo4j.com/docs/operations-manual/current/configuration/ports/
- CockroachDB 26257 [checked] → https://docs.cockroachlabs.com/docs/stable/cockroach-start
- SAP NetWeaver 32NN/33NN/36NN [checked] → https://help.sap.com/saphelp_em700_ehp01/helpdata/en/42/db8c45e873162ee10000000a1553f7/content.htm ; HANA 3NN13/3NN15 [checked] → https://pypi.org/project/hdbcli/2.30.24/ (SAP's own HANA client package) and https://blogs.sap.com/2017/12/04/hey-sap-hana-express-edition-any-idea-whats-your-sql-port-number

## Web and application servers
- Apache Tomcat 8080, 8009, 8005 [checked] → https://github.com/apache/tomcat/blob/main/conf/server.xml and https://tomcat.apache.org/tomcat-10.1-doc/config/server.html
- Oracle WebLogic 7002 [checked] → https://docs.oracle.com/cd/E13222_01/wls/docs90/ConsoleHelp/taskhelp/security/SetUpSSL.html ; 7001 [checked as Oracle's example listen port] → https://docs.oracle.com/en/cloud/paas/java-cloud/tutorial-deploy-application-eclipse-ide/files/imagedesc_connect09.txt
- IBM WebSphere 9060, 9043, 9080 [checked] → https://www.ibm.com/docs/es/was-nd/9.0.5?topic=zos-default-port-assignments
- WildFly 9990 [checked] → https://docs.jboss.org/author/display/WFLY9/Admin%20Guide.html
- GlassFish 4848 [checked] → https://docs.oracle.com/cd/E26576_01/doc.312/e24937/basic-features.htm
- Apache Solr 8983 [checked] → https://solr.apache.org/guide/taking-solr-to-production.html
- Jupyter 8888 [checked] → https://manpages.ubuntu.com/manpages/kinetic/man1/jupyter-server.1.html (jupyter-server's own --help output)

## Messaging
- Apache Kafka 9092 [checked] → https://kafka.apache.org/41/configuration/_print/
- Apache ZooKeeper 2181 [checked] → https://zookeeper.apache.org/doc/r3.9.3/zookeeperStarted.html
- RabbitMQ 5672, 5671, 15672, 4369, 25672, 1883, 8883 [checked] → https://www.rabbitmq.com/docs/networking
- Apache ActiveMQ 61616, 8161 [checked] → https://activemq.apache.org/components/classic/documentation/docker-image
- NATS 4222, 8222 [checked] → https://github.com/nats-io/nats-server/blob/main/server/const.go ; 6222 [checked] → https://github.com/docker-library/docs/blob/master/nats/content.md (official image docs: "6222 is a routing port for clustering")

## DevOps
- Kubernetes 6443, 2379-2380, 10250, 10256, 10257, 10259, 30000-32767 [checked] → https://kubernetes.io/docs/reference/networking/ports-and-protocols/
- Docker Engine 2375/2376 [checked] → https://docs.docker.com/engine/daemon/remote-access/
- Docker Swarm 2377, 7946 TCP/UDP, udp:4789 [checked] → https://docs.docker.com/engine/swarm/swarm-tutorial/
- Docker Registry 5000 [checked] → https://github.com/distribution/distribution/blob/main/cmd/registry/config-example.yml
- Portainer 9443, 8000, agent 9001 [checked] → https://docs.portainer.io/start/requirements-and-prerequisites (legacy HTTP 9000 removed: not on the page)
- Jenkins 8080, 50000 [checked] → https://www.jenkins.io/doc/book/installing/docker/
- TeamCity 8111 [checked] → https://jetbrains.com/help/teamcity/quick-setup-guide.html
- Bamboo 8085 [checked] → https://support.atlassian.com/atlassian-knowledge-base/kb/ports-used-by-atlassian-data-center-applications/
- Bitbucket Data Center 7990, 7999 [checked] → https://support.atlassian.com/bitbucket-data-center/kb/which-ports-does-bitbucket-server-listen-on-and-what-are-they-used-for/
- Gitea 3000 [checked] → https://docs.gitea.com/administration/config-cheat-sheet
- Sonatype Nexus 8081 [checked] → https://help.sonatype.com/en/network-configuration.html
- JFrog Artifactory 8081, 8082 [checked] → https://jfrog.com/help/r/jfrog-installation-setup-documentation/artifactory-network-ports
- SonarQube 9000 [checked] → https://docs.sonarsource.com/sonarqube/latest/setup-and-upgrade/install-the-server/installing-sonarqube-from-zip-file
- Puppet 8140 [checked] → https://help.puppet.com/pe/2023.8/topics/firewall_standard.htm
- Salt 4505/4506 [checked] → https://docs.saltproject.io/en/latest/topics/tutorials/firewall.html
- HashiCorp Vault 8200, 8201 [checked] → https://developer.hashicorp.com/vault/docs/configuration/listener/tcp
- HashiCorp Consul 8500, 8300, 8301-8302, 8600 [checked] → https://developer.hashicorp.com/consul/docs/install/ports
- HashiCorp Nomad 4646-4648 [checked] → https://developer.hashicorp.com/nomad/docs/configuration
- Apache Hadoop 9870, 8020, 8088 [checked] → https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml , https://hadoop.apache.org/docs/r3.2.1/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml (8020), https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-common/yarn-default.xml
- Apache Spark 7077 [checked] → https://spark.apache.org/docs/latest/security.html

## Monitoring and logging
- Zabbix 10050, 10051 [checked] → https://www.zabbix.com/documentation/current/en/manual/installation/requirements ("Default ports")
- Nagios NRPE 5666, NSCA 5667, NCPA 5693 [checked] → https://assets.nagios.com/downloads/nagiosxi/docs/Nagios-Ports-and-Protocols.pdf
- Paessler PRTG 23560 [checked] → https://paessler.com/manuals/prtg/list_of_default_ports
- Checkmk 6556, 8000 [checked] → https://docs.checkmk.com/latest/en/ports.html
- Icinga 2 5665 [checked] → https://github.com/Icinga/icinga2/blob/master/doc/06-distributed-monitoring.md
- SolarWinds agent 17778 [checked] → https://documentation.solarwinds.com/en/success_center/orionplatform/content/core-solarwinds-port-requirements.htm
- Grafana 3000 [checked] → https://github.com/grafana/grafana/blob/main/conf/defaults.ini
- Prometheus 9090, 9093, 9100 [checked] → https://github.com/prometheus/prometheus/wiki/Default-port-allocations
- Netdata 19999 [checked] → https://learn.netdata.cloud/docs/netdata-dashboards-and-visualizations/accessing-netdata-dashboards/
- Datadog DogStatsD udp:8125 [checked] → https://docs.datadoghq.com/developers/dogstatsd/
- Kibana 5601 [checked] → https://github.com/elastic/kibana/blob/main/config/kibana.yml ; Logstash 9600 [checked] → https://github.com/elastic/logstash/blob/main/config/logstash.yml ; Beats 5044 and Fleet 8220 [checked] → https://www.elastic.co/guide/en/fleet/8.9/fleet-settings.html
- Graylog 9000 [checked] → https://github.com/Graylog2/graylog2-server/blob/master/misc/graylog.conf ; GELF 12201 → https://go2docs.graylog.org/current/getting_in_log_data/gelf.html [unverified: the Graylog page does not state a default input port]
- Splunk 8000, 8089, 9997, 8088 [checked] → https://docs.splunk.com/Documentation/Splunk/latest/InheritedDeployment/Ports
- Wazuh 1514, 1515, 1516, 55000 [checked] → https://documentation.wazuh.com/current/getting-started/architecture.html
- HP JetDirect 9100 [checked: IANA hp-pdl-datastr, assigned to HP]

## Security tools
- Tenable Nessus 8834 [checked] → https://docs.tenable.com/nessus/Content/PortRequirements.htm
- Rapid7 InsightVM 3780 [checked] → https://insightvm.help.rapid7.com/docs/install
- Greenbone GSA 9392 [checked] → https://github.com/greenbone/gsad/blob/main/README.md
- Kaspersky Security Center 13000, 14000, 13291, 13299, 8080, udp:15000 [checked] → https://support.kaspersky.com/KSC/14.2/en-US/158830.htm
- ESET PROTECT 2222 (agent), 2223 (Web Console to server) [checked] → https://help.eset.com/protect_install/latest/en-US/ports_used.html and https://help.eset.com/protect_admin/13.1/en-US/admin_server_settings.html (2223 label corrected)
- Trellix ePO 8443, 8444, 8081 [checked] → https://docs-dr.trellix.com/docs/port-options
- Symantec SEPM 8443, 8014 [checked] → https://support.symantec.com/en_US/article.TECH163787.html and https://knowledge.broadcom.com/external/article/154515/symantec-endpoint-protection-14x-how-to.html
- CyberArk Vault 1858 → https://docs.cyberark.com/ [unverified: no public CyberArk page found; only third-party sources]
- RSA Authentication Manager 5500 TCP/UDP, 7004 [checked] → https://community.rsa.com/s/article/Ports-for-the-RSA-Authentication-Manager-Instance
- Velociraptor 8000, 8889 [checked] → https://docs.velociraptor.app/docs/deployment/

## Remote access tools
- TeamViewer 5938 TCP/UDP [checked] → https://www.teamviewer.com/en/global/support/knowledge-base/teamviewer-remote/troubleshooting/ports-used-by-teamviewer/
- AnyDesk 7070 [checked] → https://support.anydesk.com/docs/settings.md
- RustDesk 21114-21119, udp:21116 [checked] → https://rustdesk.com/docs/en/self-host/rustdesk-server-oss/install/ (range corrected from 21115)
- ConnectWise ScreenConnect 8040, 8041 → https://docs.connectwise.com/ScreenConnect_Documentation/On-premises/Advanced_setup/Port_configuration [unverified: doc behind ConnectWise login; values corroborated on ConnectWise's own feedback forum screenconnect.product.connectwise.com]
- NoMachine 4000 [checked] → https://kb.nomachine.com/AR04S01122
- Apache Guacamole 4822 [checked] → https://guacamole.apache.org/doc/gug/guacamole-docker.html

## Common alternate ports [convention]
Convention, not vendor-documented: SSH 2222, 2200, 22222, 8022; Telnet 2323; RDP 3388, 3390, 33890; HTTP 8000, 8008, 8080, 8888; HTTPS 8443, 4443, 9443, 10443; FTP 2121; MySQL 3307; PostgreSQL 5433. Each is its own row named "<Service> — common alternate port", tagged like the main service. (IANA registers several of these numbers to unrelated services, e.g. 2222 EtherNet/IP; the row only says that admins often move the service there.)


# Third pass (2026-11-04): vendor and cleartext columns, new families, risky tag

Same markers as above, plus `[checked via search extract]`: the vendor page refused automated fetch
(403, login, JS-only) and its text was read in the web-search result quoting that page.
Merge decisions: rows describing the same service from two families were folded into one (the risky
row wins and keeps the reason; tags are unioned); Ray worker range 10002-19999 is not tagged risky
(the entry point is the dashboard 8265, and the range would swamp a `#risky` bulk add).

## Existing rows: vendor, cleartext and re-verification


Only what changed: the 7 items that were `[unverified]` in 07-demo-port-labels-sources.md, label corrections, and the vendor pages read for the new `cleartext` column.
"via search extract" means the vendor page could not be fetched (login, 403, 404 to bots) and its indexed text was read through web search.

#### The 7 previously unverified items
- Check Point 256 (FWD_SVC), 257 (FWD_LOG), 18190 (CPMI), 18191 (CPD), 18192 (AMON), 18264 (ICA_SERVICES) [checked] → https://support.checkpoint.com/results/sk/sk17745 (public SK "Services allowed by Accept Control Connections"; use it instead of the login-only sk52421). Check Point calls 256 "FWD_SVC, between all Security Management Servers and all Security Gateways"; the "FW-1 management" label still fits.
- Ubiquiti UniFi 8080 (device and application communication), 8443 (application GUI/API) [checked via search extract] → https://help.ui.com/hc/en-us/articles/218506997-Required-Ports-Reference (still 403 to WebFetch, same as udp:3478/10001)
- CyberArk Vault 1858 [checked via search extract] → https://docs.cyberark.com/pam-self-hosted/latest/en/content/pas%20sysreq/standard%20ports%20-%20vault.htm and https://docs.cyberark.com/pam-self-hosted-legacy/latest/en/content/pas%20sysreq/network%20ports%20overview.htm (WebFetch gets 404. Indexed text: TCP 1858 for DR Vault, backup, components and clients; default set in Vault.ini; "patented CyberArk protocol". Newer pages apparently call it the "Idira protocol".)
- ConnectWise ScreenConnect 8040 (web server), 8041 (relay) [checked via search extract] → https://docs.connectwise.com/ConnectWise_ScreenConnect_Documentation/On-premises/On-premises_knowledge_base/Server_architecture and https://docs.connectwise.com/ScreenConnect_Documentation/Get_started/Security_guide (docs need a ConnectWise login)
- IBM Db2 50000 [checked, correction] → https://www.ibm.com/support/pages/installing-ibm-business-automation-workflow-24000 : "If on Db2 Version 11.5.5 and older, the default port number is 50000." / "If on Db2 Version 11.5.6 and newer, the default port number is 25000." IBM gives the reason (conflict with the ephemeral range) in https://www.ibm.com/support/pages/db2-how-exclude-db2-service-port-ephemeral-port-range [via search extract]. Suggest relabelling 50000 to "IBM Db2 default instance (11.5.5 and earlier)" and adding `25000;IBM Db2 default instance (11.5.6 and later);db;IBM;`. The Db2 docs topic "ports-default" and support note swg21573861 still need a login.
- Graylog GELF 12201 TCP/UDP [checked, with a caveat] → https://go2docs.graylog.org/current/downloading_and_installing_graylog/graylog_and_docker.htm ("12201:12201/ud[p]: Used for GELF UDP inputs", "[1]2201:12201/tcp: Used for GELF TCP inputs"; the page has typos). Graylog inputs have no built-in port. 12201 is the port Graylog's own deployment docs give for GELF.
- NetFlow udp:2055 [checked, correction] → https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/netflow/configuration-guide/netflow-configuration-ios-xr-8000/monitor-traffic-using-netflow/netflow-essential-concepts-and-terms.html : "By default, the designated destination port number is 2055." Cisco documents this as the IOS XR default, so it is more than a convention: take it out of `[convention]`, and the label could read "NetFlow export (Cisco default collector port)". Cisco Nexus 9000 defaults to 9995 instead [via search extract] → https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/93x/system-management/b-cisco-nexus-9000-series-nx-os-system-management-configuration-guide-93x/b-cisco-nexus-9000-series-nx-os-system-management-configuration-guide-93x_chapter_0100000.pdf

#### Label corrections and notes
- VMware ESXi 5988: KB 318895 now labels 5988 "CIM Secure Server / Secure server for CIM". IANA assigns 5988 to wbem-http and 5989 to wbem-https, so the KB looks like it mixed up 5988 and 5989 → https://knowledge.broadcom.com/external/article/318895/port-requirements-for-vmware-vsphere-esx.html . Cleartext is left empty for this reason; consider adding a 5989 row (CIM over HTTPS).
- Fortinet 8008 / 8010 share one label, but they differ: 8008 is "Port to use for FortiGuard Web Filter HTTP override authentication" and 8010 is "...HTTPS override authentication in proxy mode". 8015 (HTTPS, flow mode) and 8020 (warning override) also exist → https://docs.fortinet.com/document/fortigate/7.4.4/cli-reference/247552369/config-webfilter-fortiguard
- Fortinet OFTP 514: "OFTP communication occurs on TCP514 using TLS"; "Log communication occurs on UDP514 (default setting)" and is not encrypted → https://docs.fortinet.com/document/fortianalyzer/7.2.2/administration-guide/410387/appendix-b-log-integrity-and-secure-log-transfer . Consider adding a `udp:514` Fortinet log row.
- Palo Alto HA1: 28769/28260 are "clear text communication". Port 28 is "the HA1 control link for encrypted communication (SSH over TCP)". 28764-28767 (HA1 ssh tunnels), 28770 and 28771 are also listed → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-ha
- Dell iDRAC 5900: since iDRAC9 6.00.02.00, vConsole/vMedia use eHTML5 over 443 only, and the 7.xx port table no longer lists 5900, so the row only applies to older firmware [via search extract] → https://www.dell.com/support/manuals/en-us/poweredge-r660/idrac9_7.xx_ug/idrac-port-information?guid=guid-c4b751b6-0db3-4a0e-b34e-f99519fbb628
- Symantec SEPM 8014 is the unencrypted HTTP port. New SEPM 14 installs talk to clients over HTTPS 443; 8014 remains on upgraded or HTTP sites [via search extract] → https://knowledge.broadcom.com/external/article/158445/how-endpoint-protection-uses-encryption.html
- Kaspersky 14000 is plain TCP: "This port is optional. For security reasons we recommend using 13000" → https://support.kaspersky.com/KSC/14.2/en-US/158830.htm

#### Cleartext column: vendor statements read
- SQL Server 5022 / 4022: the CREATE ENDPOINT ENCRYPTION option "The default is REQUIRED" (AES since 2016) → no. The TSQL endpoint (1433) defaults to NEGOTIATED → empty → https://learn.microsoft.com/en-us/sql/t-sql/statements/create-endpoint-transact-sql
- Hyper-V live migration 6600: "live migration traffic isn't encrypted when sent over the network" → yes → https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/deploy/set-up-hosts-for-live-migration-without-failover-clustering
- WSUS 8530: "Unencrypted data, such as the EULA for specific updates, uses the HTTP port" → yes → https://learn.microsoft.com/en-us/intune/configmgr/core/plan-design/hierarchy/ports
- Docker Swarm 2377 / 7946: "Management and control plane data related to a swarm is always encrypted" → no. The overlay data path is encrypted only with `--opt encrypted` → https://docs.docker.com/engine/swarm/networking/
- Fortinet FGFM 541: the FortiGate "establishes an SSL session with the FortiManager" → no [via search extract] → https://docs.fortinet.com/document/fortigate/6.4.0/ports-and-protocols/373486/fgfm-fortigate-to-fortimanager-protocol ; OFTP TCP 514 → no; 8008 → yes; 8010 → no (pages above)
- Palo Alto: 4443 "alternative SSL port for HTTPS" → no. 6081 "without an SSL/TLS Server Profile" → yes. 6082 "with an SSL/TLS Server Profile" → no. 6080 (NTLM) and 5007 (User-ID) have no transport stated → empty → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-management-functions and .../ports-used-for-user-id . 3978 is TLS (PAN-OS 10.2+ uses TLS 1.3, which App-ID sees as ssl) → no [via search extract] → https://knowledgebase.paloaltonetworks.com/KCSArticleDetail?id=kA14u000000kI94CAE . 28769/28260 → yes (HA page above).
- Check Point 18190 CPMI: sk101269 "Is CPMI traffic from Management Clients to Management Server on TCP port 18190 secure?" answers that it is → no [via search extract; the SK needs a login] → https://support.checkpoint.com/results/sk/sk101269 . The other Check Point ports have no public statement → empty.
- Kaspersky: 13000, 13291, 13299 and 8080 are "TCP (TLS)" → no. 14000 "TCP" and udp:15000 "UDP" → yes (page above).
- Dell iDRAC: 5900 maximum encryption "128-bit SSL" → no. 5901 VNC has optional SSL → empty [via search extract] (iDRAC9 port table above).
- ScreenConnect: the relay encrypts session traffic with AES-256 by default → 8041 no. "The Web Server HTTP traffic is not encrypted unless configured with SSL" → 8040 yes (Security guide above).
- CyberArk 1858: secure, uses the "patented CyberArk protocol" → no (pages above).
- RSA AM 7004 is "SSL-encrypted" → no → https://community.rsa.com/s/article/Ports-for-the-RSA-Authentication-Manager-Instance . The page does not state the transport for 5500; it is marked no because RSA documents that agent traffic is encrypted with the node secret (not re-read this session).
- Wazuh 1514: "The Wazuh messages protocol uses AES encryption by default" → no. API 55000: "encrypted with SSL certificates" → no → https://documentation.wazuh.com/current/getting-started/architecture.html (1515 TLS enrollment and the 1516 cluster key are not on that page)
- Checkmk 6556: "TLS encrypted or in plain text (as for the Linux agent in legacy mode)" → empty. 8000: Agent Controller TLS registration / mTLS → no → https://docs.checkmk.com/latest/en/ports.html
- Nagios NSCA 5667: the default `decryption_method=1` is "Simple XOR (No security, just obfuscation, but very fast)" → yes → https://raw.githubusercontent.com/NagiosEnterprises/nsca/master/sample-config/nsca.cfg.in
- Ceph: secure mode exists only in msgr2, so 6789 (v1) → yes. ms_cluster/service/client_mode default to "crc secure" (crc gives no secrecy) → 6800-7568 yes. The mon modes default to "secure crc" → 3300 empty (secure is preferred, not required) → https://docs.ceph.com/en/latest/rados/configuration/msgr2/
- Proxmox VE 8006: "HTTP/1.1 over TLS" → no → https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html . SPICE 3128: the PVE 3.1 notes say "spice: use TLS (encrypt whole traffic)" → no. Corosync uses knet with `secauth: on` in the default config, and the udp/udpu transports "disable all cryptography" → no [both via search extract] → https://pve.proxmox.com/wiki/Cluster_Manager . Migration is secure (SSH tunnel) by default; "insecure" sends guest RAM unencrypted → 60000-60050 left empty → https://pve.proxmox.com/pve-docs/datacenter.cfg.5-plain.html
- Firebird 3050: WireCrypt defaults to "Required (for server)" since 3.0, but 2.x has no wire encryption, so it is left empty → https://raw.githubusercontent.com/FirebirdSQL/firebird/master/builds/install/misc/firebird.conf

#### Read, but no cleartext statement found (left empty)
- MikroTik Winbox 8291 → https://help.mikrotik.com/docs/display/ROS/Services ; PRTG 23560 → https://paessler.com/manuals/prtg/list_of_default_ports ; Portainer agent 9001 and Edge 8000 → https://docs.portainer.io/start/requirements-and-prerequisites ; Lenovo XCC 3900 → https://pubs.lenovo.com/xcc/NN1ia_c_configuringportassignments ; NRPE 5666 (`ssl_use_adh=1` default; the Nagios ports PDF is silent) → https://raw.githubusercontent.com/NagiosEnterprises/nrpe/master/sample-config/nrpe.cfg.in ; ConfigMgr 2701/10123 and VMware 902/8000/8182 (port pages silent) ; ESET 2223 → https://help.eset.com/protect_install/latest/en-US/ports_used.html ; Supermicro TCP 623 (the vulnerable firmware had "plaintext authentication, weak encryption"; the fix is not described) → https://www.supermicro.com/en/support/security_BMC_virtual_media
- Not readable this session: Veeam v13 used_ports (960k-character page, table not reached), Splunk Ports (403), Trellix port options (TLS handshake failure).

## OT, ICS, building automation


Vendor documentation, IETF RFCs and the IANA registry only; nothing taken from nmap-services.

Markers:
- `[checked]` = the port was read on the page (page fetched, PDF downloaded and text-extracted, or JS page rendered), and the CSV row matches it.
- `[checked via search extract]` = the vendor page refuses automated fetch (HTTP 403 / Akamai "Access Denied"); the port was read in the web-search extract of that vendor page.
- IANA rows were checked against the IANA CSV export (https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv), downloaded 2026-11-04.

#### Standard protocols (vendor column empty)
- Modbus/TCP 502 TCP and UDP, Modbus/TCP Security 802 [checked: IANA mbap / mbap-s, assignee modbus.org; 502 also listed on the Ignition, Emerson PACSystems, Beckhoff and ABB pages below] → https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml (modbus.org PDFs are behind a WAF and were not read)
- IEC 61850 MMS 102 [checked: "IEC 61850 Client, TCP 102" in the Emerson GFK-2830AD table; IANA iso-tsap 102] → https://download.astor.com.pl/dokumentacja/EMERSON/Kontrolery%20PAC/PACSystems%20RSTi-EP%20CPE200/Podr%C4%99czniki/GFK-2830AD-Secure-Deployment-Guide.pdf
- Secure ISO TP0 3782 [checked: IANA iso-tp0s "Secure ISO TP0 port"; the IEC 62351-4 (secure MMS) link in the label comes from the standard itself, not read: IEC text is paywalled] → IANA
- IEC 60870-5-104 2404, secure 19998 [checked: IANA iec-104 / iec-104-sec; 2404 also in the Emerson and ABB tables] → IANA
- DNP3 20000 TCP and UDP, DNP3 Secure 19999 [checked: IANA dnp / dnp-sec (DNP Users Group); 20000 also in the Emerson and ABB tables] → IANA
- EtherNet/IP 44818 TCP and UDP, implicit I/O udp:2222, CIP Security 2221 TLS and udp:2221 DTLS [checked: IANA EtherNet-IP-2 / EtherNet-IP-1 / ethernet-ip-s, assignee ODVA] → IANA
- PROFINET udp:34962-34963, udp:34964, udp:34965, udp:34966 [checked: IANA profinet-rt / -rtm / -cm / -cm-sec / -rt-sec, assignee PNO; DCE/RPC on UDP 34964 also in the Emerson GFK-2830AD table] → IANA
- OPC UA 4840 TCP and UDP, 4843 [checked: IANA opcua-tcp / opcua-udp / opcua-tls, assignee OPC Foundation] → IANA. Cleartext left empty on 4840: the same port carries SecurityMode None, Sign and SignAndEncrypt.
- OPC Classic (DA / HDA / A&E) over DCOM 135 [checked: "135 TCP, default DCOM port for older OPC DA servers" on the Ignition port reference; "135 TCP, DASEngine, OPC: DCOM and RPC" in the AVEVA System Platform table; Beckhoff lists OPC DA on dynamic DCOM ports 1024-65535] → https://docs.inductiveautomation.com/docs/8.1/appendix/reference-pages/gateway-port-reference and https://docs.aveva.com/bundle/system-platform-2023r2sp2/page/686254.html . Note: OPC Classic then moves to a dynamic RPC port (49152-65535, already a Microsoft row).
- BACnet/IP udp:47808 [checked: IANA bacnet; also "47808 UDP BACnet" on the Ignition port reference] → IANA
- KNXnet/IP udp:3671 [checked: IANA efcp "e Field Control (EIBnet)", contact at KNX; EIBnet/IP is the former name of KNXnet/IP] → IANA
- LonTalk over IP udp:1628-1629 [checked: IANA lontalk-norm / lontalk-urgnt] → IANA
- HART-IP 5094 TCP and UDP [checked: IANA hart-ip] → IANA
- FOUNDATION Fieldbus HSE udp:1089-1091 [checked: IANA ff-annunc / ff-fms / ff-sm, Fieldbus Foundation] → IANA
- EtherCAT udp:34980 [checked: IANA ethercat; Beckhoff lists "TwinCAT EAP, 34980 UDP"] → IANA and https://infosys.beckhoff.com/content/1033/ipc_security_win10/11019143435.html
- Ethernet POWERLINK udp:3819 [checked: IANA epl-slp "EPL Sequ Layer Protocol"] → IANA
- DLMS/COSEM 4059 [checked: IANA dlms-cosem] → IANA
- ANSI C12.22 1153 [checked: IANA c1222-acse, reference RFC 6142] → https://www.rfc-editor.org/rfc/rfc6142

#### Siemens
- S7comm / S7comm-plus 102 [checked: "S7 driver to PLC 102" on the WinCC OA page; "102 TCP Siemens Step 7" on the Ignition port reference; "102 TCP SiDirect OI Server" in the AVEVA table; Siemens TIA page (search extract): ISO-on-TCP server, port 102, RFC 1006, PG/HMI, enabled by default] → https://www.winccoa.com/documentation/WinCCOA/latest/en_US/GettingStarted/GettingStarted-85.html and https://docs.tia.siemens.cloud/r/simatic_et_200al_manual_collection_zhcn_20/function-manuals/communication/communication/communications-services/communications-protocols-and-port-numbers-used-for-ethernet-communication . Cleartext left empty: classic S7comm is plain, newer S7-1200/1500 PG/HMI traffic can be TLS on the same port.
- Automation License Manager 4410 [checked] → https://cert-portal.siemens.com/productcert/html/ssa-783261.html
- WinCC OA PMON 4999, data 4897, event 4998, distribution 4777, redundancy 4776, split 4778, proxy 5678, XML-RPC 4770 [checked] → https://www.winccoa.com/documentation/WinCCOA/latest/en_US/GettingStarted/GettingStarted-85.html

#### Beckhoff
- TwinCAT ADS 48898, ADS discovery udp:48899, Secure ADS 8016, OPC UA Gateway (TF6100) 48050, TwinCAT HMI (TF2000 1.14+) 2020 [checked] → https://infosys.beckhoff.com/content/1033/ipc_security_win10/11019143435.html (8016 also IANA ads-s). Removed 4852 (OPC UA, component not named on the page) and 1020 (TwinCAT HMI 1.12 and earlier).

#### CODESYS
- Runtime / gateway udp:1740-1743 and 11740-11743, Gateway 1217, WebVisu 8080 [checked] → https://content.helpme-codesys.com/en/CODESYS%20Control/_rtsl_start_page.html
- Network variables udp:1202 [checked: "(trasmissione UDP)"; same page confirms 1217, 11740, 502, 2404, 20000 for the CODESYS-based AC500] → https://it.help.plc.abb.com/pm56xx_protocols_sockets_ports.html (ABB AC500). Removed ABB netConfig 24576 (transport not stated).

#### Inductive Automation Ignition (and third-party ports it documents)
- Gateway 8088 / 8043, Gateway Network 8060, OPC UA 62541 (4096 up to 7.9), discovery udp:4445-4446, MQTT Distributor 1883 / 8883 [checked] → https://docs.inductiveautomation.com/docs/8.1/appendix/reference-pages/gateway-port-reference
- PTC Kepware KEPServerEX 49320 [checked on the same Ignition page, "Default Kepware port"; PTC's own Service Port Assignments page not read]
- Omron FINS 9600 TCP and UDP [checked on the same Ignition page; Omron's Ethernet unit manual not read]

#### Tridium Niagara (Honeywell)
- Fox 1911, foxs 4911, foxwss 443 (Niagara 4.15+) [checked] → https://www.tridium.com/content/dam/tridium/en/documents/niagara-forum-2025/developer/tri-NF25_Developer_Demistifying_FOX_in_Niagara.pdf
- foxs 4911, platform TLS 5011, station HTTPS 443 [checked] → https://www.tridium.com/content/dam/tridium/en/documents/document-lists/Niagara4-Hardening-Guide-2023.pdf
- Platform daemon 3011 (unsecured) / 5011 (secured) [checked] → Honeywell CIPer Model 30 Engineering User Guide 31-00237 (Niagara-based controller), https://prod-edam.honeywell.com/content/dam/honeywell-edam/hbt/en-us/documents/manuals-and-guides/user-manuals/HBT-BMS-CIPer_Model_30_Engineering_User_Guide_31-00237.pdf

#### AVEVA (Wonderware, OSIsoft PI, Citect)
- System Platform NmxSvc 5026, aaGR 8090, redundancy 30000-30001 + udp:30000, OPC UA 48031, SuiteLink 5413, InTouch Alarm Manager 51218, Historian 32568 / 32565, License Server 55559 [checked] → https://docs.aveva.com/bundle/system-platform-2023r2sp2/page/686254.html (JS-only page, rendered with headless Chrome). Removed 808, 32569, 32573, 55555, 7084-7085 (generic WCF, gateways or legacy services).
- PI Data Archive 5450 [checked] → https://docs.aveva.com/bundle/pi-server-install/page/1022146.html
- PI AF 5457, PI SQL for AF 5459, PI Analysis 5463, PI Notifications 5468 [checked] → https://cdn.osisoft.com/osi/presentations/2023-AVEVA-San-Francisco/UC23NA-2PGK06-AVEVA-Biggins-Best-practices-for-security-in--PI-System.pdf (AVEVA deck reproducing the PI port tables)
- Plant SCADA (Citect) CtAPI 2073 / 3073, alarm 2080, I/O 2082, reports 2084, trends 2085, ODBC 20222 [checked] → https://docs.aveva.com/bundle/plant-scada/page/1040274.html (ports 2074-2079 are legacy and no longer used, per the same page). Removed 2087, 2088, 5482 (local-only or internal).

#### GE Vernova (Proficy) and Emerson (ex-GE PACSystems)
- iFIX networking 2010 [checked: "By default, iFIX uses the following port: FIX 2010/tcp"] → https://gevernova.com/software/documentation/ifix/version2024/pdf/Setting%20up%20the%20Environment.pdf . Removed database synchronization 53014 (protocol not stated).
- Proficy Historian 13000, 14000, 14001-14003 [checked] → https://www.gevernova.com/software/documentation/historian/version2024/pdfs/secure_deployment_guide.pdf . Removed 8008 (second client-service port, unclear).
- CIMPLICITY 32000 TCP and UDP, 32256 / 32512 / 32768, web server 9443 [checked] → https://gevernova.com/software/documentation/cimplicity/version2024/pdf/CIMPLICITY_Secure_Deployment_Guide.pdf (the guide recommends IPsec for these flows, hence cleartext yes). Removed AlarmCast 8003 and redundancy probe 4000.
- PACSystems SRTP 18245, Remote Station Manager udp:18245, EGD udp:18246, Reliable Datagram Service / EGD control udp:7937 [checked] → GFK-2830AD Secure Deployment Guide (distributor copy) https://download.astor.com.pl/dokumentacja/EMERSON/Kontrolery%20PAC/PACSystems%20RSTi-EP%20CPE200/Podr%C4%99czniki/GFK-2830AD-Secure-Deployment-Guide.pdf and GFK-2224AG defaults (staudp 18245, gctl_port 7937, gdata_port 18246) https://download.astor.com.pl/dokumentacja/EMERSON/Kontrolery%20PAC/PACSystems%20RSTi-EP%20CPE100%20__%20CPE115/Podr%C4%99czniki/GFK-2224AG-PACS-Ethernet-Manual.pdf

#### Schneider Electric
- EcoStruxure Building Operation 4444 [checked: "TCP on port 4444 (fixed)"] → https://www.se.com/in/en/faqs/FAQ000245118
- Machine Expert protocol 1105 (M241/M251), discovery udp:27126-27127 [checked] → https://www.se.com/it/it/faqs/FAQ000271808 (the same FAQ lists UDP 1740-1743 and TCP 11740, already CODESYS rows)
- Geo SCADA Expert database server 5481, client incoming data 5500-5509 [checked via search extract] → https://tprojects.schneider-electric.com/GeoSCADAHelp/Geo%20SCADA%202021/Content/SecurityGuide/SecureNetworkPorts.htm and https://tprojects.schneider-electric.com/GeoSCADAHelp/Geo%20SCADA%202021/Content/ClientAdministrationGuide/ChangethePortfortheServersIncomingData.htm (both 403 to automated fetch)

#### Rockwell Automation
Every rockwellautomation.com and literature.rockwellautomation.com page returns 403 or Akamai "Access Denied" to automated fetch; the values below were read in search extracts of those pages.
- FactoryTalk Activation 27000-27009 (lmgrd) [checked via search extract] → https://www.rockwellautomation.com/en-us/docs/factorytalk-activation-manager/5-01-00/help-ditamap/welcome-to--ftam-/-ftam--firewall-ports-and-rules.html
- FactoryTalk Linx (RSLinxNG.exe) 4241, Rockwell Application Services (RsvcHost.exe) 4255 [checked via search extract] → https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/ftsp-rm001_-en-p.pdf
- FactoryTalk RNA 1330-1332 [checked via search extract: the advisories say to block these ports to keep RNA traffic out of the ICS] → https://www.rockwellautomation.com/en-in/trust-center/security-advisories/advisory.PN687.html and https://rockwellautomation.com/zh-tw/trust-center/security-advisories/advisory.PN759.html
- FactoryTalk Linx Gateway OPC UA 4990 [checked via search extract: "The default port is 4990 and increments by 1 for each additional endpoint"] → https://www.rockwellautomation.com/content/output/sites/content/dam/dita/en/factorytalk-linx-gateway/6-60/factorytalk-linx-gateway-help-ditamap/factorytalk-linx-gateway-help/quick-start-steps/ua-server/ua-server-endpoints/add-an--opc--ua-server-endpoint.html
- RSLinx Classic unsolicited messages udp:44818 [checked via search extract: "Accept UDP Messages on Ethernet Port", disabled by default since RSLinx Classic 4.10] → https://www.rockwellautomation.com/en-pr/trust-center/security-advisories/advisory.PN1037.html
- Allen-Bradley ABTCP 2222 TCP [checked: "2221 2222 2223, TCP, ABTCP OI Server, Allen-Bradley PLC communication" in the AVEVA System Platform table; the CSP / PLC-5 / SLC 500 wording is the documented scope of the ABTCP driver, not read on that page] → https://docs.aveva.com/bundle/system-platform-2023r2sp2/page/686254.html

#### Other vendors
- Wibu-Systems CodeMeter 22350 [checked: IANA codemeter; Rockwell's FactoryTalk Activation firewall page (search extract) lists TCP and UDP 22350] → IANA
- WAGO 2455, 6626 [checked: IANA wago-io-system / wago-service, assignee WAGO; labels follow the IANA names] → IANA

## VoIP, video surveillance, printing


Vendor documentation, IETF RFCs, ITU-T/OASIS/ONVIF specs and the IANA registry only; nothing taken from nmap-services.

Markers:
- `[checked]` = the port values were read on the vendor/standards page (page fetched, or PDF fetched and text-extracted).
- `[checked: search extract]` = the vendor page could not be fetched directly (JS-only, 403, login redirect, timeout), so the ports were read in the web-search result text quoting that vendor page. Worth a manual look before relying on them.
- No `[unverified]` rows were kept: products without a readable vendor source were dropped (list at the end).

#### Standard protocols
- SIP 5060 TCP/UDP, SIPS 5061 → https://www.rfc-editor.org/rfc/rfc3261 and https://www.rfc-editor.org/rfc/rfc5630 [checked against the IANA CSV export: sip/sips]
- H.323 1720 TCP, udp:1719, udp:1718, 1300, 11720 → https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml (h323hostcall, h323gatestat, h323gatedisc, h323hostcallsc, h323callsigalt, assignee ITU-T) [checked against the IANA CSV export]; 1719/UDP and 1720/TCP also in the Cisco CUCM and Pexip tables below
- MGCP udp:2427 (gateway), udp:2727 (call agent) [checked] → https://www.rfc-editor.org/rfc/rfc3435.txt (section 3.5) and IANA mgcp-gateway / mgcp-callagent
- Megaco / H.248 2944 (text) and 2945 (binary), TCP and UDP → IANA megaco-h248 / h248-binary [checked against the IANA CSV export]
- IAX2 udp:4569 → IANA iax [RFC 5456] [checked against the IANA CSV export]
- STUN/TURN 3478 TCP/UDP, 5349 TLS, udp:5349 DTLS → IANA stun/turn/stuns/turns [RFC 8489, RFC 8656, RFC 7350] [checked against the IANA CSV export]
- RTP/RTCP udp:5004/5005 → IANA avt-profile-1/2 [RFC 3551] [checked against the IANA CSV export]
- RTSP 554, RTSPS 322 [checked] → https://www.rfc-editor.org/rfc/rfc7826.txt (section 4.2: rtsp 554, rtsps TCP 322; RTSP 2.0 is TCP only); udp:554 = RTSP 1.0 rtspu (RFC 2326) and IANA rtsp udp; 8554 → IANA rtsp-alt [checked against the IANA CSV export]
- WS-Discovery udp:3702 [checked] → https://docs.oasis-open.org/ws-dd/discovery/1.1/os/wsdd-discovery-1.1-spec-os.html (DISCOVERY_PORT 3702, 239.255.255.250)
- ONVIF device service on 80, discovery through WS-Discovery [checked] → https://www.onvif.org/specs/core/ONVIF-Core-Specification.pdf (Core Spec 26.06, section 7.3.2.3)
- CoAP udp:5683/5684 (RFC 7252), 5683/5684 TCP/TLS (RFC 8323) → IANA coap/coaps [checked against the IANA CSV export]
- SLP udp:427 (RFC 2608) → IANA svrloc [checked]; also listed for printer discovery in the HP Jetdirect guide below
- IPPS 631 [checked] → https://www.rfc-editor.org/rfc/rfc7472.txt (section 4.3) and IANA ipps
- WSDAPI 5357/5358 → IANA wsdapi / wsdapi-s (registered by Microsoft) [checked against the IANA CSV export]
- Printer Request/Status ports 3910/3911 → IANA prnrequest / prnstatus [checked against the IANA CSV export; IANA gives a person, not a company, so vendor left empty]

#### Cisco
- Unified CM 2000, 2443, 2445, 3804, 6970, 6971-6972, udp:69/6969, 8080, 8443, 9443, 9444, 2748, 2749, 2427, 2428, 1719, 1720, udp:16384-32767 (CUCM itself 24576-32767), intracluster 1500-1501, 1515, 2551, 2552, 2555-2556, 4040, 8001, 8002-8003, 8500 TCP/UDP, 8888-8889, 1090/1099 [checked] → https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/14/systemConfig/cucm_b_system-configuration-guide-14su2/cucm_m_tcp-and-udp-port-usage-12-0.html
- Unity Connection 20532, 22000-22001 TCP/UDP, udp:16384-21511, 21000-21512, 20500-20502, 5060-5199 TCP/UDP (plus the shared 1500-1501, 1515, 2555-2556, 8001, 8500, 1090/1099) [checked] → https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/14/security/guide/b_14cucsecx/b_14cucsecx_chapter_00.html
- Expressway X14 7001, udp:6001, udp:36000-59999, udp:2776-2777, 3478-3483, udp:24000-29999 [checked] → https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/expressway/config_guide/X14-0/ip_port_usage/exwy_b_ip-port-usage-configuration-guide-14/exwy_b_ip-port-usage-configuration-guide_chapter_011.html ; 5062 MTLS, 2776-2777 TCP, 15000-19999 TCP, 24000-29999 TCP [checked] → .../exwy_b_ip-port-usage-configuration-guide_chapter_0110.html
- CUBE udp:8000-48198 [checked] → https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/voice/cube/ios-xe/config/ios-xe-book/m_voi-cube-multi-vrf.html ("The default port range is 8000-48198 for ASR and ISR G3 platforms")
- Webex Video Mesh 443, 8443, 5004 TCP/UDP, 4442, udp:10000-40000 [checked] → https://help.webex.com/en-us/article/2r5gv7/Deployment-Guide-for-Video-Mesh

#### Microsoft
- Skype for Business Server 2015/2019/SE Front End, Director, Mediation, Persistent Chat (5061, 444, 4443, 8080, 8060-8061, 8057-8058, 5062-5065, 5067, 5068, 5070, 5071-5073, 5075-5076, 5080, 448, 8404, 5086-5087, 5041, 881, 49152-57500 TCP/UDP, 57501-65535 TCP/UDP, 49152-65535 TCP) [checked] → https://learn.microsoft.com/en-us/skypeforbusiness/plan-your-deployment/network-requirements/ports-and-protocols
- Skype for Business Edge (5062 A/V auth, 4443 CMS replication, 8057, 23456, 50001-50003, udp:3478, 50000-59999 TCP/UDP, 5269) [checked] → https://learn.microsoft.com/en-us/skypeforbusiness/plan-your-deployment/edge-server-deployments/edge-environmental-requirements
- Print Spooler (RPC over named pipes, 445 + 135 + dynamic RPC) and TCP/IP Print Server LPDSVC 515 [checked] → https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/service-overview-and-network-port-requirements

#### Avaya
- IP Office R12.3 port matrix (411, 8411, 7070-7071, 7444, 5443, 8000, 9080, 52233, 50802, 50804, 50805, 50808, 50809, 50812, 50813, 50814, 50794 TCP/UDP, udp:50795, 50796, 50797, 1300, 1718-1720, udp:40750-50750 with IP500 V2 46750-50750; Voicemail Pro udp:50791, 50791 TLS, 50792-50793; one-X Portal 4560, 5222, 5269, 7171, 7443, 8443, 9443, 8666, 9092, 5433, 61615, 50815) [checked] → https://support.avaya.com/css/public/documents/101089198 (PDF "Avaya Port Matrix: IP Office R12.3", Issue 13.3, April 2026)
- Communication Manager H.248 1039 (PTLS), 2944 (TLS), 2945 (TCP), 21874 [checked: search extract] → https://documentation.avaya.com/en-us/home/bundle/communication-manager/communicationmanagersurvivabilityoptionsr102x/SurvivableCoreServerDesignAndPlanning/NetworkPortConsiderations.html and https://documentation.avaya.com/bundle/AdministeringCommunicationManager_R10.2.x/page/Networkportusage.html (JS-only pages)
- Application Enablement Services 450, 453, 1050-1065, 1066-1081, 4721, 4722 [checked: search extract] → https://documentation.avaya.com/en-us/home/bundle/application-enablement-services/administeringaeservicesr102x/tcp-ports-and-firewallsettingsontheaeservicesserver/TCPPortsAndFirewallSettings (1066-1081 range also in https://support.avaya.com/css/public/documents/100017893)

#### Mitel
- MiNet 6800/6801/6802, SAC 3998-3999, 6881, MBG cluster 6809, TFTP udp:20001, udp:20000, media udp:20002-29999 and udp:30000-30999, console 6806/6807, 36008, MiCollab 18100 [checked] → https://www.mitel.com/sites/default/files/s3_imports/Applications/MiVoice%20Border%20Gateway/12.3/en/MBG_Engineering_Guidelines.pdf (Appendix A: Firewall Configuration Reference)

#### Alcatel-Lucent Enterprise
- OmniPCX Enterprise CSTA server 2555 [checked] → https://www.al-enterprise.com/-/media/assets/internet/documents/oxe-um-nfcextendoxemob-8al90613frab-1-fr.pdf ("Port de connexion du serveur CSTA ... valeur par défaut est 2555")

#### Open-source and IP-PBX
- Asterisk AMI 5038 (disabled by default), AMI TLS 5039 [checked] → https://github.com/asterisk/asterisk/blob/master/configs/samples/manager.conf.sample ; HTTP/ARI 8088, TLS 8089 [checked] → https://github.com/asterisk/asterisk/blob/master/configs/samples/http.conf.sample ; RTP udp:10000-20000 (built-in default 5000-31000) [checked] → https://github.com/asterisk/asterisk/blob/master/configs/samples/rtp.conf.sample
- FreeSWITCH ESL 8021 (default password ClueCon, inbound ACL commented out) [checked] → https://github.com/signalwire/freeswitch/blob/master/conf/vanilla/autoload_configs/event_socket.conf.xml ; 5080/5081 [checked] → .../conf/vanilla/vars.xml ; WS 5066 / WSS 7443 [checked] → .../conf/vanilla/sip_profiles/internal.xml ; Verto 8081/8082 [checked] → .../conf/vanilla/autoload_configs/verto.conf.xml ; 5080 TCP/UDP, 8021, udp:16384-32768 [checked: search extract] → https://developer.signalwire.com/freeswitch/FreeSWITCH-Explained/Networking/Firewall_1048908/
- 3CX 5060/5061, 5090 TCP/UDP, udp:9000-10999, 443 or 5001 [checked: search extract] → https://www.3cx.com/docs/manual/firewall-router-configuration/ ; 5000/5001 as the HTTP/HTTPS alternative to 80/443 [checked: search extract] → https://www.3cx.com/blog/docs/http-https-ports-3cx-phone-system/ (both pages return truncated content to automated fetch)

#### Video conferencing and endpoint management
- Pexip Infinity 443 (Management Node), 8443 (Conferencing Node provisioning), 1719, 1720, 5060, 5061, 33000-39999, 40000-49999 TCP/UDP, 4277 [checked] → https://docs.pexip.com/admin/port_usage.htm
- Poly VideoOS command-line API on telnet port 24 (default; telnet disabled by default) [checked] → https://kaas.hpcloud.hp.com/pdf-public/pdf_8740172_en-US-1.pdf (Poly VideoOS Configuration Parameter Reference Guide 4.1.0, sec.telnet.apiPort)
- Yealink Device Management Platform 443, 80, 9989, 9090, 8446 [checked] → https://support-cdn.yealink.com/attachment/upload/attachment/2021-5-19/3/c7add9e5-db9b-47df-be53-a6f41e47d26b/Yealink+Device+Management+Platform+Administrator+Guide+V3.7.0.10.pdf ("Port Requirements")

#### Video surveillance and IoT
- Milestone XProtect 2025 R2 (80/443 IIS, 9000, 7609, 1234 TCP/UDP, 1235, 9090, 22331, 22332, 22333, 5210, 7563, 9001, 11000, udp:8844, 8990, 22337, 8081, 8082, 12345, 580, 554, 9100, 9200) [checked] → https://doc.milestonesys.com/mc/pdf/2025r2/en-US/MilestoneXProtectVMSproducts_AdministratorManual_en-US.pdf ("Ports used by the system")
- Genetec Security Center 5.14 (5500, 4502, 80, 443, 555, 605, 5602, 558, 560, 960, 5004, 554, 654, 570, udp:15000-19999, udp:6000-6500, udp:8000-12000, udp:47806-47807, udp:65246) [checked] → https://techdocs.genetec.com/api/khub/documents/dSJLhNKI2N3eXrdeZ7RBpQ/content (Network Diagram - Video, May 2026) ; Web SDK 4590, Map Manager 8012 [checked] → https://techdocs.genetec.com/api/khub/documents/JzIQszwPNbkhWxthQ_ugTQ/content (Network Diagram - Platform)
- Axis devices 80, 443, 49152 UPnP, 3702, 322 [checked] → https://help.axis.com/en-us/axis-os-knowledge-base ("Commonly used network ports")
- AXIS Camera Station 5 55752, 55754, 55756, 55757 [checked] → https://help.axis.com/en-us/axis-camera-station-5 ; AXIS Camera Station Pro 29202, 29204 [checked] → https://help.axis.com/en-us/axis-camera-station-pro
- Hikvision 80, 554, 8000 (server port), 8443 (enhanced SDK over TLS) [checked] → https://enpinfo.hikvision.com/hkwsen/unzip/20230410194813_20373_doc/GUID-E852C255-D9BD-4288-959E-584EC975B407.html
- Dahua 37777 TCP, udp:37778 (plus 80, 443, 554) [checked] → https://www.dahuasecurity.com/asset/upload/uploads/soft/20181107/Dahua-Network-Video-Server-Users-Manual-V1.1.1.pdf
- Bosch IP camera RCP+ 1756 (closed by default on recent firmware) [checked] → https://media.boschsecurity.com/fs//media/pb/images/products/video_systems/data_security_1/bosch_secure_by_default_technote.pdf
- Bosch BVMS Management Server 5390, 5322, 5389, 5393, 5395, VRM 1756, udp:1757-1758, udp:1800 [checked: search extract, older BVMS release] → https://community.boschsecurity.com/t5/Security-Video/Which-are-the-ports-that-must-be-open-within-a-LAN-for-all-BVMS/ta-p/22412 (Bosch tech knowledge base article, now redirects to a Keenfinity wiki login; BVMS Configuration Manual "used ports" chapter is the canonical list)
- Ubiquiti UniFi Protect 7441, 7442, 7443, 7444, 7445, 7447 [checked: search extract] → https://help.ui.com/hc/en-us/articles/218506997-Required-Ports-Reference ; 7550 [checked: search extract] → https://help.ui.com/hc/en-us/articles/360012622613-UniFi-Device-Adoption (help.ui.com returns 403 to automated fetch)

#### Printing
- HP Jetdirect raw 9100 (already shipped), IPP on 80/280/631, FTP printing 20/21, SLP udp:427 [checked] → https://h10032.www1.hp.com/ctg/Manual/c04500237.pdf (HP Jetdirect Administrator's Guide, firmware V.40) ; 280 TCP/UDP HTTP management, 9280 scan, 9281-9282 [checked: search extract] → https://support.hp.com/hr-en/document/c00832492 ; 9101-9102 [checked: search extract] → https://support.hp.com/us-en/product/hp-jetdirect-300x-print-server-series/27316/document/bpj02745 (support.hp.com timed out on fetch)
- PaperCut NG/MF 9191, 9192, 9193, 9195 [checked] → https://www.papercut.com/kb/Main/FirewallPorts/ ; Mobility Print 9163, 9164 [checked] → https://www.papercut.com/help/manuals/mobility-print/set-up/installation/
- Canon BJNP 8611-8614 TCP/UDP, MFNP 8610 TCP/UDP, CPP discovery udp:8609, CAPT 3756 TCP/UDP → IANA canon-* (registered by Canon) [checked against the IANA CSV export]
- Kyocera 1063 TCP/UDP → IANA kyoceranetdev [checked against the IANA CSV export]
- Epson ENPC 3289 TCP/UDP → IANA enpc (registered by Seiko Epson) [checked against the IANA CSV export]

#### Dropped (no readable vendor source, or out of scope)
- Alcatel-Lucent OXE NOE/IP Touch signaling ports (32512/32513, 32640): only on the ALE Business Portal (login).
- Avaya Aura Session Manager / System Manager port matrices: behind support.avaya.com login; their SIP 5060/5061 are covered by the generic SIP rows.
- Microsoft Teams Rooms: cloud-only outbound media (udp:3478-3481 to Microsoft 365), not an internal listener.
- Zoom on-prem connectors, Avigilon ACC, Hanwha/Wisenet (WAVE 7001, device ports), HikCentral, Dahua DSS, Poly phones / Group Series / RealPresence, Cisco IM and Presence, Xerox/Ricoh/Kyocera web management, HP Web Jetadmin: vendor port page not reachable (search budget exhausted, PDF downloads blocked or 403). The device web UIs of these printer brands are plain 80/443, already covered by the generic HTTP/HTTPS rows.
- udp:322 (RTSPS over UDP, listed by the Axis KB): RFC 7826 defines RTSPS as TCP 322 only, and the Axis row describes the SRTP media transport, not a UDP listener.
- IANA-only UDP twins with no use documented by the vendor or the spec (udp:1720, tcp 1719/1718, tcp 3702, udp:5357/5358, udp:8554, udp:2000, tcp 4569): left out.
- SNMP for printers: same udp:161 SNMP agent as the existing row, so no separate row.

## Mail, collaboration, enterprise apps


Vendor documentation, IETF RFCs and the IANA registry only; nothing taken from nmap-services.

Markers:
- `[checked]` = the port values were read on the vendor page (fetched with WebFetch unless noted), and the CSV row matches it.
- `[checked: search extract]` = the vendor page is JS-rendered or now redirects, so WebFetch could not read it; the port was read in that page's own text as returned by web search.
- `[checked: direct download]` = WebFetch got HTTP 403; the same public page was downloaded directly and read.
- No `[unverified]` row was kept: anything that could not be read on a vendor page was dropped.

#### Mail and collaboration
- Microsoft Exchange 2016/2019 client access 443, 80 and EdgeSync 50636 [checked] → https://learn.microsoft.com/en-us/exchange/plan-and-deploy/deployment-ref/network-ports
- Microsoft Exchange default receive connectors 717 (Outbound Proxy Frontend), 465 (Client Proxy, Transport service), 2525 (Default <Server>), 475 (Mailbox Transport Delivery) [checked] → https://learn.microsoft.com/en-us/exchange/mail-flow/connectors/receive-connectors
- Microsoft Exchange 2010 AD LDS 50389 ("Connections to this port don't use SSL"), DAG log shipping/seeding 64327 (not encrypted by default), MRS 808, RPC over HTTP 6001-6004 (firewall rules), OWA/OCS integration 5075-5077, UM worker 5065-5068, UM control 16000-17000, cluster service udp:3343 [checked] → https://learn.microsoft.com/en-us/previous-versions/office/exchange-server-2010/bb331973(v=exchg.141)
- Microsoft Exchange 2013/2016 Unified Messaging 5060/5061 (Call Router), 5062/5063 (UM service), 5065-5068 (worker process) [checked] → https://learn.microsoft.com/en-us/exchange/um-protocols-ports-and-services-exchange-2013-help
- ManageSieve 4190 [checked] → https://www.rfc-editor.org/rfc/rfc5804 (IANA "sieve", TCP only)
- MUPDATE 3905 [checked] → https://www.rfc-editor.org/rfc/rfc3656 (IANA "mupdate")
- Dovecot LMTP 24 [checked: "By general convention, LMTP is expected to listen on port 24"; IANA lists 24 only as "any private mail system"] → https://doc.dovecot.org/latest/core/config/delivery/lmtp.html
- XMPP 5222, 5269 [checked] → https://www.rfc-editor.org/rfc/rfc6120 (IANA "xmpp-client", "xmpp-server")
- HCL Domino NRPC 1352, IIOP 63148 / 63149 (60148 on Linux), Server Controller 2050 (TLS) [checked] → https://help.hcl-software.com/domino/12.0.0/admin/conf_changingatcporsslportnumber_t.html (1352 also IANA "lotusnote")
- HCL Domino REST API 8880, 8886, 8889, 8890 [checked] → https://opensource.hcltechsw.com/Domino-rest-api/topicguides/configuringPorts.html
- Zimbra 389, 5222, 7025, 7026, 7047, 7071, 7072, 7073, 7110, 7143, 7780, 7993, 7995, 8080, 8443, 9071, 10027, 10031, 10032, 11211 [checked] → https://wiki.zimbra.com/wiki/Ports (Zimbra KB 1391). Ports the page marks localhost-only (7306, 7171, 8465, 10024-10026, 10028-10030, 23232, 23233) and 7307 (removed in ZCS 7) were left out.
- Microsoft SharePoint 32843, 32844, 32845, 32846, 16500-16519, 22233-22236, 808 [checked] → https://learn.microsoft.com/en-us/sharepoint/security-for-sharepoint-server/security-hardening
- Microsoft Office Online Server 80, 443, 809 [checked] → https://learn.microsoft.com/en-us/officeonlineserver/plan-office-online-server
- Mattermost 8065 [checked, as bundled with GitLab] → https://docs.gitlab.com/administration/package_information/defaults/

#### Microsoft infrastructure applications
- SCOM 5723, 5724, 1270, 8886 (OMED), 51905, 51906, 51907, 51909 [checked] → https://learn.microsoft.com/en-us/system-center/scom/plan-security-config-firewall (5723 / 5724 / 1270 also IANA "omhs", "omsdk", "opsmgr")
- SCVMM 8100, 8101, 8102, 8103, BITS 443 [checked] → https://learn.microsoft.com/en-us/system-center/vmm/plan-ports-protocols
- MSMQ 1801 TCP/UDP, 2101, 2103, 2105, 2107, udp:3527 [checked] → https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/service-overview-and-network-port-requirements
- Dynamics 365 Business Central 7045 (v21 only), 7046 (v20 and earlier), 7047, 7048, 7049, 7083, 7085, 7086 [checked] → https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/server-instance-settings
- Dynamics AX AOS 2712 [checked: IANA "aocp", Axapta Object Communication Protocol] → https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- AD CS NDES 443 [checked: "allow TCP traffic on port 443 ... to the NDES service"] and 80 [checked: the page's test URL is http://Server_FQDN/certsrv/mscep/mscep.dll, no explicit port] → https://learn.microsoft.com/en-us/intune/fundamentals/certificates/scep-infrastructure ; Web Enrollment and Certificate Enrollment Web Service over HTTP / HTTPS ("We recommend enabling EPA and disabling HTTP") → https://support.microsoft.com/en-us/topic/kb5005413-mitigating-ntlm-relay-attacks-on-active-directory-certificate-services-ad-cs-3612b773-4043-4aa9-b23d-b87910cd3429

#### Citrix
- Delivery Controller XML Service 80 / 443 [checked: "By default, the XML Service on the Controller listens on port 80 for HTTP traffic and port 443 for HTTPS traffic"] → https://docs.citrix.com/us/en/citrix-virtual-apps-desktops/current-release/secure/tls-ddc.html
- VDA registration 80, ICA over TLS 443, EDT udp:443, HTML5 ICA proxy 8008, telemetry 7502 (Controller side) / 7503 (VDA side), HDX Screen Sharing 52525-52624, HDX Direct udp:55000-55250, session shadowing 6001-6099 [checked] → https://docs.citrix.com/en-us/linux-virtual-delivery-agent/current-release/configure/administration/network-port-matrix
- EDT udp:1494 and udp:2598, Local Host Cache 89, orchestration 9095, License Administration Console 8082, Web Services for Licensing 8083 [checked: search extract; the 7.15 LTSR page now redirects to the Citrix home page] → https://docs.citrix.com/en-us/xenapp-and-xendesktop/7-15-ltsr/technical-overview/default-network-ports
- License server 27000, 7279, 8082, 8083 [checked: "Port 27000, 7279, 8082 and 8083 are required to connect to Citrix license server"] → https://support.citrix.com/external/article/CTX263623/citrix-licensing-studio-unable-to-connec.html ; roles of 27000 (License Server Manager) and 7279 (vendor daemon) [checked: search extract] → https://docs.citrix.com/en-us/licensing/current-release/manage/change-port-numbers.html ; 7279 also IANA "ctxlic"
- StoreFront 808 [checked: "confirm that all StoreFront servers are listening on port 808"] → https://support.citrix.com/external/article/CTX206872/troubleshooting-storefront-propagation-i.html (subscription synchronization purpose from the Citrix blog post "StoreFront synchronization VIP", search extract)
- Provisioning 6890-6909 TCP and UDP, udp:6910-6930, udp:6901 / 6902 / 6905 [checked] → https://docs.citrix.com/us/en/provisioning/current-release/system-requirements.html

#### Omnissa (VMware) Horizon, App Volumes, Access
- Connection Server 443, 389, 4001, 4002, 4100, 4101, 32111, 9427, Cloud Pod Architecture 22389 / 22636 / 8472; Unified Access Gateway 443, udp:443, udp:8443, 9443; Blast udp:22443; Recording Server 9443; Edge Gateway 31883; App Volumes Manager 443 / 80, 3001-3004, 54311; Omnissa Access 7443, 5262, 88 TCP/UDP, 8443, 8200, 5701, 40002-40003, 9300, udp:54328, 9400; Log Insight 9543 [checked: direct download] → https://techzone.omnissa.com/resource/network-ports-horizon-8
- PCoIP 4173 and udp:4173-4182 on virtual desktops, Blast udp:22443 [checked: direct download] → https://docs.omnissa.com/Horizon-Security/FirewallRulesforHorizonAgent
- Cloud Pod Architecture 8472 is HTTPS (cleartext column) [checked: search extract] → https://docs.omnissa.com/bundle/Horizon-Cloud-Pod-Architecture/page/CloudPodArchitecturePortRequirementsinHorizon8.html

#### Atlassian
- Jira 8080, Ehcache 40001 / 40011; Confluence 8090, Synchrony 8091, Hazelcast 5801 / 5701, cluster base 25500, multicast 54327; Bitbucket search 7992 / 7993, Hazelcast 5701; Bamboo 54663 / 54664, internal node communication 9090; Crowd 8095; Fisheye / Crucible 8060; Tomcat control port 8000 [checked] → https://support.atlassian.com/atlassian-knowledge-base/kb/ports-used-by-atlassian-data-center-applications/ (Bamboo 54665 left out: localhost only)

#### GitLab
- Gitaly 8075 / 9999 (TLS), Praefect 2305 / 3305 (TLS), Registry 5050 / 5000 / exporter 5001, KAS 8150, Patroni 8008, PgBouncer 6432, Mattermost 8065, NGINX status 8060, exporters 9168 / 9121 / 9187 / 9188 / 8082 / 8083 / 9236 / 9229, Sidekiq health check 8092, Workhorse 8181, Puma 8080, Geo PostgreSQL 5431 [checked] → https://docs.gitlab.com/administration/package_information/defaults/ (6432 also IANA "pgbouncer")

#### SAP
- ICM HTTP 80NN, ICM HTTPS 443NN, message server HTTP 81NN / HTTPS 444NN, ICM SMTP 25 (not active by default), start service 5NN13 / 5NN14 (rows for instances 00 and 01) [checked] → https://help.sap.com/saphelp_em700_ehp01/helpdata/en/42/db8c45e873162ee10000000a1553f7/content.htm
- SAProuter 3299 [checked: "The default value for service is "3299""] → https://support.sap.com/en/tools/connectivity-tools/saprouter.html
- SAP Host Agent 1128 / 1129 [checked: IANA "saphostctrl" / "saphostctrls", SAPHostControl over SOAP/HTTP and SOAP/HTTPS] ; BusinessObjects 6400 / 6410 [checked: IANA "boe-cms" / "boe-resssvr4", assignee SAP] → https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml

#### Oracle and Java
- WebLogic managed server 7003, Node Manager 5556, Oracle HTTP Server 7777 / 8888 and 4443, Business Activity Monitoring 9001, Data Integrator 15000 [checked] → https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/asadm/port-numbers.html
- Oracle Coherence 7574 TCP and udp:7574 [checked: IANA "coherence" / "coherence-disc", assignee Oracle]
- Java RMI registry 1099 [checked: IANA "rmiregistry"]

#### IBM
- WebSphere Application Server 9.0 defaults (application server, deployment manager and node agent tables), IBM HTTP Server 80 and its administration port 8008 [checked] → https://www.ibm.com/docs/en/SSAW57_9.0.5/com.ibm.websphere.migration.nd.doc/ae/rmig_portnumber.html ("Node Multicast Discovery Address" 5000 entered as UDP because it is multicast; the page gives no protocol. "Node IPV6 Discovery Address" 5001 left out for that reason.)
- IBM MQ 1414 [checked: IANA "ibm-mqseries"]

#### Red Hat WildFly / JBoss EAP
- http 8080, https 8443, management-https 9993, iiop 3528 / 3529, jgroups-tcp 7600, jgroups-udp 55200 with multicast 45688, jgroups-mping multicast 45700, modcluster multicast 23364, txn-recovery-environment 4712, txn-status-manager 4713 [checked] → https://docs.redhat.com/en/documentation/red_hat_jboss_enterprise_application_platform/7.4/html/configuration_guide/network_and_port_configuration
- Native management 9999 [checked: "By default, it runs on port 9999"] → https://docs.jboss.org/author/display/WFLY9/Admin%20Guide.html

#### Apache Tomcat
- Cluster replication receiver 4000-4100 and membership multicast 228.0.0.4:45564, not encrypted by default [checked] → https://tomcat.apache.org/tomcat-10.1-doc/cluster-howto.html
- HTTPS connector 8443 (commented out by default) [checked] → https://github.com/apache/tomcat/blob/main/conf/server.xml

#### IT asset management
- GLPI Agent 62354 [checked: "The default is 62354"] → https://glpi-agent.readthedocs.io/en/latest/configuration.html

## Storage, SAN/NAS, Linux/Unix infrastructure


Vendor documentation, IETF RFCs and the IANA registry only; nothing taken from nmap-services.

Markers:
- `[checked]` = the port was read on the vendor page (fetched with WebFetch or curl), and the CSV row matches it.
- `[checked: IANA]` = read in the IANA service-names-port-numbers CSV export (https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv, fetched 2026-11-04). The assignee is named when it is the vendor.
- `[checked: search extract]` = the vendor page's own text was read in web search results; the page itself could not be fetched (reason given).
- No row in the CSV is `[unverified]`. Products that could not be verified were dropped (see the end of this file).

#### Storage and SAN protocols (vendor-neutral)
- iSNS 3205, FCIP 3225, NFS over RDMA 20049 (RFC 8267) [checked: IANA, RFCs named on the rows] → https://www.rfc-editor.org/rfc/rfc4171 , https://www.rfc-editor.org/rfc/rfc3821 , https://www.rfc-editor.org/rfc/rfc8267
- NVMe/TCP 4420 (I/O) and 8009 (discovery) [checked: IANA "nvme" and "nvme-disc", assignee NVM Express Inc]
- NFS mountd 20048 [checked: IANA "mountd"] and [checked] → https://raw.githubusercontent.com/firewalld/firewalld/main/config/services/mountd.xml (firewalld's mountd service: 20048 TCP/UDP)
- RoCEv2 udp:4791 [checked: IANA "roce", assignee InfiniBand Trade Association]
- SMB Direct over iWARP 5445 [checked: IANA "smbdirect", assignee Microsoft]. The Microsoft SMB Direct page (https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-direct) does not give the port.
- WBEM CIM-XML 5988/5989 (SMI-S providers) [checked: IANA "wbem-http" / "wbem-https"]
- NDMP over TLS 30000 [checked: IANA "ndmps"], also listed by NetApp ONTAP (below)
- NFS lock manager 4045 [checked] → NetApp ONTAP and Synology port pages below (IANA registers 4045 to an unrelated service)

#### NetApp
- ONTAP 443 (System Manager / cluster management LIF), 635 mountd, 2050 NRV, 4045 NLM, 4046 NSM, udp:4049 rquotad, 30000 NDMP over TLS [checked] → https://docs.netapp.com/us-en/ontap/networking/ontap_port_usage_on_a_storage_system_overview.html (fetched with curl; WebFetch gets 403). SnapMirror 11104/11105 already in port_labels.csv and confirmed on the same page.

#### Dell
- PowerStore 443, 26 (SSH redirect target), 3261 data mobility, 8443 VASA, NAS 2000 SSHD, 1234 mountd, 4000 statd, 4001 NLM, 4002 rquotad, 4658 PAX, 8888 RCPD, 10500-10531 NDMP, 12228 CAVA [checked] → PowerStore Security Configuration Guide, "Appliance network ports" and "Appliance network ports related to file" tables, https://dl.dell.com/topicspdf/pwrstr-scg_en-us.pdf
- Unity 443, 1234, 4000-4002, 4658, 5085, 5086 (OE 5.5+), 8888, 12228 [checked] → https://www.dell.com/support/kbdoc/en-us/000068506/dell-emc-unity-network-ports-list and https://www.dell.com/support/kbdoc/en-us/000009368/unity-the-network-tcp-ports-for-unity-replication-customer-correctable
- Data Domain 2051 (replication / DD Boost), 2052 (mountd / DD Boost), 3008 (RSS) [checked] → https://www.dell.com/support/kbdoc/en-us/000004184/port-requirements-for-allowing-access-to-a-data-domain-through-a-firewall (3009 already in port_labels.csv, same page)
- Unisphere for PowerMax 8443 [checked: search extract] → https://www.dell.com/support/kbdoc/en-us/000052016 (KB text, "Unisphere requires exclusive use of 8443 for HTTPS and 3324 for SMAS_DB", read in search results; the KB page now requires a Dell sign-in)
- Solutions Enabler 2707 [checked: IANA "emcsymapiport"; no Dell page read]

#### HPE
- 3PAR 5781 events, 5782 management (plain), 5783 management (SSL), 5785 Remote Copy [checked: IANA "3par-evts", "3par-mgmt", "3par-mgmt-ssl", "3par-rcopy"]
- 3PAR WSAPI 8080 [checked] → https://github.com/hpe-storage/python-3parclient/blob/master/hpe3parclient/client.py (HPE's client: "http://<3par server>:8080/api/v1")
- Nimble 5392 REST API [checked] → https://github.com/hpe-storage/nimble-python-sdk/blob/master/nimbleclient/v1/restclient.py (HPE SDK default port=5392)

#### Pure Storage
- 8117 purityrpc (replication, clustering, remote management) [checked: IANA, assignee Pure_Storage]

#### Hitachi Vantara
- VSP SVP / Storage Navigator 443, RMI 1099, 51099, 51100-51355; Ops Center Administrator 20961 [checked] → https://docs.hitachivantara.com/r/en-us/mk-99adm000/latest/hitachi-ops-center-administrator-environment/port-requirements
- Hitachi Command Suite / Ops Center common component 22015 (HTTP), 22016 (HTTPS) [checked] → https://itpfdoc.hitachi.co.jp/manuals/3021/30219008F0/DMSJ0070.HTM (Hitachi, Japanese)

#### Broadcom (Brocade)
- SANnav Management Portal 443, Kafka 19092 and 19094 (TLS) [checked] → https://docs.broadcom.com/htmldocs/SANnav111/SANnav111/v25436141.html ; telemetry port list also in https://support.broadcom.com/web/ecx/support-content-notification/-/external/content/SecurityAdvisories/0/23286 (BSA-2024-2577)

#### NAS appliances
- Synology Assistant udp:9997-9999, Active Backup for Business 5510, Hyper Backup Vault 6281, WebDAV 5005/5006, Snapshot Replication 5566, Synology Drive 6690, NFS statd 662 / mountd 892 / lockd 4045, High Availability 7400-7999 [checked] → https://kb.synology.com/en-global/DSM/tutorial/What_network_ports_are_used_by_Synology_services (table read in the page's embedded HTML)
- QNAP 443 web admin, RTRR 8899, SnapSync 874-875, Qfinder udp:8097, Telnet 13131, Q'center 6600, QuWAN 7788 [checked] → https://www.qnap.com/en/how-to/faq/article/what-network-ports-are-used-by-qts-quts-hero-and-qutscloud-systems
- TrueNAS 443 [checked] → https://www.truenas.com/docs/solutions/optimizations/security/ ("TrueNAS Default Ports")

#### Software-defined storage
- Ceph RGW 7480 [checked] → https://docs.ceph.com/en/latest/radosgw/config-ref/ (rgw_frontends default "beast port=7480"); Dashboard 8443 / 8080 without SSL [checked] → https://docs.ceph.com/en/latest/mgr/dashboard/ ; mgr Prometheus 9283 [checked] → https://docs.ceph.com/en/latest/mgr/prometheus/ . Existing rows 3300, 6789, 6800-7568 re-confirmed (unchanged).
- GlusterFS bricks 49152-49251, Gluster NFS 38465-38469 [checked] → https://docs.redhat.com/en/documentation/red_hat_gluster_storage/3.1/html/administration_guide/chap-getting_started (brick range scales with bricks per node)
- DRBD 7788-7799 [checked] → https://kb.linbit.com/generic-linux-tips/configure-firewalld-for-pacemaker-drbd-and-linstor/ and https://documentation.suse.com/sle-ha/15-SP6/html/SLE-HA-all/cha-ha-drbd.html ("TCP ports 7788 and higher")
- LINSTOR 3370, 3376, 3366, DRBD range 7000-7999 [checked] → same LINBIT KB ; 3371 HTTPS [checked] → https://linbit.com/?p=30234 (LINBIT "Security Best Practices For LINSTOR")
- IBM Storage Scale (GPFS) 1191 [checked] → https://www.ibm.com/docs/en/storage-scale/5.1.9?topic=reference-mmchconfig-command (tscTcpPort, default 1191) and IANA "gpfs"

#### Linux / Unix administration
- Cockpit 9090, HTTP redirected to HTTPS [checked] → https://docs.cockpit-project.org/cockpit-guide/latest/guide/listen.html and https://docs.cockpit-project.org/cockpit-guide/latest/guide/https.html
- Webmin 10000 [checked] → https://webmin.com/faq/ ; Usermin 20000 [checked] → https://webmin.com/usermin/
- IBM AIX WebSM 9090 [checked: IANA "websm"]
- Pacemaker / Corosync: pcsd 2224, Pacemaker Remote 3121, corosync-qnetd 5403, corosync udp:5404-5412, DLM 21064, Booth 9929 [checked] → https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_high_availability_clusters/assembly_creating-high-availability-cluster-configuring-and-managing-high-availability-clusters ("Ports to enable for High Availability Add-On"); 3121 also IANA "pcmk-remote"
- Red Hat Ansible Automation Platform 443, receptor 27199 [checked] → https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.4/html/red_hat_ansible_automation_platform_planning_guide/ref-network-ports-protocols_planning
- Chef Infra Server 443, 9683 [checked] → https://docs.chef.io/server/server_firewalls_and_ports/
- Foreman / Satellite 443, 8000, 9090, 9191 (Salt API), 1883 (pull REX), 5910-5930, ISC DHCP OMAPI 7911 [checked] → https://docs.theforeman.org/nightly/Planning_for_Project/index-katello.html (port and firewall requirements) ; Satellite 5647 (katello-agent firewall-cmd example) [checked] → https://docs.redhat.com/en/documentation/red_hat_satellite/6.11/html-single/installing_satellite_server_in_a_connected_network_environment/index
- Uyuni / SUSE Manager 443, proxy 8022, JMX exporters 5556/5557 [checked] → https://www.uyuni-project.org/uyuni-docs/en/uyuni/installation-and-upgrade/network-requirements.html (Salt 4505/4506 already in port_labels.csv)
- FreeIPA / Red Hat IdM 443, Dogtag pki-tomcat 8080/8443 (internal, keep blocked) [checked] → https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/installing_identity_management/preparing-the-system-for-ipa-server-installation_installing-identity-management ("Port requirements for IdM")
- MIT Kerberos kadmind 749 [checked] → https://web.mit.edu/kerberos/krb5-latest/doc/admin/conf_files/kdc_conf.html ; kpropd 754 [checked] → https://web.mit.edu/kerberos/krb5-latest/doc/admin/admin_commands/kpropd.html
- Samba SWAT 901 [checked] → https://www.samba.org/samba/docs/old/Samba3-HOWTO/SWAT.html ; CTDB 4379 [checked: IANA "ctdb"]
- Network UPS Tools 3493 [checked] → https://networkupstools.org/docs/man/upsd.conf.html and IANA "nut"
- inetd / xinetd simple services: echo 7, daytime 13, chargen 19, finger 79, ident 113 [checked: IANA, RFCs named on the rows] ; CVS pserver 2401, Amanda 10080 [checked: IANA "cvspserver", "amanda"]

#### Time, DHCP, DNS, proxies
- PTP udp:319/320 [checked: IANA "ptp-event" / "ptp-general"; protocol is IEEE 1588]
- NTS-KE 4460 [checked] → https://www.rfc-editor.org/rfc/rfc8915 and https://chrony-project.org/doc/4.6/chrony.conf.html (ntsport default 4460)
- chrony command port udp:323 [checked] → https://chrony-project.org/doc/4.6/chrony.conf.html (cmdport default 323)
- ISC dhcpd failover 647 [checked] → https://kb.isc.org/docs/isc-dhcp-44-manual-pages-dhcpdconf ("IANA assigned port number 647 will be used by default") ; 847 [checked: IANA "dhcp-failover2"]
- ISC Kea Control Agent 8000 [checked] → https://kea.readthedocs.io/en/kea-2.6.0/arm/agent.html (default http://127.0.0.1:8000/, plain HTTP unless TLS is configured)
- BIND rndc 953 [checked] → https://bind9.readthedocs.io/en/latest/reference.html ("If no port is specified, port 953 is used"; HMAC-authenticated, not encrypted)
- PowerDNS Authoritative 8081 [checked] → https://doc.powerdns.com/authoritative/settings.html (webserver-port) ; Recursor 8082 [checked] → https://doc.powerdns.com/recursor/yamlsettings.html (webservice.port)
- Unbound control 8953, TLS on by default [checked] → https://unbound.docs.nlnetlabs.nl/en/latest/manpages/unbound.conf.html
- Squid 3128 [checked] → https://www.squid-cache.org/Doc/config/http_port/ ; ICP udp:3130 [checked] → https://www.squid-cache.org/Doc/config/icp_port/
- HAProxy Data Plane API 5555 [checked] → https://www.haproxy.com/documentation/haproxy-data-plane-api/installation/install-on-haproxy/ ; stats page 8404 (HAProxy's documented example; there is no built-in default stats port) [checked] → https://www.haproxy.com/documentation/haproxy-configuration-tutorials/alerts-and-monitoring/statistics/

#### IBM Power, AIX, z/OS
- HMC 443, 12443, 9960, 5250 console 2300/2301, udp:9900, 9920, eBMC 17443, FSP 30000-30001, RSCT RMC 657 TCP/UDP, RSCT peer domains udp:12347-12348 [checked] → https://www.ibm.com/support/pages/hmc-firewall-information
- AIX NIM 1058 (nimesis) / 1059 (nimreg) [checked] → https://ibm.com/docs/en/ssw_aix_73/n_commands/niminit.html ; nimsh 3901 / nimaux 3902 [checked: IANA "nimsh" / "nimaux"] (IBM's own NIM firewall technote, https://www.ibm.com/support/pages/nim-communication-within-firewall-environment, now returns 404)
- z/OS TN3270E 23 (basic) and 992 (SECUREPORT) [checked] → https://www.ibm.com/support/pages/how-can-i-use-telnet-multiple-port-support-enable-combination-secure-and-non-secure-traffic and https://www.ibm.com/support/pages/node/6453635 ; RFC 2355, IANA "telnets" 992

#### Dropped (not verified or no fixed port)
- Varnish 6081/6082: the current varnishd reference (https://www.varnish.org/docs/reference/varnishd/) gives no default -T port, and -a now defaults to :80.
- Dell PowerScale / Isilon OneFS (WebUI 8080, SyncIQ, statd/lockd): the Dell InfoHub pages redirect to a JS-only landing page; no Dell page could be read.
- HPE SSMC 8443, Primera WSAPI 443: only HPE Community posts and Veeam pages.
- Brocade Fabric OS switch ports (RPC 897/898 etc.) and Cisco MDS / NDFC: no vendor page found before the web-search budget ran out.
- FreeIPA 7389 (domain level 0 Dogtag LDAP): not in the RHEL 7 or RHEL 9 IdM port tables.
- IBM Storage Scale GUI / performance monitoring ports: no IBM page found.
- Spacewalk / Satellite 5 osad (5222/5269): no source found (product is EOL).
- Pure Storage management 443, Solaris SMC 898: no public vendor page (898 is not in IANA).
- No port: Keepalived/VRRP (IP protocol 112), NIS/YP and Linux statd/lockd (dynamic via rpcbind unless pinned), SSSD (client only), Nginx/Apache admin pages (URL paths on 80/443), NetApp SP/BMC (SSH 22), NFSv4.1 (2049 only, already listed). CUPS skipped (print family).
- Verified rows first cut to stay near 160 are now restored in storage-unix-extra.csv (see below): udp:3205, iFCP 3420, qotd 17, time 37, discard 9, klogin 543, kshell 544, Hitachi 11099 and 5443, SANnav 19095 and 18081-18082, QNAP 38898-38899 and 16500-16550, Synology 3261, Chef 4321/8000/9463, Uyuni 9800, Satellite 5646, HMC PowerSC 11125, Webmin 10001-10010, Ceph 9284, oVirt VDSM 54321, Squid HTCP udp:4827 and SNMP udp:3401, plus the UDP twins udp:635, udp:4046, udp:4045, udp:20048, udp:9929.

#### storage-unix-extra.csv (86 rows: the 30 restored rows, 14 UDP twins, 42 more verified rows)
All of these come from pages already read for storage-unix.csv; no new search was run. udp:12348 is not restored on its own: the kept row udp:12347-12348 covers it.
- Restored rows: their sources are the bullets above (same product, same page). The one exception: Hitachi SVP RMI class loader SSL 5443 [checked: search extract] → Hitachi Vantara SVP pages ("RMIClassLoaderHttps 5443", "RMI (SSL) 5443"), read in search results. https://knowledge.hitachivantara.com/Documents/Storage/SVP/Service_Processor/SVP1_and_SVP2_Installation_and_Maintenance/14_Changing_and_initializing_SVP_port_numbers now returns 404.
- Restored 9 discard, 17 qotd, 37 time [checked: IANA, RFCs named on the rows] ; 543 klogin, 544 kshell, 3420 iFCP, udp:3205 iSNS [checked: IANA]
- UDP twins, documented TCP/UDP by the vendor: Dell udp:1234, udp:4000, udp:4001, udp:4002 → PowerStore Security Configuration Guide and the Unity network ports KB (above) ; Synology udp:662, udp:892 → Synology KB "NFS ... TCP/UDP" ; QNAP udp:874-875 SnapSync, udp:6600 Q'center → QNAP ports FAQ ; IBM udp:9920 ("9920 tcp/udp" in the example configuration), udp:11125 PowerSC → IBM HMC firewall information page
- UDP twins defined by the RFC: udp:9 (RFC 863), udp:13 (RFC 867), udp:17 (RFC 865), udp:37 (RFC 868) [checked: IANA udp entries]
- NetApp udp:4444 krb524 [checked] → ONTAP port usage page ("UDP 4444 KRB524") and IANA "krb524"
- Dell PowerStore XATTRPD 4003 TCP/UDP [checked] → PowerStore Security Configuration Guide
- Dell Data Domain iPerf 5001; Dell Avamar 27000, 28001, 28002, 29000 (Data Domain outbound targets) [checked] → Data Domain firewall KB 000004184 (above)
- Brocade SANnav 8081 (Avro schema registry), Kafka 29092/29094/39092/39094 [checked] → SANnav 1.1.1 firewall table (above)
- Synology Tiering Vault 30700-30701, Presto File Server 3360-3361 TCP/UDP, Virtual Machine Manager cluster network 2379-2382 and Redis 2385, Synology Contacts 5555 [checked] → Synology KB (above)
- QNAP Q'center 6606 and managed NAS 6621/6623 (TCP/UDP), Virtualization Station 3 web 8088/8089, HDP for SaaS 9045-9049, QuLog Center 1514 TCP/UDP, Qsirch 5027-5029, Web Server 8081 [checked] → QNAP ports FAQ (above)
- GlusterFS legacy bricks 24009-24108, Gluster NFS NLM 965 / udp:963, Swift object/container/account 6010-6012 and proxy 8080 on RHGS [checked] → Red Hat Gluster Storage 3.1 port tables (above)
- IBM Storage Scale tscCmdPortRange 60000-61000 (install toolkit, releases before 5.0.0) [checked] → IBM mmchconfig page (above)
- Chef Infra Server oc-id 9090, redis_lb 16379 [checked] → Chef firewalls and ports page (above)
- Foreman Discovery 8443 (Smart Proxy to discovered host) [checked] → Foreman planning guide outgoing table (above)
- Prometheus PostgreSQL exporter 9187 on Uyuni [checked] → Uyuni network requirements (above)
- Left out because the vendor table is ambiguous: Unity 5080/8000/9443 and statd 32768 / lockd 39494, NetApp udp:953 "Name daemon", Synology HA 874/1234, QNAP udp for web UIs (HTTP does not run over UDP), and UDP entries that exist only as IANA block assignments for TCP protocols (FCIP, iFCP, NVMe/TCP, WBEM, 3PAR, NUT, CTDB, GPFS, NIM, kadmin).

## Security products


Vendor documentation, IETF RFCs and the IANA registry only; nothing taken from nmap-services.

Markers:
- `[checked]` = the port values were read on the vendor page (fetched with WebFetch/curl) and the row matches it.
- `[checked via search extract]` = the vendor page refused automated fetch; the port was read in the search engine's quote of that vendor page.
- `[checked: IANA]` = read in the IANA service-names CSV export (https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv).

Note: the shared WebSearch budget ran out midway; the rest was done with WebFetch/curl on vendor URLs already known.

#### EDR / antivirus / endpoint management
- Trellix ePO agent-server 80 (HTTP), 443 (secure) [checked] → https://docs.trellix.com/bundle/trellix-epolicy-orchestrator-on-prem-5.10.0-product-guide/page/UUID-2508f8a1-2d62-3c4a-4ce3-f920a5b094b2.html and https://docs.trellix.com/docs/port-options ("legacy agents" on 80: Trellix's port-requirements page, read as a search extract, says Trellix Agent 5.x and later do not support port 80)
- Trellix Agent udp:8082 broadcast, udp:8083 RelayServer discovery for older agents [checked] → https://docs.trellix.com/docs/ports-used-by-trellix-agent-1 (8082 also in the ePO 5.10 page above)
- Trellix DXL broker 8883 [checked] → https://docs.trellix.com/docs/network-ports-and-url-allow-list (Trellix EDR page: "TCP 8883, Endpoint to DXL broker, DXL messaging"; IANA secure-mqtt)
- Trellix IPS / Network Security Platform udp:4166, udp:4167, udp:8500, 8501-8504, 8505, 8506-8510, NTBA udp:9996 and udp:9008, Logon Collector 61641 [checked] → https://docs.trellix.com/network-and-platform/docs/set-the-desktop-firewall-3 (IPS 11.1.x)
- Trellix DLP: Logon Collector 61613, Network Prevent ICAP over SSL 11344 [checked] → https://docs.trellix.com/data-and-email/docs/default-trellix-dlp-ports
- Symantec Endpoint Protection Manager 2638 (embedded DB), 2967 (GUP), 8444, 8445, 9090, 443 [checked] → https://knowledge.broadcom.com/external/article/184204/communication-ports-used-by-endpoint-pro.html ; 8446 web services [checked] → https://knowledge.broadcom.com/external/article/155708/best-practices-symantec-endpoint-protect.html . IANA agrees: 2638 sybaseanywhere, 2967 ssc-agent (Symantec System Center agent).
- Trend Micro Deep Security 4118, 4119, 4120, 4122; Smart Protection Server 5274, 5275 [checked] → https://help.deepsecurity.trendmicro.com/20_0/on-premise/communication-ports-urls-ip.html
- Trend Micro Apex One 8080, 4343 [checked] → https://success.trendmicro.com/en-US/solution/KA-0002016 (the agent listening port is a random 5-digit value chosen at install; no row)
- Bitdefender GravityZone on-premises 8443, 8080, 7074, 7075, 7076, 7077, 7081, 7083, 8444, 6150, 32002, 48652, 27017, 6379, 8887 [checked] → https://www.bitdefender.com/business/support/en/77212-376333-gravityzone-communication-ports.html (the page gives no TCP/UDP column; rows use TCP)
- WithSecure (F-Secure) Policy Manager Server 8080, 8081, 443, 80 and Policy Manager Proxy 443, 80 [checked] → https://support.withsecure.com/community/en/kb/articles/32292-what-are-the-default-ports-used-by-policy-manager-server-and-policy-manager-proxy
- ESET Bridge 3128 [checked] → https://help.eset.com/protect_install/latest/en-US/ports_used.html
- Kaspersky Security Center 8060, 8061, udp:13000, 13001, 13111, udp:15111, 17111, 17000, 17100, 19170, 13292, 13294, 13295, 13296, udp:15001 [checked] → https://support.kaspersky.com/KSC/14.2/en-US/158830.htm
- Sophos Enterprise Console 8192, 8193-8194 [checked] → http://downloads.sophos.com/readmes/readec.txt (Enterprise Console 2.0 release notes, 2006; the product is end-of-life. The "message router" naming appears only on Sophos Community, so the row does not use it)
- Sophos Firewall captive portal 8090, RADIUS SSO udp:6060, SSL VPN 8443, web proxy 3128, user portal 443 [checked] → https://docs.sophos.com/nsg/sophos-firewall/19.0/Help/en-us/webhelp/onlinehelp/AdministratorHelp/Administration/DeviceAccess/DeviceAccessLocalServiceACL/index.html (8090 served over HTTPS: "https://<device>:8090" in the Sophos docs, read as a search extract)
- Microsoft Defender for Identity sensor udp:1813 (RADIUS accounting received by the sensor) [checked] → https://learn.microsoft.com/en-us/defender-for-identity/deploy/prerequisites (sensor v2.x page; everything else there is outbound or localhost 444)
- Microsoft ATA Center 443, ATA Gateway syslog udp:514 [checked] → https://learn.microsoft.com/en-us/advanced-threat-analytics/ata-prerequisites (archived page, ATA 1.9)

#### SIEM / logging
- IBM QRadar 8000, 7800, 7801, 7803, 6543 TCP/UDP, 7789 TCP/UDP, 7676-7677, 10000 TCP/UDP (legacy), 23111, 23333 (Emulex HBAnyware), 32000-33999, 32004, 32005, 32006, 32009, 32010, 32011, udp:9995, 40799 [checked] → https://public.dhe.ibm.com/software/security/products/qradar/documents/71MR2/QNAD/EN/CommonPorts.pdf (IBM "QRadar Common Ports" technote, 7.1 MR2, 2013; old, so check against the current release). 32004 and 32000 are also in the 7.6 docs, read as a search extract → https://www.ibm.com/docs/en/qsip/7.6.0?topic=systems-adding-forwarding-destinations
- IBM QRadar WinCollect 8413 [checked] → https://www.ibm.com/support/knowledgecenter/SS42VS_SHR/com.ibm.wincollect.doc/c_ug_wincollect_comm_event_collector.html
- OpenText (Micro Focus) ArcSight ESM 8443, 9000 peering, 9443, 9090, udp:694, 7789, 3179-3182, 10000-10100; Logger 443/9000, 515, udp:8514, 8515; ArcMC 7913, 9001-9008; Event Broker / Transformation Hub 5443, 38080, 9093; Load Balancer 6702 [checked] → https://community.opentext.com/cfs-file/__key/communityserver-discussions-components-files/224/0066.ArcSight_5F00_Ports_5F00_Protocols.pdf ("ArcSight Ports and Protocols", Micro Focus, 3 October 2019, hosted on OpenText's site). IANA agrees: 694 ha-cluster.
- LogRhythm 40000, 8501, 30000-30001, 8443, 8089, 9300-9400, 8400, udp:5500, 8076 [checked] → https://docs.logrhythm.com/lrsiem/docs/networking-and-communication ("no" in the cleartext column for 40000: the 7.23 page says agent-to-Data Processor traffic is TLS, read as a search extract → https://docs.logrhythm.com/lrsiem/7.23.0/networking-and-communication)
- Splunk 8065 (app server), 8191 (KV store), 9887, 8080, 8081, 8181 (cluster replication) [checked] → https://help.splunk.com/en/splunk-enterprise/administer/inherit-a-splunk-deployment/9.0/inherited-deployment-tasks/components-and-their-relationship-with-the-network (the replication ports are the values in Splunk's table; replication_port has no fixed default)
- Wazuh udp:1514, 514 TCP/UDP syslog collector, indexer 9200 and 9300-9400 [checked] → https://documentation.wazuh.com/current/getting-started/architecture.html

#### Vulnerability scanners
- Tenable Network Monitor 8835, Security Center linked scans 8837 [checked] → https://docs.tenable.com/security-center/Content/PortRequirements.htm
- Rapid7 InsightVM / Nexpose 40814 (console to engine), 40815 (engine-to-console pairing) [checked] → https://docs.rapid7.com/insightvm/configuring-distributed-scan-engines/
- Greenbone GSA 443 (HTTPS default; 9392 is the existing fallback row) [checked] → https://github.com/greenbone/gsad/blob/main/README.md
- OpenVAS Transfer Protocol 9390 [checked: IANA "otp"]. gvmd states no default TCP port (its man page only says "-p, --port=NUMBER") → https://raw.githubusercontent.com/greenbone/gvmd/main/docs/gvmd.8

#### NAC / identity / PAM
- Cisco ISE 12001, 8671, 7800, 9060, 9062, 9002, 9063, 9070, 9993, 5701, 9644, 9300, 6379, 15672, 8080, 8444, 8445, 8449, 8084, 9090, 2560, udp:1700, udp:20514, 1468, 9094, 9095, udp:40514, 11468, 64999 (SXP), 9443, udp:9996 [checked] → https://www.cisco.com/c/en/us/td/docs/security/ise/3-3/install_guide/b_ise_installationGuide33/b_ise_InstallationGuide33_chapter_7.html (this ISE 3.3 ports chapter was readable this time; it also confirms the existing 8443, 8905 and 8910 rows)
- RADIUS over DTLS udp:2083 → RFC 7360 [checked], also listed by Cisco ISE above and IANA radsec/udp
- HPE Aruba ClearPass 6658 (OnGuard), 5433 (Insight database), 7432 (cluster diagnostics) [checked via search extract] → https://arubanetworking.hpe.com/techdocs/ClearPass/6.11/PolicyManager/Content/Deploy/About%20ClearPass/Accessing_ClearPass.htm (Akamai returns 403 to WebFetch and curl)
- Forescout eyeSight 13000, SecureConnector 10003 / 10005 / 10006, HA SSH 2222 [checked] → https://docs.forescout.com/eyesight/eyesight-install-8-5-x/eyesight-install-8-5-x/c-network-access-requirements.htm ; 2200 (Linux SecureConnector, older releases) [checked via search extract] → https://www.forescout.com/wp-content/uploads/2018/04/CounterACT_Installation_Guide_8.0-2.pdf
- Fortinet FortiNAC 4568, udp:4567, 1050, 5555, 8443, 8080, 8000, 8180, 8543 [checked] → https://docs.fortinet.com/document/fortinac/9.2.0/administration-guide/482422/open-ports
- CyberArk Vault udp:1858, Remote Control Agent 9022 [checked] → https://docs.cyberark.com/pam-self-hosted/latest/en/content/pas%20sysreq/standard%20ports%20-%20vault.htm and https://docs.cyberark.com/pam-self-hosted-legacy/latest/en/content/pas%20sysreq/network%20ports%20overview.htm ; IANA agrees: 1858 privateark, 9022 paragent ("PrivateArk Remote Agent"). **The existing row 1858 "CyberArk Vault", marked unverified in 07-demo-port-labels-sources.md, is now verified by these pages.**
- Delinea Secret Server 3390 (RDP proxy), 8443 (RDP Gateway), 8672 / 8671 (MemoryMQ) [checked] → https://docs.delinea.com/online-help/secret-server/networking/general/secret-server-ports/index.htm
- BeyondTrust passive Jump Client 5832 [checked] → https://www.beyondtrust.com/docs/archive/privileged-remote-access/22-2/pra-admin-22-2.pdf ("Passive Jump Client Port … The default port is 5832")
- HashiCorp Boundary 9200, 9201, 9202, 9203 [checked] → https://developer.hashicorp.com/boundary/docs/configuration/listener
- Teleport 3021, 3022, 3023, 3024, 3025, 3026, 3028, 3036, 3080 [checked] → https://goteleport.com/docs/reference/deployment/networking/
- RSA Authentication Manager 5550, 5555, 5580, 7002, 7022, 7072, 7082, 9786, 1812 TCP, 1813 TCP, 8443 [checked] → https://community.rsa.com/s/article/Ports-for-the-RSA-Authentication-Manager-Instance
- Duo Authentication Proxy udp:1812, 2083 (RadSec), 389 / 636 (ldap_server_auto), 80 (http_proxy) [checked] → https://duo.com/docs/authproxy-reference
- Keycloak 8080, 8443, 9000, 7800, 57800 [checked] → https://www.keycloak.org/server/all-config , https://www.keycloak.org/server/enabletls , https://www.keycloak.org/server/management-interface , https://www.keycloak.org/server/caching
- KMIP 5696 [checked: IANA "kmip", OASIS KMIP TC] (the cleartext column says "no" because the KMIP profiles require TLS)

#### Firewall management and security appliances
- Palo Alto Networks Panorama / Log Collector 28270, 9300-9302, 8765, 23000-23999 [checked] → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-panorama
- Palo Alto Networks HA 28, 28764-28767, 28770, 28771, udp:29281 [checked] → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-ha (the cell for 28 renders cut off in the fetched page; the value read is 28)
- Palo Alto Networks User-ID 5006, 5009, 6514, udp:514, 514 [checked] → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-user-id
- Fortinet FortiManager 542, 8890, udp:53, udp:9443, 6028 [checked] → https://docs.fortinet.com/document/fortigate/6.0.0/fortinet-communication-ports-and-protocols/761434/fortimanager-open-ports
- Fortinet FortiAnalyzer 3000, 8443 [checked] → https://docs.fortinet.com/document/fortigate/6.0.0/fortinet-communication-ports-and-protocols/492866/fortianalyzer-open-ports
- Fortinet FortiAuthenticator udp:720, udp:721, udp:1194, 8000, 8001, 8002-8003, 2560, 389, 636 [checked] → https://docs.fortinet.com/document/fortigate/6.0.0/fortinet-communication-ports-and-protocols/176524/fortiauthenticator-open-ports
- Fortinet FortiGate 8001 and 8013 (FortiClient connections); FortiClient EMS Chromebook 8443 [checked] → https://docs.fortinet.com/document/fortigate/6.0.0/fortinet-communication-ports-and-protocols/250063/forticlient-open-ports
- Fortinet FortiSandbox 11344 [checked] → https://docs.fortinet.com/document/fortigate/6.0.0/fortinet-communication-ports-and-protocols/558306/fortisandbox-open-ports
- Check Point 18184 OPSEC LEA, 18187 OPSEC ELA, udp:8116 cp-cluster [checked: IANA]; 18184 also in the LogRhythm and ArcSight pages above. 18210 [checked: ArcSight Ports and Protocols PDF, "pull OPSEC SSL certificate"]. Check Point's own sk52421 still needs a login.
- Cisco Secure Firewall Management Center eStreamer 8302 [checked] → ArcSight Ports and Protocols PDF ("SSL connection for the Defense Center eStreamer protocol") and https://docs.logrhythm.com/lrsiem/docs/networking-and-communication . Cisco's own https://docs.manage.security.cisco.com/c_communication_port_requirements.html lists only 8305.
- ICAP 1344 → RFC 3507 [checked] and IANA icap

#### Dropped (no vendor page could be read; not guessed)
- Stormshield SNS 1300/1301: no Stormshield page reachable without search (IANA 1300 = H.323 secure call signalling).
- WatchGuard 4105/4117/4118: the help-center ports page was not found (every guessed URL returned 404).
- SonicWall, Barracuda, Imperva, F5 ASM (my.f5.com K13250 renders only through JavaScript), Wallix Bastion, Entrust nShield: no vendor page read.
- Thales Luna 1792 (NTLS): the thalesdocs pages fetched never state the port, and IANA 1792 = ibm-dt-2. YubiHSM connector 12345: the developers.yubico.com page gives no default.
- Cortex XDR Broker VM, SentinelOne on-prem (documentation behind a login), Tanium (help.tanium.com did not render).
- Okta AD/RADIUS agents, Microsoft Entra Connect / pass-through agent, Qualys scanner appliance, Nessus Agent: outbound only, nothing listens internally.
- Sumo Logic installed collector (no fixed listening port), Graylog 5555 (no Graylog page read), ArcSight 1514 (third-party guide only), Trellix 8801 (outbound from ePO to McAfee Labs), Duo 18120 (not in Duo's documentation), gvmd 9391 (no IANA entry, no default documented).

## Network vendors, wireless, SD-WAN


Vendor documentation, IETF RFCs and the IANA registry only; nothing taken from nmap-services.
`[checked]` = port read on the page with WebFetch. `[checked via search extract]` = the page refused automated fetch (403, JS app), and the port was read in the web-search text quoted from that vendor page.

#### Standard protocols (IANA / RFC)
- LWAPP udp:12222 data, udp:12223 control [checked: RFC 5412 §3.3.1, "12222 for LWAPP data and 12223 for LWAPP control frames"] → https://www.rfc-editor.org/rfc/rfc5412.txt
- IANA-registered rows: RPKI-RTR 323/324 (RFC 6810), DHCPv6 udp:546/547 (RFC 9915), MSDP 639, DNS over QUIC/DTLS udp:853 (RFC 9250, RFC 8094), OWAMP 861 (RFC 4656), TWAMP 862 and udp:862 (RFC 5357, RFC 8545), Cisco HSRPv6 udp:2029, Cisco GLBP udp:3222, Cisco VQP udp:1589, STUN/TURN 3478 and 5349 TCP/UDP (RFC 8489, RFC 8656, RFC 7350), WS-Discovery udp:3702, altserviceboot udp:4011 (PXE), BFD echo udp:3785 (RFC 5881), BFD on LAG udp:6784 (RFC 7130), S-BFD udp:7784 (RFC 7881), LSP ping udp:3503 (RFC 8029), LISP udp:4341/4342 (RFC 9300/9301), PCEP 4189 (RFC 5440), IPFIX 4739 TCP/SCTP and 4740 TCP/UDP, IKE/IPsec over TCP 4500 (RFC 9329), NETCONF Call Home 4334/4335 (RFC 8071), OVSDB 6640 (RFC 7047), gNMI/gNOI 9339, Silver Peak 4163/4164 TCP [checked against the IANA CSV export] → https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- The HSRPv6, GLBP, VQP and Silver Peak rows are IANA-only: no vendor page could be read for them (web search budget ran out).

#### Cisco
- Catalyst SD-WAN udp:12346-12445 (base 12346, port hopping 12346/12366/12386/12406/12426 + offset 0-19), udp:12446-13046 and 23456-24156 (per-core DTLS/TLS), cluster ports 7600, 57600, 8553, 50051, 10502-10503 [checked] → https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/cisco-sd-wan-overlay-network-bringup.html ("Firewall Ports for Cisco Catalyst SD-WAN Deployments"; the GUI is 443, 8443 is a cluster port only)
- Catalyst 9800 mobility udp:16666 control, udp:16667 data [checked] → https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/221707-configure-9800-wireless-lan-controller-m.html ; control-plane encryption always on, data encryption optional [checked] → https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/213913-building-mobility-tunnels-on-catalyst-98.html
- Catalyst Center 2222, 9004, udp:6007, 9991, udp:21730, 25103, 32626, plus NMSP 16113 (WLC to MSE / Spectrum Expert) [checked] → https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/2-3-7/install_guide/b_cisco_catalyst_center_install_guide_237x_3rdgen/m_plan_deployment_2_x_x_3rdgen.html
- Prime Infrastructure HA 8082, 1522, 8085 [checked] → https://www.cisco.com/c/en/us/td/docs/net_mgmt/prime/infrastructure/3-10/admin/cisco_prime_infrastructure_3_10_admin_guide/configure_high_availability.html
- IOS XR gRPC 57400 [checked: "The port number ranges from 57344 to 57999. The default port is 57400."] → https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/programmability/b-programmability-configuration-guide-cisco8000/m-grpc-fundamentals-and-authentication.html
- NX-OS gRPC 50051 [checked: "50051 is the default"] → https://www.cisco.com/c/en/us/td/docs/dcn/nx-os/nexus9000/106x/programmability/cisco-nexus-9000-series-nx-os-programmability-guide-106x/m-grpc-agent.html
- IOS XE gNMI 50052 insecure (9339 secure) [checked] → https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b-1718-programmability-cg/gnmi.html

#### Other routing and switching vendors
- Nokia SR OS gRPC 57400 [checked] → https://documentation.nokia.com/sr/24-7/7x50-shared/system-management/grpc.html ; SR Linux 57400 [checked] → https://documentation.nokia.com/srlinux/24-3/books/config-basics/management-servers.html
- Arista EOS gNMI 6030 [checked] → https://aristanetworks.github.io/openmgmt/configuration/openconfig
- Arista CloudVision TerminAttr 9910 [checked via search extract] → https://avd.arista.com/4.4/roles/eos_cli_config_gen/docs/input-variables.html (on-prem CloudVision on TCP 9910) and https://www.arista.com/en/support/advisories-notices/security-advisory/12166-security-advisory-62 (restrict inbound TCP 9910)
- Arista MLAG 4432 TCP/UDP [checked via search extract: Arista EOS Central "Default Control Plane ACL Explained", "both must be permitted to destination port 'mlag' (4432)"; the EOS manual https://www.arista.com/en/um-eos/eos-multi-chassis-link-aggregation names the port 'mlag' only]
- Juniper Junos Space 7804 [checked] → https://networkingdocs.hpe.com/documentation/us/en/software/junos-space23.1/junos-space-workspaces/topics/concept/nat-configuration-overview.html (juniper.net now redirects here)
- HPE Aruba AOS-CX VSX keepalive udp:7678 [checked via search extract] → https://arubanetworking.hpe.com/techdocs/AOS-CX/10.14/HTML/vsx/Content/Chp_Pre_tra_loss/kee-con-10.htm
- MikroTik bandwidth test 2000 [checked] → http://manual.mikrotik.com/docs/7.25/diagnostics-monitoring-and-troubleshooting/bandwidth-test/ ; MAC Telnet / MAC WinBox / MAC ping udp:20561 [checked] → http://manual.mikrotik.com/docs/7.25/management-tools/mac-server/

#### Wireless
- HPE Aruba secure PAPI udp:8209 [checked via search extract] → https://arubanetworking.hpe.com/techdocs/ArubaOS-8.x-Books/Release-Notes/85/ArubaOS-8.5.0.1-Release-Notes.pdf ("secure port 8209") and https://arubanetworking.hpe.com/techdocs/CLI-Bank/Content/sd-branch/sh-fir-cp-int.htm
- HPE Aruba CPsec / Remote AP IPsec udp:4500 [checked via search extract] → https://arubanetworking.hpe.com/techdocs/ArubaOS/AOS_8x_WebHelp/Content/arubaos-solutions/external-firewallconf/fire-port-conf-arub.htm (arubanetworking.hpe.com returns 403 to fetch)
- Ubiquiti UniFi 8880-8882, 8843, 8444, 6789, udp:5514, 27117, udp:1900, 28082, udp:10101, udp:20100-22100 [checked via search extract] → https://help.ui.com/hc/en-us/articles/218506997-Required-Ports-Reference (403 to fetch)
- TP-Link Omada 8088, 8043, 8843, udp:29810, 29811-29817, udp:27001, 27217 [checked] → https://support.omadanetworks.com/au/document/13090/ (TP-Link FAQ 3281 redirects there). Dropped 19810 (OLT discovery, protocol not stated).
- Ruckus SmartZone 91, udp:12222-12223, 23232, 23233 TCP/UDP, 8443, 8022, 9997, 6868, 8090, 8099, 9080, 9443, 9998, 3333, 7000, 7800 TCP/UDP [checked] → https://docs.ruckuswireless.com/smartzone/5.1/sz100-vsze-administrator-guide/GUID-078C00BE-7543-4439-9326-F6509EA404A0.html (16567 is not on the page: dropped)

#### Load balancers, DDI, WAN optimisation, SD-WAN
- NetScaler ADC udp:3003, 3008-3011, udp:7000 (cluster) [checked] → https://docs.netscaler.com/en-us/citrix-adc/current-release/networking/access-control-lists-acls/acls-blocking-traffic-on-internal-ports.html ; HA roles (3003 heartbeat, 3008/3010 sync, 3009/3011 propagation, secure/non-secure) [checked via search extract] → https://docs.netscaler.com/us/en/citrix-adc/current-release/system/high-availability-introduction/high-availability-faqs.html ; GSLB MEP [checked: "uses TCP port 3011 or 3009"] → https://docs.netscaler.com/en-us/citrix-adc/current-release/global-server-load-balancing/configuring-metrics-exchange-protocol.html . NetScaler pages disagree on sync vs propagation per port, so the labels name both.
- F5 BIG-IP mirroring 1028 (single channel before 11.4) and 1029-1155 (per traffic group) [checked via search extract] → https://my.f5.com/manage/s/article/K14894 and https://my.f5.com/manage/s/article/K17333 (myF5 is a JS app)
- Infoblox NIOS udp:2114 key exchange, udp:1194 Grid VPN [checked via search extract] → https://docs.infoblox.com/space/nios90/319488802 ; reporting 9997 → https://docs.infoblox.com/space/nios90/1456865327 ; vNIOS AWS API proxy 8787 → https://infoblox-docs.atlassian.net/wiki/spaces/DeploymentGuidevNIOSforAWS/pages/736363674
- BlueCat 10042, udp:694 xHA heartbeat, 7788-7789, 30865 [checked] → https://docs.bluecatnetworks.com/r/Address-Manager-Administration-Guide/DNS/DHCP-Server-firewall-requirements/9.5.0 ; 10045 unencrypted vs 10046 encrypted notifications [checked via search extract, same doc set]
- Riverbed SteelHead 7744, 7800, 7801, 7810, 7820, 7850, 7860, 7870, 7881-7882 [checked] → https://support.riverbed.com/bin/support/static/lqsl3m5h2fuficj2gfmhpgfm9r/html/818s8586in61okh97e9a7vf4mq/sh-ug-html/sh_10.2.0_ug/appx-ports.html
- VMware SD-WAN (VeloCloud) VCMP udp:2426 [checked: IANA vcmp; Broadcom KB via search extract, IPsec-encrypted tunnel] → https://knowledge.broadcom.com/external/article/312353/inbound-outbound-ports-protocols-for-v.html

#### Security appliances (management and HA)
- Fortinet FortiManager 542, 8888 TCP/UDP, 8889, 8890, 8900, 5199, 300, 8080, 8082, udp:9443 [checked] → https://docs.fortinet.com/document/fortimanager/7.4.0/fortimanager-ports ; FortiAnalyzer 5199 and 8080 [checked] → https://docs.fortinet.com/document/fortianalyzer/7.4.0/fortianalyzer-ports (8900 is a FortiManager local FortiGuard port, not FortiAnalyzer)
- Palo Alto Networks HA 28, 28764-28767, 28770, 28771, udp:29281 [checked] → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-ha ; Panorama 28270, 9300-9302 [checked] → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-panorama
- Check Point 264, 18181-18184, 18202, 18205, 18208, 18210, 18211, 18221, udp:259, udp:18233, udp:18234 [checked] → https://support.checkpoint.com/results/sk/sk17745 (public, no login). This page also confirms the shipped rows 256, 257, 18190, 18191, 18192 and 18264, still marked unverified in 07-demo-port-labels-sources.md. ClusterXL CCP udp:8116 [checked: IANA cp-cluster]. 19009 dropped (not in sk17745; sk52421 needs a login).

#### Extra rows (network-extra.csv)
These were verified during the same research pass, then trimmed from network.csv for size. They are restored here, with no new searches.
- IANA-registered rows: GTP-C udp:2123 and GTP-U udp:2152 (gtp-control, gtp-user, 3GPP), Diameter 3868 TCP/SCTP (diameter; the SCTP entry cites RFC 3588, which RFC 6733 obsoletes), Diameter over TLS 5868 (diameters, RFC 6733), FCIP 3225 (fcip-port, RFC 3821), Babel udp:6696 (RFC 8966) and over DTLS udp:6699 (babel-dtls, RFC 8968), GRE-in-UDP udp:4754 (RFC 8086), MPLS-in-UDP udp:6635 (RFC 7510), VXLAN-GPE udp:4790, Silver Peak udp:4163/4164 (silverpeakpeer, silverpeakcomm), SNMP over SSH 5161/5162 (snmpssh, snmpssh-trap, RFC 5592), RESTCONF Call Home 4336 (restconf-ch-tls, RFC 8071), OWAMP test udp:861 (owamp-test, RFC 8545), gRIBI 9340 (gribi), P4Runtime 9559 (p4runtime, Open Networking Foundation), Linux-HA heartbeat udp:694 (ha-cluster) [checked against the IANA CSV export] → https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- Cisco Catalyst SD-WAN Manager cluster application server 8443 [checked: listed with 80, 443, 7600, 8080 and 57600] → https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/cisco-sd-wan-overlay-network-bringup.html
- Cisco Catalyst Center web installation API 9005 [checked: open until cluster formation completes] → https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/2-3-7/install_guide/b_cisco_catalyst_center_install_guide_237x_3rdgen/m_plan_deployment_2_x_x_3rdgen.html
- Fortinet FortiManager cascade mode 8891 and local FortiGuard antispam udp:8889 [checked] → https://docs.fortinet.com/document/fortimanager/7.4.0/fortimanager-ports
- Check Point OPSEC ELA 18187, Policy Server logon 18231, ExtraNet 18262-18263 (ExNet_PK, ExNet_Resolve) [checked] → https://support.checkpoint.com/results/sk/sk17745

## Backup, data platforms, remote access


Vendor documentation and the IANA registry only; nothing taken from nmap-services.

Markers:
- `[checked]` = the port value was read on the page during this pass (page fetched, PDF downloaded, or table parsed from the page HTML).
- `[checked: IANA]` = read in the IANA CSV export (https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv) under a service name registered by or for that vendor.
- `[checked via search extract]` = the vendor page blocks automated fetches, so the port was read in the web-search tool's quote of that page.
- `[documented example]` / `[conventional]` = the vendor shows the port in its own sample config but defines no fixed default.

#### Backup

##### Veeam
- Veeam B&R v13 port tables: 6163, 6164, 6165, 6166, 6167, 6173, 6182, 6190, 6210, 6220, 6960 (application backup repository), 11731, 33032-33036, 33050 (universal CDP agent, HTTPS) [checked] → https://helpcenter.veeam.com/docs/vbr/userguide/used_ports.html
- Veeam B&R v12 labels for the same ports, plus 6290 (guest interaction proxy control channel), 10003 (console, Cloud Connect) [checked] → https://helpcenter.veeam.com/docs/backup/vsphere/used_ports.html?ver=120
- Veeam Hyper-V Integration Service 6163 label [checked] → https://helpcenter.veeam.com/docs/backup/hyperv/used_ports.html?ver=120
- Veeam ONE 1239 (Web Services, HTTPS), 2741 (internal Web API), 2805 (Monitoring service / Analytics data collection) [checked] → https://helpcenter.veeam.com/docs/one/userguide/ports.html
- Veeam Backup for Microsoft 365 9191, 9193, 9194, 4443 (REST API / Restore Portal) [checked] → https://helpcenter.veeam.com/docs/vbo365/guide/vbo_used_ports.html
- HPE StoreOnce Catalyst 9387, 9388 [checked on the Veeam v13 page: backup server or gateway to StoreOnce on these two ports. No HPE page was read, so the rows do not say which port is command and which is data] → https://helpcenter.veeam.com/docs/vbr/userguide/used_ports.html
- Not added: 9393, 6172, 6175, 33033-33035 "(local)" (Veeam marks them local only); 2714, 2742, 2743 (Veeam ONE internal only); 10005, 10006 (on neither the v12 nor the v13 page).

##### Veritas NetBackup (docs now hosted by Cohesity, NetBackup 10.5 Network Ports Reference Guide)
- NetBackup web UI 443 (NBWMC), 13731 (smart card) [checked] → https://docs.cohesity.com/docs/netbackup/10.5/80731497-165998031-0/v145994452-165998031
- MSDP 10082 (spoold), 10102 (spad) [checked] → https://docs.cohesity.com/docs/netbackup/10.5/80731497-165998031-0/v124789758-165998031 and https://docs.cohesity.com/docs/netbackup/10.5/80731497-165998031-0/v124789605-165998031
- Legacy Web Services 8443, 8553, 8663 (HTTPS port sets) [checked] → https://docs.cohesity.com/docs/netbackup/10.5/80731497-165998031-0/v97545688-165998031
- nbfsd 7394 (GRT) [checked] → https://docs.cohesity.com/docs/netbackup/10.5/80731497-165998031-0/v124789746-165998031
- Messaging Broker 13781 (nbmqbroker) [checked] → https://docs.cohesity.com/docs/netbackup/10.5/80731497-165998031-0/v124789754-165998031
- Snapshot Manager agents 5671 [checked] → https://docs.cohesity.com/docs/netbackup/10.5/80731497-165998031-0/v167301781-165998031
- bprd 13720, bpdbm 13721, bpjava-msvc 13722, NBDB 13785 [checked: IANA, Veritas registrations]
- Not added: 56371, 56372, 5637 (only for back-level 7.7.x-8.1.2 cloud media servers).

##### Veritas Backup Exec
- 3527 and 6106 (beserver), 10000 (Agent for Windows / Linux, NDMP), 10082 and 10102 (dedup engine and manager, same rows as MSDP), 50104 (Management Service), 6103 (Agent for Windows) [checked] → https://docs.backupexec.com/us/en/backupexec-userdocs/product-guides/all-platforms/backup-exec-administrators-guide/20-0/configuration-and-settings/using-backup-exec-with-firewalls/backup-exec-ports.html
- 1125 (MSSQL$BKUPEXEC), 5633 (DBA-initiated Oracle backups) [checked] → https://docs.backupexec.com/us/en/backupexec-userdocs/product-guides/all-platforms/backup-exec-administrators-guide/20-0/configuration-and-settings/using-backup-exec-with-firewalls/backup-exec-listening-ports.html
- 3527 also [checked: IANA beserver-msg-q]
- Not added: 3106, 103x, 441 (unclear entries in the vendor table).

##### Zerto
- 4005, 4006, 4007, 4008, 4009, 9071, 9080, 9081, 9180, 9669, 9779, 9989 [checked] → https://s3.amazonaws.com/zertodownload_docs/8.5_Latest/Zerto%20Virtual%20Replication%20Zerto%20Virtual%20Manager%20(ZVM)%20-%20AWS%20Online%20Help/Content/Security_Hardening/Port_Usage.htm (Zerto's own documentation bucket, vSphere, Hyper-V and MSP tables)
- cleartext=yes on 4007/4008 rests on Zerto's own wording "unencrypted" [checked via search extract] → https://help.zerto.com/bundle/Install.ZCM.HTML.10.0_U4/page/Firewall_Considerations_in_Zerto_Cloud_Manager.htm (this page is JS-only to fetchers)
- Not added: 7073 (internal to the ZVM VM), 9072-9079 and 9082+ (Cloud Connector ranges, whose exact assignment I could not read).

##### NAKIVO
- 4443 (Director web UI), 9446 (Transporter), 9448-10000 (data transfer; the brief's "9448" is the start of this range), 9445 (Hyper-V config service), 33088-33091 (real-time replication) [checked] → https://helpcenter.nakivo.com/display/NH/Deployment+Requirements

##### Arcserve
- UDP 10 Console 8015, 6052, 6054 [checked] → https://documentation.arcserve.com/Arcserve-UDP/available/10.0/ENU/Bookshelf_Files/HTML/SolG/UDPSolnGuide/tngstn_port_comp_ms_Wind_udp_cnsl.htm
- UDP 10 RPS 8014, 5000-5060 [checked] → https://documentation.arcserve.com/Arcserve-UDP/available/10.0/ENU/Bookshelf_Files/HTML/SolG/UDPSolnGuide/tngstn_port_comp_ms_Wind_udp_rps.htm
- UDP 10 Windows Agent 8014, 4090 [checked] → https://documentation.arcserve.com/Arcserve-UDP/available/10.0/ENU/Bookshelf_Files/HTML/SolG/UDPSolnGuide/tngstn_port_comp_ms_Wind_agnt.htm
- UDP 10 Linux Backup Server 8021, 8016, 8014 [checked] → https://documentation.arcserve.com/Arcserve-UDP/available/10.0/ENU/Bookshelf_Files/HTML/SolG/UDPSolnGuide/tngstn_port_comp_lnx_bkup_srvr.htm
- UDP Appliance NAT redirects 8017, 8018, 8019, 8036, 50000-50004 [checked] → https://documentation.arcserve.com/Arcserve-UDP/Available/9.0/ENU/Bookshelf_Files/HTML/ApplUG/Content/Appliance_4_lnx_spprt.htm
- Arcserve Backup 6050 TCP/UDP, 6502, 6503, 6504, 7854, 41523, udp:41524 [checked] → https://documentation.arcserve.com/Arcserve-UDP/Available/9.0/ENU/Bookshelf_Files/HTML/ApplUG/Content/Arcserve_Backup.htm
- Not added: 8016 on Windows RPS and 8012, 8029, 8030, 18005, 18007, 7788 (Arcserve marks them internal, ignore for firewall).

##### IBM Storage Protect
- 1501 (client scheduler, prompted mode), 11090 (Operations Center HTTPS), 9028 (client management service) [checked] → https://ibm.com/support/knowledgecenter/SSEQVQ_8.1.11/srv.solutions/r_msdisk_firewall.html ; 1501 default also on https://www.ibm.com/docs/en/storage-protect/8.2.2?topic=reference-tcpclientport [checked via search extract]
- Not added: 1580 (on no IBM page; IANA gives it to an unrelated service).

##### Dell NetWorker
- 7937, 7938, 9090 (AUTHC), 9000 (NMC HTTPS), 9001 (NMC RPC), 9095, 5435 TCP/UDP (NWUI to NetWorker server), 6278/6279 (NMM), 10024, 10099, 11000 (NMM Hyper-V FLR) [checked] → https://www.dell.com/support/kbdoc/en-us/000204031/networker-processes-and-ports
- 7937/7938 and default service range 7937-9936 [checked] → https://www.dell.com/support/kbdoc/000041168
- NWUI at https://host:9090/nwui, AUTHC default 9090 [checked via search extract] → https://www.dell.com/support/kbdoc/en-us/000008992/networker-management-ui-nwui-how-to-install

##### Dell Avamar and Data Domain
- Avamar 27000, 28001, 28002, 29000; Data Domain 2051, 2052, 3008, 5001 (iPerf) [checked] → https://www.dell.com/support/kbdoc/en-us/000004184/port-requirements-for-allowing-access-to-a-data-domain-through-a-firewall
- Avamar 28001/30001 (MCS / utility node), 28002/30002 (avagent, NDMP 30002 with certificates) [checked] → https://www.dell.com/support/kbdoc/en-us/000065540/avamar-client-browsing-and-backup-issues
- Data Domain 2051/2052 also [checked] in the NetBackup DataDomain OST page → https://docs.cohesity.com/docs/netbackup/10.5/80731497-165998031-0/v124789736-165998031 (this resolves the "2051 removed" note in 07-demo-port-labels-sources.md)
- Not added: 28003+, 30003, 30102-30109 (only community posts).

##### Cohesity
- Agent 50051 [checked via search extract: the page needs a login] → https://docs.cohesity.com/baas/data-protect/dataprotect-firewall-ports.htm
- 21213 "Cohesity backup agents" [checked: IANA cohesity-agent, assignee Cohesity Inc]

##### Unitrends
- 1743, 1745-1749 (Windows), 888 (secure agent pairing) [checked] → https://helpdesk.kaseya.com/hc/en-gb/articles/4407522354449
- 1745-1844 (Linux/Unix data ports), udp:1194 (Hot Copy OpenVPN) [checked] → https://helpdesk.kaseya.com/hc/en-gb/articles/4407593650833
- 443 (Web Recovery Console) [checked] → https://helpdesk.kaseya.com/hc/en-gb/articles/4407601937553

##### Quest Rapid Recovery
- 8006 (management, agent tasks), 8009 (transfer data) [checked via search extract: support.quest.com serves a JS challenge to fetchers] → https://support.quest.com/kb/4036155/default-ports-used-by-rapid-recovery

##### Acronis
- 9876 (storage node), 9200 (catalog), 44445 (Backup Gateway), 8888 (gateway HTTPS management) [checked] → https://www.acronis.com/en/support/documentation/AcronisCyberProtect_15/network-connection-diagram.html ; 44445 also [checked: IANA acronis-backup]

##### Microsoft System Center DPM
- 5718, 5719, 6075 [checked] → https://learn.microsoft.com/en-us/system-center/dpm/configure-firewall-settings-for-dpm

##### Synology
- Active Backup for Business 5510, Hyper Backup Vault 6281, Drive Server 6690, WebDAV 5005/5006, VMM replication 5566 [checked: table read from the page's embedded content] → https://kb.synology.com/en-global/DSM/tutorial/What_network_ports_are_used_by_Synology_services

#### Databases and data platforms

##### Oracle
- EM Database Control 1158 (11g), Clusterware CSS udp:42424 [checked] → https://docs.oracle.com/cd/E11882_01/install.112/e47689/app_port.htm
- EM Cloud Control 13.5 defaults: upload 4889 HTTP / 1159 HTTPS, console 7788 HTTP / 7799 HTTPS, agent 3872, Admin Server 7101 [checked, "What Default Ports Are Used" section] → https://docs.oracle.com/en/enterprise-manager/cloud-control/enterprise-manager-cloud-control/13.5/emadv/enterprise-manager-cloud-control-advanced-installation-and-configuration-13.5.pdf ; 1158, 1159, 3872 also [checked: IANA dbcontrol-oms, oracle-oms, oem-agent]
- Not added: 7802/7803 (the guide gives ranges 7788-7798 / 7799-7809, not 7802/7803 as defaults); Data Guard (it uses the listener port, with no port of its own).

##### IBM Db2, Informix, SAP
- Db2 TLS 25100 [checked: IANA db2c-tls, assignee IBM]
- Informix 9088 (sqlexec), 9089 (sqlexec-ssl) [checked: IANA, "IBM Informix SQL Interface"]
- SAP SQL Anywhere 2638 [checked: IANA sybaseanywhere, assignee SAP]
- Db2 50000 / 25000: still unverified (https://www.ibm.com/docs/en/db2/11.5?topic=ports-default returns only a JS table of contents). No row added.

##### Others
- Neo4j 7473, 6000, 7000, 7688, 6362 (backup, 127.0.0.1 by default) [checked] → https://neo4j.com/docs/operations-manual/current/configuration/ports/
- ClickHouse 8443, 9004, 9005, 9009, 9010, 9011, 9019, 9100, 9181, 9234, 9281, 9363, 9440 [checked] → https://clickhouse.com/docs/en/guides/sre/network-ports
- CockroachDB DB Console 8080 (--http-addr default) [checked] → https://www.cockroachlabs.com/docs/stable/cockroach-start
- TiDB / TiKV / PD / TiFlash / TiCDC 4000, 10080, 20160, 20180, 2379, 2380, 3930, 20170, 20292, 8234, 8300, 12020 [checked] → https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements
- Couchbase 8092-8097, 18091-18097, 11210, 11207, 11209, 11206, 11280, 4369, 21100, 21150, 9100-9105, 19102, 9999, 9110-9118, 9120, 9123, 9124, 9130, 19130, 9140 [checked; cleartext from the page's "Unencrypted / Encrypted" lists] → https://docs.couchbase.com/server/current/install/install-ports.html
- RavenDB 8080 (ServerUrl default http://localhost:8080) [checked]; 38888 [documented example: tcp://0.0.0.0:38888, ServerUrl.Tcp has no default] → https://ravendb.net/docs/article-page/6.2/csharp/server/configuration/core-configuration
- InfluxDB 1.x 8088 (RPC backup/restore), 2003, 4242, udp:8089, udp:25826 (disabled by default) [checked] → https://docs.influxdata.com/influxdb/v1/administration/ports/
- Prometheus Pushgateway 9091, Alertmanager cluster 9094, exporters 9101, 9102, 9104, 9107, 9108, 9114, 9115, 9116, 9122, 9150, 9182, 9187 [checked] → https://github.com/prometheus/prometheus/wiki/Default-port-allocations (only exporters from the prometheus / prometheus-community projects. Third-party exporters such as redis, mongodb, kafka and oracle were left out because their vendor attribution is unclear)
- Hadoop HDFS 9866, 9864, 9865, 9867, 9868, 9869, 9871, 8485, 8480, 8481, 8019 [checked] → https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml
- Hadoop YARN 8032, 8030, 8031, 8033, 8090, 8042, 8044, 8040, 8188, 10200 [checked] → https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-common/yarn-default.xml
- Hadoop MapReduce 10020, 19888, 19890, 13562 [checked] → https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml
- Hive 10000, 10001, 10002, 9083 [checked] → https://github.com/apache/hive/blob/master/common/src/java/org/apache/hadoop/hive/conf/HiveConf.java
- Spark 8080, 8081, 6066, 4040, 18080 [checked] → https://spark.apache.org/docs/latest/security.html (7337 shuffle service is not on that page, so it was not added)
- HBase 16000, 16010, 16020, 16030, REST 8080 [checked] → https://github.com/apache/hbase/blob/master/hbase-common/src/main/resources/hbase-default.xml
- ZooKeeper AdminServer 8080, Prometheus 7000 [checked]; 2888/3888 [conventional: the admin guide's sample server.N=host:2888:3888, also HBase defaults hbase.zookeeper.peerport/leaderport] → https://zookeeper.apache.org/doc/current/zookeeperAdmin.html
- Solr embedded ZooKeeper 9983 [checked] → https://solr.apache.org/guide/solr/latest/getting-started/tutorial-solrcloud.html
- Kafka KRaft controller 9093 [checked: shipped config/server.properties] → https://github.com/apache/kafka/blob/trunk/config/server.properties ; Kafka Connect 8083 [checked] → https://github.com/apache/kafka/blob/trunk/config/connect-distributed.properties
- Confluent 8081, 8082, 8088, 9021, 8090, 9091 (9093 and 8083 also listed, merged into the Apache rows) [checked] → https://docs.confluent.io/platform/current/installation/system-requirements.html
- Redpanda 9092, 9644, 33145, 8082, 8081 [checked] → https://docs.redpanda.com/current/reference/properties/broker-properties/
- OpenSearch 9200, 9300, 5601 [checked] → https://docs.opensearch.org/latest/install-and-configure/install-opensearch/index/ ; 9600 (Performance Analyzer, removed in 3.0) [checked] → https://docs.opensearch.org/latest/tuning-your-cluster/monitoring/telemetry/performance-analyzer/
- MongoDB 27018, 27019 [checked] → https://www.mongodb.com/docs/manual/reference/default-mongodb-port/
- Redis Cluster bus 16379 [checked] → https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/
- SQL Server SSAS 2383, SSAS Browser 2382, DAC 1434/TCP [checked] → https://learn.microsoft.com/en-us/sql/sql-server/install/configure-the-windows-firewall-to-allow-sql-server-access
- PgBouncer 6432 [checked] → https://www.pgbouncer.org/config.html
- Patroni 8008 [documented example: the REST API probes use port 8008, no fixed default. The Veeam v13 HA table also lists 8008 between cluster members] → https://patroni.readthedocs.io/en/latest/rest_api.html

#### Remote access
- AnyDesk 6568, udp:50001-50003 (Discovery) [checked] → https://support.anydesk.com/docs/firewall
- NoMachine 4022 (SSH on Windows), 4443 (web, up to v8) [checked] → https://kb.nomachine.com/AR04S01122 (udp:4011-4999 is not on that page and was not added)
- Apache Guacamole web app 8080 [checked] → https://guacamole.apache.org/doc/gug/guacamole-docker.html
- TightVNC 5800 [checked] → https://www.tightvnc.com/doc/win/TightVNC_for_Windows-Installation_and_Getting_Started.pdf ; 5500 [checked] → https://www.tightvnc.com/doc/win/TightVNC_2.7_for_Windows_Server_Command-Line_Options.pdf
- Apple Remote Desktop 3283 TCP/UDP, Screen Sharing 5900 TCP/UDP, udp:5901-5902, Remote Apple Events 3031 TCP/UDP [checked] → https://support.apple.com/en-us/103229
- SolarWinds Dameware 6129, 6130, 6132, 6133, 443 (Internet Proxy) [checked] → https://documentation.solarwinds.com/en/success_center/dameware/content/install-drs-mrc-port-requirements-centralized.htm ; 6130 also [checked: IANA damewaremobgtwy]
- Intel AMT 16992, 16993, 16994, 16995 [checked: IANA amt-soap-http/https, amt-redir-tcp/tls]; 16992/16993 also on the Dameware page above
- Radmin 4899 [checked: IANA radmin-port]
- NetSupport Manager 5405 [checked: IANA netsupport] (kb.netsupportsoftware.com returned HTTP 520)
- Symantec pcAnywhere 5631, udp:5632 [checked: IANA pcanywheredata / pcanywherestat]
- ManageEngine Endpoint Central 8383/8384 [checked] → https://www.manageengine.com/products/desktop-central/changing-distribution-server-ports-in-a-remote-office-setting-how-to.html ; 8443/8444 [checked] → https://www.manageengine.com/products/desktop-central/help/tools/changing-ports-how-to.html ; 8443 chat [checked] → https://www.manageengine.com/products/desktop-central/help/tools/configuring-ports-for-chat-how-to.html ; 8031 [checked] → https://www.manageengine.com/products/desktop-central/help/server/server-port-not-reachable-kb.html
- ManageEngine ADManager Plus 8080 [checked] → https://www.manageengine.com/products/ad-manager/admanager-kb/how-to-change-admanager-plus-port-number.html
- Ivanti EPM / LANDesk 9535 (remote control), 9592 (gateway), 9593 (CBA8 agent) [checked: IANA mngsuite, ldgateway, cba8]
- Xpra 14500 [checked: IANA xpra, assignee Xpra]
- Teleport 3021, 3022, 3023, 3024, 3025, 3026, 3028, 3036, 3080 [checked] → https://goteleport.com/docs/reference/deployment/networking/

#### Dropped (no readable vendor source)
- Rubrik (12800/12801): docs need a login; only a spam page carries the numbers.
- HYCU (8443): only a DISA STIG, no HYCU page.
- Hornetsecurity / Altaro VM Backup (351xx): no vendor page found.
- Vertica (5433/5444/5450): docs moved behind a Rocket Software login.
- Teradata 1025, SAP ASE 5000: vendor docs are JS-only. IANA gives 1025/5000 to other services.
- IBM Db2 50000/25000: IBM page not readable (see above).
- Splashtop 6783-6785, BeyondTrust, RealVNC, N-able N-central: HTTP 403 to every fetch.
- Kaseya VSA 5721: help.kaseya.com unreachable. IANA 5721 is registered as "Desktop Passthru Service", not to Kaseya.
- ConnectWise Automate: docs behind a login.
- LogMeIn, Chrome Remote Desktop, Datto RMM, NinjaOne: the agents only connect outbound, and no listening port is documented.
- ManageEngine Endpoint Central 8020/8027, ServiceDesk Plus 8080: no readable ManageEngine page states them.
- Netop (IANA 1970/1971): registration may not match the product's current default, so left out.

## Risky services (tag risky)


Ports come from vendor documentation, IETF RFCs or the IANA registry. Risk reasons come from vendor security pages, CISA alerts, or NVD records (KEV = listed in CISA's Known Exploited Vulnerabilities catalog, read from the NVD API field `cisaExploitAdd`). Nothing was taken from nmap-services.

Markers:
- `[checked]` = page fetched during this pass and the port and the risk statement were read on it.
- `[convention]` = no vendor default port; the row names the port the vendor docs use in examples.
- `[unverified: …]` = no readable source; reason given.

The WebSearch budget ran out partway through, so the later pages were reached by WebFetch on known URLs only.

#### Monitoring
- Checkmk Livestatus 6557 [checked] → https://docs.checkmk.com/latest/en/ports.html (6557/TCP, optional, per site) ; risk → https://docs.checkmk.com/latest/en/livestatus.html ("Access protection is regulated exclusively via the IP addresses", the certificate "does not provide authentication", clients can issue commands to the core). Cleartext left empty: TLS is on by default in current releases.
- Munin node 4949 [checked] → https://guide.munin-monitoring.org/en/latest/reference/munin-node.conf.html (port 4949, access control is only the `allow` regex / `cidr_allow` list)
- Prometheus Pushgateway 9091, Blackbox exporter 9115, SNMP exporter 9116 [checked] → https://github.com/prometheus/prometheus/wiki/Default-port-allocations ; risk → https://prometheus.io/docs/operating/security/ (anyone with Pushgateway access "can create, modify and delete the metrics"; SNMP and Blackbox exporters "send requests to arbitrary endpoints")
- Grafana Loki 3100 → https://grafana.com/docs/loki/latest/operations/authentication/ [checked risk: "does not come with any included authentication layer"; port 3100 is the one used in that page's example, the default was not read on the config reference]

#### Kubernetes, gateways and proxies
- Kubernetes kubelet read-only 10255 [checked] → https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/ (`--read-only-port` default 10255, "with no authentication/authorization")
- Kubernetes API server insecure port 8080 [checked for 1.19] → https://github.com/kubernetes/website/blob/release-1.19/content/en/docs/concepts/security/controlling-access.md ("default is port 8080", the request "bypasses authentication and authorization modules"). Removal in 1.20 is from the release notes, not re-read.
- Helm v2 Tiller 44134 [checked] → https://v2.helm.sh/docs/securing_installation/ (default install "applies no security configurations", any process in the cluster can use the gRPC endpoint, `--listen` default :44134)
- Traefik API / dashboard 8080 [checked] → https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/ (`api.insecure`, "will expose all configuration elements, including sensitive data") and https://doc.traefik.io/traefik/reference/install-configuration/entrypoints/ ("`traefik` (port 8080)")
- Envoy admin 9901 [convention: Envoy has no default admin port, 9901 is the docs example] → https://www.envoyproxy.io/docs/envoy/latest/operations/admin [checked risk: "allows destructive operations", exposes private information, secure network only]
- Kong Admin API 8001 [checked] → https://developer.konghq.com/gateway/secure-the-admin-api/ (local interface 8001 by default, "allows full control of Kong Gateway")
- Squid 3128 [checked] → https://www.squid-cache.org/Doc/config/http_port/ ("Squid normally listens to port 3128") ; risk [checked, misconfiguration] → https://www.squid-cache.org/Doc/config/http_access/ (shipped config denies everything but localhost and keeps `http_access allow localnet` commented: the risk is a widened ACL that lets clients relay into zones they cannot reach directly)
- Weave Scope 4040 [checked] → https://github.com/weaveworks/scope/blob/master/README.md ("http://localhost:4040", "Ensure your computer is behind a firewall that blocks port 4040", the UI can "Launch a command line" in containers). Weaveworks has ceased trading; the project is archived.
- Apache Mesos master 5050 → https://mesos.apache.org/documentation/latest/authentication/ [checked risk: "Authentication is disabled by default", unauthenticated frameworks may register; port 5050 is the page's example, the default was not found on the configuration page]

#### Debug and runtime interfaces
- JDWP 5005 [checked] → https://www.jetbrains.com/help/idea/tutorial-remote-debug.html ("The default port (5005)") ; JDWP 8000 [convention: JDK has no default, 8000 is the JDK docs example] → https://docs.oracle.com/en/java/javase/21/docs/specs/jpda/conninv.html (`address=8000`, `*:8000`, `allow=*`) ; risk [checked] → https://docs.oracle.com/en/java/javase/21/docs/specs/jdwp/jdwp-protocol.html (ClassType/ObjectReference InvokeMethod, "Access control is not enforced")
- Node.js inspector 9229 [checked] → https://nodejs.org/en/learn/getting-started/debugging (default 127.0.0.1:9229, a public bind lets clients "run arbitrary code")
- Chrome DevTools Protocol 9222 [convention: no default, `--remote-debugging-port` takes any port; 9222 is the conventional one] → risk [checked] https://developer.chrome.com/blog/remote-debugging-port (attackers use remote debugging "to extract cookies"; Chrome 136+ ignores the switch for the default profile)
- PHP-FPM 9000 [checked] → https://github.com/php/php-src/blob/master/sapi/fpm/www.conf.in (`listen = 127.0.0.1:9000`, `listen.allowed_clients` default any) ; risk → https://www.php.net/manual/en/install.fpm.configuration.php ("php-fpm should not be bound to a worldwide accessible address. Otherwise, anyone could alter the PHP configuration options")
- Java RMI registry 1099 [checked] → https://docs.oracle.com/en/java/javase/21/docs/specs/man/rmiregistry.html ("started on port 1099") ; risk → https://docs.oracle.com/en/java/javase/21/management/monitoring-and-management-using-jmx-technology.html (with auth and SSL off, an MLet MBean lets a remote client "execute arbitrary code"; JMX itself has no default port)
- Jolokia JVM agent 8778 [checked] → https://jolokia.org/reference/html/manual/agents.html (port 8778, authentication only when `user` is set) and https://jolokia.org/reference/html/manual/security.html
- Flask / Werkzeug dev server 5000 [checked] → https://flask.palletsprojects.com/en/stable/server/ (localhost:5000) ; risk → https://werkzeug.palletsprojects.com/en/stable/debug/ ("allows the execution of arbitrary code", "must never be used on production machines", PIN only)
- Android Debug Bridge 5555 [checked] → https://developer.android.com/tools/adb (`adb tcpip 5555`, adb "provides access to a Unix shell")

#### AI and data science
- Ray GCS 6379, dashboard / Jobs 8265, Client 10001, dashboard agent 52365, workers 10002-19999 [checked] → https://docs.ray.io/en/latest/ray-core/configure.html ; risk → https://docs.ray.io/en/latest/ray-security/index.html ("anybody who can access the associated ports can execute arbitrary code"; token auth on by default from 2.59 for local clusters and 2.61 for all)
- MLflow 5000 [checked] → https://mlflow.org/docs/latest/api_reference/cli.html (`mlflow server` port 5000, host 127.0.0.1) ; https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/ (auth only with `--app-name basic-auth`)
- Ollama 11434 [checked] → https://docs.ollama.com/faq (binds 127.0.0.1:11434 by default, `OLLAMA_HOST=0.0.0.0` to expose, no API authentication described)
- PyTorch TorchServe management 8081 [checked] → https://github.com/pytorch/serve/blob/master/docs/configuration.md and https://github.com/pytorch/serve/blob/master/docs/management_api.md (8081, localhost by default, model archives downloaded from HTTP URLs, `allowed_urls` default all). Note https://github.com/pytorch/serve/blob/master/docs/token_authorization_api.md: current releases enforce token auth by default, and the project is no longer maintained.
- Dask scheduler 8786, dashboard 8787 [checked] → https://docs.dask.org/en/stable/deploying-cli.html ; risk → https://distributed.dask.org/en/stable/tls.html (default `tcp` is "unauthenticated and unencrypted")
- H2O 54321 [checked] → https://docs.h2o.ai/h2o/latest-stable/h2o-docs/security.html (web port 54321; security is enabled only by explicit options)
- Langflow 7860 [checked] → https://docs.langflow.org/api-keys-and-authentication (http://localhost:7860; auto-login now off by default in official releases) ; https://nvd.nist.gov/vuln/detail/CVE-2025-3248 (unauthenticated code execution before 1.3.0, KEV 2025-05-05)
- vLLM 8000 [checked] → https://docs.vllm.ai/en/latest/cli/serve.html (`--port` 8000) ; https://docs.vllm.ai/en/latest/usage/security.html ("Many other sensitive endpoints are exposed on the same HTTP server without any authentication enforcement", inter-node traffic "insecure by default")
- Apache Superset 8088 [checked] → https://github.com/apache/superset/blob/master/docker-compose.yml (`8088:8088`) ; https://github.com/apache/superset/blob/master/superset/config.py (SECRET_KEY must be overridden) ; https://nvd.nist.gov/vuln/detail/CVE-2023-27524 (KEV 2024-01-08)
- Triton Inference Server: dropped. https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/customization_guide/deploy.html says dynamic model loading is off by default, so it is not risky by default.

#### Big data
- Apache Spark REST submission 6066, master UI 8080, application UI 4040 [checked] → https://spark.apache.org/docs/latest/security.html ("Security features like authentication are not enabled by default", standalone ports table)
- Apache Flink 8081 [checked] → https://nightlies.apache.org/flink/flink-docs-stable/docs/deployment/config/ (`rest.port` 8081, `web.submit.enable` true by default) ; https://nightlies.apache.org/flink/flink-docs-stable/docs/deployment/security/security-ssl/ ("the REST endpoint does not authenticate clients")
- Apache Kafka Connect 8083 [checked] → https://kafka.apache.org/41/configuration/kafka-connect-configs/ (`listeners` default http://:8083) ; https://kafka.apache.org/community/cve-list/ (REST access escalates to file/environment read, SSRF and RCE: CVE-2024-31141, CVE-2025-27817, CVE-2025-27818)
- Apache ZooKeeper AdminServer 8080 [checked] → https://zookeeper.apache.org/doc/current/zookeeperAdmin.html (`admin.serverPort` 8080, enabled by default, client auth disabled, "Most administrative commands can be executed by any client")
- Apache Hadoop YARN 8032, 8042 [checked] → https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-common/yarn-default.xml ; HDFS DataNode 9864, 9866, 9867 [checked] → https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml ; risk → https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SecureMode.html (`simple`: "No authentication. (default)")
- Apache Hive HiveServer2 10000, Metastore 9083 [checked] → https://cwiki.apache.org/confluence/display/Hive/Configuration+Properties (`hive.server2.authentication` NONE: "no authentication check", `hive.metastore.sasl.enabled` false)
- Apache Druid 8888 [checked] → https://druid.apache.org/docs/latest/tutorials/ (console at localhost:8888, served by the router) ; https://druid.apache.org/docs/latest/operations/security-overview/ (security disabled by default, `allowAll` authorizer, ingestion tasks can read or write local files)
- Apache Zeppelin 8080 [checked] → https://zeppelin.apache.org/docs/latest/setup/operation/configuration.html (port 8080, bind 127.0.0.1) ; https://zeppelin.apache.org/docs/latest/setup/security/shiro_authentication.html ("By default, Zeppelin allows anonymous access")
- Apache NiFi 8080 before 1.14 [checked] → https://cwiki.apache.org/confluence/display/NIFI/Migration+Guidance ("The default port has been changed from 8080 to 8443") ; https://nifi.apache.org/docs/nifi-docs/html/administration-guide.html ("NiFi does not perform user authentication over HTTP. Using HTTP, all users will be granted all roles")
- Apache Airflow 8080 (1.x) [checked] → https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html (port 8080) ; https://airflow.apache.org/docs/apache-airflow/1.10.15/security.html ("By default, all gates are opened")
- Apache Livy 8998 [checked] → https://livy.apache.org/get-started/ ; https://livy.apache.org/docs/latest/rest-api.html (statement `code`: "The code to execute") ; https://github.com/apache/incubator-livy/blob/master/conf/livy.conf.template (Kerberos auth commented out)
- OpenSearch 9200 [checked] → https://docs.opensearch.org/docs/2.11/install-and-configure/install-opensearch/docker/ (demo config: "The default username and password are `admin`") ; https://docs.opensearch.org/latest/security/configuration/demo-configuration/ (2.12+ requires a custom admin password)
- Apache CouchDB Erlang distribution 9100-9200 [checked] → https://docs.couchdb.org/en/stable/setup/cluster.html (range chosen by the docs, "the only thing protecting you is the Erlang cookie") ; https://nvd.nist.gov/vuln/detail/CVE-2022-24706 (default install before 3.2.2, KEV 2022-08-25)
- Apache Ignite 10800, 47100, 47500 [checked] → https://ignite.apache.org/docs/latest/thin-clients/getting-started-with-thin-clients and https://ignite.apache.org/docs/latest/clustering/network-configuration ; risk → https://ignite.apache.org/docs/latest/security/authentication (off until `authenticationEnabled` is true)
- Hazelcast 5701 [checked] → https://docs.hazelcast.com/hazelcast/latest/clusters/network-configuration ; https://docs.hazelcast.com/hazelcast/latest/security/overview (security is an Enterprise feature, unsecured members and clients are supported)

#### Ops and developer tools
- Rundeck 4440 [checked] → https://docs.rundeck.com/docs/administration/install/linux-deb.html (localhost:4440, admin/admin) ; https://docs.rundeck.com/docs/administration/security/authentication.html (`realm.properties` admin:admin, user:user)
- Webmin 10000 [checked] → https://webmin.com/faq/ (port 10000, runs as root) ; https://nvd.nist.gov/vuln/detail/CVE-2019-15107 (backdoored 1.882 to 1.920, KEV 2022-03-25)
- distcc 3632 [checked] → https://www.distcc.org/security.html ("Anyone who can connect to the distcc server port can run arbitrary commands"; 3.0+ refuses to start without `--allow`) and IANA `distcc`
- Selenium Grid 4444 [checked] → https://www.selenium.dev/documentation/grid/getting_started/ ("must be protected from external access", otherwise outsiders can run custom binaries)
- Subversion svnserve 3690 [checked] → https://svnbook.red-bean.com/en/1.7/svn.serverconfig.svnserve.html (`anon-access` default read, data not encrypted)
- Git daemon 9418 [checked] → https://git-scm.com/docs/git-daemon (no authentication, anonymous read, push off by default)
- Jenkins UDP discovery udp:33848 [checked] → https://www.jenkins.io/security/advisory/2020-01-29/ (SECURITY-1641 / CVE-2020-2100, off by default since 2.219 and LTS 2.204.2)

#### Legacy and reflection protocols
- Finger 79 → https://www.rfc-editor.org/rfc/rfc1288 [checked] ; Ident 113 → https://www.rfc-editor.org/rfc/rfc1413 [checked] ; Active Users 11 → https://www.rfc-editor.org/rfc/rfc866 [checked]
- Character Generator udp:19 → https://www.rfc-editor.org/rfc/rfc864 ; Quote of the Day udp:17 → https://www.rfc-editor.org/rfc/rfc865 [checked] ; amplification factors → https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks [checked]
- WS-Discovery udp:3702 [checked] → same CISA alert (port 3702 and factor 10 to 500 stated there)
- SLP udp:427 → https://www.rfc-editor.org/rfc/rfc2608 §6.1 [checked] ; risk → https://www.cisa.gov/news-events/alerts/2023/04/25/abuse-service-location-protocol-may-lead-dos-attacks [checked]
- CUPS browsing udp:631 → https://nvd.nist.gov/vuln/detail/CVE-2024-47176 [checked: "binds to INADDR_ANY:631, causing it to trust any packet from any source"; not in KEV. The NVD text does not name UDP; UDP is the CUPS browsing transport]

#### SAP
- SAProuter 3299 [checked] → https://support.sap.com/en/tools/connectivity-tools/saprouter.html ("The default value for service is 3299") ; risk → https://www.cisa.gov/news-events/cybersecurity-advisories/aa19-122a (a misconfigured router "can act as an internal host and proxy the attacker's requests")
- SAP message server internal port 39NN [checked] → https://www.cisa.gov/news-events/cybersecurity-advisories/aa19-122a ("By default, Message Servers listen on a port 39XX and have no authentication")
- SAP start service 5NN13 / 5NN14 (sapstartsrv): dropped. The port is documented (https://help.sap.com/saphelp_em700_ehp01/helpdata/en/42/db8c45e873162ee10000000a1553f7/content.htm) but I found no public risk source.

#### Out-of-band
- Intel AMT 16992, 16993, 16994, 16995 [checked] → IANA `amt-soap-http`, `amt-soap-https`, `amt-redir-tcp`, `amt-redir-tls` (https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml?search=amt-) ; https://nvd.nist.gov/vuln/detail/CVE-2017-5689 (KEV 2022-01-28)

#### Retag reasons (risky-retag.txt)
Ports are already sourced in 07-demo-port-labels-sources.md. Sources for the reasons only:
- Checkmk agent 6556 [checked] → https://docs.checkmk.com/latest/en/agent_linux_legacy.html (legacy mode: unencrypted output on 6556; process table "can already provide valuable clues"; `only_from` IPs are spoofable)
- Docker Engine 2375 [checked] → https://docs.docker.com/engine/daemon/remote-access/ ("remote non-root users to gain root access on the host")
- Redis 6379 [checked] → https://redis.io/docs/latest/operate/oss_and_stack/management/security/
- Memcached 11211 [checked] → https://github.com/memcached/memcached/wiki/ConfiguringServer ("must not expose memcached directly to the internet, or otherwise any untrusted users") ; udp:11211 → CISA UDP amplification alert [checked]
- MongoDB 27017 [checked] → https://www.mongodb.com/docs/manual/core/authorization/ ("MongoDB does not enable access control by default")
- CouchDB 5984 [checked] → https://docs.couchdb.org/en/stable/whatsnew/3.0.html ("The Admin Party is now over")
- Elasticsearch 9200, Kibana 5601 [checked] → https://www.elastic.co/guide/en/elasticsearch/reference/7.17/security-minimal-setup.html (basic license: security disabled by default)
- Cassandra 9042, 7199 [checked] → https://cassandra.apache.org/doc/latest/cassandra/managing/operating/security.html (AllowAllAuthenticator, `cqlsh -u cassandra -p cassandra`, JMX localhost-only by default) ; JMX code execution → the Oracle JMX page above
- InfluxDB 8086 [checked] → https://docs.influxdata.com/influxdb/v1/administration/authentication_and_authorization/
- ClickHouse 8123, 9000 [checked] → https://github.com/ClickHouse/ClickHouse/blob/master/programs/server/users.xml (`<password></password>`, networks `::/0`)
- ZooKeeper 2181 [checked] → https://zookeeper.apache.org/doc/current/zookeeperAdmin.html (`enforce.auth.enabled` disabled by default)
- Kafka 9092 [checked] → https://github.com/apache/kafka/blob/trunk/docs/security/security-model.md ("accepts unauthenticated PLAINTEXT connections on every listener and applies no authorization")
- RabbitMQ 15672 [checked] → https://www.rabbitmq.com/docs/access-control ; 4369 and 25672 [checked] → https://www.rabbitmq.com/docs/clustering and https://www.erlang.org/doc/system/distributed.html (an insecure node gives "complete access to the node and by extension the cluster"; cleartext by default)
- MQTT 1883 [checked] → https://mosquitto.org/documentation/migrating-to-2-0/ (`allow_anonymous` "now defaults to false")
- NATS 4222 [checked] → https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro ("A server with no `authorization` block admits every connection")
- ActiveMQ 61616 [checked] → https://nvd.nist.gov/vuln/detail/CVE-2023-46604 (KEV 2023-11-02) ; 8161 [checked] → https://activemq.apache.org/components/classic/documentation/web-console (`admin/admin`)
- kubelet 10250 [checked] → https://kubernetes.io/docs/reference/access-authn-authz/kubelet-authn-authz/ (anonymous requests allowed, `AlwaysAllow` default). kubeadm overrides these defaults.
- etcd 2379-2380 [checked] → https://etcd.io/docs/v3.5/op-guide/security/ ("doesn't enable RBAC based authentication or the authentication feature in the transport layer by default")
- Docker Registry 5000 [checked] → https://distribution.github.io/distribution/about/deploying/ (access restriction is an added step)
- Jenkins 8080 [checked] → https://www.jenkins.io/doc/book/managing/script-console/
- Nexus 8081 [checked] → https://support.sonatype.com/hc/en-us/articles/213467158 (admin123 before 3.17.0) and https://help.sonatype.com/en/post-install-checklist.html
- SonarQube 9000 [checked via search extract] → https://docs.sonarsource.com/sonarqube-server/instance-administration/user-management/introduction (default admin/admin)
- MinIO 9000, 9001 [checked] → https://docs.min.io/enterprise/aistor-object-store/reference/aistor-server/settings/root-credentials/ (default `minioadmin`)
- Grafana 3000 [checked] → https://grafana.com/docs/grafana/latest/setup-grafana/sign-in-to-grafana/
- Prometheus 9090, Alertmanager 9093, node_exporter 9100 [checked] → https://prometheus.io/docs/operating/security/ (untrusted users are presumed to reach the HTTP endpoint; anyone reaching Alertmanager "can create, modify and delete silences"; TLS and basic auth are opt-in)
- Netdata 19999 [checked] → https://learn.netdata.cloud/docs/netdata-agent/securing-netdata-agents/
- Zabbix agent 10050 [checked] → https://www.zabbix.com/documentation/current/en/manual/appendix/config/zabbix_agentd (TLSAccept/TLSConnect default unencrypted, EnableRemoteCommands default 0)
- NRPE 5666 [checked] → https://github.com/NagiosEnterprises/nrpe/blob/master/SECURITY.md ("should be considered a security risk", "Always encrypt NRPE traffic!")
- Consul 8500 [checked] → https://developer.hashicorp.com/consul/docs/security/security-models/core ("Consul is not secure-by-default", script checks are a "remote code execution threat")
- Nomad 4646-4648 [checked] → https://developer.hashicorp.com/nomad/docs/concepts/security ("Nomad is not secure-by-default")
- Salt 4505, 4506 [checked] → https://nvd.nist.gov/vuln/detail/CVE-2020-11651 (KEV 2021-11-03)
- Hadoop 9870, 8020, 8088 and Spark 7077 [checked] → Hadoop SecureMode page and Spark security page above
- Solr 8983 [checked] → https://solr.apache.org/guide/solr/latest/deployment-guide/securing-solr.html ("No Solr API, including the Admin UI, is designed to be exposed to non-trusted parties")
- Jupyter 8888 [checked] → https://jupyter-server.readthedocs.io/en/latest/operators/security.html ("access to the Jupyter Server means access to running arbitrary code")
- Tomcat AJP 8009 [checked] → https://tomcat.apache.org/tomcat-9.0-doc/config/ajp.html and https://nvd.nist.gov/vuln/detail/CVE-2020-1938 (KEV 2022-03-03) ; Tomcat 8080 Manager [checked] → https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html
- WebLogic 7001 [checked] → https://nvd.nist.gov/vuln/detail/CVE-2023-21839 (unauthenticated via T3/IIOP, KEV 2023-05-01)
- IPMI udp:623 [checked] → https://www.cisa.gov/news-events/alerts/2013/07/26/risks-using-intelligent-platform-management-interface-ipmi
- Dell iDRAC 443 [checked] → https://www.dell.com/support/kbdoc/en-us/000133536/dell-poweredge-what-is-the-default-username-and-password-for-idrac
- SNMP udp:161 [checked] → https://www.cisa.gov/news-events/alerts/2017/06/05/reducing-risk-snmp-abuse
- Cisco Smart Install 4786, Telnet 23 [checked] → https://www.cisa.gov/news-events/alerts/2018/04/16/russian-state-sponsored-cyber-actors-targeting-network-infrastructure-devices
- FTP 21 → RFC 2577 [checked] ; TFTP udp:69 → RFC 1350 [checked] ; rlogin 513 → RFC 1282 [checked] ; NFS 2049 TCP/UDP → RFC 5531 (AUTH_SYS "known to be insecure due to the lack of a verifier") [checked] ; VNC 5900-5903 → RFC 6143 [checked] ; X11 6000-6063 → https://xorg.freedesktop.org/archive/current/doc/man/man7/Xsecurity.7.xhtml [checked] ; rsync 873 → https://download.samba.org/pub/rsync/rsyncd.conf.5 [checked]
- rexec 512, rsh 514 [unverified: BSD r-services have no RFC or vendor page; reason follows the RFC 1282 rlogin trust model]
- NTP udp:123 [checked] → https://www.cisa.gov/news-events/alerts/2014/01/13/ntp-amplification-attacks-using-cve-2013-5211 ; SSDP, mDNS, NetBIOS, CLDAP, rpcbind, RIPv1 amplification [checked] → CISA UDP amplification alert above
- LLMNR udp:5355, NBT-NS udp:137, SMB 445 and 139 [checked] → https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-278a (LLMNR/NBT-NS exploited "to compromise entire Windows' environments"; SMB default "does not require signing")
- LDAP 389 [checked] → https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server (unsigned binds open to replay and MITM; Event 2886 reminds that signing is not required)
- DNS 53 AXFR [checked] → https://www.cisa.gov/news-events/alerts/2015/04/13/dns-zone-transfer-axfr-requests-may-leak-domain-information
- PPTP 1723 [checked] → https://learn.microsoft.com/en-us/security-updates/securityadvisories/2012/2743314
- WSUS 8530 [checked] → https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/2-configure-wsus §2.3 ("the attacker can install malicious software on client computers")
- SMTP 25 → RFC 2505 (BCP 30) and RFC 5321 §3.5.2 [checked]
- VMware ESXi SLP 427 [checked] → https://nvd.nist.gov/vuln/detail/CVE-2021-21974 (OpenSLP in ESXi; the record has no KEV date)
- SAP gateway 3300-3399 [checked] → https://www.cisa.gov/news-events/cybersecurity-advisories/aa19-122a ("The default secinfo configuration ... allows any internal host to run OS commands anonymously")
- Guacamole guacd 4822 [checked, inferred] → https://guacamole.apache.org/doc/gug/guacamole-architecture.html (authentication is the web application's layer; guacd only listens for the web application). The manual does not state the exposure risk outright.

#### Dropped (no readable source, or not risky by default)
Oracle TNS listener poison (Oracle alert page returned 403), Splunk default `changeme` (docs.splunk.com returned 403), Firebird SYSDBA/masterkey (guide URL 404), Cisco HSRP default auth string, GlusterFS `auth.allow`, Apache Derby, HSQLDB, Jaeger UI, Trino, IBM MQ CHLAUTH, XDMCP udp:177 (IANA port found, no risk source), Apple ARMS udp:3283, echo udp:7, Cloudera Manager, Kubernetes Dashboard (no fixed port), GlassFish/Payara 4848, WildFly 9990 and WebLogic Node Manager 5556 (auth on by default), Triton (safe default), SAP start service (no public risk source), Veeam / NDMP / Data Protector / TeamCity / ScreenConnect / MikroTik Winbox (single-CVE issues, not default-config risks).
