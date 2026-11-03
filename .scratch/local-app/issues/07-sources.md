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
